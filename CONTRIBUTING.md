# Contributing / 贡献指南

Thank you for helping improve PHI / PII Medical De-identify. Privacy tooling needs conservative changes, reproducible tests, and careful handling of examples.

感谢你帮助改进 PHI / PII 病历去隐私化。隐私工具的修改必须保持保守、可复现，并谨慎处理所有示例材料。

## Ground rules / 基本规则

- Never commit, upload, paste, or screenshot real PHI, PII, medical records, credentials, or production logs.
- 绝不提交、上传、粘贴或截图真实 PHI、PII、病历、凭证或生产日志。
- Use synthetic values and generated documents in tests and issue reproductions.
- 测试和问题复现只能使用合成值与生成材料。
- Do not weaken irreversible masking, residual verification, audit-value omission, or human-review gates without an explicit security rationale.
- 除非有明确安全论证，不得弱化不可逆遮挡、残留复检、审计原值省略或人工审核闸门。
- Keep runtime code independent of application databases, project configuration, and cloud OCR services.
- 运行时代码必须继续独立于业务数据库、项目配置和云端 OCR 服务。

## What to contribute / 可以贡献什么

- Detection coverage for patient identifiers, OCR splits, Chinese document layouts, and medical record-number variants.
- 患者标识符、OCR 拆框、中文文档版面和医疗编号变体的检测规则。
- False-positive reductions that preserve clinical findings, medication, dose, laboratory values, and institution contact details.
- 在保留临床所见、药物、剂量、检验值和机构联系信息前提下减少误遮。
- Cross-platform file handling, local OCR compatibility, performance, documentation, and synthetic regression tests.
- 跨平台文件处理、本地 OCR 兼容性、性能、文档和合成回归测试。

## Local validation / 本地验证

The lightweight test suite does not require model inference:

```bash
python -m pip install pytest Pillow
python scripts/validate_skill.py
python -m pytest -q
```

For an OCR integration test, install the full requirements and run only on synthetic materials:

```bash
python -m pip install -r requirements.txt
python scripts/deidentify.py \
  --input /path/to/synthetic-materials \
  --output-dir /path/to/test-run \
  --max-rounds 2
```

## Detection-rule checklist / 检测规则变更清单

When adding or changing a rule, include:

1. A synthetic positive case that should be masked.
2. A nearby negative case that must remain readable.
3. A split-OCR or layout case when geometry matters.
4. Assertions that reports do not contain the original sensitive value.
5. An explanation of whether the change affects body-mask width or manual-review behavior.

新增或修改规则时，请同时提供：应遮挡的合成正例、必须保留的相邻反例、必要的拆框/版面案例、报告不含原值的断言，以及对正文遮挡宽度和人工审核行为的影响说明。

## Pull requests / Pull Request

- Keep each pull request focused on one detection, format, safety, or documentation concern.
- In the description, list the synthetic cases, test commands, results, and privacy impact.
- Do not describe automatic OCR proxy metrics as real-world accuracy without a labeled evaluation set.
- If behavior becomes broader or more destructive, call it out explicitly and include visual-review guidance.

自动化测试通过只表示实现可复现，不表示已经完成隐私、法律或 HIPAA 合规验收。
