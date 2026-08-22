---
name: phi-pii-medical-deidentify
description: Local PHI and PII de-identification and irreversible redaction for Chinese medical records and sensitive healthcare documents. Use for privacy masking, anonymization, HIPAA-oriented data preparation, export review, or residual-identifier checks across images, screenshots, scans, PDFs, DOCX, XLSX, TXT, Markdown, JSON, CSV, and OCR output.
---

# 病历材料去隐私化

这是一个不依赖任何业务项目的本地化去隐私 Skill。它使用本地 PaddleOCR、确定性检测规则和不可逆黑块生成去隐私化副本，并用二次 OCR 做残留复检。需要增强复杂上下文判断时，可在 OCR 后接入运行于本机或受控内网的 4B 参数以下小语言模型；OCR 与小模型是串联关系，不是二选一。原图、完整 OCR 明文和患者字段不得发送给公共 OCR 服务或云端大模型。

`PHI` 指与个人身份关联的健康信息，`PII` 指可识别个人身份的信息。这里的 `HIPAA-oriented` 仅表示面向相关隐私准备场景，不代表获得认证，也不构成 HIPAA 合规保证。

## 路由

- 文本文件：运行 `scripts/deidentify.py` 的确定性文本规则；输出占位符副本，不支持还原。
- 图片：使用本地 OCR 获取文字与坐标，检测后写入黑块。
- PDF：逐页渲染、遮挡、重新组装；保留逐页审计报告。
- DOCX：无媒体时直接处理 OOXML 文本；含媒体时转 PDF 后按图像处理。
- XLSX：转 PDF 后按图像处理。
- 目录：批量处理并生成 `summary.json`、`summary.md`、缩略图和 contact sheet。

## 快速使用

先安装依赖：

```bash
python -m pip install -r requirements.txt
```

如果平台没有可用的 PaddlePaddle wheel，先按平台安装 PaddlePaddle，再安装 `paddleocr`。敏感材料默认只交给本地 OCR，不上传公共 OCR API。

运行批处理：

```bash
python scripts/deidentify.py \
  --input /path/to/materials \
  --output-dir /path/to/redacted-run \
  --model PP-OCRv6_medium \
  --max-rounds 2
```

运行 Skill 自检：

```bash
python scripts/validate_skill.py
python -m pytest -q
```

`--max-rounds` 只能是 `1` 或 `2`；生产去隐私化使用 `2`。原文件不会被覆盖，结果写入独立的 `redacted_files/` 目录。

## 默认遮挡与保留

默认遮挡：患者姓名、联系人/家属姓名、身份证和其他证件号、手机/座机、邮箱、银行卡号、家庭或联系地址、工作单位、出生日期，以及病案号、住院号、门诊号、处方号、医保卡号、检验单号、医嘱号、病理号、样本号、CT/MRI 号等患者关联编号。

默认保留：疾病、诊断、药物、剂量、检验项目和值、参考范围、检查结论、医院/科室、入出院和检查日期、医务人员姓名。二维码和条码按当前策略不主动遮挡。

详细字段边界与人工审核条件见 [references/redaction-policy.md](references/redaction-policy.md)。需要调整字段范围时先修改该策略和测试，再修改检测器。

## 安全要求

1. 只能写独立输出目录，不覆盖原件。
2. 图片和渲染后的文档使用不透明黑块，不使用模糊、透明层或前端遮罩。
3. 第一轮遮挡后必须再 OCR；若仍命中，最多补遮一次。
4. 补遮后仍有敏感命中、OCR 过稀/过低置信度、文本框几何明显不规则、旋转严重或正文遮挡过宽时，报告 `needs_manual_review`，不能宣称自动通过。
5. 审计报告只保存实体类型、检测来源、坐标、轮次、置信度（若 OCR 提供）和不含原值的审核指纹。
6. 不把二次 OCR 代理通过率当作真实召回率或准确率。
7. 人脸、头像、手写签名、指纹和未被 OCR 识别的图形信息仍需人工视觉审核。
8. 默认不允许把原图、完整 OCR 明文或患者字段发送给公共大模型；可选语义模型必须部署在本机或受控内网。

## 代码边界

- `scripts/detector.py`：OCR 记录标准化、正则/校验码、标签邻域、同行重组、版面和来源文件名检测。
- `scripts/policy.py`：正文/结构化身份区的遮挡宽度和行覆盖率限制。
- `scripts/pipeline.py`：方向选择、遮挡、二次 OCR 和人工审核结果。
- `scripts/deidentify.py`：文件格式路由、PDF/Office 转换、输出、审计和汇总。
- `scripts/evaluation.py`：生成字段/页面/文档级二次 OCR 代理指标。
- `scripts/evaluate_labeled_set.py`：用显式真值独立检查脱敏前后 OCR，不复用检测规则。

这些脚本只能依赖本目录内模块和 `requirements.txt` 中的第三方库；不要加入业务项目、数据库、项目配置或云端 OCR 依赖。

## 失败处理

- 输入格式不支持、依赖缺失、OCR 失败、输出文件缺失或最终残留不为零，都应停止该文档并保留错误报告。
- 先检查 `summary.json` 的 `residual_detections` 和 `manual_review`，再使用 `redacted_files/`。
- `summary.md` 中的通过率只用于自动复检趋势，不用于合规或准确率承诺。
