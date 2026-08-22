---
name: connector-wiring-table-generator
description: 从固定格式的 Altium 引脚-网络表、外部连接器 pinout 和信号属性表自动求出板端 Pin，生成并脚本校验标准接线表 Excel。禁止人工抄写板端 Pin；板端 Pin 必须由 AD 网络数据按 NetName 匹配得到。
---

# Connector Wiring Table Generator

## 1. 固定流程

```text
AD pin/net + 外部连接器 pinout + 信号属性
             ↓
       Python 自动匹配 NetName
             ↓
       自动求 BoardPin
             ↓
 normalized_connections.csv
             ↓
       wiring_table.xlsx
             ↓
      Excel 回读逐字段比较
             ↓
 validation_report.md = PASS
```

最重要的规则：

> **外部 pin 来自设备/线缆 pinout；板端 pin 来自 Altium；两者通过 NetName 自动匹配。**

用户不需要先手工填写最终的 `CablePin -> BoardPin` 映射，否则等于先做了一遍接线表。

## 2. 固定输入：只认 3 个 CSV

```text
input/
├─ ad_pin_net.csv
├─ external_pinout.csv
└─ signal_catalog.csv
```

### 2.1 `ad_pin_net.csv`

这是**板端连接真值源**，优先从 Altium Designer 导出/整理。

```csv
BoardConnector,BoardPin,NetName
U1,7,POR_A
U1,8,POR_B
U1,9,POR_C
```

固定列：

- `BoardConnector`
- `BoardPin`
- `NetName`

要求：

- `BoardConnector + BoardPin` 唯一；
- 不允许同一个 pin 同时属于两个不同 Net；
- pin 使用连接器标准编号，不按公母视图镜像；
- 只需要外部接口相关连接器，不要求整板所有器件。

如果用户直接给 AD 原始 Netlist/连接表，AI 的第一步是把它规范化为该 CSV。**优先要 AD 的线表/Netlist，而不是截图。**

### 2.2 `external_pinout.csv`

这是**外部设备/线缆端 pin 真值源**，通常由设备官方 connector pin definition、旧接线表或用户明确资料整理。

```csv
SheetName,CableEnd,CablePin,NetName,TargetBoardConnector,BoardPinHint,CableConnectorModel,Gender,MatesTo
AVRplus方向,L1,1,POR_A,U1,,UTG62448SN,母头,AVRplus
AVRplus方向,L1,2,POR_B,U1,,UTG62448SN,母头,AVRplus
```

含义：

- `CableEnd` / `CablePin`：外部线缆端及其标准 pin；
- `NetName`：该外部 pin 对应的信号网络；
- `TargetBoardConnector`：这根线接板上的哪个连接器，例如 U1；
- `BoardPinHint`：通常留空；
- `CableConnectorModel` / `Gender` / `MatesTo`：连接器说明；
- `SheetName`：输出放在哪个接线 Sheet。

**BoardPin 不由用户填写。**

脚本会查询：

```text
(TargetBoardConnector, NetName) -> BoardPin
```

若 AD 中唯一匹配，则自动得到 BoardPin。

如果同一连接器上同一个 Net 出现在多个 pin（并联 pin），脚本会拒绝猜测；此时才填写 `BoardPinHint` 指定其中一个，并再次由 AD 数据验证该 Hint 是否正确。

### 2.3 `signal_catalog.csv`

```csv
NetName,SignalDefinition,WireType,ElectricalAttribute,Include
POR_A,POR Phase A,0.5,"300/600Vac，360–2000Hz，10mA，隔离输入",yes
```

固定列：

- `NetName`
- `SignalDefinition`
- `WireType`
- `ElectricalAttribute`
- `Include`

规则：

- NetName 唯一；
- 线型来自用户既有规则/旧表；
- 电气属性来自官方资料；
- 没依据就留空，不猜；
- `Include=no` 不进入最终表。

## 3. 固定输出

```text
output/
├─ normalized_connections.csv
├─ wiring_table.xlsx
└─ validation_report.md
```

### `normalized_connections.csv`

固定列：

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

其中 `BoardPin` 是脚本从 AD 数据求出的，不是人工抄入。

### `wiring_table.xlsx`

每个 `SheetName` 一个接线 Sheet，最后固定 `连接器型号` Sheet。

接线 Sheet：

| 序号 | 连接点1代号 | 节点号1 |  | 连接点2代号 | 节点号2 | 线型 | 信号定义 | 电气属性/备注 |
|---:|---|---|---|---|---|---|---|---|

映射：

- 连接点1 = CableEnd
- 节点号1 = CablePin
- 连接点2 = TargetBoardConnector
- 节点号2 = **脚本从 AD 求出的 BoardPin**

## 4. 固定脚本

```bash
python scripts/build_wiring_table.py input output
```

必须执行：

1. 校验三个输入文件和固定列；
2. 建立 AD `(BoardConnector, BoardPin) -> NetName`；
3. 建立 AD `(BoardConnector, NetName) -> BoardPin候选`；
4. 校验外部 `CableEnd + CablePin` 唯一；
5. 用 `TargetBoardConnector + NetName` 自动求 BoardPin；
6. 0 个候选：FAIL；
7. 1 个候选：自动采用；
8. 多个候选：FAIL，必须使用 `BoardPinHint`；
9. `BoardPinHint` 必须再次与 AD 数据一致；
10. 检查板端 pin 不被意外重复接出；
11. 合并 signal_catalog；
12. 生成 normalized CSV；
13. 由 normalized CSV 生成 Excel；
14. 重新打开 Excel；
15. 对每个连接逐字段回读；
16. 与 normalized 数据完全一致才 PASS。

## 5. 原始资料与固定输入的关系

用户每次最好给：

1. **AD 导出的连接/Netlist 数据**；
2. **外部设备 connector pin definition / 旧 pinout**；
3. 若项目已有，给已有的线型/电气属性规则。

AI 可以读取 PDF、旧 Excel、截图等，但正式生成前必须把信息收敛为三个固定 CSV。

所以以后对用户而言，最推荐的原始资料就是：

```text
AD 线表/Netlist
+ 设备端 Pin 定义
+ 项目接线规则（若已有）
```

## 6. 工程规则

- Field + / -、High Current Field + / - 不混；
- Shield / PMG Shield / Chassis Ground / Signal Ground 不混；
- IN / OUT 不互换；
- NC / Reserved 由 Include 决定；
- 多针并联若导致同一 `(Connector, Net)` 多个候选，必须显式 Hint；
- 表内始终使用标准 pin number，不做人为镜像。

## 7. 审核与交付

第一层硬门槛是脚本 PASS，负责 pin 映射、重复、生成和 Excel 回读一致性。

之后主代理做语义审核：方向、公母、连接器型号、信号定义、线型、电气属性和易混信号。

若环境支持子代理，继续两个独立完整审核；任何修改都必须重新运行脚本并让此前人工审核结果作废。

只有 `validation_report.md = PASS` 且语义审核通过才交付。
