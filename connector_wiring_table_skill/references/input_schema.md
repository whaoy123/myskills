# 输入数据契约

正式生成前必须整理出四个 UTF-8 CSV。不要从截图直接抄最终 Pin 映射。

## `ad_pin_net.csv`

`BoardConnector,BoardPin,NetName`

- 是板端连接真值源；`BoardConnector + BoardPin` 唯一。
- `BoardEndpoint=1/2` 的节点号必须由本表按 `BoardConnector + NetName` 求出。
- 同一连接器同一网络有多个 Pin 时，`BoardPinHint` 只用于消歧，并必须再次通过 AD 数据验证。

## `connection_plan.csv`

固定列：

```text
SheetName,Order,Topology,Point1Code,Point1Node,Point2Code,Point2Node,
BoardEndpoint,BoardConnector,BoardPinHint,NetName,PairGroup,CoreRole,
FanoutId,WireType,LabelText,Include,Notes
```

- 一行表示一根实际导线。
- `Order` 是工作表内的正整数显示顺序。
- `Topology=direct`：普通一对一转接线。`PairGroup` 必须留空，不应用双绞约束。
- 多对一或一对多仍使用 `direct`；重复的物理端点必须由所有相关行填写同一个 `FanoutId` 显式声明。
- `Topology=twisted_pair`：仅用于确实要求双绞的导线。每个 `PairGroup` 必须恰好有一根 `signal` 和一根 `return`，两行必须相邻。
- `FanoutId` 与双绞是正交属性：同一个地 Pin 分出两根回线时，各回线可属于不同 `PairGroup`，同时共享一个 `FanoutId`。
- `BoardEndpoint=1/2` 表示哪一侧与板端对应；该侧节点号由 AD 自动填充。普通连接器转接线不涉及板端时填 `0`，两端节点均显式填写。
- `LabelText` 留空时默认为 `NetName`；双绞回线留空时默认为 `<配对信号>-GND`。
- `Include=no` 不输出。是否输出电源线束由输入决定，不能把“去掉电源”写成通用规则。

## `signal_catalog.csv`

`NetName,SignalDefinition,WireType,ElectricalAttribute`

信号定义必须能支持现场贴标签和识别用途；无依据的电气属性可以留空，不能猜。

## `interface_catalog.csv`

```text
SheetName,BoardConnector,BoardConnectorModel,BoardGender,
MatingConnectorModel,MatingGender,TerminalModel,MatesTo,
Point2NodeHeader,Title,Description
```

- 每个输出接线 Sheet 一行。
- 板端与对插连接器公母必须相反。
- 未确定自由端端子型号时 `TerminalModel` 留空，输出显示“待下游接口确认”。
- `Point2NodeHeader` 必须按线束填写 `节点号` 或 `端子号`；自由端端子线束用后者，普通连接器转接线用前者。
- `Title` 可覆盖自动标题。
