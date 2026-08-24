# invoice_components_extractor_skill

从采购资料中提取明确的可焊接电子元器件，并把无法可靠判断的行单独放进待复核清单。

支持：

- PDF 电子发票（逐页文本提取）
- XLSX 采购/发票明细
- CSV 采购/发票明细
- include / exclude / review 三态判定
- 来源文件、页/Sheet/行、原始文本追溯
- 默认单来源内部安全合并，避免采购表 + 发票重复计数
- Excel / CSV / JSON 输出
- 可选 Markdown 输出

## 安装

```bash
pip install pdfplumber openpyxl
```

## 使用

```bash
python scripts/extract_soldering_components.py \
  --input /path/to/invoices \
  --output-dir /path/to/output
```

兼容旧接口：

```bash
python scripts/extract_soldering_components.py \
  --invoices-dir /path/to/invoices \
  --output-xlsx /path/to/components.xlsx
```

可选 Markdown：

```bash
--markdown /path/to/components.md
```

不同输入文件已经确认代表独立采购、不会重复计数时，才允许：

```bash
--merge-across-sources
```

默认不会把 `采购表.xlsx` 和 `发票.pdf` 中的同型号数量直接相加。

## 输出

```text
components_output/
├── components.xlsx
├── components.csv
├── review.csv
├── normalized_records.csv
└── validation_report.json
```

`components.xlsx` 包含：

- `元器件清单`
- `待复核`

## 重要边界

这个 Skill 只回答“采购证据里出现了什么”。

它不能仅凭发票判断 PCB 实际应该焊什么，也不能自行确定缺货替换关系。正式焊接清单仍应结合 BOM、网表、原理图、采购表和发票，由 `pcb_soldering_table_skill` 完成。

## 测试

```bash
python -m unittest discover -s tests -v
```
