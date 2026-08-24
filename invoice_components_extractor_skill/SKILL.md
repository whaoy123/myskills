---
name: invoice_components_extractor_skill
description: 从采购发票或采购明细 PDF/XLSX/CSV 中提取“采购证据里出现的可焊接电子元器件”，保留来源证据并将每条记录判为 include/exclude/review。用于采购清单整理、焊接物料采购证据提取和下游焊接清单输入准备。不得仅凭发票判断 PCB 实际需要焊什么；最终装配集合仍由 BOM/网表/原理图决定。
---

# Invoice Components Extractor

从采购资料里整理出：

> **明确买了哪些可焊接电子元器件，以及哪些行还需要人工复核。**

这个 Skill 处理的是**采购证据**，不是 PCB 装配真值。

## 职责边界

本 Skill 负责：

- 读取 PDF / XLSX / CSV 采购资料；
- 将原始行规范化；
- 区分元器件、费用/折扣、工具/机械件和无法判断项；
- 对每条记录保留来源文件、页/Sheet/行、原始文本和判定依据；
- 只对明确可安全合并的元器件汇总数量；
- 生成清单、待复核项和校验报告；
- 为 `pcb_soldering_table_skill` 提供采购侧证据。

本 Skill 不负责：

- 判断某个器件是否真的应该装到 PCB；
- 用发票替代 BOM、网表或原理图；
- 根据相似名字擅自建立 `原型号 → 替换型号` 映射；
- 猜测缺失型号、封装或数量；
- 因为某行“看起来不像器件”就静默丢弃不确定记录；
- 默认把采购表和发票中的同一笔订单重复累加。

下游正式焊接清单仍应使用：

```text
网表 / BOM / 原理图
        +
采购表 / 发票采购证据
        ↓
pcb_soldering_table_skill
```

## 输入

接受：

- 单个 `.pdf`；
- 单个 `.xlsx`；
- 单个 `.csv`；
- 包含上述文件的目录。

### PDF

逐页读取文本，不再只读第一页。

适合已经能直接提取文字的电子发票。扫描件如果没有可提取文本，本 Skill 只记录 source warning，不应通过反复 OCR 猜数据。

### XLSX / CSV

结构化输入至少需要能识别：

- 项目/商品名称；
- 数量。

可选：

- 规格型号；
- 单位。

脚本支持常见中文表头别名，例如 `项目名称 / 商品名称 / 名称 / 品名`、`规格型号 / 型号 / 规格`。

## 三态判定

每条规范化记录必须进入且只进入一种状态：

```text
include
exclude
review
```

### `include`

有足够证据判断为实际可焊接电子元器件，例如：

- 电阻、电容、电感；
- IC、传感器、运放、隔离器；
- 二极管、MOSFET；
- 端子、连接器、排针；
- 晶振、继电器、保险丝、电源模块等。

### `exclude`

有明确证据不是目标元器件，例如：

- 运费、配送费、包装费、服务费；
- 折扣、优惠、负数金额行；
- 工具、劳保；
- PCB 裸板；
- 外壳、螺丝、铜柱、胶水等机械/辅材。

### `review`

当前证据不足，例如：

- PDF 行结构解析失败；
- 数量字段无法读取；
- 名称过于宽泛，无法确定是否为焊接件；
- 型号/规格信息不足而会影响后续合并；
- 新供应商格式不符合已有解析规则。

核心规则：

> **不确定就进入 review，不静默排除。**

`review` 不是脚本失败，而是明确的人机验收点。

## Provenance

每条标准化记录至少保存：

```text
source_file
source_type
source_page / source_sheet
source_row
raw_text
name
model
qty
unit
decision
reason
```

最终清单中的聚合行必须保留来源集合，例如：

```text
invoice-a.pdf:page 1 line 18
```

如果用户明确允许跨来源合并，也可以出现：

```text
order-a.csv:row 7；order-b.csv:row 11
```

不能只输出一个无法回溯的总数量。

## 分类与封装

`include` 后再推断：

```text
category
normalized_model
package
```

封装只在文本有明确证据时写具体值，例如：

```text
0805 (SMD)
SOP-8 (SMD)
QFN-32 (SMD)
间距 9.52 mm (THT)
```

证据不足就写：

```text
待确认
```

不要因为“电容通常是贴片”就自动写 0805。

## 合并规则

同一来源内部，只有以下关键字段一致时才允许合并数量：

```text
category
normalized_model
package
unit
```

### 默认：不跨来源合并

不同输入文件可能只是同一笔采购的不同证据，例如：

```text
采购表.xlsx
发票.pdf
```

所以默认把 `source_file` 也纳入合并边界，**不会把不同文件里的同型号数量直接相加**。

只有已经确认不同来源代表独立采购、不会重复计数时，才允许：

```bash
--merge-across-sources
```

无可靠型号时继续保守，不跨来源机械合并。

例如：

```text
同一采购表内：OPA197ID + 同封装 + 同单位
→ 可以汇总数量
```

而：

```text
采购表.xlsx：OPA197ID × 10
发票.pdf：OPA197ID × 10
```

默认输出为两条来源证据，不直接得到 `20`。

## 固定 CLI

脚本：

```text
scripts/extract_soldering_components.py
```

推荐：

```bash
python scripts/extract_soldering_components.py \
  --input /path/to/invoices \
  --output-dir /path/to/output
```

兼容旧参数：

```bash
--invoices-dir
--output-xlsx
```

可选 Markdown：

```bash
--markdown components.md
```

确认来源互不重复时，才使用：

```bash
--merge-across-sources
```

## 固定输出

默认输出目录：

```text
components_output/
├── components.xlsx
├── components.csv
├── review.csv
├── normalized_records.csv
└── validation_report.json
```

如果指定 `--markdown`，额外输出：

```text
components.md
```

### `components.xlsx`

两个 Sheet：

```text
元器件清单
待复核
```

元器件清单包含：

| 字段 | 含义 |
|---|---|
| 类别 | 电阻、电容、连接器等 |
| 型号 / 规格 | 规范化后型号 |
| 封装 / 安装形式 | 有证据则具体，无则待确认 |
| 原始品名 | 发票原始语义 |
| 数量 | 安全聚合后的数量 |
| 单位 | 原采购单位 |
| 来源 | 文件 + 页/行/Sheet |
| 判定依据 | 为什么被 include |

### `review.csv`

只放必须人工确认的行，不与正式 components 混在一起。

### `normalized_records.csv`

保存全部 include / exclude / review 标准化记录，用于审计和调试解析器。

### `validation_report.json`

至少记录：

- 实际读取的文件；
- source warning；
- normalized / include / exclude / review 数量；
- 聚合后 components 数量；
- 是否启用了跨来源合并；
- Excel 回读行数；
- 输出路径。

## 固定工作流程

### Step 1 — Inspect sources

先看输入文件类型和数量，并判断它们之间是什么关系。

如果同时出现采购表和发票：

- 两者都可以提取；
- 默认按两份独立证据保留，不跨来源加总；
- 如果需要算“实际采购总量”，先确认它们是否对应同一订单；
- 只有确认不会重复计数后，才允许跨来源合并。

### Step 2 — Normalize

把每一条候选采购行转成统一记录，并保留 provenance。

解析失败必须进入 warning 或 review，不允许 `except: pass`。

### Step 3 — Decide include/exclude/review

先做排除，再做明确元器件识别，最后把剩余项放 review。

规则可以扩展，但不能把某一个项目的特殊料号硬编码成所有项目的通用真理。

### Step 4 — Infer category/model/package

只对 include 项执行。

任何推断都必须允许降级到 `待确认`。

### Step 5 — Aggregate safely

先在单来源内部合并。

跨来源合并属于额外决策，必须有“这些来源代表不同采购、不会重复计数”的依据。

### Step 6 — Export

生成 CSV / XLSX / JSON；可选 Markdown。

### Step 7 — Read back

重新打开生成的 `components.xlsx`，确认：

- `元器件清单` 行数与聚合结果一致；
- `待复核` 行数与 review 数一致；
- 文件可正常打开。

## Gate

本 Skill 可以在存在 review 或 source warning 时完成，但必须明确报告数量和内容。

只有以下情况属于 Blocking：

- 没有找到任何支持的输入文件；
- 输入文件全部无法读取；
- 输出 XLSX 无法回读；
- 聚合后行数与 Excel 回读不一致；
- 解析器出现异常但被静默吞掉。

## 与焊接清单 Skill 的 Handoff

给 `pcb_soldering_table_skill` 的是：

```text
采购证据：components / normalized records
待确认采购项：review
```

下游仍必须自己根据 BOM / 网表 / 原理图确认：

```text
需要数量
最终实际型号
是否发生替换
是否需要补购
```

总结：这个 Skill 回答“采购资料里有什么”；焊接清单回答“板子最终要焊什么”。

## Tests

运行：

```bash
python -m unittest discover -s tests -v
```

测试至少覆盖三态判定、PDF 行解析、CSV/XLSX 输入、跨来源防重复、安全合并和 XLSX 回读。
