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

## Public Chinese occupational-report evaluation asset

- Source ID: `SRC-PUBLIC-CN-OCCUPATIONAL-001`
- Document type: Chinese occupational health examination report with demo identity fields
- Upstream project: healthyCheckUi
- Upstream file: https://github.com/scmt1/healthyCheckUi/blob/c6b50346993f7e8debdc567e3469b8fa74eaaafb/vx_images/206350912225539.jpg
- Upstream license: LGPL-3.0
- Upstream use statement: screenshots are from completed functionality; personal learning and teaching cases are permitted with attribution
- Accessed: 2026-08-22
- Repository before-image SHA-256: `92a716af0c62ede83854b09e775cfa99eaddfa962558cc7da363e3482bb3ea33`
- Repository after-image SHA-256: `34ca89dc781aeebd70127282c379bcc06f9d3c33698756292a1cc150e4c38db1`
- Result: seven masks covered names, phone, birth date, examination IDs, and the identifier below the barcode; zero residual detections; occupational history and examination content preserved; irregular combined-page geometry requires human review.

## Public English handwritten patient-register failure case

- Source ID: `SRC-PUBLIC-EN-HANDWRITING-002`
- Document type: photographed 1890 Hong Kong Hospital patient register with handwritten patient names, ages, addresses, and diseases
- Collection: Wellcome Collection
- Work record: https://wellcomecollection.org/works/rj3pbbjd
- IIIF manifest: https://iiif.wellcomecollection.org/presentation/v2/b19581841
- IIIF page: `b19581841_MS_1469_0002.jp2`
- Rights: CC BY-NC 4.0; credit Wellcome Collection
- Accessed: 2026-08-22
- Original SHA-256: `77662f3dd25d776d3c62870bd267e88261369ba0f547a05c6d26bdbca070034f`
- Project output SHA-256: `73f3cbd4dbbbfa3e905bd0657d2983d0b148af98857a23b2272eaef816d2837d`
- Policy version: `2026-08-22.3`
- Result: no automatic mask; patient names, ages, addresses, and diseases remained visible; zero OCR residual detections are not treated as a pass because OCR did not reliably read the handwriting; low-confidence unstructured text routed the page to mandatory human review.

## Public English photographed-document failure-case asset

- Source ID: `SRC-PUBLIC-EN-PHOTO-001`
- Document type: upside-down photograph of an English prescription envelope with a handwritten patient name
- Collection: Wellcome Collection
- Work record: https://wellcomecollection.org/works/wr7zhrz9
- IIIF image record: https://iiif.wellcomecollection.org/image/L0040456/info.json
- Rights: CC BY 4.0; credit Wellcome Collection
- Accessed: 2026-08-22
- Original SHA-256: `d2bc3951954dbacd0188ae44659daae319aa028dfd2a8aaf26875edbf16ca875`
- Project output SHA-256: `58757f12e4afaf91202bfdbb78b9d589285f73dbce2f40e691f546eb7b5ba89a`
- Result: no automatic rotation or mask; the handwritten patient name remained visible; irregular text geometry routed the page to mandatory human review; this is a documented failure case, not a privacy pass.
