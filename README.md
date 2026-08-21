# Medical Record Privacy Redaction

**Identify and cover patient information locally while preserving useful diagnoses, laboratory results, and treatment details.**

[![GitHub stars](https://img.shields.io/github/stars/JuneYaooo/phi-pii-medical-deidentify?style=flat)](https://github.com/JuneYaooo/phi-pii-medical-deidentify/stargazers)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Local processing](https://img.shields.io/badge/privacy-local%20processing-blue.svg)
![Medical documents](https://img.shields.io/badge/documents-images%20%7C%20PDF%20%7C%20Office-orange.svg)

English | [简体中文](README.zh-CN.md)

This project is designed for photographs, scans, prescriptions, laboratory reports, and other medical material. It uses local text recognition to locate patient identity fields, creates a new copy with opaque black masks, and checks the result again. Originals remain unchanged, and real records do not need to be sent to a public recognition service.

> This project is not a privacy certification, legal advice, or a guarantee of complete anonymity. Every document requires a final human review before external release.

## Before and after

The images below are the actual input and actual project output from the same medical image; no masks were added by hand. The source had a patient name, sex, and birth date burned into its upper-left pixels. The output covers those identity fields with opaque black masks while preserving the medical image itself.

| Before processing | Project output |
| --- | --- |
| ![Before processing: identity text appears in the upper-left corner](docs/assets/evaluation/open-medical-image-before.png) | ![After processing: identity text is covered with opaque masks](docs/assets/evaluation/open-medical-image-after.png) |

| Result | Explanation |
| --- | --- |
| Covered | Name, sex, and birth date |
| Residual text findings | 0 |
| Preserved | Medical image and non-identity content |
| Review status | Human review required because the image contains only two recognized lines of small text, which the automatic quality check considers too sparse |

The image comes from Pseudo-PHI-DICOM-Data, a dataset designed to evaluate medical-image de-identification. Its identity fields are pseudo-PHI used for evaluation, not a real patient's identity. The Cancer Imaging Archive publishes the dataset under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); this project uses a [Presidio test file stored with permission from the original dataset owners](https://github.com/data-privacy-stack/presidio/blob/main/presidio-image-redactor/tests/test_data/png_images/2_ORIGINAL.png). The complete dataset and citation are tracked through [DOI 10.7937/s17z-r072](https://doi.org/10.7937/s17z-r072), and the local source ID is `SRC-PUBLIC-DICOM-001`.

## Real pathology-report evaluation

One real Chinese pathology-report photograph containing complete patient fields was evaluated in an isolated environment.

| Evaluation result | Value or conclusion |
| --- | --- |
| Real patient-field case | 1 pathology report |
| Final masks | 19 |
| Residual text findings after recheck | 0 |
| Manual source-to-output review | All visible textual patient fields were covered |
| Clinical content preservation | Diagnosis, specimen, tumor site, grade, clinicians, and report date remained readable |
| Photo metadata | Location and other original metadata were removed |
| Remaining concern | The barcode remains visible and may encode a patient number |

| Before processing | After processing |
| --- | --- |
| Patient name was clearly visible | Covered |
| National identity number was clearly visible | Covered |
| Inpatient and pathology numbers were visible | Covered |
| Sex, age, and other identity-row fields were visible | Relevant identity regions covered |
| Diagnosis and pathology content were readable | Remained readable |

The first pass missed one plain-text pathology number below the barcode, and the automatic recheck did not find it. Manual comparison exposed the problem, the recognition coverage was extended, and a new evaluation covered the number. The project therefore records discovered failures and corrections, not only successful outcomes.

Redistribution permission and patient authorization for the source could not be verified, so the complete before-and-after images are not committed publicly. The material is restricted to controlled local evaluation and tracked under a stable source ID. This result describes a text-field review of one sample; it does not establish accuracy, recall, compliance certification, or unconditional release approval.

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
| Medical images | Phone photos, prescription images, report screenshots, and scans |
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
| Prescription, examination, laboratory, pathology, and specimen numbers | Admission, discharge, examination, and report dates |

Preserved details can still create indirect identification risk when combined with a rare condition, institution, or date. The final policy should reflect the material's intended use and the organization's privacy requirements.

## How it works

1. **Classify the material**: determine whether it is a photo, scan, prescription, report, table, or plain text.
2. **Read locally with OCR**: extract words and page positions for precise masking.
3. **Identify private fields**: combine number formats and validation, field labels, neighboring text, row structure, and page layout.
4. **Create a redacted copy**: mask individual values where possible and use broader coverage for headers, identity rows, and uncertain regions.
5. **Recheck with OCR**: inspect the processed page again, enlarge masks when identifiers remain, and route unresolved cases to human review.
6. **Report review status**: describe categories handled and pages needing attention without repeating raw identifiers in ordinary reports.

The default approach combines local OCR, deterministic rules, and layout relationships. It does not depend on a generative large language model. This keeps decisions easier to explain and allows medical-field policies to be refined deliberately.

## Local deployment recommendations

| Use case | Suggested choice | Reason |
| --- | --- | --- |
| Clear printed Chinese documents | A small Chinese PaddleOCR model | Runs on ordinary computers with balanced speed and resource use |
| Dense text, complex tables, and poor photographs | A medium Chinese PaddleOCR model | Usually provides steadier text and position recognition but runs more slowly |
| Identity, phone, bank card, and business numbers | Format rules, validation rules, and field position | Decisions are explainable and unusual numbers are easier to flag |
| Natural-language names, addresses, and organizations | A lightweight Chinese BERT or RoBERTa entity model | Optional enhancement for expressions that fixed rules do not cover well |
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

## Other real-layout testing

Six additional publicly accessible medical images were evaluated, including handwritten or photographed prescriptions, a previously redacted prescription, and cropped blood test reports.

- Clear printed documents with complete fields were more suitable for automatic masking and rechecking.
- Two handwriting-heavy or poorly photographed cases were correctly routed to human review.
- Previously masked or cropped images can still expose information at their edges, in metadata, or through other identifiers.

These materials lacked complete field-level ground truth, so they are used to observe layout behavior rather than publish an accuracy score.

## Material provenance

| Source ID | Material | Permission and use |
| --- | --- | --- |
| `SRC-PUBLIC-DICOM-001` | A TCIA Pseudo-PHI-DICOM-Data medical image obtained through Presidio's test resources | CC BY 4.0; suitable for public display and tracking |
| `SRC-REAL-PATHOLOGY-001` | A pathology report with real patient fields from a public page | Redistribution and patient authorization could not be verified; isolated local evaluation only |

The public medical-image citation is: Rutherford, M. et al., *A DICOM dataset for evaluation of medical image de-identification (Pseudo-PHI-DICOM-Data)*, The Cancer Imaging Archive, 2021, [DOI 10.7937/s17z-r072](https://doi.org/10.7937/s17z-r072).

The real pathology report is tracked as follows:

| Item | Record |
| --- | --- |
| Publisher | Mijian lung-cancer recovery community |
| Discovery | Bing Images |
| Accessed | August 21, 2026 |
| Redistribution permission | Not confirmed |
| Patient authorization | Could not be verified |
| Evaluation scope | Isolated local evaluation only |

The protected provenance ledger records the original page, asset address, access date, file fingerprints, and corresponding results under this source ID. Direct links, source images, and raw identity values are not published or committed because doing so could redistribute identifiable patient material.

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
