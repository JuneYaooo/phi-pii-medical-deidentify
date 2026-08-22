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

## Public laboratory-report evaluation asset

- Source ID: `SRC-PUBLIC-CBC-001`
- Document type: complete blood count laboratory report with demo identity fields
- Upstream project: ReportSenseAI
- Upstream file: https://github.com/MEDHANGSHI0708/ReportSenseAI/blob/fe7e800f607c873717b72072018faf36bb83ec77/MINI/uploaded_image.png
- Upstream license: MIT
- Demo-data documentation: https://docs.gnuhealth.org/his/userguide/demodb.html
- Accessed: 2026-08-22
- Original SHA-256: `700648e4c367ac42a84f3c48123c3daf1aa85114b984aab7752cf4be1523ebb3`
- Redacted SHA-256: `379dff3994538c5aa155c988a71ca0649e4a56f349a866688914c287aa3bbda2`
- Result: demo patient name, patient ID, age, sex, and repeated test ID covered; zero residual detections; 18 CBC rows and clinician information preserved.
