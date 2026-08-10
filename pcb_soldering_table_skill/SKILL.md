---
name: pcb_soldering_table_from_schematic
description: 从固定格式 BOM 与器件焊接规则表生成 PCB 焊接清单 Excel。器件数量、贴片/直插焊点、固定脚和总焊点全部由 Python 确定性计算并回读校验；LLM 只负责整理输入规则和处理无法从 BOM 自动确定的器件属性。
---

# PCB 焊接清单生成 Skill

## 1. 固定流程

```text
AD/BOM 原始资料
    ↓
固定输入 2 份 CSV
    ↓
Python 校验 + 计算
    ↓
soldering_table.xlsx
    ↓
Python 回读校验
    ↓
validation_report.md = PASS
    ↓
语义复核
```

原则：

- 不让 LLM 计算数量和焊点；
- Excel 里的公式可以作为展示，但**不是唯一计算依据**；
- Python 必须独立算出数量、贴片焊点、直插焊点和总焊点；
- 生成后重新打开 Excel，比对脚本计算结果；
- 不认识的器件规则必须阻断，不静默猜测。

## 2. 固定输入

```text
input/
├─ bom.csv
└─ component_rules.csv
```

### 2.1 `bom.csv`

优先来自 Altium BOM 导出后整理成固定列：

```csv
Designator,Model,Footprint
R1,100R,R0805
R2,100R,R0805
J1,DSUB-M-44H,DB44
```

要求：

- 一行一个实际器件位号；
- `Designator` 全表唯一；
- 测试点、机械孔等是否保留不在 BOM 阶段猜，由规则表决定；
- 如果 AD 原始 BOM 是“多个位号合并一行”，先展开为一行一个位号。

### 2.2 `component_rules.csv`

固定列：

```csv
MatchField,MatchValue,DisplayPackage,MountType,PinsPerPart,FixedPinsPerPart,Include,Notes
Footprint,R0805,0805,SMD,2,0,yes,
Model,DSUB-M-44H,DB44公头,THT,44,2,yes,含固定脚
```

含义：

- `MatchField`：只能是 `Model` 或 `Footprint`；
- `MatchValue`：精确匹配值；
- `DisplayPackage`：最终 Excel 的封装/类型名称；
- `MountType`：`SMD` / `THT` / `NONE`；
- `PinsPerPart`：每只器件正常焊接 pin 数；
- `FixedPinsPerPart`：每只器件额外固定焊脚数；
- `Include`：是否进入焊接清单；
- `Notes`：装配备注。

匹配优先级：Model 精确规则 > Footprint 精确规则。没有任何规则匹配时必须 FAIL。

## 3. 固定计算

每组相同器件：

```text
Quantity = Designator 数量
PerPartJoints = PinsPerPart + FixedPinsPerPart
SMD: SMDPoints = Quantity × PerPartJoints
THT: THTPoints = Quantity × PerPartJoints
TotalJoints = ΣSMDPoints + ΣTHTPoints
```

这些数值由 Python 计算。Excel 可写合计公式，但必须同时通过 Python 回读验证，不能把“Excel 有公式”视为已校验。

## 4. 固定输出

```text
output/
├─ soldering_table.xlsx
└─ validation_report.md
```

`焊接清单` Sheet 固定 7 列：

| 位号 | 型号/规格 | 封装 | 数量 | 贴片焊点 | 直插焊点 | 备注 |
|---|---|---|---:|---:|---:|---|

最后固定 `合计` 行。样式固定为白底、黑字、浅灰表头、细边框、自动换行、冻结表头。

## 5. 固定脚本

运行：

```bash
python scripts/build_soldering_table.py input output
```

脚本必须检查输入文件和固定列、BOM 位号唯一、每个器件有规则、类型合法、pin 数非负，并由 Python 计算数量/焊点。Excel 生成后必须重新打开，逐行和合计再次比对，全部一致才输出 PASS。

## 6. LLM 负责什么

LLM 只负责从 BOM/原理图/PCB/装配图确定 `component_rules.csv`，判断固定焊脚、SMD/THT/NONE、易读封装名称和装配备注，并处理资料冲突。

LLM 不负责乘法、数量汇总、总焊点、Excel 逐行手工填写或靠肉眼确认合计。

## 7. 交付审核

脚本 PASS 是第一层硬门槛。之后主代理检查型号/封装语义、SMD/THT、固定脚、测试点/机械件、DNP、备注和可读性。

若环境支持子代理，继续执行两个独立完整审核；修改后重新运行脚本并让全部审核结果失效后重审。

最终只有在 `validation_report.md = PASS` 且语义审核通过后才能交付。
