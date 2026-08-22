#!/usr/bin/env python3
import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw

try:
    from . import detector, evaluation, pipeline
except ImportError:  # Direct script execution.
    import detector
    import evaluation
    import pipeline


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".bmp"}
PDF_EXTENSIONS = {".pdf"}
OFFICE_EXTENSIONS = {".docx", ".xlsx"}
TEXT_EXTENSIONS = {".txt", ".md", ".json", ".csv"}
GENERIC_NAME_TERMS = {"病例", "病例汇总", "测试病例", "交付物", "去隐私化测试", "检查报告", "病历材料"}
NON_NAME_DIRECTORY_HINTS = (
    "癌", "病", "肿瘤", "患者", "队列", "样本", "病例", "报告", "检查", "检验", "化验",
    "影像", "用药", "记录", "汇总", "测试", "手术", "住院", "门诊", "资料", "文档",
    "医院", "诊所", "中心", "大学", "公司", "集团", "研究院", "卫生院", "科室",
)
POLICY_VERSION = "2026-08-22.6"


def classify_path(path):
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in PDF_EXTENSIONS:
        return "pdf"
    if suffix in OFFICE_EXTENSIONS:
        return "office"
    if suffix in TEXT_EXTENSIONS:
        return "text"
    return "unsupported"


def source_name_terms(path, root):
    try:
        parts = path.resolve().relative_to(root.resolve()).parts[:-1]
    except (ValueError, OSError):
        parts = path.parts[:-1]
    terms = set()
    for part in parts:
        token = part.strip()
        if not re.fullmatch(r"[\u4e00-\u9fff·]{2,4}", token):
            continue
        if token in GENERIC_NAME_TERMS:
            continue
        if any(word in token for word in NON_NAME_DIRECTORY_HINTS):
            continue
        terms.add(token)
    filename_match = re.match(
        r"(?P<name>[\u4e00-\u9fff·]{2,4})(?=出院|住院|病历|病例|检查|检验|报告|资料)",
        path.stem,
    )
    if filename_match:
        candidate = filename_match.group("name")
        if candidate not in GENERIC_NAME_TERMS and not any(word in candidate for word in NON_NAME_DIRECTORY_HINTS):
            terms.add(candidate)
    return tuple(sorted(terms, key=lambda value: (-len(value), value)))


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_context_hash(source_digest, source_terms):
    payload = "\0".join((source_digest, *source_terms)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class PaddleOCRAdapter:
    MODEL_NAMES = {
        "PP-OCRv6_tiny": ("PP-OCRv6_tiny_det", "PP-OCRv6_tiny_rec"),
        "PP-OCRv6_small": ("PP-OCRv6_small_det", "PP-OCRv6_small_rec"),
        "PP-OCRv6_medium": ("PP-OCRv6_medium_det", "PP-OCRv6_medium_rec"),
    }

    def __init__(self, model_name="PP-OCRv6_medium"):
        from paddleocr import PaddleOCR

        detection_model, recognition_model = self.MODEL_NAMES[model_name]
        self.ocr = PaddleOCR(
            text_detection_model_name=detection_model,
            text_recognition_model_name=recognition_model,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

    def records(self, image):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "ocr-input.png"
            image.convert("RGB").save(input_path)
            records = []
            for result in self.ocr.predict(str(input_path)):
                records.extend(detector.normalize_records(result.json))
            return records


def downscale_large_image(image, max_side=2600):
    image = image.convert("RGB")
    if max(image.size) <= max_side:
        return image
    resized = image.copy()
    resized.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return resized


def open_image(path):
    if path.suffix.lower() in {".heic", ".heif"}:
        from pillow_heif import register_heif_opener

        register_heif_opener()
    return downscale_large_image(Image.open(path))


def write_image(image, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".jpg", ".jpeg"}:
        image.save(path, quality=95)
    else:
        image.save(path)


def redacted_output_path(directory, doc_id, source_path, material_type):
    if material_type == "image":
        suffix = ".jpg" if source_path.suffix.lower() in {".heic", ".heif"} else source_path.suffix.lower()
    elif material_type == "office" and source_path.suffix.lower() == ".docx" and not docx_contains_media(source_path):
        suffix = ".docx"
    elif material_type in {"pdf", "office"}:
        suffix = ".pdf"
    else:
        suffix = source_path.suffix.lower()
    return directory / f"{doc_id}{suffix}"


def clone_duplicate_artifacts(source_doc_id, doc_id, source_result, source_output, output_path, directories):
    result = copy.deepcopy(source_result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_output, output_path)
    for source_thumbnail in sorted(directories["thumbnails"].glob(f"{source_doc_id}_p*.jpg")):
        target_thumbnail = directories["thumbnails"] / source_thumbnail.name.replace(source_doc_id, doc_id, 1)
        shutil.copy2(source_thumbnail, target_thumbnail)
    for page_number, page_report in enumerate(result.get("page_reports") or [], 1):
        page_report["thumbnail"] = str(directories["thumbnails"] / f"{doc_id}_p{page_number:03d}.jpg")
    result["doc_id"] = doc_id
    return result


def serializable_result(result):
    return {key: value for key, value in result.items() if key != "image"}


def process_image(path, output_path, ocr, source_terms, max_rounds):
    result = pipeline.redact_image(
        open_image(path), ocr, source_terms=source_terms, max_rounds=max_rounds, auto_rotate=True
    )
    write_image(result["image"], output_path)
    report = serializable_result(result)
    report["pages"] = 1
    return report, [result["image"]]


def render_pdf(path):
    import pypdfium2 as pdfium

    document = pdfium.PdfDocument(str(path))
    for page_number in range(len(document)):
        page = document[page_number]
        yield page_number + 1, page.render(scale=2).to_pil().convert("RGB")


def process_pdf(path, output_path, ocr, source_terms, max_rounds):
    pages = []
    page_reports = []
    for page_number, image in render_pdf(path):
        result = pipeline.redact_image(
            image, ocr, source_terms=source_terms, max_rounds=max_rounds, auto_rotate=True
        )
        pages.append(result["image"])
        report = serializable_result(result)
        report["page"] = page_number
        page_reports.append(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if pages:
        pages[0].save(output_path, save_all=True, append_images=pages[1:])
    return {
        "pages": len(pages),
        "detections": sum(item["detections"] for item in page_reports),
        "residual_detections": sum(item["residual_detections"] for item in page_reports),
        "manual_review": [finding for item in page_reports for finding in item["manual_review"]],
        "page_reports": page_reports,
    }, pages or [Image.new("RGB", (100, 100), "white")]


def convert_office_to_pdf(path):
    directory = Path(tempfile.mkdtemp(prefix="medical-record-redaction-"))
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(directory), str(path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    candidates = list(directory.glob("*.pdf"))
    if not candidates:
        shutil.rmtree(directory, ignore_errors=True)
        raise RuntimeError(f"Office conversion produced no PDF: {path}")
    return candidates[0], directory


TEXT_PATTERNS = (
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "[电话]"),
    (re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?[2-9]\d{2}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)"), "[电话]"),
    (re.compile(r"(?<!\d)[1-9]\d{16}[\dXx](?![\dXx])"), "[身份证]"),
    (re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), "[邮箱]"),
)
BANK_CARD_TEXT_RE = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


def _label_pattern(labels, value_pattern):
    label_expression = "|".join(re.escape(label) for label in sorted(labels, key=len, reverse=True))
    return re.compile(
        rf"(?P<label>{label_expression})(?P<separator>\s*[：:]?\s*)(?P<value>{value_pattern})",
        re.MULTILINE,
    )


TEXT_LABELED_PATTERNS = (
    (_label_pattern(detector.LABELS["NAME"], r"[\u4e00-\u9fff·]{2,4}"), "[姓名]"),
    (_label_pattern(
        detector.LABELS["ADDRESS"],
        r"[^\n,，;；]{4,}?(?=\s+(?:诊断|临床诊断|性别|年龄|出生日期|病历号|住院号|门诊号)[：:]|$)",
    ), "[地址]"),
    (_label_pattern(
        detector.LABELS["BIRTH_DATE"],
        r"(?:\d{4}[-./年]\d{1,2}[-./月]\d{1,2}日?|\d{1,2}[-./]\d{1,2}[-./]\d{4}|\d{8})",
    ), "[出生日期]"),
    (_label_pattern(detector.LABELS["BANK_CARD"], r"\d[\d -]{11,25}\d"), "[银行卡]"),
    (_label_pattern(
        detector.LABELS["PHONE"],
        r"(?:\+?86[- ]?)?(?:1[3-9]\d{9}|0\d{2,3}[- ]?\d{7,8}(?:-\d{1,6})?)|(?:\+?1[-. ]?)?\(?[2-9]\d{2}\)?[-. ]\d{3}[-. ]\d{4}",
    ), "[电话]"),
    (_label_pattern(detector.LABELS["ID_NUMBER"], r"[A-Za-z0-9][A-Za-z0-9\-]{5,23}"), "[证件号]"),
    (_label_pattern(detector.LABELS["MEDICAL_ID"], r"[A-Za-z0-9][A-Za-z0-9_./\-]{1,}"), "[医疗编号]"),
)


def redact_native_text(text):
    redacted = text
    detections = 0
    for pattern, replacement in TEXT_LABELED_PATTERNS:
        redacted, count = pattern.subn(
            lambda match: f"{match.group('label')}{match.group('separator')}{replacement}",
            redacted,
        )
        detections += count
    for pattern, replacement in TEXT_PATTERNS:
        redacted, count = pattern.subn(replacement, redacted)
        detections += count
    parts = []
    cursor = 0
    for match in BANK_CARD_TEXT_RE.finditer(redacted):
        if not detector.valid_luhn(match.group(0)):
            continue
        parts.extend((redacted[cursor:match.start()], "[银行卡]"))
        cursor = match.end()
        detections += 1
    if parts:
        parts.append(redacted[cursor:])
        redacted = "".join(parts)
    residuals = sum(len(pattern.findall(redacted)) for pattern, _ in TEXT_LABELED_PATTERNS)
    residuals += sum(len(pattern.findall(redacted)) for pattern, _ in TEXT_PATTERNS)
    residuals += sum(
        detector.valid_luhn(match.group(0)) for match in BANK_CARD_TEXT_RE.finditer(redacted)
    )
    return redacted, detections, residuals


def process_text(path, output_path):
    text = path.read_text(encoding="utf-8", errors="replace")
    redacted, detections, residuals = redact_native_text(text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(redacted, encoding="utf-8")
    manual_review = []
    if text.strip():
        manual_review.append({
            "status": "needs_manual_review",
            "entity": "TEXT_REVIEW",
            "source": "deterministic-text-redaction",
            "box": [],
            "reason": "text_requires_tool_or_manual_review",
            "finding_hash": hashlib.sha256(b"text-requires-review").hexdigest()[:16],
        })
    return {
        "pages": 0,
        "detections": detections,
        "residual_detections": residuals,
        "residual_by_entity": {"TEXT_REDACTION": residuals} if residuals else {},
        "manual_review": manual_review,
    }, [Image.new("RGB", (100, 100), "white")]


def docx_contains_media(path):
    try:
        with ZipFile(path) as archive:
            return any(
                name.startswith("word/media/") and not name.endswith("/")
                for name in archive.namelist()
            )
    except (OSError, ValueError):
        return True


def _redact_xml_text(root):
    detections = 0
    residuals = 0
    handled = set()

    # Word often splits one logical value across several styled runs. Redact
    # the joined paragraph so values such as a patient name cannot evade a
    # deterministic rule merely because they cross a run boundary.
    for paragraph in (node for node in root.iter() if node.tag.endswith("}p")):
        text_nodes = [node for node in paragraph.iter() if node.tag.endswith("}t")]
        if not text_nodes:
            continue
        joined = "".join(node.text or "" for node in text_nodes)
        protected, found, remaining = redact_native_text(joined)
        text_nodes[0].text = protected
        for node in text_nodes[1:]:
            node.text = ""
        handled.update(id(node) for node in text_nodes)
        detections += found
        residuals += remaining

    for node in (item for item in root.iter() if item.tag.endswith("}t") and id(item) not in handled):
        protected, found, remaining = redact_native_text(node.text or "")
        node.text = protected
        detections += found
        residuals += remaining
    return detections, residuals


def process_docx(path, output_path):
    detections = 0
    residuals = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(path) as source, ZipFile(output_path, "w", ZIP_DEFLATED) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename.startswith("word/") and info.filename.endswith(".xml"):
                root = ElementTree.fromstring(data)
                found, remaining = _redact_xml_text(root)
                detections += found
                residuals += remaining
                data = ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)
            elif info.filename == "docProps/core.xml":
                root = ElementTree.fromstring(data)
                for node in root.iter():
                    if node.tag.rsplit("}", 1)[-1] in {"creator", "lastModifiedBy"} and (node.text or "").strip():
                        node.text = "[已移除]"
                data = ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)
            target.writestr(info, data)

    # Verify the actual stored package, rather than trusting only the in-memory
    # replacements above.
    verified_residuals = 0
    with ZipFile(output_path) as archive:
        for name in archive.namelist():
            if not (name.startswith("word/") and name.endswith(".xml")):
                continue
            root = ElementTree.fromstring(archive.read(name))
            stored_text = "".join(
                node.text or "" for node in root.iter() if node.tag.endswith("}t")
            )
            _, _, remaining = redact_native_text(stored_text)
            verified_residuals += remaining
    residuals = max(residuals, verified_residuals)
    return {
        "pages": 0,
        "detections": detections,
        "residual_detections": residuals,
        "residual_by_entity": {"DOCX_TEXT_REDACTION": residuals} if residuals else {},
        "manual_review": [],
        "native_text_redaction": True,
    }, [Image.new("RGB", (100, 100), "white")]


def save_thumbnail(image, path, doc_id, detections, residual):
    thumbnail = image.copy()
    thumbnail.thumbnail((360, 500))
    canvas = Image.new("RGB", (390, 560), "white")
    canvas.paste(thumbnail, ((390 - thumbnail.width) // 2, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 515), doc_id, fill="black")
    draw.text((10, 535), f"det={detections} residual={residual}", fill="black")
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, quality=90)


def build_contact_sheets(thumbnail_dir, output_dir):
    paths = sorted(thumbnail_dir.glob("*.jpg"))
    output_dir.mkdir(parents=True, exist_ok=True)
    result = []
    for offset in range(0, len(paths), 20):
        canvas = Image.new("RGB", (1560, 2800), (235, 235, 235))
        for index, path in enumerate(paths[offset:offset + 20]):
            image = Image.open(path).convert("RGB")
            canvas.paste(image, ((index % 4) * 390, (index // 4) * 560))
        output_path = output_dir / f"contact_sheet_{offset // 20 + 1:03d}.jpg"
        canvas.save(output_path, quality=92)
        result.append(str(output_path))
    return result


def collect_files(input_path, excluded_roots=()):
    if input_path.is_file():
        return [input_path]
    excluded = tuple(Path(path).expanduser().resolve() for path in excluded_roots)
    return [
        path for path in sorted(input_path.rglob("*"))
        if path.is_file() and not any(root == path.resolve() or root in path.resolve().parents for root in excluded)
    ]


def report_matches_run(existing, source_digest, context_digest, output_path, model, max_rounds):
    return (
        existing.get("source_hash") == source_digest
        and existing.get("source_context_hash") == context_digest
        and existing.get("policy_version") == POLICY_VERSION
        and existing.get("ocr_model") == model
        and existing.get("max_rounds") == max_rounds
        and output_path.exists()
        and existing.get("artifact_hash") == file_hash(output_path)
    )


def run(args):
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.resume_run or args.output_dir).expanduser().resolve()
    directories = {
        "redacted": output_dir / "redacted_files",
        "reports": output_dir / "reports",
        "thumbnails": output_dir / "audit_thumbnails",
        "sheets": output_dir / "audit_contact_sheets",
    }
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)

    requested_indexes = {int(value) for value in args.only_indices.split(",")} if args.only_indices else None
    excluded_roots = [output_dir]
    excluded_roots.extend(Path(value).expanduser().resolve() for value in args.exclude)
    files = collect_files(input_path, excluded_roots)
    ocr = None
    items = []
    unsupported = []
    processed_by_content = {}

    for index, path in enumerate(files, 1):
        if requested_indexes is not None and index not in requested_indexes:
            continue
        doc_id = f"doc_{index:04d}"
        report_path = directories["reports"] / f"{doc_id}.json"
        material_type = classify_path(path)
        if material_type == "unsupported":
            unsupported.append({"doc_id": doc_id, "suffix": path.suffix.lower() or "<none>"})
            continue
        terms = source_name_terms(path, input_path if input_path.is_dir() else input_path.parent)
        output_path = redacted_output_path(directories["redacted"], doc_id, path, material_type)
        source_digest = file_hash(path)
        context_digest = source_context_hash(source_digest, terms)
        needs_ocr = material_type in {"image", "pdf"} or (
            material_type == "office"
            and not (path.suffix.lower() == ".docx" and not docx_contains_media(path))
        )
        report_model = args.model if needs_ocr else None
        report_max_rounds = args.max_rounds if needs_ocr else None
        if report_path.exists() and not args.force:
            existing = json.loads(report_path.read_text(encoding="utf-8"))
            report_matches_source = report_matches_run(
                existing,
                source_digest,
                context_digest,
                output_path,
                report_model,
                report_max_rounds,
            )
            if report_matches_source:
                if existing.get("kind") == "image":
                    existing.setdefault("pages", 1)
                items.append(existing)
                content_key = (source_digest, material_type, output_path.suffix.lower(), terms)
                processed_by_content.setdefault(content_key, (doc_id, existing, output_path))
                continue
        content_key = (source_digest, material_type, output_path.suffix.lower(), terms)
        duplicate = processed_by_content.get(content_key)
        if duplicate:
            source_doc_id, source_result, source_output = duplicate
            result = clone_duplicate_artifacts(
                source_doc_id,
                doc_id,
                source_result,
                source_output,
                output_path,
                directories,
            )
            result.update({
                "doc_id": doc_id,
                "kind": material_type,
                "policy_version": POLICY_VERSION,
                "ocr_model": report_model,
                "max_rounds": report_max_rounds,
                "source_hash": source_digest,
                "source_context_hash": context_digest,
                "artifact_hash": file_hash(output_path),
                "suffix": path.suffix.lower(),
                "deduplicated_from": source_doc_id,
            })
            report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            items.append(result)
            processed_by_content[content_key] = (doc_id, result, output_path)
            continue
        if needs_ocr and ocr is None:
            ocr = PaddleOCRAdapter(args.model)
        if material_type == "image":
            result, previews = process_image(path, output_path, ocr, terms, args.max_rounds)
        elif material_type == "pdf":
            result, previews = process_pdf(path, output_path, ocr, terms, args.max_rounds)
        elif material_type == "office":
            if path.suffix.lower() == ".docx" and not docx_contains_media(path):
                result, previews = process_docx(path, output_path)
            else:
                converted, temporary_directory = convert_office_to_pdf(path)
                try:
                    result, previews = process_pdf(converted, output_path, ocr, terms, args.max_rounds)
                finally:
                    shutil.rmtree(temporary_directory, ignore_errors=True)
        else:
            result, previews = process_text(path, output_path)
        result.update({
            "doc_id": doc_id,
            "kind": material_type,
            "policy_version": POLICY_VERSION,
            "ocr_model": report_model,
            "max_rounds": report_max_rounds,
            "source_hash": source_digest,
            "source_context_hash": context_digest,
            "artifact_hash": file_hash(output_path),
            "suffix": path.suffix.lower(),
        })
        for page_number, preview in enumerate(previews, 1):
            page_report = result.get("page_reports", [{}] * len(previews))[page_number - 1]
            thumbnail_path = directories["thumbnails"] / f"{doc_id}_p{page_number:03d}.jpg"
            save_thumbnail(
                preview,
                thumbnail_path,
                f"{doc_id} p{page_number}",
                page_report.get("detections", result["detections"]),
                page_report.get("residual_detections", result["residual_detections"]),
            )
            if result.get("page_reports"):
                page_report["thumbnail"] = str(thumbnail_path)
        report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        items.append(result)
        processed_by_content[content_key] = (doc_id, result, output_path)

    summary = evaluation.summarize(items)
    summary.update({
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "unsupported_files": unsupported,
        "contact_sheets": build_contact_sheets(directories["thumbnails"], directories["sheets"]),
        "items": items,
    })
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "summary.md").write_text(evaluation.render_markdown(summary), encoding="utf-8")
    return summary


def build_parser():
    parser = argparse.ArgumentParser(description="Redact Chinese medical-record materials with local OCR.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--resume-run")
    parser.add_argument("--only-indices")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-rounds", type=int, default=2, choices=(1, 2))
    parser.add_argument("--model", default="PP-OCRv6_medium", choices=tuple(PaddleOCRAdapter.MODEL_NAMES))
    parser.add_argument("--exclude", action="append", default=[], help="Directory tree to exclude; repeatable.")
    return parser


def main():
    summary = run(build_parser().parse_args())
    print(json.dumps({key: summary[key] for key in ("documents", "pages", "residual_detections")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
