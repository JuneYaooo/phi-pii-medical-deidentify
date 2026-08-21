def _rate(numerator, denominator):
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator * 100, 2)


def _add_counts(target, source):
    for entity, count in source.items():
        target[entity] = target.get(entity, 0) + count


def _detection_counts(item):
    counts = {}
    scopes = item.get("page_reports") or [item]
    for scope in scopes:
        found_audit_detections = False
        for audit_round in scope.get("audit_rounds") or []:
            for detection in audit_round.get("detections") or []:
                entity = detection.get("entity", "UNKNOWN")
                counts[entity] = counts.get(entity, 0) + 1
                found_audit_detections = True
        if not found_audit_detections:
            _add_counts(counts, scope.get("by_entity") or {})
    return counts


def _residual_counts(item):
    counts = {}
    scopes = item.get("page_reports") or [item]
    for scope in scopes:
        _add_counts(counts, scope.get("residual_by_entity") or {})
    return counts


def _manual_review_count(items):
    total = 0
    for item in items:
        seen = set()
        for index, finding in enumerate(item.get("manual_review") or []):
            key = finding.get("finding_hash") or (
                finding.get("entity"),
                finding.get("source"),
                tuple(finding.get("box") or ()),
                finding.get("reason"),
                index,
            )
            seen.add(key)
        total += len(seen)
    return total


def summarize(items):
    total_documents = len(items)
    total_pages = sum(item.get("pages", 0) for item in items)
    total_detections = sum(item.get("detections", 0) for item in items)
    total_residual = sum(item.get("residual_detections", 0) for item in items)
    clean_documents = sum(
        1 for item in items
        if item.get("residual_detections", 0) == 0 and not (item.get("manual_review") or [])
    )
    clean_pages = 0
    detections_by_entity = {}
    residual_by_entity = {}
    for item in items:
        _add_counts(detections_by_entity, _detection_counts(item))
        _add_counts(residual_by_entity, _residual_counts(item))
        page_reports = item.get("page_reports") or []
        if page_reports:
            clean_pages += sum(
                1 for page in page_reports
                if page.get("residual_detections", 0) == 0 and not (page.get("manual_review") or [])
            )
        elif item.get("residual_detections", 0) == 0 and not (item.get("manual_review") or []):
            clean_pages += item.get("pages", 0)
    proxy_by_entity = {}
    for entity in sorted(set(detections_by_entity) | set(residual_by_entity)):
        detections = detections_by_entity.get(entity, 0)
        residuals = residual_by_entity.get(entity, 0)
        proxy_by_entity[entity] = {
            "detections": detections,
            "residual_detections": residuals,
            "proxy_pass_rate": _rate(max(0, detections - residuals), detections),
        }
    return {
        "documents": total_documents,
        "pages": total_pages,
        "detections": total_detections,
        "residual_detections": total_residual,
        "documents_with_residual": total_documents - clean_documents,
        "manual_review_findings": _manual_review_count(items),
        "proxy_field_pass_rate": _rate(total_detections - total_residual, total_detections),
        "proxy_page_pass_rate": _rate(clean_pages, total_pages),
        "proxy_document_pass_rate": _rate(clean_documents, total_documents),
        "detections_by_entity": detections_by_entity,
        "residual_by_entity": residual_by_entity,
        "proxy_by_entity": proxy_by_entity,
    }


def render_markdown(summary):
    lines = [
        "# 病历材料脱敏评估",
        "",
        f"- 文档数: {summary['documents']}",
        f"- 页数: {summary['pages']}",
        f"- 二次 OCR 仍有规则命中的文档: {summary.get('documents_with_residual', 0)}",
        f"- 二次 OCR 规则命中总数: {summary['residual_detections']}",
        f"- 人工复核项: {summary.get('manual_review_findings', 0)}",
        f"- 字段级二次 OCR 表观通过率: {summary['proxy_field_pass_rate']}%",
        f"- 页面级二次 OCR 表观通过率: {summary['proxy_page_pass_rate']}%",
        f"- 文档级二次 OCR 表观通过率: {summary['proxy_document_pass_rate']}%",
        "",
        "> 上述指标是自动复检代理指标，不是人工标注准确率。",
    ]
    proxy_by_entity = summary.get("proxy_by_entity") or {}
    if proxy_by_entity:
        lines.extend([
            "",
            "## 分类二次 OCR 表观通过率",
            "",
            "| 类型 | 遮挡命中 | 最终残留 | 表观通过率 |",
            "|---|---:|---:|---:|",
        ])
        for entity, values in proxy_by_entity.items():
            lines.append(
                f"| {entity} | {values['detections']} | "
                f"{values['residual_detections']} | {values['proxy_pass_rate']}% |"
            )
    return "\n".join(lines) + "\n"

