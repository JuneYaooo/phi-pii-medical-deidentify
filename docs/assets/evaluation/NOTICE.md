# Evaluation image attribution

Evaluation source images are third-party materials. They are not covered by this repository's MIT License unless an entry explicitly states otherwise; downstream users must follow the original source terms and independently assess patient authorization.

The modern English CBC image is `labimage.png` from MedOCR at commit `9da1023b2c51079220ea1a0378ceadcf1ce8eb73`:

https://github.com/DeepLumiere/MedOCR/blob/9da1023b2c51079220ea1a0378ceadcf1ce8eb73/labimage.png

MedOCR is distributed under the MIT License. The image contains a visible patient name, age, sex, registration number, street address, barcode, and QR code. The upstream repository does not independently document patient consent or publication status. The local before image is `english-modern-cbc-before.png`; `english-modern-cbc-after.png` is actual project output. Source ID: `SRC-CONTROLLED-EN-MEDOCR-CBC-001`.

The photographed English handwritten prescription is `ocr/sample_files/hw_prescription.jpg` from healthcare-ocr at commit `a7a11f01f0f70b072e00ba4c3b4f0a13ad8e900f`:

https://github.com/United-We-Care/healthcare-ocr/blob/a7a11f01f0f70b072e00ba4c3b4f0a13ad8e900f/ocr/sample_files/hw_prescription.jpg

healthcare-ocr is distributed under the MIT License. The image contains a visible patient name, age, and sex and credits an earlier Facebook post in the image itself. The repository does not independently establish original image rights or patient consent. The local before image is `english-handwritten-prescription-before.webp`; `english-handwritten-prescription-after.webp` is actual project output. Source ID: `SRC-CONTROLLED-EN-HANDWRITTEN-RX-001`.

The Chinese occupational-report images are based on `vx_images/206350912225539.jpg` from healthyCheckUi at commit `c6b50346993f7e8debdc567e3469b8fa74eaaafb`:

https://github.com/scmt1/healthyCheckUi/blob/c6b50346993f7e8debdc567e3469b8fa74eaaafb/vx_images/206350912225539.jpg

healthyCheckUi is distributed under the LGPL-3.0 License. Its README states that the screenshots show completed functionality and permits personal learning and teaching cases with source attribution. The processed image is actual project output and remains subject to mandatory human review because the source combines multiple report pages. Source ID: `SRC-PUBLIC-CN-OCCUPATIONAL-001`.

The English handwritten patient-register photograph comes from Wellcome Collection work `rj3pbbjd`, "Register of Patients in the Hong Kong Hospital", digitized volume `b19581841`, page `b19581841_MS_1469_0002.jp2`:

https://wellcomecollection.org/works/rj3pbbjd

https://iiif.wellcomecollection.org/presentation/v2/b19581841

The image is licensed CC BY-NC 4.0 and credited to Wellcome Collection. The page contains handwritten patient names, ages, addresses, and diseases. The after image is actual project output: no automatic mask was applied, those fields remain visible, and low-confidence handwriting routed the page to mandatory human review. Source ID: `SRC-PUBLIC-EN-HANDWRITING-002`.

The two controlled Chinese sources used in the README comparison are stored under `third-party/` so the before/after examples remain reproducible. Their pages do not clearly grant image-republication rights, so those original files are third-party evaluation material, are not covered by this repository's MIT License, and retain links to the exact source URLs. File-level provenance is recorded in `third-party/NOTICE.md`.

Source ID `SRC-CONTROLLED-CN-PUMCH-LAB-001` is the Beijing Union Medical College Hospital report-query image:

https://www.pumch.cn/reportquery.html

https://www.pumch.cn/Uploads/Picture/2018/03/23/u5ab4722672c19.png

The original is stored as `third-party/chinese-pumch-lab-before.png`. It contains a patient name and partially masked order number. The project output is stored as `chinese-pumch-lab-after.png`; it masks the name and order number but requires human review because a department field is overmasked.

Source ID `SRC-CONTROLLED-CN-TEXTIN-FOLDED-001` is the folded photographed report used on TextIn's medical-report example page:

https://www.textin.com/tasks/medical-report-extraction

https://www.textin.com/images/medical-report-parse/example-file-cover-3.jpg

The original is stored as `third-party/chinese-textin-folded-report-before.jpg`. It contains MR number, age, inpatient and bed numbers, and a QR code. The project output is stored as `chinese-textin-folded-report-after.jpg`; identifiers are covered, while the QR code and fold distortion require human review.

Source ID `SRC-CONTROLLED-CN-YANGTSE-001` is the already-edited laboratory photograph from Yangtse Evening News:

https://m.yangtse.com/news_details.html?id=4308066

https://imgcdn.yzwb.net/181_1738735693000.jpg?imageMogr2/thumbnail/1080x%3E/strip/ignore-error/1%7Cimageslim

The source already hides identity fields and contains editorial arrows and boxes. It is recorded as an excluded candidate, not as a privacy-recall result.

The 1910 patient-register image comes from Wellcome Collection work `b9gymynv`, volume `b21892830`, page `b21892830_HB13_6_29_0006.JP2`:

https://wellcomecollection.org/works/b9gymynv

https://iiif.wellcomecollection.org/presentation/v2/b21892830

The image is licensed CC BY 4.0 and credited to Wellcome Collection. It contains a printed patient-name column with handwritten names. The after image is actual project output: 40 opaque name masks were applied and the page remains mandatory-review material. Source ID: `SRC-PUBLIC-EN-REGISTER-1910-001`.

The St Luke's Hospital register image comes from Wellcome Collection work `jkk57nqr`, volume `b22001487`, page `b22001487_h64_b_01_021_0006.JP2`:

https://wellcomecollection.org/works/jkk57nqr

https://iiif.wellcomecollection.org/presentation/v2/b22001487

The image is available under the Open Government Licence. It contains patient names, ages, occupations, addresses, admission dates, and family relationships. The after image is actual project output: eight name-related masks were applied, other privacy fields remain visible, and the page requires human review. Source ID: `SRC-PUBLIC-EN-ST-LUKES-001`.

The handwritten clinical case-note image comes from Wellcome Collection work `ye6fsdb8`, volume `b19030356`, page `b19030356_0001.jp2`:

https://wellcomecollection.org/works/ye6fsdb8

https://iiif.wellcomecollection.org/presentation/v2/b19030356

The digital item carries the Public Domain Mark. It contains a handwritten patient name, age, dates, and medical history. The after image is actual project output: one unrelated text box was masked, the page was rotated incorrectly, and the patient name remains visible. Source ID: `SRC-PUBLIC-EN-CASE-NOTES-001`.

The English prescription-envelope photograph comes from Wellcome Collection work `wr7zhrz9`, "Small prescription envelope for a Mr Clay":

https://wellcomecollection.org/works/wr7zhrz9

The image is licensed CC BY 4.0 and credited to Wellcome Collection. The after image is actual project output: no automatic rotation or mask was applied, and the page was routed to mandatory human review. Source ID: `SRC-PUBLIC-EN-PHOTO-001`.
