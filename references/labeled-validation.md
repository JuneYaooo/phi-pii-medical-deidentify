# Labeled validation

Use `scripts/evaluate_labeled_set.py` to check redacted images against explicit
ground-truth values. This is separate from the production detector: it searches
for the labeled values directly in source and redacted OCR text, so a missing
detection rule cannot silently produce a passing validation result.

Only use synthetic or already de-identified values in a manifest that may be
committed or shared. A manifest containing real identifiers is itself sensitive
and must remain in protected local storage.

## Manifest

Paths may be absolute or relative to the manifest file.

```json
{
  "cases": [
    {
      "id": "synthetic-prescription-001",
      "source": "source.png",
      "redacted": "redacted.png",
      "sensitive_fields": {
        "NAME": ["张三"],
        "MEDICAL_ID": ["RX20250315001"]
      },
      "preserve_fields": {
        "CLINICAL_TEXT": ["阿莫西林"]
      }
    }
  ]
}
```

Run the evaluator with the same OCR model used for the redaction job:

```bash
python scripts/evaluate_labeled_set.py \
  --manifest /path/to/synthetic-manifest.json \
  --model PP-OCRv6_medium \
  --output /path/to/labeled-report.json
```

The command exits nonzero when a labeled sensitive value remains, most of a long
identifier remains, source OCR cannot observe a labeled sensitive value, or an
observable preservation field is lost. Unobservable and suspicious partial
fields require human review and are excluded from a passing result. Reports
contain only hashed case references, entity names, ordinals, and statuses; they
do not copy case IDs or labeled values.

This test measures only the selected labeled cases. It does not establish a
general recall, precision, compliance, or legal result.
