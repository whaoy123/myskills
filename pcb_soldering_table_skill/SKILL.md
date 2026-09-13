---
name: pcb-soldering-table-from-schematic
description: 从网表、原理图、BOM 和采购证据生成 PCB 焊接清单与备料核对 Excel；确定性计算数量/焊点，校验最终型号与设计封装、DNP 证据、预留量、备料倍率和到货状态。
---

# PCB 焊接与备料清单

生成一份既能交给焊接人员、又能回答“物料是否真的够”的工作簿。

## 不可违反的原则

- 网表与 BOM 决定实际装配位号；未采购不能成为删除器件的理由。
- 用户明确替换 > 有明确映射的采购替换 > BOM 原型号。不能凭相似名称猜替换关系。
- 最终型号必须与设计封装兼容；LED、阻容的 0603/0805 等差异必须实际核对。
- 不焊接器件必须留下原因、确认人和日期，不能被规则静默排除。
- 备料目标按每个型号 `ceil(板上数量 × 倍率)` 计算，并扣除明确预留数量。
- “采购数量覆盖”和“实物已经到货覆盖”必须分开表达。
- 数量、焊点、目标数和缺口只由脚本计算。

## 执行流程

1. 交叉核对网表、原理图、BOM、采购表和发票，处理位号差异、替换型号与重复订单。
2. 整理 `bom.csv`、`component_rules.csv`、`procurement.csv`。字段见 [references/input_schema.md](references/input_schema.md)。
3. 运行：

   ```bash
   python scripts/build_soldering_table.py input output
   ```

4. 脚本生成 `soldering_table.xlsx` 和 `validation_report.md`。
5. 对型号、封装、DNP、来源和异常状态做最后语义复核；报告 PASS 后交付。

工作簿固定结构和样式见 [references/output_contract.md](references/output_contract.md)。

## 规格和合并

- “型号/规格”第一段只写一次标称值，最后固定写 `具体型号：...`。
- 相同 `FinalModel + 最终规格 + DisplayPackage + MountType + 焊点规则` 合并，位号自然排序。
- SMD/THT 焊点均为 `数量 × (正常焊脚 + 固定焊脚)`。
- 端子、机械件、测试点是否计入必须由有证据的规则决定。
