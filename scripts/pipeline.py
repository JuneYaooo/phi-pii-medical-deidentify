import hashlib
import statistics

from PIL import ImageDraw

try:
    from . import detector, policy
except ImportError:  # Direct script execution.
    import detector
    import policy


def _safe_detection(detection):
    return {
        "entity": detection["entity"],
        "source": detection["source"],
        "record_index": detection["record_index"],
        "box": detection["box"],
    }


def _padded_box(box, width, height, padding):
    return [
        max(0, int(box[0] - padding)),
        max(0, int(box[1] - padding)),
        min(width, int(box[2] + padding)),
        min(height, int(box[3] + padding)),
    ]


def _draw_boxes(image, detections, padding):
    draw = ImageDraw.Draw(image)
    for detection in detections:
        draw.rectangle(_padded_box(detection["box"], image.width, image.height, padding), fill="#000000")


def _dedupe_reviews(findings):
    result = []
    seen = set()
    for finding in findings:
        key = finding.get("finding_hash") or (
            finding.get("entity"),
            finding.get("source"),
            tuple(finding.get("box") or ()),
            finding.get("reason"),
        )
        if key not in seen:
            seen.add(key)
            result.append(finding)
    return result


def _final_review_item(detection):
    fingerprint = f"final:{detection['entity']}:{detection['source']}:{detection['record_index']}:{detection['box']}"
    return {
        "status": "needs_manual_review",
        "entity": detection["entity"],
        "source": detection["source"],
        "box": detection["box"],
        "reason": "final_sensitive_detection_remaining",
        "finding_hash": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
    }


def _sparse_ocr_review(image_size):
    width, height = image_size
    fingerprint = f"sparse-ocr:{width}x{height}"
    return {
        "status": "needs_manual_review",
        "entity": "OCR_QUALITY",
        "source": "orientation-fallback",
        "box": [0, 0, width, height],
        "reason": "ocr_records_too_sparse",
        "finding_hash": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
    }


def _low_confidence_review(image_size):
    width, height = image_size
    fingerprint = f"low-confidence-ocr:{width}x{height}"
    return {
        "status": "needs_manual_review",
        "entity": "OCR_QUALITY",
        "source": "ocr-confidence",
        "box": [0, 0, width, height],
        "reason": "ocr_confidence_too_low",
        "finding_hash": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
    }


def _unstructured_low_confidence_review(records, image_size, threshold=0.75, minimum_records=20):
    label_hits, median_score, _, record_count = _record_quality(records)
    if record_count < minimum_records or label_hits or median_score >= threshold:
        return None
    width, height = image_size
    fingerprint = f"unstructured-low-confidence:{width}x{height}:{record_count}:{median_score:.3f}"
    return {
        "status": "needs_manual_review",
        "entity": "OCR_QUALITY",
        "source": "ocr-confidence",
        "box": [0, 0, width, height],
        "reason": "unstructured_low_confidence_text_requires_review",
        "finding_hash": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
    }


def _english_patient_register_review(records, image_size):
    text = " ".join(str(record.get("text") or "") for record in records).upper()
    name_anchor = any(anchor in text for anchor in (
        "NAME OF PATIENT",
        "PATIENT NAME",
        "CHRISTIAN AND SURNAME",
    ))
    register_context = "REGISTER" in text or any(anchor in text for anchor in (
        "DATE OF ADMISSION",
        "DATE OF DISCHARGE",
        "PLACE OF ABODE",
        "PREVIOUS OCCUPATION",
    ))
    if not name_anchor or not register_context:
        return None
    width, height = image_size
    fingerprint = f"english-patient-register:{width}x{height}"
    return {
        "status": "needs_manual_review",
        "entity": "NAME",
        "source": "document-structure",
        "box": [0, 0, width, height],
        "reason": "english_patient_register_requires_review",
        "finding_hash": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
    }


def _irregular_text_geometry_review(records, image_size, threshold=0.35):
    heights = [
        max(1.0, float(record["box"][3]) - float(record["box"][1]))
        for record in records
        if record.get("box") and len(record["box"]) == 4
    ]
    if len(heights) < 8:
        return None
    variation = statistics.pstdev(heights) / max(statistics.mean(heights), 1.0)
    if variation <= threshold:
        return None
    width, height = image_size
    fingerprint = f"irregular-text-geometry:{width}x{height}:{variation:.3f}"
    return {
        "status": "needs_manual_review",
        "entity": "DOCUMENT_QUALITY",
        "source": "ocr-layout-heuristic",
        "box": [0, 0, width, height],
        "reason": "irregular_text_geometry_requires_review",
        "finding_hash": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
    }


def _large_text_geometry_review(records, image_size, threshold=0.06):
    heights = [
        max(1.0, float(record["box"][3]) - float(record["box"][1]))
        for record in records
        if record.get("box") and len(record["box"]) == 4
    ]
    if len(heights) < 8:
        return None
    _, height = image_size
    median_ratio = statistics.median(heights) / max(float(height), 1.0)
    if median_ratio <= threshold:
        return None
    fingerprint = f"large-text-geometry:{image_size[0]}x{height}:{median_ratio:.3f}"
    return {
        "status": "needs_manual_review",
        "entity": "DOCUMENT_QUALITY",
        "source": "ocr-layout-heuristic",
        "box": [0, 0, image_size[0], height],
        "reason": "large_text_geometry_requires_review",
        "finding_hash": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
    }


def _sensitive_low_confidence_reviews(records, accepted=(), threshold=0.3):
    accepted_entities = {}
    for detection in accepted:
        index = detection["record_index"]
        entity = detection["entity"]
        current = accepted_entities.get(index)
        if current in {None, "IDENTITY_ROW", "HEADER_FOOTER_TEXT"}:
            accepted_entities[index] = entity
    findings = []
    for index, record in enumerate(records):
        if record.get("score") is None or float(record["score"]) >= threshold:
            continue
        entity = accepted_entities.get(index)
        if not entity:
            entity, _ = detector.label_for_text(record["text"])
        if not entity:
            direct = detector.direct_detections([record])
            entity = direct[0]["entity"] if direct else None
        if not entity:
            continue
        box = list(record["box"])
        fingerprint = f"sensitive-low-confidence:{entity}:{index}:{box}"
        findings.append({
            "status": "needs_manual_review",
            "entity": entity,
            "source": "ocr-confidence-sensitive-field",
            "box": box,
            "reason": "sensitive_ocr_confidence_too_low",
            "finding_hash": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
        })
    return findings


def _record_quality(records):
    scores = [float(record["score"]) for record in records if record.get("score") is not None]
    median_score = statistics.median(scores) if scores else (1.0 if records else 0.0)
    label_hits = sum(1 for record in records if detector.label_for_text(record["text"])[0])
    chinese_chars = sum(
        sum("\u4e00" <= character <= "\u9fff" for character in record["text"])
        for record in records
    )
    return label_hits, median_score, chinese_chars, len(records)


def _best_oriented_records(image, ocr):
    base_records = detector.normalize_records(ocr.records(image))
    base_quality = _record_quality(base_records)
    candidates = [(base_quality, 0, image, base_records)]
    if not base_records or base_quality[1] < 0.75:
        for angle in (90, 270, 180):
            rotated = image.rotate(angle, expand=True)
            records = detector.normalize_records(ocr.records(rotated))
            candidates.append((_record_quality(records), angle, rotated, records))
    _, angle, oriented, records = max(candidates, key=lambda item: item[0])
    return oriented, records, angle


def redact_image(image, ocr, source_terms=(), max_rounds=2, padding=8, auto_rotate=False):
    current = image.convert("RGB").copy()
    audit_rounds = []
    manual_review = []
    rotation_degrees = 0

    for round_number in range(1, max_rounds + 1):
        if round_number == 1 and auto_rotate:
            current, records, rotation_degrees = _best_oriented_records(current, ocr)
            if len(records) < 3:
                manual_review.append(_sparse_ocr_review(current.size))
        else:
            records = detector.normalize_records(ocr.records(current))
        if round_number == 1 and records and _record_quality(records)[1] < 0.5:
            manual_review.append(_low_confidence_review(current.size))
        if round_number == 1:
            unstructured_confidence = _unstructured_low_confidence_review(records, current.size)
            if unstructured_confidence:
                manual_review.append(unstructured_confidence)
            patient_register = _english_patient_register_review(records, current.size)
            if patient_register:
                manual_review.append(patient_register)
            irregular_geometry = _irregular_text_geometry_review(records, current.size)
            if irregular_geometry:
                manual_review.append(irregular_geometry)
            large_geometry = _large_text_geometry_review(records, current.size)
            if large_geometry:
                manual_review.append(large_geometry)
        detections = detector.detect(records, current.size, tuple(source_terms))
        accepted, review = policy.apply_balanced_policy(detections, current.size, records)
        if round_number == 1:
            manual_review.extend(_sensitive_low_confidence_reviews(records, accepted))
        manual_review.extend(review)
        audit_rounds.append({
            "round": round_number,
            "detections": [_safe_detection(item) for item in accepted],
            "manual_review": review,
        })
        if not accepted:
            break
        _draw_boxes(current, accepted, padding)

    final_records = detector.normalize_records(ocr.records(current))
    final_detections = detector.detect(final_records, current.size, tuple(source_terms))
    residual, final_review = policy.apply_balanced_policy(final_detections, current.size, final_records)
    manual_review.extend(final_review)
    manual_review.extend(_final_review_item(detection) for detection in residual)
    return {
        "image": current,
        "rotation_degrees": rotation_degrees,
        "rounds": len(audit_rounds),
        "audit_rounds": audit_rounds,
        "detections": sum(len(item["detections"]) for item in audit_rounds),
        "residual_detections": len(residual),
        "residual_by_entity": _count_by_entity(residual),
        "manual_review": _dedupe_reviews(manual_review),
    }


def _count_by_entity(detections):
    counts = {}
    for detection in detections:
        entity = detection["entity"]
        counts[entity] = counts.get(entity, 0) + 1
    return counts
