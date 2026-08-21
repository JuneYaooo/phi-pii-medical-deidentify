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

## Public evaluation asset

- Source ID: `SRC-PUBLIC-DICOM-001`
- Document type: medical image with burned-in pseudo-PHI
- Dataset: Pseudo-PHI-DICOM-Data
- Publisher: The Cancer Imaging Archive
- Dataset DOI: https://doi.org/10.7937/s17z-r072
- Dataset license: CC BY 4.0
- Upstream copy: https://github.com/data-privacy-stack/presidio/blob/main/presidio-image-redactor/tests/test_data/png_images/2_ORIGINAL.png
- Upstream permission statement: Presidio documents that its DICOM test data is stored with permission from the original dataset owners.
- Accessed: 2026-08-21
- Original SHA-256: `1ced84107c8b6b152242a46f84426cff2e3639cead1e756108932a5a00074d6d`
- Redacted SHA-256: `eba94ebcaee512309ab74f6d7a75a2f95b95678104a0f0b977ae8b4ef79c1fc2`
- Result: name, sex, and birth date covered; zero residual text detections; human review retained because OCR content was sparse.
