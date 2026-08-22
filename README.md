# Medical Record Privacy Redaction

**Identify and cover patient information locally while preserving useful diagnoses, laboratory results, and treatment details.**

[![GitHub stars](https://img.shields.io/github/stars/JuneYaooo/phi-pii-medical-deidentify?style=flat)](https://github.com/JuneYaooo/phi-pii-medical-deidentify/stargazers)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Local processing](https://img.shields.io/badge/privacy-local%20processing-blue.svg)
![Medical documents](https://img.shields.io/badge/documents-images%20%7C%20PDF%20%7C%20Office-orange.svg)

English | [简体中文](README.zh-CN.md)

This project is designed for laboratory sheets, pathology reports, examination reports, prescriptions, and other text- or table-heavy medical documents. It uses local text recognition to locate patient identity fields, creates a new copy with opaque black masks, and checks the result again. Originals remain unchanged, and real records do not need to be sent to a public recognition service.

> This project is not a privacy certification, legal advice, or a guarantee of complete anonymity. Every document requires a final human review before external release.

## English before-and-after cases

Every case below is an English medical text document with visible patient information in the source. Images that contain medical content but no patient name, identifier, address, phone number, or comparable identity field are not used as de-identification evidence. No masks were added by hand.

### Standard report: modern complete blood count

This modern CBC report visibly contains a patient name, age and sex, registration number, street address, barcode, and QR code. The project covered the text identity fields while preserving the test table, values, reference ranges, clinical notes, dates, and laboratory staff details.

| Before processing | Project output |
| --- | --- |
| ![Before processing: modern CBC report with patient name, age, registration number, address, barcode, and QR code](docs/assets/evaluation/english-modern-cbc-before.png) | ![Project output: patient text fields are covered while CBC results remain readable](docs/assets/evaluation/english-modern-cbc-after.png) |

| Evaluation item | Actual result |
| --- | --- |
| Privacy fields in the source | Patient name, age and sex, registration number, street address, barcode, and QR code |
| Automatic masks | 4 text regions covering the name, age and sex, registration number, and address |
| OCR residual count | 0 for the text fields matched by the policy |
| Preserved | CBC results, units, reference ranges, clinical notes, report dates, and laboratory staff details |
| Manual comparison | The age mask slightly overlaps the referring-doctor line; the barcode and QR code remain visible |
| Final status | Human review required before release, especially for the barcode and QR code |

The source is the MIT-licensed [MedOCR laboratory image at a fixed commit](https://github.com/DeepLumiere/MedOCR/blob/9da1023b2c51079220ea1a0378ceadcf1ce8eb73/labimage.png). The upstream repository does not independently establish the patient's publication status, so this copy is retained as traceable evaluation material rather than presented as proof of patient consent. Source ID: `SRC-CONTROLLED-EN-MEDOCR-CBC-001`.

### Photographed handwritten prescription

This phone photograph contains a handwritten patient name, age, sex, clinical description, and prescription. The project covered the patient identity fields and preserved the date, clinical text, medicines, doses, and clinician contact block.

| Before processing | Project output |
| --- | --- |
| ![Before processing: photographed handwritten prescription with patient name, age, and sex](docs/assets/evaluation/english-handwritten-prescription-before.webp) | ![Project output: patient name, age, and sex are covered while the prescription remains readable](docs/assets/evaluation/english-handwritten-prescription-after.webp) |

| Evaluation item | Actual result |
| --- | --- |
| Privacy fields in the source | Patient name, age, and sex |
| Automatic masks | 3 masks across two patient fields; the second OCR round enlarged the age and sex coverage |
| OCR residual count | 0 for the matched patient fields |
| Preserved | Date, clinical description, medicines, doses, weight, and clinician information |
| Final status | Mandatory human review because handwriting and irregular text geometry can still hide OCR misses |

The source is the MIT-licensed [healthcare-ocr sample prescription at a fixed commit](https://github.com/United-We-Care/healthcare-ocr/blob/a7a11f01f0f70b072e00ba4c3b4f0a13ad8e900f/ocr/sample_files/hw_prescription.jpg). The image itself credits a prior Facebook post, and the upstream repository does not independently establish patient consent or original image rights. It is therefore tracked as evaluation material, not as freely reusable patient data. Source ID: `SRC-CONTROLLED-EN-HANDWRITTEN-RX-001`.

### Structured handwriting: 40 patient names

This scanned register has a clearly printed “Name of Patient” column followed by 40 handwritten names. The project uses that column structure to cover all 40 OCR name boxes while leaving admission dates and payment columns readable.

| Before processing | Project output |
| --- | --- |
| ![Before processing: historical patient register with 40 handwritten names](docs/assets/evaluation/english-register-1910-before.jpg) | ![Project output: the patient-name column is covered with opaque masks](docs/assets/evaluation/english-register-1910-after.jpg) |

| Evaluation item | Actual result |
| --- | --- |
| Automatic masks | 40 name boxes |
| OCR residual count | 0 |
| Manual comparison | The visible name column is covered; dates and payment entries remain readable |
| Final status | Mandatory human review because handwriting outside the recognized column may still be missed |

The source is Wellcome Collection record [Register of patients](https://wellcomecollection.org/works/b9gymynv), produced in 1910 and licensed CC BY 4.0. The exact source is volume `b21892830`, page `b21892830_HB13_6_29_0006.JP2`. The local source ID is `SRC-PUBLIC-EN-REGISTER-1910-001`.

These three cases cover a standard digital report, a phone photograph, and structured handwriting. Each source contains visible patient information, and every result remains subject to human review. Additional historical failure material is retained in the evaluation source ledger, but it is not used as headline product evidence.

## What it does

- **Protects originals**: always creates a separate copy instead of overwriting source material.
- **Processes locally**: OCR, privacy decisions, masking, and rechecking can remain on the device or private network.
- **Uses irreversible masks**: applies opaque black coverage rather than recoverable blur, transparency, or removable overlays.
- **Preserves medical value**: aims to keep diagnoses, medicines, doses, laboratory values, and conclusions readable.
- **Checks outputs again**: expands coverage when residual identifiers are found or requests human review when uncertain.
- **Reviews batches**: provides a result summary, page overview, and review status for multiple files.
- **Routes risky pages**: handwriting, poor images, cropping, and abnormal layouts are not forced into an automatic pass.

## Supported material

| Material | Common examples |
| --- | --- |
| Medical document images | Phone photos of laboratory sheets, prescriptions, report screenshots, and scans |
| Multi-page reports | PDF records, examination reports, and discharge material |
| Office documents | Word records, Excel laboratory tables, and registries |
| Text material | Plain, tabular, and structured text |
| Batch collections | Folders containing several kinds of material |

## What is hidden and preserved

| Hidden by default | Preserved by default |
| --- | --- |
| Patient, relative, and contact names | Diseases, symptoms, and diagnoses |
| National identity and other document numbers | Medication, dosage, and treatment details |
| Phones, email addresses, and home addresses | Laboratory items, values, and reference ranges |
| Birth dates, employers, and bank card numbers | Specimen details, lesion sites, grades, and conclusions |
| Medical record, inpatient, outpatient, and insurance numbers | Institutions, departments, and clinicians |
| Prescription, examination, laboratory, pathology, specimen, and medical billing receipt numbers | Admission, discharge, examination, and report dates |

Preserved details can still create indirect identification risk when combined with a rare condition, institution, or date. The final policy should reflect the material's intended use and the organization's privacy requirements.

## How it works

1. **Classify the material**: determine whether it is a photo, scan, prescription, report, table, or plain text.
2. **Read locally with OCR**: extract words and page positions for precise masking.
3. **Identify private fields**: combine number formats and validation, field labels, neighboring text, row structure, and page layout.
4. **Create a redacted copy**: mask individual values where possible and use broader coverage for headers, identity rows, and uncertain regions.
5. **Recheck with OCR**: inspect the processed page again, enlarge masks when identifiers remain, and route unresolved cases to human review.
6. **Report review status**: describe categories handled and pages needing attention without repeating raw identifiers in ordinary reports.

The current repository implementation combines local OCR, deterministic rules, and layout relationships; it does not claim to use a generative model. For stronger natural-language and contextual decisions, a locally hosted language model with 4B parameters or fewer can be added after OCR: OCR supplies text and coordinates, the small model decides which content is private, and the result is mapped back to image regions. Deterministic validation still handles identifiers with well-defined formats, such as phone numbers, identity numbers, and medical record numbers.

## Local deployment recommendations

| Use case | Suggested choice | Reason |
| --- | --- | --- |
| Clear printed Chinese documents | A small Chinese PaddleOCR model | Runs on ordinary computers with balanced speed and resource use |
| Dense text, complex tables, and poor photographs | A medium Chinese PaddleOCR model | Usually provides steadier text and position recognition but runs more slowly |
| Identity, phone, bank card, and business numbers | Format rules, validation rules, and field position | Decisions are explainable and unusual numbers are easier to flag |
| Names, addresses, organizations, and complex context | A local language model with 4B parameters or fewer | Uses OCR context to decide what is private without requiring a separate BERT or RoBERTa entity model |
| Handwriting, glare, and severe distortion | Human review as the primary safeguard | A small model should not issue an independent privacy pass |

Local workflows should also:

- Store originals, recognition intermediates, and redacted copies separately with restricted access.
- Keep raw identifiers out of ordinary audit records; store only category, position, reason, and a non-reversible fingerprint.
- Handle barcodes and QR codes separately by masking them or decoding and assessing them locally.
- Validate both required masking and required preservation on authorized real-world examples.
- Route low-quality, handwritten, cropped, tilted, or unusually masked pages to human review.
- Define retention periods for originals, intermediate files, and final results.

A larger model is not automatically safer. Stable rules, representative domain examples, output rechecking, and human review jointly determine reliability.

## Adapting it to other domains

The workflow is not limited to healthcare. Define three groups: information that must be removed, content that should remain useful, and conditions that require human confirmation. Add the relevant labels, formats, validation methods, and layout positions, and the same process can be adapted to other fields.

| Domain | Information that can be private | Information usually preserved |
| --- | --- | --- |
| Finance and insurance | Customer names, identity numbers, cards, accounts, and policy numbers | Products, value ranges, and business conclusions |
| Legal documents | Party identities, addresses, contacts, and personal case identifiers | Legal provisions, reasoning, and general case facts |
| Education | Student names, student numbers, parent phones, and home addresses | Courses, aggregate grades, and teaching feedback |
| Human resources | Employee names, staff numbers, payroll accounts, and contacts | Roles, departments, and aggregate data |
| Customer support | User accounts, phones, addresses, and personal order identifiers | Issue types, handling steps, and resolutions |

Stable document layouts usually require only a new masking, preservation, and review policy. Major differences in layout, handwriting, or specialist numbering still need corresponding layout rules and authorized evaluation examples.

## Real-layout observations

Handwriting, poor photographs, cropping, glare, and partial prior redaction are treated as risk conditions. Sources without independently verified patient authorization are labeled as controlled evaluation material rather than freely reusable data. Clear printed reports remain the strongest automated path; handwritten and incomplete documents remain review-first.

## Material provenance

| Source ID | Material | Permission and use |
| --- | --- | --- |
| `SRC-CONTROLLED-EN-MEDOCR-CBC-001` | MedOCR modern CBC report with patient identity fields | Upstream repository is MIT; patient publication status is not independently verified |
| `SRC-CONTROLLED-EN-HANDWRITTEN-RX-001` | healthcare-ocr photographed handwritten prescription | Upstream repository is MIT; original image rights and patient consent are not independently verified |
| `SRC-PUBLIC-EN-REGISTER-1910-001` | Wellcome Collection structured patient register | CC BY 4.0; public result display and tracking permitted |

The MedOCR CBC is fixed to commit `9da1023b2c51079220ea1a0378ceadcf1ce8eb73`; its source and project-output SHA-256 values are `5dcff5590bfb6c5095db7fbe239eac9309d1670e147daeb8c9c266ce65e8bf39` and `a6b0781ebdc668b7e2b48473b7f369ba33cb860633deebefb8331601e24c39ee`. The photographed prescription is fixed to healthcare-ocr commit `a7a11f01f0f70b072e00ba4c3b4f0a13ad8e900f`; its source and output values are `c82e02d455321cd22ee34b7328e30a83012fcfe40f1be0dde7af7b91e0f2954a` and `c16ff6cf2e4ea0f0dc5bca75e76c11638e0c19e89e9e4e169cbc32e504c72811`. Both were accessed on August 22, 2026 and processed with policy version `2026-08-22.6`.

The structured-register source and output SHA-256 values are `02942007c14ab77f58567f1ef93cb759860d5dd648017875a49fe78fb0dd3141` and `18c99d754b3910f7844fbab266d082e6a69835b6bf3e6aed1fe60473e5591718`. It was accessed on August 22, 2026 and processed with policy version `2026-08-22.4`.

## Human review is required

- Handwriting, signatures, stamps, or poor-quality photographs
- Tilt, rotation, perspective distortion, glare, or partial obstruction
- Faces, portraits, fingerprints, and other non-text identifiers
- Barcodes or QR codes that may encode patient numbers
- Cropped pages without enough field labels or context
- Rare conditions, dates, and institutions that may identify someone in combination
- Any result explicitly marked for review

Before external release, inspect every page's text, image edges, barcodes, QR codes, filename, and metadata.

## License

This project is available under the [MIT License](LICENSE). The license applies to the project itself and does not grant permission to redistribute evaluation materials.
