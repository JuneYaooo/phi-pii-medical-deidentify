import hashlib
import re
import statistics


LABELS = {
    "NAME": ("Patient Name", "PatientName", "患者姓名", "病员姓名", "联系人姓名", "姓名", "名字", "联系人", "家属姓名"),
    "ID_NUMBER": ("公民身份号码", "身份证号码", "身份证号", "身份证", "证件号码", "护照号", "社保号"),
    "PHONE": ("联系电话", "联系方式", "手机号", "手机", "电话"),
    "ADDRESS": ("联系人地址", "联系地址", "户籍地址", "现住址", "家庭地址", "工作单位", "住址", "地址"),
    "BIRTH_DATE": ("Date of Birth", "DOB", "出生日期", "出生年月", "出生"),
    "BANK_CARD": ("银行卡号码", "银行卡号", "银行账号", "银行账户", "银行卡"),
    "MEDICAL_ID": (
        "住院病历号", "患者编号", "患者ID", "病案号", "病历号", "病人号", "门诊号", "住院号",
        "医保卡编号", "医保卡号码", "医保卡号", "医保号", "电子处方编号", "电子处方号", "处方编号",
        "处方号码", "处方号", "检验单编号", "检验单号", "化验单编号", "化验单号", "医嘱编号", "医嘱号",
        "检查号", "检验号", "申请单号", "申请号", "病理号", "样本编号", "样本号",
        "肿瘤样本ID", "对照样本ID", "样本ID", "分子病理号", "分子检测", "标本号",
        "影像编号", "影像号", "报告编号", "报告ID", "报告号", "登记号", "会诊编号",
        "会诊号", "胃镜号", "CT号", "MRI号", "MR号", "放射号", "就诊卡号", "就诊号", "体检号",
        "条码编号", "条形码号", "条码号", "病人编号", "超声号", "ID号", "Patient ID", "PatientID",
        "送检切片编号", "切片编号",
        "病理 No", "病理No", "Pathology No", "PathologyNo",
        "X光 No", "X光No", "X线 No", "X线No", "X-ray No", "X-rayNo",
        "Hospital No", "HospitalNo", "住院 No", "住院No",
        "X光号", "X线号", "检查编号", "检验流水号", "报告流水号", "流水号",
        "收费票据号码", "收费票据号", "电子票据号码", "电子票据号", "发票号码", "发票号", "结算单号",
        "Test ID", "Test Id", "Test id", "病人ID号", "患者ID号",
        "Accession Number", "AccNum", "摄片编号", "摄片号", "GCP编号", "GCP号", "床号",
    ),
}

IDENTITY_ROW_HINTS = (
    "姓名", "患者", "病案号", "病历号", "病人号", "住院号", "门诊号", "申请号", "病理号",
    "检查号", "床号", "性别", "年龄", "出生日期", "科室", "病区",
)
ALL_LABELS = tuple(sorted({label for values in LABELS.values() for label in values}, key=len, reverse=True))
FIELD_BOUNDARY_LABELS = ALL_LABELS + (
    "入院日期", "出院日期", "手术日期", "检查日期", "报告日期", "送检日期", "采样日期",
    "性别", "年龄", "科室", "病区", "床号", "诊断", "临床诊断", "检查项目", "检验项目",
)
PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
LANDLINE_RE = re.compile(r"(?<!\d)0\d{2,3}[- ]?\d{7,8}(?:-\d{1,6})?(?!\d)")
NANP_PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[-. ]?)?\(?[2-9]\d{2}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)")
PHONE_VALUE_RE = re.compile(
    r"(?:1[3-9]\d{9}|0\d{2,3}[- ]?\d{7,8}(?:-\d{1,6})?|(?:\+?1[-. ]?)?\(?[2-9]\d{2}\)?[-. ]\d{3}[-. ]\d{4})"
)
ID_RE = re.compile(r"(?<!\d)[1-9]\d{16}[\dXx](?![\dXx])")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
BANK_CARD_RE = re.compile(r"(?<!\d)\d{13,19}(?!\d)")
PATHOLOGY_ID_RE = re.compile(r"(?<![A-Za-z0-9])(?:MP|HP|SE|P|T)\d{2,4}[-_]\d{4,}(?![A-Za-z0-9])", re.IGNORECASE)
PAREN_PATHOLOGY_ID_RE = re.compile(r"(?<=[（(])B\d{7,}(?=[）)])", re.IGNORECASE)
HEADER_YEAR_SERIAL_ID_RE = re.compile(r"(?:19|20)\d{2}[-_]\d{4,}")
ADDRESS_MARKERS = ("省", "市", "区", "县", "镇", "乡", "村", "路", "街", "道", "号", "栋", "单元", "室")
ORGANIZATION_CONTACT_HINTS = (
    "联系我们", "公司地址", "医院地址", "实验室地址", "机构地址",
    "客服电话", "服务热线", "官方网站", "医院网址", "检验科", "免疫室",
    "http://", "https://", "www.",
)
INSTITUTION_TITLE_HINTS = ("医院", "医学院", "诊所", "卫生院", "医学中心", "检验中心", "公司", "集团", "实验室")
STAFF_NAME_HINTS = ("随访医生姓名", "报告医生", "审核医生", "复诊医生", "初诊医生", "记录者", "医师签名", "医生签名")
UI_PERSON_ROLE_HINTS = (
    "门诊医师", "住院医师", "主治医师", "主任医师", "副主任医师", "医生", "护士",
)
CONTACT_IDENTITY_HINTS = (
    "联系人姓名", "联系人地址", "联系电话", "联系人电话", "联系人手机", "联系方式",
)
PATIENT_CONTACT_HINTS = (
    "患者地址", "病人地址", "联系人地址", "联系地址", "家庭地址", "现住址", "户籍地址",
    "患者电话", "病人电话", "联系人电话", "家属电话", "患者手机", "病人手机", "联系人手机",
)


def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def to_rect(box):
    if box is None:
        return None
    if len(box) == 4 and all(isinstance(value, (int, float)) for value in box):
        return [float(value) for value in box]
    points = [point for point in box if isinstance(point, (list, tuple)) and len(point) >= 2]
    if not points:
        return None
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def rect_center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def rect_height(box):
    return max(1.0, box[3] - box[1])


def span_box(text, box, start, end):
    if start is None or end is None or end <= start:
        return list(box)
    length = max(len(text), 1)
    start = max(0, min(start, length))
    end = max(start, min(end, length))
    width = (box[2] - box[0]) / length
    return [box[0] + width * start, box[1], box[0] + width * end, box[3]]


def normalize_records(data):
    records = []

    def add(text, box, score=None):
        rect = to_rect(box)
        if text is not None and str(text).strip() and rect:
            records.append({"text": str(text), "box": rect, "score": score})

    def walk(value):
        if isinstance(value, dict):
            texts = value.get("rec_texts") or value.get("texts")
            boxes = value.get("rec_polys") or value.get("rec_boxes") or value.get("boxes")
            scores = value.get("rec_scores") or value.get("scores") or []
            if isinstance(texts, list) and isinstance(boxes, list):
                for index, text in enumerate(texts):
                    add(text, boxes[index] if index < len(boxes) else None, scores[index] if index < len(scores) else None)
                return
            if "text" in value and any(key in value for key in ("box", "bbox", "poly", "points")):
                add(value.get("text"), value.get("box") or value.get("bbox") or value.get("poly") or value.get("points"), value.get("score"))
                return
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(data)
    return records


def valid_cn_id(candidate):
    text = re.sub(r"[\s\-]", "", candidate).upper()
    if not re.fullmatch(r"[1-9]\d{16}[\dX]", text):
        return False
    weights = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    checks = "10X98765432"
    return checks[sum(int(text[index]) * weights[index] for index in range(17)) % 11] == text[-1]


def valid_luhn(candidate):
    text = re.sub(r"[\s\-]", "", candidate)
    if not re.fullmatch(r"\d{13,19}", text):
        return False
    total = 0
    parity = len(text) % 2
    for index, character in enumerate(text):
        digit = int(character)
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def make_detection(entity, source, record_index, text, box, span=None):
    start, end = span if span else (None, None)
    value = text[start:end] if span else text
    return {
        "entity": entity,
        "source": source,
        "record_index": record_index,
        "text_hash": hash_text(value),
        "value_span": [start, end] if span else None,
        "box": span_box(text, box, start, end),
    }


def label_for_text(text):
    matches = []
    for entity, labels in LABELS.items():
        for label in labels:
            if label in text:
                matches.append((len(label), entity, label))
    if matches:
        _, entity, label = max(matches)
        return entity, label
    return None, None


def is_staff_name_text(text):
    return any(hint in text for hint in STAFF_NAME_HINTS)


def inline_value_span(text, entity, label):
    start = text.find(label) + len(label)
    while start < len(text) and text[start] in " ：:\t":
        start += 1
    remainder = text[start:]
    if not remainder:
        return None
    if entity == "NAME":
        if label in {"Patient Name", "PatientName"}:
            match = re.match(r"[A-Za-z][A-Za-z .,'\-]{2,40}", remainder)
        else:
            match = re.match(r"[\u4e00-\u9fff·][\u4e00-\u9fff·*＊]{1,3}", remainder)
    elif entity == "PHONE":
        match = PHONE_VALUE_RE.search(remainder)
    elif entity == "ID_NUMBER":
        match = re.search(r"[A-Za-z0-9][A-Za-z0-9*＊\s\-]{5,23}", remainder)
    elif entity == "BIRTH_DATE":
        match = re.search(
            r"(?:\d{4}[-./年]\d{1,2}[-./月]\d{1,2}日?|\d{1,2}[-./]\d{1,2}[-./]\d{4}|\d{8})",
            remainder,
        )
    elif entity == "BANK_CARD":
        match = re.search(r"\d[\d\s-]{11,25}\d", remainder)
    elif entity == "ADDRESS":
        value_end = len(remainder)
        for boundary in FIELD_BOUNDARY_LABELS:
            if boundary in LABELS["ADDRESS"]:
                continue
            position = remainder.find(boundary)
            if position >= 0:
                value_end = min(value_end, position)
        value = remainder[:value_end].rstrip(" ：:\t")
        if len(value) < 4:
            return None
        return start, start + len(value)
    else:
        match = re.search(r"[A-Za-z0-9][A-Za-z0-9_./\-]{1,}", remainder)
    if not match:
        return None
    return start + match.start(), start + match.end()


def direct_detections(records):
    hits = []
    for index, record in enumerate(records):
        text = record["text"]
        order_number = re.match(r"^\s*单号\s*[：:]\s*([A-Za-z0-9*＊][A-Za-z0-9*＊\s./_-]{1,})", text)
        if order_number:
            hits.append(make_detection(
                "MEDICAL_ID", "medical-report-order-number", index, text, record["box"], order_number.span(1)
            ))
        for match in PHONE_RE.finditer(re.sub(r"[\s\-]", "", text)):
            compact = re.sub(r"[\s\-]", "", text)
            if compact == text:
                hits.append(make_detection("PHONE", "regex", index, text, record["box"], match.span()))
            else:
                hits.append(make_detection("PHONE", "regex-normalized", index, text, record["box"]))
        for match in LANDLINE_RE.finditer(text):
            hits.append(make_detection("PHONE", "landline-regex", index, text, record["box"], match.span()))
        for match in NANP_PHONE_RE.finditer(text):
            hits.append(make_detection("PHONE", "nanp-phone-regex", index, text, record["box"], match.span()))
        for match in ID_RE.finditer(re.sub(r"[\s\-]", "", text)):
            candidate = match.group(0)
            if valid_cn_id(candidate):
                hits.append(make_detection("ID_NUMBER", "checksum", index, text, record["box"]))
        for match in EMAIL_RE.finditer(text):
            hits.append(make_detection("EMAIL", "regex", index, text, record["box"], match.span()))
        compact = re.sub(r"[\s\-]", "", text)
        for match in BANK_CARD_RE.finditer(compact):
            if valid_luhn(match.group(0)):
                span = match.span() if compact == text else None
                hits.append(make_detection("BANK_CARD", "luhn", index, text, record["box"], span))
        for match in PATHOLOGY_ID_RE.finditer(text):
            hits.append(make_detection("MEDICAL_ID", "pathology-id-regex", index, text, record["box"], match.span()))
        for match in PAREN_PATHOLOGY_ID_RE.finditer(text):
            hits.append(make_detection("MEDICAL_ID", "parenthesized-pathology-id", index, text, record["box"], match.span()))
        entity, label = label_for_text(text)
        if entity == "NAME" and is_staff_name_text(text):
            entity, label = None, None
        if entity and label:
            value_span = inline_value_span(text, entity, label)
            if value_span:
                hits.append(make_detection(entity, "label-inline-value", index, text, record["box"], value_span))
    return hits


def group_rows(records):
    rows = []
    median_height = statistics.median_low([rect_height(record["box"]) for record in records]) if records else 1.0
    for index, record in sorted(enumerate(records), key=lambda item: (rect_center(item[1]["box"])[1], item[1]["box"][0])):
        _, center_y = rect_center(record["box"])
        record_height = rect_height(record["box"])
        for row in rows:
            capped_row_height = min(row["height"], median_height * 1.5)
            capped_record_height = min(record_height, median_height * 1.5)
            center_matches = abs(row["center_y"] - center_y) <= max(capped_row_height, capped_record_height) * 0.8
            vertical_overlap = min(row["y_max"], record["box"][3]) - max(row["y_min"], record["box"][1])
            overlap_matches = (
                len(row["items"]) == 1
                and abs(row["center_y"] - center_y) <= median_height * 1.75
                and vertical_overlap >= min(row["height"], record_height, median_height * 1.5) * 0.5
            )
            if center_matches or overlap_matches:
                row["items"].append((index, record))
                row["item_heights"].append(record_height)
                row["height"] = statistics.median(row["item_heights"])
                row["y_min"] = min(row["y_min"], record["box"][1])
                row["y_max"] = max(row["y_max"], record["box"][3])
                row["center_y"] = sum(rect_center(item[1]["box"])[1] for item in row["items"]) / len(row["items"])
                break
        else:
            rows.append({
                "center_y": center_y,
                "height": record_height,
                "item_heights": [record_height],
                "y_min": record["box"][1],
                "y_max": record["box"][3],
                "items": [(index, record)],
            })
    for row in rows:
        row["items"].sort(key=lambda item: item[1]["box"][0])
    return rows


def row_item_segments(row):
    segments = []
    current = []
    for item in row["items"]:
        if current:
            gap = item[1]["box"][0] - current[-1][1]["box"][2]
            if gap > max(row["height"] * 3.0, 24.0):
                segments.append(current)
                current = []
        current.append(item)
    if current:
        segments.append(current)
    return segments


def virtual_row(items):
    text_parts = []
    mapping = []
    for record_index, record in items:
        raw_text = record["text"]
        token = raw_text.strip()
        leading_offset = len(raw_text) - len(raw_text.lstrip())
        text_parts.append(token)
        mapping.extend((record_index, leading_offset + offset) for offset in range(len(token)))
    return "".join(text_parts), mapping


def virtual_match_detections(records, rows):
    hits = []
    for row in rows:
        for segment in row_item_segments(row):
            text, mapping = virtual_row(segment)
            row_has_id_label = any(label in text for label in LABELS["ID_NUMBER"])
            for match in PHONE_RE.finditer(text):
                hits.extend(mapped_match(records, mapping, match.span(), "PHONE", "split-row"))
            for match in LANDLINE_RE.finditer(text):
                hits.extend(mapped_match(records, mapping, match.span(), "PHONE", "split-row-landline"))
            for match in NANP_PHONE_RE.finditer(text):
                hits.extend(mapped_match(records, mapping, match.span(), "PHONE", "split-row-nanp-phone"))
            for match in ID_RE.finditer(text):
                if valid_cn_id(match.group(0)) or row_has_id_label:
                    hits.extend(mapped_match(records, mapping, match.span(), "ID_NUMBER", "split-row"))
            for match in BANK_CARD_RE.finditer(text):
                if valid_luhn(match.group(0)):
                    hits.extend(mapped_match(records, mapping, match.span(), "BANK_CARD", "split-row-luhn"))
            for label in LABELS["ID_NUMBER"]:
                position = text.find(label)
                if position < 0:
                    continue
                value_start = position + len(label)
                while value_start < len(text) and text[value_start] in " ：:":
                    value_start += 1
                match = re.match(r"[A-Za-z0-9][A-Za-z0-9\-]{5,23}", text[value_start:])
                if match:
                    hits.extend(mapped_match(
                        records,
                        mapping,
                        (value_start + match.start(), value_start + match.end()),
                        "ID_NUMBER",
                        "split-row-labeled-id",
                    ))
                break
            for label in LABELS["BANK_CARD"]:
                position = text.find(label)
                if position < 0:
                    continue
                value_start = position + len(label)
                while value_start < len(text) and text[value_start] in " ：:":
                    value_start += 1
                match = re.match(r"\d{13,19}", text[value_start:])
                if match:
                    hits.extend(mapped_match(
                        records,
                        mapping,
                        (value_start + match.start(), value_start + match.end()),
                        "BANK_CARD",
                        "split-row-labeled-bank-card",
                    ))
                break
            for label in LABELS["MEDICAL_ID"]:
                position = text.find(label)
                if position < 0:
                    continue
                value_start = position + len(label)
                while value_start < len(text) and text[value_start] in " ：:":
                    value_start += 1
                match = re.match(r"[A-Za-z0-9][A-Za-z0-9_./\-]{1,}", text[value_start:])
                if match:
                    hits.extend(mapped_match(records, mapping, (value_start + match.start(), value_start + match.end()), "MEDICAL_ID", "split-row"))
                break
    return hits


def mapped_match(records, mapping, span, entity, source):
    start, end = span
    offsets_by_index = {}
    for position in range(start, min(end, len(mapping))):
        record_index, offset = mapping[position]
        offsets_by_index.setdefault(record_index, []).append(offset)
    return [
        make_detection(
            entity,
            source,
            index,
            records[index]["text"],
            records[index]["box"],
            (min(offsets), max(offsets) + 1),
        )
        for index, offsets in offsets_by_index.items()
    ]


def label_neighbor_detections(records, rows):
    hits = []
    for row in rows:
        for position, (record_index, record) in enumerate(row["items"]):
            entity, label = label_for_text(record["text"])
            if not entity or not label or inline_value_span(record["text"], entity, label):
                continue
            if entity == "NAME" and is_staff_name_text(record["text"]):
                continue
            if position + 1 < len(row["items"]):
                next_index, next_record = row["items"][position + 1]
                horizontal_gap = next_record["box"][0] - record["box"][2]
                pair_height = max(rect_height(record["box"]), rect_height(next_record["box"]))
                max_neighbor_gap = max(pair_height * 4.0, 80.0)
                if horizontal_gap <= max_neighbor_gap and candidate_matches_entity(next_record["text"], entity):
                    hits.append(make_detection(entity, "label-neighbor", next_index, next_record["text"], next_record["box"]))
    return hits


def candidate_matches_entity(text, entity):
    value = text.strip().strip("：:")
    if entity == "NAME":
        name_shape = bool(
            re.fullmatch(r"[\u4e00-\u9fff·][\u4e00-\u9fff·*＊]{1,3}", value)
            or re.fullmatch(r"[A-Za-z][A-Za-z .,'\-]{2,40}", value)
        )
        return name_shape and value not in {
            "检查结论", "临床诊断", "检查项目", "报告日期", "患者信息", "基本信息", "联系电话",
        }
    if entity == "PHONE":
        return bool(PHONE_VALUE_RE.fullmatch(value))
    if entity == "ID_NUMBER":
        compact = re.sub(r"[\s\-]", "", value)
        return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9]{5,23}", compact))
    if entity == "ADDRESS":
        return len(value) >= 4 and bool(re.search(r"省|市|区|县|镇|乡|村|路|街|道|号|栋|单元|室|工作单位", value))
    if entity == "BIRTH_DATE":
        return bool(re.fullmatch(r"(?:\d{4}[-./年]\d{1,2}[-./月]\d{1,2}日?|\d{8})", value))
    if entity == "BANK_CARD":
        return bool(re.fullmatch(r"\d[\d\s-]{11,25}\d", value))
    if entity == "MEDICAL_ID":
        return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./\-]{1,}", value)) and any(character.isdigit() for character in value)
    return False


def address_block_detections(records):
    hits = []
    ordered = sorted(enumerate(records), key=lambda item: (item[1]["box"][1], item[1]["box"][0]))
    median_height = statistics.median([rect_height(record["box"]) for _, record in ordered]) if ordered else 1.0
    for position, (label_index, label_record) in enumerate(ordered):
        label = next((value for value in LABELS["ADDRESS"] if value in label_record["text"]), None)
        if not label:
            continue
        previous_y = rect_center(label_record["box"])[1]
        for other_index, other in ordered[position + 1:]:
            _, other_y = rect_center(other["box"])
            if other_y - previous_y > median_height * 1.8:
                break
            boundary = next((value for value in FIELD_BOUNDARY_LABELS if value in other["text"]), None)
            if boundary and boundary not in LABELS["ADDRESS"]:
                break
            same_line = abs(other_y - rect_center(label_record["box"])[1]) <= median_height * 0.8
            if same_line and other["box"][0] < label_record["box"][2] - median_height:
                continue
            if not any(marker in other["text"] for marker in ADDRESS_MARKERS):
                break
            hits.append(make_detection("ADDRESS", "address-block", other_index, other["text"], other["box"]))
            previous_y = other_y
    return hits


def patient_card_detections(records, image_size):
    if not image_size:
        return []
    _, height = image_size
    hits = []
    for index, record in enumerate(records):
        if rect_center(record["box"])[1] > height * 0.35:
            continue
        match = re.search(r"([\u4e00-\u9fff·][\u4e00-\u9fff·*＊]{1,3})\s*(?:男|女)\s*\d{1,3}\s*岁?", record["text"])
        if match and match.group(1) not in {"患者", "姓名", "报告", "检查", "检验", "临床", "诊断"}:
            hits.append(make_detection("NAME", "patient-card-name", index, record["text"], record["box"], match.span(1)))
    return hits


def masked_id_card_detections(records, rows, image_size):
    if not image_size:
        return []
    hits = []
    for index, record in enumerate(records):
        match = re.search(r"([\u4e00-\u9fff·]{2,4})\s*[（(]\s*身份证", record["text"])
        if match:
            hits.append(make_detection("NAME", "masked-id-card-name", index, record["text"], record["box"], match.span(1)))
    for row in rows:
        for segment in row_item_segments(row):
            text, mapping = virtual_row(segment)
            value_match = re.search(r"身份证\s*([1-9\d*＊Xx][\d*＊Xx\s-]{7,22})", text)
            if not value_match or not re.search(r"[*＊]{2,}", value_match.group(1)):
                continue
            hits.extend(mapped_match(
                records,
                mapping,
                value_match.span(1),
                "ID_NUMBER",
                "masked-id-card-value",
            ))
            identity_card_row = re.search(
                r"[\u4e00-\u9fff·]{2,4}\s*[（(]\s*身份证\s*[1-9\d*＊Xx\s-]{8,23}\s*[）)]",
                text,
            )
            if identity_card_row:
                hits.extend(mapped_match(
                    records,
                    mapping,
                    identity_card_row.span(),
                    "IDENTITY_ROW",
                    "masked-id-card-row",
                ))
    return hits


def source_term_detections(records, source_terms):
    hits = []
    for index, record in enumerate(records):
        for term in source_terms:
            start = 0
            while term:
                position = record["text"].find(term, start)
                if position < 0:
                    break
                end = position + len(term)
                hits.append(make_detection("NAME", "source-name-exact", index, record["text"], record["box"], (position, end)))
                start = end
    return hits


def peripheral_ui_identity_detections(records, image_size):
    """Mask identities shown by PACS/browser chrome around a medical document.

    Medical screenshots frequently include a safely masked report inside an
    otherwise unmasked PACS viewer.  Patient names then survive in a right
    sidebar, image filename, account badge, or browser tab.  These patterns
    are deliberately limited to strong UI evidence so clinical prose is not
    treated as a person name.
    """
    if not image_size:
        return []
    width, height = image_size
    hits = []
    ui_badges = [
        record for record in records
        if re.fullmatch(r"(?:RE|DR|RN|MD)", record["text"].strip(), re.IGNORECASE)
    ]
    for index, record in enumerate(records):
        text = re.sub(r"\s+", "", record["text"])
        center_x, center_y = rect_center(record["box"])

        # PACS/export filenames such as 20248106_张三_2 or 20248106张.
        if re.fullmatch(r"\d{5,}[_-]?[一-鿿·]{1,4}(?:[_-]?\d+)?", text):
            hits.append(make_detection("UI_IDENTITY", "ui-patient-file-name", index, record["text"], record["box"]))
            continue

        # Standalone account/patient names in a right-side viewer panel.
        near_ui_badge = any(
            abs(rect_center(badge["box"])[0] - center_x) <= width * 0.12
            and abs(rect_center(badge["box"])[1] - rect_center(record["box"])[1]) <= 80
            for badge in ui_badges
        )
        if (
            center_x >= width * 0.78
            and near_ui_badge
            and re.fullmatch(r"[一-鿿·]{2,4}", text)
        ):
            hits.append(make_detection("NAME", "ui-side-panel-name", index, record["text"], record["box"]))
            continue

        # Browser/PACS tabs often merge a name and role into one OCR token.
        in_ui_chrome = center_y <= height * 0.12 or center_x >= width * 0.78
        if (
            in_ui_chrome
            and not is_staff_name_text(text)
            and "姓名" not in text
            and any(role in text for role in UI_PERSON_ROLE_HINTS)
        ):
            match = re.match(r"[一-鿿·]{2,4}(?=" + "|".join(map(re.escape, UI_PERSON_ROLE_HINTS)) + r")", text)
            if match:
                hits.append(make_detection("NAME", "ui-name-before-role", index, record["text"], record["box"], match.span()))
    return hits


def english_medical_identity_detections(records, rows, image_size):
    if not image_size:
        return []
    _, height = image_size
    header_limit = height * 0.35
    header_records = [
        (index, record) for index, record in enumerate(records)
        if rect_center(record["box"])[1] <= header_limit
    ]
    header_text = " ".join(record["text"] for _, record in header_records).upper()
    page_text = " ".join(record["text"] for record in records).upper()
    report_anchor = any(
        title in header_text
        for title in (
            "LABORATORY REPORT", "LAB REPORT", "PATHOLOGY REPORT", "MEDICAL REPORT",
            "COMPLETE BLOOD COUNT", "HAEMATOLOGY",
        )
    )
    prescription_anchor = (
        "CLINICAL DESCRIPTION" in page_text
        and ("ADVICE" in page_text or "PRESCRIPTION" in page_text)
    )
    identity_anchors = sum(
        bool(re.search(pattern, header_text))
        for pattern in (
            r"\bNAME\b", r"\bPATIENT\s*ID\b", r"\bAGE\b", r"\bSEX\b",
            r"\bGENDER\b", r"\bTEST\s*ID\b", r"\bREG(?:ISTRATION)?\.?\s*(?:NO|NUMBER)\b",
        )
    )
    if not (report_anchor or prescription_anchor) or identity_anchors < 2:
        return []

    hits = []
    for index, record in header_records:
        text = record["text"].strip()
        name_match = re.match(
            r"(?:Patient\s+)?Name\s*[:：]\s*([A-Za-z][A-Za-z .,'\-]{1,60})",
            text,
            re.IGNORECASE,
        )
        if name_match:
            hits.append(make_detection(
                "NAME", "english-medical-identity", index, text, record["box"], name_match.span(1)
            ))
        age_sex_match = re.match(
            r"Age\s*(?:/|,|and)\s*(?:Sex|Gender)\s*[:：]?\s*(.+)",
            text,
            re.IGNORECASE,
        )
        if not age_sex_match:
            age_sex_match = re.match(r"Age\s*[:：]?\s*(\d.{0,25})", text, re.IGNORECASE)
        if age_sex_match:
            hits.append(make_detection(
                "AGE_SEX", "english-medical-identity", index, text, record["box"], age_sex_match.span(1)
            ))
        sex_match = re.match(r"(?:Sex|Gender)\s*[:：]?\s*(.+)", text, re.IGNORECASE)
        if sex_match:
            hits.append(make_detection(
                "SEX", "english-medical-identity", index, text, record["box"], sex_match.span(1)
            ))
        if report_anchor:
            registration_match = re.match(
                r"Reg(?:istration)?\.?\s*(?:No|Number)\.?\s*[:：]\s*([A-Za-z0-9][A-Za-z0-9./_\-]{1,30})",
                text,
                re.IGNORECASE,
            )
            if registration_match:
                hits.append(make_detection(
                    "MEDICAL_ID", "english-medical-identity", index, text, record["box"], registration_match.span(1)
                ))
        address_match = re.match(
            r"(?:Patient\s+Address|Address|Collected\s+at)\s*[:：]\s*(.{4,100})",
            text,
            re.IGNORECASE,
        )
        if address_match:
            hits.append(make_detection(
                "ADDRESS", "english-medical-identity", index, text, record["box"], address_match.span(1)
            ))

        # Some reports print the patient name alone above the demographic labels.
        honorific_name = re.fullmatch(
            r"(?:Mr|Mrs|Ms|Miss|Master)\.?\s+[A-Za-z][A-Za-z .,'\-]{1,60}",
            text,
            re.IGNORECASE,
        )
        if honorific_name and rect_center(record["box"])[1] <= height * 0.15:
            hits.append(make_detection(
                "NAME", "english-medical-header-name", index, text, record["box"]
            ))

    for row in rows:
        for segment in row_item_segments(row):
            text, mapping = virtual_row(segment)
            patterns = [
                ("AGE_SEX", r"Age\s*(?:/|,|and)\s*(?:Sex|Gender)\s*[:：]?\s*([^:]{1,30})"),
            ]
            if report_anchor:
                patterns.append((
                    "MEDICAL_ID",
                    r"Reg(?:istration)?\.?\s*(?:No|Number)\.?\s*[:：]\s*([A-Za-z0-9][A-Za-z0-9./_\-]{1,30})",
                ))
            for entity, pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    hits.extend(mapped_match(
                        records, mapping, match.span(1), entity, "english-medical-split-row"
                    ))

    name_label_indexes = {
        index for index, record in header_records
        if re.fullmatch(r"Name\s*[:：]?", record["text"].strip(), re.IGNORECASE)
    }
    for row in rows:
        items = sorted(row["items"], key=lambda item: item[1]["box"][0])
        for position, (index, record) in enumerate(items):
            if index not in name_label_indexes:
                continue
            for value_index, value_record in items[position + 1:]:
                gap = value_record["box"][0] - record["box"][2]
                if gap < -2 or gap > max(row["height"] * 4.0, 90.0):
                    continue
                value = value_record["text"].strip()
                if re.fullmatch(r"[A-Za-z][A-Za-z .,'\-]{1,60}", value):
                    hits.append(make_detection("NAME", "english-medical-name-neighbor", value_index, value, value_record["box"]))
                break
    return hits


def english_patient_register_name_detections(records, image_size):
    if not image_size:
        return []
    page_text = " ".join(record["text"] for record in records).upper()
    if "REGISTER" not in page_text and "DATE OF ADMISSION" not in page_text:
        return []
    anchors = [
        record for record in records
        if any(label in record["text"].upper() for label in (
            "NAME OF PATIENT",
            "PATIENT NAME",
            "CHRISTIAN AND SURNAME",
        ))
    ]
    hits = []
    for anchor in anchors:
        anchor_width = max(1.0, anchor["box"][2] - anchor["box"][0])
        anchor_center = (anchor["box"][0] + anchor["box"][2]) / 2
        left = anchor_center - anchor_width * 0.9
        right = anchor_center + anchor_width * 0.9
        for index, record in enumerate(records):
            if record is anchor or record["box"][1] <= anchor["box"][3]:
                continue
            record_center = (record["box"][0] + record["box"][2]) / 2
            if not left <= record_center <= right:
                continue
            text = record["text"].strip()
            if not re.search(r"[A-Za-z]", text) or len(text) > 80:
                continue
            hits.append(make_detection(
                "NAME", "english-patient-register-column", index, text, record["box"]
            ))
    return hits


def identity_row_detections(records, rows, image_size):
    hits = []
    height_limit = image_size[1] * 0.35 if image_size else float("inf")
    for row in rows:
        if row["center_y"] > height_limit:
            continue
        text = " ".join(record["text"] for _, record in row["items"])
        hint_count = sum(1 for hint in IDENTITY_ROW_HINTS if hint in text)
        anchor = any(value in text for value in ("姓名", "患者", "病案号", "病历号", "住院号", "门诊号", "申请号", "病理号", "检查号"))
        if not anchor or hint_count < 2:
            continue
        for index, record in row["items"]:
            hits.append(make_detection("IDENTITY_ROW", "identity-context-row", index, record["text"], record["box"]))
    return hits


def contact_identity_row_detections(rows):
    hits = []
    for row in rows:
        text = " ".join(record["text"] for _, record in row["items"])
        if sum(1 for hint in CONTACT_IDENTITY_HINTS if hint in text) < 2:
            continue
        for index, record in row["items"]:
            hits.append(make_detection("IDENTITY_ROW", "contact-identity-row", index, record["text"], record["box"]))
    return hits


def contact_address_row_detections(rows):
    hits = []
    for row in rows:
        text = "".join(record["text"] for _, record in row["items"])
        hierarchy_markers = sum(marker in text for marker in ("省", "市", "区", "县", "镇", "乡", "村", "路", "街", "号"))
        complete_address_label = any(label in text for label in LABELS["ADDRESS"])
        if "联系" not in text or hierarchy_markers < 2 or complete_address_label:
            continue
        for index, record in row["items"]:
            hits.append(make_detection("IDENTITY_ROW", "contact-address-row", index, record["text"], record["box"]))
    return hits


def header_medical_id_band_detections(rows, image_size):
    if not image_size:
        return []
    width, height = image_size
    labels = ("ID号", "影像号", "检查号", "检验号", "病理号", "报告号", "住院号", "门诊号", "病案号", "病历号")
    graphic_code_hints = ("二维码", "条形码", "条码", "扫码", "QR")
    hits = []
    for row in rows:
        if row["center_y"] > height * 0.35:
            continue
        text = re.sub(r"\s", "", "".join(record["text"] for _, record in row["items"]))
        if sum(label in text for label in labels) < 2:
            continue
        band_items = [
            (index, record)
            for index, record in row["items"]
            if not any(hint.lower() in record["text"].lower() for hint in graphic_code_hints)
        ]
        first_index = band_items[0][0]
        boxes = [record["box"] for _, record in band_items]
        padding = max(row["height"] * 0.2, 2.0)
        band_box = [
            max(0.0, min(box[0] for box in boxes) - padding),
            max(0.0, min(box[1] for box in boxes) - padding),
            min(float(width), max(box[2] for box in boxes) + padding),
            min(float(height), max(box[3] for box in boxes) + padding),
        ]
        hits.append(make_detection("IDENTITY_ROW", "header-medical-id-band", first_index, text, band_box))
    return hits


def header_identifier_detections(records, rows, image_size):
    if not image_size:
        return []
    height_limit = image_size[1] * 0.35
    exclusion_hints = ("组织机构代码", "机构代码", "设备型号", "仪器型号", "型号")
    hits = []
    for row in rows:
        if row["center_y"] > height_limit:
            continue
        row_text = " ".join(record["text"] for _, record in row["items"])
        if any(hint in row_text for hint in exclusion_hints):
            continue
        for index, record in row["items"]:
            value = re.sub(r"\s", "", record["text"])
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_\-]{5,}", value):
                continue
            if sum(character.isdigit() for character in value) < 4:
                continue
            if re.fullmatch(r"20\d{2}[-_]?\d{1,2}[-_]?\d{1,2}", value):
                continue
            if (
                "-" in value
                and not any(character.isalpha() for character in value)
                and not HEADER_YEAR_SERIAL_ID_RE.fullmatch(value)
            ):
                continue
            hits.append(make_detection("MEDICAL_ID", "header-unlabeled-identifier", index, record["text"], record["box"]))
    return hits


def header_footer_detections(records, image_size):
    if not image_size:
        return []
    _, height = image_size
    hits = []
    for index, record in enumerate(records):
        center_y = rect_center(record["box"])[1]
        entity, label = label_for_text(record["text"])
        if (
            (center_y <= height * 0.08 or center_y >= height * 0.90)
            and len(record["text"].strip()) >= 3
            and entity
            and label
            and not (entity == "NAME" and is_staff_name_text(record["text"]))
        ):
            hits.append(make_detection("HEADER_FOOTER_TEXT", "header-footer-band", index, record["text"], record["box"]))
    return hits


def organization_contact_indexes(records, image_size=None):
    anchors = [
        rect_center(record["box"])[1]
        for record in records
        if any(hint in record["text"] for hint in ORGANIZATION_CONTACT_HINTS)
    ]
    if not anchors:
        return set()
    page_height = image_size[1] if image_size else max(record["box"][3] for record in records)
    patient_anchors = (
        "患者姓名", "病员姓名", "姓名", "患者电话", "患者手机", "病人电话", "病人手机",
        "家属电话", "联系人电话", "身份证", "病历号", "病案号", "住院号", "门诊号",
    )
    result = set()
    for anchor_y in anchors:
        upper_y = anchor_y + page_height * 0.22
        boundaries = [
            rect_center(record["box"])[1]
            for record in records
            if rect_center(record["box"])[1] > anchor_y
            and any(label in record["text"] for label in patient_anchors)
        ]
        if boundaries:
            upper_y = min(upper_y, min(boundaries))
        result.update(
            index for index, record in enumerate(records)
            if anchor_y <= rect_center(record["box"])[1] < upper_y
        )
    return result


def institution_title_contact_indexes(records):
    title_records = [
        record for record in records
        if any(hint in record["text"] for hint in INSTITUTION_TITLE_HINTS)
    ]
    if not title_records:
        return set()
    result = set()
    for index, record in enumerate(records):
        if not LANDLINE_RE.search(record["text"]):
            continue
        _, phone_y = rect_center(record["box"])
        for title in title_records:
            _, title_y = rect_center(title["box"])
            nearby_limit = max(rect_height(record["box"]), rect_height(title["box"])) * 3.0 + 20.0
            if abs(phone_y - title_y) <= nearby_limit:
                result.add(index)
                break
    return result


def institution_footer_contact_indexes(records, rows, image_size):
    if not image_size or not any(
        any(hint in record["text"] for hint in INSTITUTION_TITLE_HINTS)
        for record in records
    ):
        return set()
    footer_start = image_size[1] * 0.88
    footer_records = [
        (index, record) for index, record in enumerate(records)
        if rect_center(record["box"])[1] >= footer_start
    ]
    footer_text = "".join(record["text"] for _, record in footer_records)
    has_url = any(hint in footer_text for hint in ("网址", "网站", "http://", "https://", "www."))
    has_landline = bool(LANDLINE_RE.search(footer_text))
    has_explicit_organization_hint = any(hint in footer_text for hint in ORGANIZATION_CONTACT_HINTS)
    block_has_organization_evidence = has_url or has_landline or has_explicit_organization_hint
    result = set()
    for index, record in footer_records:
        text = record["text"]
        if any(hint in text for hint in PATIENT_CONTACT_HINTS):
            continue
        explicit = any(hint in text for hint in ORGANIZATION_CONTACT_HINTS)
        url = any(hint in text for hint in ("网址", "网站", "http://", "https://", "www."))
        landline = bool(LANDLINE_RE.search(text))
        address = "地址" in text
        if explicit or url or landline or (address and block_has_organization_evidence):
            result.add(index)
    for row in rows:
        if row["center_y"] < footer_start:
            continue
        text = "".join(record["text"] for _, record in row["items"])
        hierarchy_markers = sum(marker in text for marker in ("省", "市", "区", "县", "镇", "乡", "村", "路", "街", "号"))
        organization_contact_row = (
            any(hint in text for hint in ORGANIZATION_CONTACT_HINTS)
            or any(hint in text for hint in ("网址", "网站", "http://", "https://", "www."))
            or bool(LANDLINE_RE.search(text))
            or (("地址" in text or ("联系" in text and hierarchy_markers >= 2)) and block_has_organization_evidence)
        )
        if organization_contact_row and not any(hint in text for hint in PATIENT_CONTACT_HINTS):
            result.update(index for index, _ in row["items"])
    return result


def institution_staff_footer_contact_indexes(rows):
    staff_hints = ("送检医师", "检验医师", "审核医师", "报告医师", "报告医生", "报告时间")
    contact_hints = ("地址", "联系电话", "电话", "网址", "网站", "http://", "https://", "www.")
    result = set()
    for anchor in rows:
        anchor_text = "".join(record["text"] for _, record in anchor["items"])
        if sum(hint in anchor_text for hint in staff_hints) < 2:
            continue
        lower_limit = anchor["center_y"] + max(anchor["height"] * 4.0, 120.0)
        for row in rows:
            if not (anchor["center_y"] <= row["center_y"] <= lower_limit):
                continue
            text = "".join(record["text"] for _, record in row["items"])
            if any(hint in text for hint in contact_hints) and not any(hint in text for hint in PATIENT_CONTACT_HINTS):
                result.update(index for index, _ in row["items"])
    return result


def merge_detections(detections):
    merged = []
    seen = set()
    for detection in detections:
        key = (
            detection["entity"],
            detection["record_index"],
            tuple(round(value, 1) for value in detection["box"]),
        )
        if key not in seen:
            seen.add(key)
            merged.append(detection)
    return merged


def detect(records, image_size=None, source_terms=()):
    records = normalize_records(records)
    rows = group_rows(records)
    detections = direct_detections(records)
    detections.extend(virtual_match_detections(records, rows))
    detections.extend(label_neighbor_detections(records, rows))
    detections.extend(address_block_detections(records))
    detections.extend(patient_card_detections(records, image_size))
    detections.extend(masked_id_card_detections(records, rows, image_size))
    detections.extend(source_term_detections(records, source_terms))
    detections.extend(peripheral_ui_identity_detections(records, image_size))
    detections.extend(english_medical_identity_detections(records, rows, image_size))
    detections.extend(english_patient_register_name_detections(records, image_size))
    detections.extend(header_identifier_detections(records, rows, image_size))
    detections.extend(identity_row_detections(records, rows, image_size))
    detections.extend(contact_identity_row_detections(rows))
    detections.extend(contact_address_row_detections(rows))
    detections.extend(header_medical_id_band_detections(rows, image_size))
    detections.extend(header_footer_detections(records, image_size))
    organization_indexes = organization_contact_indexes(records, image_size)
    organization_indexes.update(institution_title_contact_indexes(records))
    organization_indexes.update(institution_footer_contact_indexes(records, rows, image_size))
    organization_indexes.update(institution_staff_footer_contact_indexes(rows))
    detections = [
        detection for detection in detections
        if not (
            detection["record_index"] in organization_indexes
            and (
                detection["entity"] in {"ADDRESS", "PHONE", "EMAIL"}
                or detection["source"] == "header-footer-band"
                or detection["source"] == "contact-address-row"
            )
        )
    ]
    return merge_detections(detections)
