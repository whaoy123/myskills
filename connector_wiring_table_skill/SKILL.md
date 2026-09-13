---
name: connector-wiring-table-generator
description: 从 Altium 引脚网络数据和线束规划生成并校验标准接线表 Excel；支持普通一对一转接、显式多对一/一对多和双绞线，板端 Pin 必须按 NetName 从 AD 数据求得。
---

# 接线表生成

把连接关系先规范化为“每根实际导线一行”，再由脚本生成可直接施工和贴标签的接线表。

## 不可违反的原则

- 板端 Pin 必须由 AD 的 `BoardConnector + NetName` 自动求得；不允许先人工抄出最终映射。
- 先识别拓扑，再套用规则：普通转接、多对一/一对多、双绞是不同情况。
- 双绞约束只适用于明确标为 `twisted_pair` 的导线，不能强加给普通转接线。
- 多对一/一对多必须用 `FanoutId` 显式声明；未声明的重复端点视为错误。
- 信号名和标签必须进入备注，供现场识别与贴签。
- 输出统一使用最终版双层表头、白底黑字、自动换行和适应行高。

## 执行流程

1. 从 AD、接口定义、旧线表和用户要求整理四个 CSV。字段和拓扑规则见 [references/input_schema.md](references/input_schema.md)。
2. 运行：

   ```bash
   python scripts/build_wiring_table.py input output
   ```

3. 脚本输出 `normalized_connections.csv`、`wiring_table.xlsx`、`validation_report.md`。
4. 只有报告为 PASS，且人工复核方向、公母、型号、标签和未确认端子后才交付。

最终工作表结构、文字和视觉要求见 [references/output_contract.md](references/output_contract.md)。

## 工程边界

- 使用连接器标准 Pin 编号，不因公母视图手工镜像。
- Shield、Chassis Ground、Signal Ground、不同方向和不同极性的信号不得混用。
- 端子或连接器型号没有证据时标“待确认”，不能猜。
- `Include` 决定线束范围；项目里删除某类线束不自动成为通用规则。
