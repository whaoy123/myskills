---
name: connector-wiring-table-generator
description: 从固定格式的 Altium 引脚-网络表、线缆物理映射表和信号属性表，生成并脚本校验可直接用于做线/验线的标准接线表 Excel。优先使用结构化输入和确定性 Python 校验，不从截图人工抄 pin，不依赖 LLM 计算或逐行生成 Excel。
---

# Connector Wiring Table Generator

## 1. 目标

把接线表流程固定成：

```text
固定输入 3 份 CSV
    ↓
Python 结构校验
    ↓
生成唯一 normalized_connections.csv
    ↓
Python 生成 wiring_table.xlsx
    ↓
Python 回读 Excel 与 normalized_connections.csv 逐行比较
    ↓
validation_report.md = PASS
    ↓
人工/代理做语义复核
```

核心原则：

1. **AD 导出的 pin-to-net 数据是板内连接真值源。**
2. **线缆物理映射是线缆端到板端的真值源。**
3. **信号属性表是线型、信号定义和电气属性的真值源。**
4. LLM 只负责从原始资料整理这三份输入、解释异常和做语义复核。
5. pin 映射、重复检查、Excel 生成、数量和回读一致性由脚本完成。
6. 禁止直接根据截图逐行手写最终 Excel。
7. 不因公母正视图/焊接面镜像而修改标准 pin number。

## 2. 固定输入

每次任务统一使用一个 `input/` 目录，文件名和列名固定：

```text
input/
├─ ad_pin_net.csv
├─ cable_map.csv
└─ signal_catalog.csv
```

### 2.1 `ad_pin_net.csv`

来源：优先由 Altium Designer 工程导出/整理得到的引脚—网络表。

固定列：

```csv
BoardConnector,BoardPin,NetName
U1,1,POR_A
U1,2,POR_B
U1,3,POR_C
```

要求：

- `BoardConnector + BoardPin` 在表内唯一；
- 同一个板端 pin 不允许属于两个不同 Net；
- `BoardPin` 使用连接器标准引脚号；
- 不手动按公母视角镜像；
- 只记录与线缆/外部接口有关的连接器 pin 即可，不要求导出整板所有器件。

如果用户能提供 AD 的连接/Netlist 数据，优先直接使用；如果只有原理图/PDF，可先由 AI 提取成该 CSV，但在最终生成前必须让脚本校验。

### 2.2 `cable_map.csv`

这是**线缆物理关系真值源**。一行表示一个实际需要焊接/连接的 pin-to-pin 关系。

固定列：

```csv
SheetName,CableEnd,CablePin,BoardConnector,BoardPin,CableConnectorModel,Gender,MatesTo
AVRplus方向,L1,1,U1,1,UTG62448SN,母头,AVRplus
AVRplus方向,L1,2,U1,2,UTG62448SN,母头,AVRplus
```

字段含义：

- `SheetName`：该连接所属输出 Sheet，例如 `AVRplus方向`、`发电机方向`；
- `CableEnd`：L1/L2/L3...；
- `CablePin`：线缆端标准 pin number；
- `BoardConnector`：板上 U/J 位号；
- `BoardPin`：板端标准 pin number；
- `CableConnectorModel`：线缆端连接器型号；
- `Gender`：公头/母头/端接形式；
- `MatesTo`：线缆另一侧实际对接对象。

不要默认 `CablePin == BoardPin`。即使大多数直通连接相同，也必须在 CSV 中明确写出。

### 2.3 `signal_catalog.csv`

这是显示名称、线型和电气属性真值源。

固定列：

```csv
NetName,SignalDefinition,WireType,ElectricalAttribute,Include
POR_A,POR Phase A,0.5,"300/600Vac，360–2000Hz，10mA，隔离输入",yes
POR_B,POR Phase B,0.5,"300/600Vac，360–2000Hz，10mA，隔离输入",yes
```

要求：

- `NetName` 唯一；
- `Include=yes/no` 决定是否进入最终接线表；
- `WireType` 只能来自用户旧表、明确说明或项目规则，不凭经验猜；
- `ElectricalAttribute` 只来自官方资料/用户资料；没有依据则留空；
- AI 不在生成 Excel 时再次重解释这些字段。

## 3. 固定输出

统一生成：

```text
output/
├─ normalized_connections.csv
├─ wiring_table.xlsx
└─ validation_report.md
```

### 3.1 `normalized_connections.csv`

这是最终接线关系的机器可审计版本，固定列：

```text
SheetName
CableEnd
CablePin
BoardConnector
BoardPin
NetName
WireType
SignalDefinition
ElectricalAttribute
```

最终 Excel 必须由该文件生成。

### 3.2 `wiring_table.xlsx`

每个 `SheetName` 生成一个接线 Sheet，最后固定增加 `连接器型号` Sheet。

接线 Sheet 固定列：

| 序号 | 连接点1代号 | 节点号1 |  | 连接点2代号 | 节点号2 | 线型 | 信号定义 | 电气属性/备注 |
|---:|---|---|---|---|---|---|---|---|

其中：

- 连接点1 = `CableEnd`
- 节点号1 = `CablePin`
- D 列为空白视觉分隔列
- 连接点2 = `BoardConnector`
- 节点号2 = `BoardPin`
- 线型/信号定义/电气属性来自 `signal_catalog.csv`

`连接器型号` Sheet 固定列：

| 线缆端编号 | 连接器型号/规格 | 公母/端接形式 | 对接板端 | 对接对象 | 说明 |
|---|---|---|---|---|---|

样式固定为白底、黑字、浅灰表头、细边框、自动换行、冻结表头。

### 3.3 `validation_report.md`

必须给出：

- `PASS` / `FAIL`
- 连接数
- 接线 Sheet 数量
- Excel 回读是否与 normalized 数据完全一致
- Warning 数量

只有 `PASS` 才能交付。

## 4. 固定脚本

使用：

```bash
python scripts/build_wiring_table.py input output
```

脚本必须完成：

1. 检查三个输入文件存在；
2. 检查固定列；
3. 检查 AD `BoardConnector + BoardPin` 唯一；
4. 检查同一 AD pin 不属于多个 Net；
5. 检查 `CableEnd + CablePin` 不重复；
6. 检查同一个板端 pin 不被重复接出；
7. 检查 `cable_map.csv` 中每个板端 pin 都存在于 AD 表；
8. 从 AD 表取得该 pin 的真实 `NetName`；
9. 检查每个 Net 都存在于 `signal_catalog.csv`；
10. 按 `Include` 过滤；
11. 生成 `normalized_connections.csv`；
12. 生成 Excel；
13. 重新打开 Excel；
14. 将每个接线 Sheet 逐行回读；
15. 与 normalized 数据逐字段比较；
16. 全部一致才写 `PASS`。

脚本禁止：

- 猜 pin；
- 猜 Net；
- 自动镜像 pin；
- 自动补电气参数；
- 靠 Excel 公式计算接线映射。

## 5. 原始资料如何进入固定输入

用户提供的原始资料可以是：

- Altium 工程/Netlist/连接表；
- PDF；
- 设备 connector pin definition；
- 旧接线表；
- 用户说明。

但这些都只是**输入资料来源**，不能直接成为最终生成步骤。

AI 的任务是把原始资料转换成固定的三个 CSV。转换完成后，正式生成只认三个 CSV。

优先级：

1. 用户当前明确说明；
2. AD pin-to-net 数据；
3. 用户确认的 cable physical mapping；
4. 官方设备/连接器资料；
5. 旧接线表；
6. 其他资料仅作辅助。

资料冲突时不得静默选一个值。

## 6. 关键工程规则

- Field + / Field -、High Current Field + / - 不得混并；
- Shield、PMG Shield、Chassis Ground、Signal Ground 不得混淆；
- IN/OUT 不得因名称相似而互换；
- 多针并联必须在 `cable_map.csv` 中逐针展开；
- NC/Reserved 是否包含由 `signal_catalog.csv -> Include` 明确决定；
- 节点号永远写标准 pin number；
- 连接器正视图与焊接面视图只影响操作人员看图，不改变表内 pin number。

## 7. 交付前审核

### 7.1 第一层：确定性脚本审核

`validation_report.md` 必须为 PASS。

这是 pin 映射和 Excel 数据一致性的主要保障，不允许用人工抽查替代。

### 7.2 第二层：主代理语义审核

主代理仍需检查：

- 两端物理方向；
- 公母/连接器型号；
- Sheet 分组；
- 信号定义；
- Field / Shield / Ground / IN-OUT 等易混语义；
- 电气属性来源；
- 线型来源。

### 7.3 第三层：两个独立子代理审核

若运行环境支持子代理，继续执行两个独立完整审核。任何一方发现问题：

1. 修改输入 CSV；
2. 重新运行脚本；
3. 原审核结果作废；
4. 三方重新审核同一最终版本。

若环境不支持子代理，必须明确说明，不得假装执行。

## 8. 最终交付条件

同时满足：

- 三个固定输入已保存；
- Python 脚本运行成功；
- `validation_report.md = PASS`；
- Excel 回读与 normalized 数据一致；
- 主代理语义审核通过；
- 若环境支持子代理，则两个子代理也通过；
- 最近一次审核后未再修改文件。

最终交付以 `wiring_table.xlsx` 为主，同时保留 `normalized_connections.csv` 和 `validation_report.md` 供追溯。
