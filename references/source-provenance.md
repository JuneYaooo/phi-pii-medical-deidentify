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

## Public English handwriting failure-case asset

- Source ID: `SRC-PUBLIC-EN-HANDWRITING-001`
- Document type: photographed historical handwritten prescription with a recipient name
- Collection: Wellcome Collection
- Work record: https://wellcomecollection.org/works/sxd2fhzw
- IIIF manifest: https://iiif.wellcomecollection.org/presentation/v2/b33046694
- Rights: Public Domain Mark
- Accessed: 2026-08-22
- Original SHA-256: `42dae1d4c8e7e4fa5a8f8254224972db834b3b736b6cd767ec8489fcb65da1fd`
- Project output SHA-256: `8e52e5ef23945fdc128fdb40fa4b97cf263518ccf1e695982136fcd14e8858c5`
- Result: no automatic mask; the handwritten recipient name remained visible; large OCR text geometry routed the page to mandatory human review; this is a documented failure case, not a privacy pass.

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

## Public Chinese handwriting negative-control asset

- Source ID: `SRC-PUBLIC-CN-HANDWRITING-001`
- Document type: Chinese handwritten manuscript containing three prescriptions without a patient identity block
- Collection: Wellcome Collection
- Work record: https://wellcomecollection.org/works/fzyw6u4c
- IIIF image record: https://iiif.wellcomecollection.org/image/L0020840/info.json
- Rights: CC BY 4.0; credit Wellcome Collection
- Accessed: 2026-08-22
- Original SHA-256: `eaa894e2a76c3789c494267d988e2b2dc69b91f6aa2d54231191462f5e4e68c8`
- Project output SHA-256: `675d34a71c923454b125b98bfb44c71f01e5df64cf272b2380f889b665122746`
- Result: no automatic mask and no visible medicine-name overmasking; irregular and large text geometry routed the page to mandatory human review; because the source has no patient identity field, it is a handwriting negative control rather than a recall test.
