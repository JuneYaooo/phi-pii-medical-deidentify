#!/usr/bin/env python3
"""Evaluate redacted images against explicit ground-truth values.

This evaluator deliberately does not call the redaction detector. It checks
ground-truth values directly in OCR text so detector blind spots cannot turn
into false passes in the validation report.
"""

import argparse
import hashlib
import json
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

try:
    from .deidentify import PaddleOCRAdapter, open_image
except ImportError:  # Direct script execution.
    from deidentify import PaddleOCRAdapter, open_image


def normalize_text(value):
    normalized = unicodedata.normalize("NFKC", str(value)).casefold()
    return "".join(character for character in normalized if not character.isspace())


def _field_items(fields):
    for entity, values in (fields or {}).items():
        if isinstance(values, str):
            values = [values]
        for ordinal, value in enumerate(values or [], 1):
            if str(value).strip():
                yield str(entity), ordinal, normalize_text(value)


def _has_suspicious_partial(text, value):
    if len(value) < 8 or not value.isalnum():
        return False
    longest = SequenceMatcher(None, value, text, autojunk=False).find_longest_match().size
    return longest / len(value) >= 0.8


def evaluate_text_pair(original_text, redacted_text, sensitive_fields, preserve_fields=None):
    original = normalize_text(original_text)
    redacted = normalize_text(redacted_text)
    sensitive_results = []
    for entity, ordinal, value in _field_items(sensitive_fields):
        observable = value in original
        remains = observable and value in redacted
        suspicious_partial = observable and not remains and _has_suspicious_partial(redacted, value)
        status = (
            "residual" if remains
            else "suspicious_partial" if suspicious_partial
            else "removed" if observable
            else "unobservable"
        )
        sensitive_results.append({
            "entity": entity,
            "ordinal": ordinal,
            "observable_in_source_ocr": observable,
            "remains_in_redacted_ocr": remains,
            "status": status,
        })

    preservation_results = []
    for entity, ordinal, value in _field_items(preserve_fields):
        observable = value in original
        retained = observable and value in redacted
        preservation_results.append({
            "entity": entity,
            "ordinal": ordinal,
            "observable_in_source_ocr": observable,
            "retained_in_redacted_ocr": retained,
            "status": "retained" if retained else ("lost" if observable else "unobservable"),
        })
    return sensitive_results, preservation_results


def _rate(numerator, denominator):
    if denominator <= 0:
        return None
    return round(numerator / denominator * 100, 2)


def _resolve_path(manifest_path, value):
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = manifest_path.parent / path
    return path.resolve()


def _case_reference(case_id):
    return hashlib.sha256(case_id.encode("utf-8")).hexdigest()[:12]


def evaluate_manifest(manifest_path, model_name):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("manifest must contain a non-empty 'cases' list")

    ocr = PaddleOCRAdapter(model_name)
    case_results = []
    for index, case in enumerate(cases, 1):
        case_id = str(case.get("id") or f"case_{index:04d}")
        source_path = _resolve_path(manifest_path, case["source"])
        redacted_path = _resolve_path(manifest_path, case["redacted"])
        if not source_path.is_file() or not redacted_path.is_file():
            raise FileNotFoundError(f"missing source or redacted image for case {case_id}")

        source_records = ocr.records(open_image(source_path))
        redacted_records = ocr.records(open_image(redacted_path))
        sensitive, preservation = evaluate_text_pair(
            "\n".join(record["text"] for record in source_records),
            "\n".join(record["text"] for record in redacted_records),
            case.get("sensitive_fields") or {},
            case.get("preserve_fields") or {},
        )
        case_results.append({
            "case_reference": _case_reference(case_id),
            "sensitive_fields": sensitive,
            "preserve_fields": preservation,
            "requires_manual_review": any(
                item["status"] in {"residual", "suspicious_partial", "unobservable"}
                for item in sensitive
            ),
        })

    sensitive = [item for case in case_results for item in case["sensitive_fields"]]
    preservation = [item for case in case_results for item in case["preserve_fields"]]
    observable_sensitive = [item for item in sensitive if item["observable_in_source_ocr"]]
    observable_preservation = [item for item in preservation if item["observable_in_source_ocr"]]
    removed = sum(item["status"] == "removed" for item in observable_sensitive)
    retained = sum(item["status"] == "retained" for item in observable_preservation)
    residuals = sum(item["status"] == "residual" for item in sensitive)
    suspicious_partials = sum(item["status"] == "suspicious_partial" for item in sensitive)
    unobservable = sum(item["status"] == "unobservable" for item in sensitive)
    lost_preservation = sum(item["status"] == "lost" for item in preservation)
    return {
        "model": model_name,
        "cases": len(case_results),
        "sensitive_fields_labeled": len(sensitive),
        "sensitive_fields_observable": len(observable_sensitive),
        "sensitive_fields_removed": removed,
        "residual_sensitive_fields": residuals,
        "suspicious_partial_sensitive_fields": suspicious_partials,
        "unobservable_sensitive_fields": unobservable,
        "labeled_removal_rate": _rate(removed, len(observable_sensitive)),
        "preserve_fields_observable": len(observable_preservation),
        "preserve_fields_retained": retained,
        "preserve_fields_lost": lost_preservation,
        "preservation_rate": _rate(retained, len(observable_preservation)),
        "manual_review_cases": sum(case["requires_manual_review"] for case in case_results),
        "case_results": case_results,
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description="Evaluate redacted images against labeled sensitive and preserved values."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--model", default="PP-OCRv6_medium", choices=tuple(PaddleOCRAdapter.MODEL_NAMES)
    )
    return parser


def main():
    args = build_parser().parse_args()
    report = evaluate_manifest(args.manifest.expanduser().resolve(), args.model)
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.expanduser().resolve().write_text(serialized + "\n", encoding="utf-8")
    print(serialized)
    failed = any(report[key] for key in (
        "residual_sensitive_fields",
        "suspicious_partial_sensitive_fields",
        "unobservable_sensitive_fields",
        "preserve_fields_lost",
    ))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
