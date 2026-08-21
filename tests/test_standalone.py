import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))

from scripts import detector, pipeline  # noqa: E402
from scripts.deidentify import (  # noqa: E402
    POLICY_VERSION,
    file_hash,
    redact_native_text,
    report_matches_run,
    source_name_terms,
)
from scripts.evaluate_labeled_set import evaluate_text_pair  # noqa: E402
from scripts.validate_skill import validate  # noqa: E402


def test_text_rules_mask_identity_and_preserve_clinical_text():
    text = (
        "姓名：张三 手机：13800138000 身份证号：11010519491231002X "
        "处方号：RX20250315001 银行卡：6222020202020202026 诊断：高血压"
    )
    redacted, detections, residuals = redact_native_text(text)

    assert detections >= 5
    assert residuals == 0
    assert "张三" not in redacted
    assert "13800138000" not in redacted
    assert "11010519491231002X" not in redacted
    assert "RX20250315001" not in redacted
    assert "6222020202020202026" not in redacted
    assert "高血压" in redacted


def test_unlabeled_text_bank_card_requires_luhn():
    redacted, detections, residuals = redact_native_text(
        "付款号 6222020202020202026；订单号 6222020202020202027"
    )

    assert detections == 1
    assert residuals == 0
    assert "6222020202020202026" not in redacted
    assert "6222020202020202027" in redacted


def test_detector_reassembles_split_phone_and_maps_back_to_boxes():
    records = [
        {"text": "患者电话", "box": [10, 10, 80, 30]},
        {"text": "138", "box": [90, 10, 120, 30]},
        {"text": "0013", "box": [124, 10, 164, 30]},
        {"text": "8000", "box": [168, 10, 208, 30]},
    ]
    detections = detector.detect(records, image_size=(500, 300))

    assert any(item["entity"] == "PHONE" for item in detections)
    phone_boxes = [item["box"] for item in detections if item["entity"] == "PHONE"]
    assert all(box[0] >= 90 for box in phone_boxes)


def test_north_american_phone_is_masked_in_images_and_native_text():
    records = [{"text": "Contact (212) 555-1234", "box": [10, 10, 260, 35]}]

    detections = detector.detect(records, image_size=(500, 300))
    redacted, count, residuals = redact_native_text("Contact (212) 555-1234")

    assert any(item["entity"] == "PHONE" for item in detections)
    assert count == 1
    assert residuals == 0
    assert "555-1234" not in redacted


def test_burned_in_medical_image_header_masks_name_sex_and_birth_date():
    records = [
        {"text": "KAUFMAN SCOTT [M] 03.09.2012", "box": [0, 0, 230, 12]},
        {"text": "DOB: 07.22.1943", "box": [1, 12, 116, 28]},
    ]

    detections = detector.detect(records, image_size=(394, 552))
    entities = {item["entity"] for item in detections}

    assert "IDENTITY_ROW" in entities
    assert "BIRTH_DATE" in entities
    assert all(item["box"][1] <= 28 for item in detections)


def test_medical_identifier_labels_mask_values_and_preserve_nearby_batch_number():
    records = [
        {"text": "处方号：RX20250315001", "box": [10, 10, 230, 35]},
        {"text": "医保卡号：YB202500123456", "box": [10, 45, 270, 70]},
        {"text": "检验单号", "box": [10, 80, 90, 105]},
        {"text": "LAB20250315001", "box": [100, 80, 260, 105]},
        {"text": "药品批号：LOT20250315001", "box": [10, 120, 270, 145]},
    ]

    detections = detector.detect(records, image_size=(600, 400))
    medical_indexes = {
        item["record_index"] for item in detections if item["entity"] == "MEDICAL_ID"
    }

    assert {0, 1, 3}.issubset(medical_indexes)
    assert 4 not in medical_indexes


def test_header_year_serial_medical_id_is_masked_but_dates_are_preserved():
    records = [
        {"text": "某医院临床病理诊断报告", "box": [90, 10, 360, 40]},
        {"text": "2024-53821", "box": [420, 45, 540, 70]},
        {"text": "报告日期：2024-05-18", "box": [400, 100, 570, 125]},
    ]

    detections = detector.detect(records, image_size=(800, 1000))
    medical_indexes = {
        item["record_index"] for item in detections if item["entity"] == "MEDICAL_ID"
    }

    assert 1 in medical_indexes
    assert 2 not in medical_indexes


def test_bank_card_requires_luhn_and_supports_split_ocr_boxes():
    records = [
        {"text": "银行卡号", "box": [10, 10, 90, 35]},
        {"text": "622202", "box": [100, 10, 170, 35]},
        {"text": "020202", "box": [175, 10, 245, 35]},
        {"text": "0202026", "box": [250, 10, 330, 35]},
        {"text": "订单号：6222020202020202027", "box": [10, 55, 330, 80]},
    ]

    detections = detector.detect(records, image_size=(600, 400))
    bank_indexes = {
        item["record_index"] for item in detections if item["entity"] == "BANK_CARD"
    }

    assert {1, 2, 3}.issubset(bank_indexes)
    assert 4 not in bank_indexes


def test_labeled_bank_card_masks_even_when_ocr_breaks_luhn_checksum():
    records = [
        {"text": "银行卡号：6222020202020202027", "box": [10, 10, 330, 35]},
    ]

    detections = detector.detect(records, image_size=(600, 400))

    assert any(item["entity"] == "BANK_CARD" for item in detections)


class SequenceOCR:
    def __init__(self):
        self.calls = 0

    def records(self, image):
        self.calls += 1
        if self.calls <= 2:
            return [{"text": "电话：13800138000", "box": [20, 20, 220, 45], "score": 0.99}]
        return []


def test_pipeline_performs_second_pass_and_returns_no_raw_text():
    result = pipeline.redact_image(
        Image.new("RGB", (400, 200), "white"),
        SequenceOCR(),
        max_rounds=2,
        auto_rotate=False,
    )

    assert result["rounds"] == 2
    assert result["residual_detections"] == 0
    assert result["manual_review"] == []
    assert all("text" not in detection for round_item in result["audit_rounds"] for detection in round_item["detections"])


class IrregularGeometryOCR:
    def records(self, image):
        heights = (8, 9, 10, 11, 18, 24, 31, 40)
        return [
            {
                "text": f"临床内容{index}",
                "box": [10, index * 45, 150, index * 45 + height],
                "score": 0.95,
            }
            for index, height in enumerate(heights)
        ]


def test_irregular_text_geometry_requires_manual_review_without_extra_masking():
    result = pipeline.redact_image(
        Image.new("RGB", (400, 400), "white"),
        IrregularGeometryOCR(),
        max_rounds=2,
        auto_rotate=False,
    )

    assert result["detections"] == 0
    assert result["residual_detections"] == 0
    assert [item["reason"] for item in result["manual_review"]] == [
        "irregular_text_geometry_requires_review"
    ]


def test_source_name_terms_only_uses_strong_filename_or_directory_hints(tmp_path):
    root = tmp_path / "materials"
    source = root / "张三" / "张三住院病历.png"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"synthetic")

    terms = source_name_terms(source, root)

    assert terms == ("张三",)


def test_reports_do_not_contain_original_sensitive_value():
    report = {"entity": "PHONE", "source": "regex", "box": [1, 2, 3, 4], "finding_hash": "abc"}
    serialized = json.dumps(report, ensure_ascii=False)
    assert "13800138000" not in serialized


def test_labeled_evaluation_detects_detector_blind_spots_without_raw_values():
    sensitive, preserved = evaluate_text_pair(
        "姓名：贾敏 处方号：RX20250315001 药品：阿莫西林",
        "处方号：RX20250315001 药品：阿莫西林",
        {"NAME": ["贾敏"], "MEDICAL_ID": ["RX20250315001"]},
        {"CLINICAL_TEXT": ["阿莫西林"]},
    )

    assert [item["status"] for item in sensitive] == ["removed", "residual"]
    assert [item["status"] for item in preserved] == ["retained"]
    assert "贾敏" not in json.dumps(sensitive, ensure_ascii=False)
    assert "RX20250315001" not in json.dumps(sensitive, ensure_ascii=False)


def test_labeled_evaluation_flags_mostly_visible_identifier_as_partial():
    sensitive, _ = evaluate_text_pair(
        "处方号：RX20250315001",
        "处方号：RX2025031500",
        {"MEDICAL_ID": ["RX20250315001"]},
    )

    assert sensitive[0]["status"] == "suspicious_partial"


def test_resume_cache_requires_current_policy_and_ocr_configuration(tmp_path):
    artifact = tmp_path / "redacted.png"
    artifact.write_bytes(b"synthetic-redacted-image")
    report = {
        "source_hash": "source",
        "source_context_hash": "context",
        "artifact_hash": file_hash(artifact),
        "policy_version": POLICY_VERSION,
        "ocr_model": "PP-OCRv6_medium",
        "max_rounds": 2,
    }

    assert report_matches_run(
        report, "source", "context", artifact, "PP-OCRv6_medium", 2
    )
    assert not report_matches_run(
        {**report, "policy_version": "old"},
        "source",
        "context",
        artifact,
        "PP-OCRv6_medium",
        2,
    )
    assert not report_matches_run(
        report, "source", "context", artifact, "PP-OCRv6_tiny", 2
    )


def test_cli_redacts_text_into_an_isolated_output_directory(tmp_path):
    source = tmp_path / "input" / "record.txt"
    source.parent.mkdir()
    source.write_text("姓名：张三 电话：13800138000 诊断：高血压", encoding="utf-8")
    output = tmp_path / "run"

    completed = subprocess.run(
        [
            sys.executable,
            str(SKILL_ROOT / "scripts" / "deidentify.py"),
            "--input",
            str(source),
            "--output-dir",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    status = json.loads(completed.stdout)
    [artifact] = (output / "redacted_files").glob("doc_0001.txt")
    protected = artifact.read_text(encoding="utf-8")
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))

    assert status["documents"] == 1
    assert status["residual_detections"] == 0
    assert summary["items"][0]["source_hash"]
    assert "张三" not in protected
    assert "13800138000" not in protected
    assert "高血压" in protected


def test_agent_skill_layout_is_self_validating():
    assert validate() == []
