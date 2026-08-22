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

## Public English structured patient-register evaluation asset

- Source ID: `SRC-PUBLIC-EN-REGISTER-1910-001`
- Document type: 1910 patient register with a printed name column and 40 handwritten patient names
- Collection: Wellcome Collection
- Work record: https://wellcomecollection.org/works/b9gymynv
- IIIF manifest: https://iiif.wellcomecollection.org/presentation/v2/b21892830
- IIIF page: `b21892830_HB13_6_29_0006.JP2`
- Rights: CC BY 4.0; credit Wellcome Collection
- Accessed: 2026-08-22
- Original SHA-256: `02942007c14ab77f58567f1ef93cb759860d5dd648017875a49fe78fb0dd3141`
- Project output SHA-256: `18c99d754b3910f7844fbab266d082e6a69835b6bf3e6aed1fe60473e5591718`
- Policy version: `2026-08-22.4`
- Result: 40 name-column masks, zero OCR residual detections, and mandatory human review because handwriting outside the recognized column can still be missed.

## Public English mixed-layout patient-register evaluation asset

- Source ID: `SRC-PUBLIC-EN-ST-LUKES-001`
- Document type: St Luke's Hospital register with patient names, ages, occupations, addresses, admission dates, and relationships
- Collection: Wellcome Collection
- Work record: https://wellcomecollection.org/works/jkk57nqr
- IIIF manifest: https://iiif.wellcomecollection.org/presentation/v2/b22001487
- IIIF page: `b22001487_h64_b_01_021_0006.JP2`
- Rights: Open Government Licence
- Accessed: 2026-08-22
- Original SHA-256: `985b02f8f8f5d35d6dc09cebea6926a3bcba79c400c396660673adf47da1e6cd`
- Project output SHA-256: `37fab39d522542c5d0a574979cd7bd5dcc895414b8b0efc024d051a0290c263e`
- Policy version: `2026-08-22.4`
- Result: eight name-related masks and zero OCR residual detections, but ages, occupations, addresses, and relationships remain visible; some masks are wider than the name value; mandatory human review.

## Public English handwritten clinical case-note failure case

- Source ID: `SRC-PUBLIC-EN-CASE-NOTES-001`
- Document type: handwritten clinical case note with patient name, age, dates, and medical history
- Collection: Wellcome Collection
- Work record: https://wellcomecollection.org/works/ye6fsdb8
- IIIF manifest: https://iiif.wellcomecollection.org/presentation/v2/b19030356
- IIIF page: `b19030356_0001.jp2`
- Rights: Public Domain Mark
- Accessed: 2026-08-22
- Original SHA-256: `7769336c7005f354c7314ad757fee22226e59d1867ec43b2781d711905034b3b`
- Project output SHA-256: `757d26d173d0f8857e734f5d54e3415e6471c1f7d87be56e7dd66d7faa2c660b`
- Policy version: `2026-08-22.4`
- Result: one unrelated text box masked, 270-degree rotation, patient name still visible, and mandatory human review; this is a failure case, not a privacy pass.

## Controlled Chinese image-search evaluation sources

- Source ID: `SRC-CONTROLLED-CN-PUMCH-LAB-001`
- Document type: Chinese laboratory report screenshot
- Publisher: Peking Union Medical College Hospital report-query site
- Landing page: https://www.pumch.cn/reportquery.html
- Exact image: https://www.pumch.cn/Uploads/Picture/2018/03/23/u5ab4722672c19.png
- Accessed: 2026-08-22
- Authorization: source page does not clearly grant image redistribution; a traceable evaluation copy is stored at `docs/assets/evaluation/third-party/chinese-pumch-lab-before.png`, outside the repository MIT License
- Direct identifiers visible: patient name and partially masked order number
- Original SHA-256: `bc990c967a9fec9e7aafc86b1c7aa5e08adcfeba35e0d3093fa3ce71e3cf4547`
- Project output SHA-256: `fea8b59940b045445052d098b19f3a1a7eae73e2a6b18d82a8be0b6a6536f695`
- Policy version: `2026-08-22.5`
- Result: four masks; name and order number covered; department overmasked; zero OCR residual detections; manual review required.

- Source ID: `SRC-CONTROLLED-CN-TEXTIN-FOLDED-001`
- Document type: folded and photographed Chinese MR examination report
- Publisher: TextIn medical-report extraction example
- Landing page: https://www.textin.com/tasks/medical-report-extraction
- Exact image: https://www.textin.com/images/medical-report-parse/example-file-cover-3.jpg
- Accessed: 2026-08-22
- Authorization: source page does not clearly grant image redistribution; a traceable evaluation copy is stored at `docs/assets/evaluation/third-party/chinese-textin-folded-report-before.jpg`, outside the repository MIT License
- Direct identifiers visible: MR number, age, inpatient number, bed number, QR code; name field blank
- Original SHA-256: `817ee7f7181a545b083bc47e06b374cad115a7bc3fab0b2bd135350e62f0d80d`
- Project output SHA-256: `7fad0bd5f67d3a1f5b5fb0a7f86c251b7871ffe36fe9a8a48551d1cfbc5c34ce`
- Policy version: `2026-08-22.5`
- Result: seven masks; identifiers covered; QR code remains; layout irregularity requires manual review; not a name-recall test.

- Source ID: `SRC-CONTROLLED-CN-YANGTSE-001`
- Document type: photographed Chinese laboratory report already edited by the publisher
- Publisher: Yangtse Evening News
- Landing page: https://m.yangtse.com/news_details.html?id=4308066
- Exact image: https://imgcdn.yzwb.net/181_1738735693000.jpg?imageMogr2/thumbnail/1080x%3E/strip/ignore-error/1%7Cimageslim
- Accessed: 2026-08-22
- Authorization: source page does not clearly grant image redistribution; original is not committed
- Direct identifiers visible: identity fields already obscured by the publisher
- Original SHA-256: `d47503a271f9d5c65cb8334e5bc1b8d737b988f3e0b576e1e1dbf6e5f4de6d69`
- Result: excluded from effectiveness claims; project produced 14 masks and visibly overmasked clinical results and reference ranges; it cannot measure identity recall because the source is pre-redacted.
