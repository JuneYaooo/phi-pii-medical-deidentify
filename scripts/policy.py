import hashlib


BODY_SINGLE_MASK_LIMIT = 0.45
BODY_LINE_MASK_LIMIT = 0.60
FOOTER_PROSE_MASK_LIMIT = 0.30
FOOTER_PROSE_MIN_CHARS = 18
STAFF_LABELS = ("书写者", "报告医师", "审核医师", "报告医生", "审核医生", "医师", "医生", "护士")
STRUCTURED_SOURCES = {
    "header-footer-band",
    "identity-row-band",
    "identity-context-row",
    "masked-id-card-value",
    "masked-id-card-row",
    "patient-card-name",
    "english-patient-register-column",
}


def _record_text(records, record_index):
    if 0 <= record_index < len(records):
        return str(records[record_index].get("text") or "").strip()
    return ""


def _review_item(detection, reason):
    fingerprint = f"{detection['entity']}:{detection['source']}:{detection['record_index']}:{detection['box']}"
    return {
        "status": "needs_manual_review",
        "entity": detection["entity"],
        "source": detection["source"],
        "box": detection["box"],
        "reason": reason,
        "finding_hash": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16],
    }


def apply_balanced_policy(detections, image_size, records):
    width, height = image_size
    accepted = []
    review = []
    body_rows = []

    for detection in detections:
        box = detection["box"]
        box_width = max(0.0, box[2] - box[0])
        center_y = (box[1] + box[3]) / 2
        if detection["source"] == "header-footer-band":
            text = _record_text(records, detection["record_index"])
            if any(label in text for label in STAFF_LABELS):
                continue
            looks_like_prose = len(text) >= FOOTER_PROSE_MIN_CHARS and any(mark in text for mark in "，。；")
            if looks_like_prose and box_width / max(width, 1) > FOOTER_PROSE_MASK_LIMIT:
                review.append(_review_item(detection, "footer_clinical_prose_too_wide"))
                continue
        structured = detection["source"] in STRUCTURED_SOURCES or center_y <= height * 0.35
        if structured or box_width / max(width, 1) <= BODY_SINGLE_MASK_LIMIT:
            accepted.append(detection)
            if not structured:
                body_rows.append(detection)
        else:
            review.append(_review_item(detection, "single_body_mask_too_wide"))

    for detection in list(body_rows):
        box = detection["box"]
        center_y = (box[1] + box[3]) / 2
        row_height = max(1.0, box[3] - box[1])
        peers = [item for item in body_rows if abs(((item["box"][1] + item["box"][3]) / 2) - center_y) <= row_height * 0.8]
        intervals = sorted((item["box"][0], item["box"][2]) for item in peers)
        covered = 0.0
        current_start = current_end = None
        for start, end in intervals:
            if current_start is None:
                current_start, current_end = start, end
            elif start <= current_end:
                current_end = max(current_end, end)
            else:
                covered += current_end - current_start
                current_start, current_end = start, end
        if current_start is not None:
            covered += current_end - current_start
        if covered / max(width, 1) > BODY_LINE_MASK_LIMIT:
            for peer in peers:
                if peer in accepted:
                    accepted.remove(peer)
                    review.append(_review_item(peer, "body_row_mask_coverage_too_high"))

    return accepted, review
