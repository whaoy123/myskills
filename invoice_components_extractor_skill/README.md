# invoice_components_extractor_skill

从采购发票 PDF 自动化提取纯焊接元器件清单（格式：类别 + 型号 + 封装 + 数量）。

## 特性
- 自动过滤手套劳保、PCB裸板、塑料外壳、运费及折扣
- 纯净提取电阻、电容、芯片、传感器、端子与连接器
- 自动识别封装形式（0805贴片、SOP-8、AXIAL插件、D-SUB弯插等）
- 导出格式美观的 Excel 表格与 Markdown 表格

## 使用方法
```bash
python scripts/extract_soldering_components.py \
  --invoices-dir "/path/to/invoices" \
  --output-xlsx "焊接元器件清单.xlsx"
```
