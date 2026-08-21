# Test source provenance

Every non-synthetic evaluation asset must have a stable `source_id` and a
provenance record before its results are cited. Keep records that link directly
to identifiable patient material in `.local-evaluation/provenance.json`; this
directory is excluded from Git.

Each record should include:

- stable source ID and document type;
- discovery service and access date;
- publisher, landing-page URL, and original asset URL;
- SHA-256 of the downloaded original and generated artifact;
- local input, output, report, and evaluation paths;
- license and authorization status;
- whether direct identifiers are visible;
- redistribution and Git eligibility;
- OCR model, policy version, redaction rounds, and result counts.

The committed README may cite the source ID, publisher, discovery method,
access date, and risk status. Do not commit direct links to identifiable patient
material, original images, OCR text, or raw identifiers unless there is explicit
authorization and an approved data-handling process.

Example public citation:

```text
Source ID: SRC-EXAMPLE-001
Publisher: example medical education provider
Discovered via: public image search
Accessed: YYYY-MM-DD
Authorization: verified educational sample
Exact provenance: protected local manifest
```
