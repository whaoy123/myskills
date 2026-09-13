# 中间输入契约

原始网表、原理图、BOM、采购记录和发票先交叉核对，再整理成三个 CSV。

## `bom.csv`

`Designator,Nominal,ResolvedDescription,Footprint,DesignModel,FinalModel`

- 一行一个实际器件位号；位号唯一。
- `Footprint` 必须来自设计数据，不能按采购型号反推后覆盖。
- `FinalModel` 是实际拟焊型号；发生替换时，规格描述必须同步改成新型号参数。

## `component_rules.csv`

```text
MatchField,MatchValue,DisplayPackage,MountType,PinsPerPart,
FixedPinsPerPart,Include,CompatibleFootprints,DNPReason,
ConfirmedBy,ConfirmedDate,Notes
```

- `Model` 规则优先于 `Footprint` 规则。
- `Model` 规则必须填写用分号分隔的 `CompatibleFootprints`；实际设计封装不在其中时失败。
- `Footprint` 规则天然与该封装匹配，可不重复填写兼容封装。
- 只要 `FinalModel != DesignModel`，必须建立 `FinalModel` 精确规则；不能让替换料绕过封装兼容检查后继续套用通用 Footprint 规则。
- `Include=no` 或 `MountType=NONE` 必须同时填写不焊接原因、确认人和确认日期，不能静默排除。
- 引脚数和固定脚数均参与焊点计算。

## `procurement.csv`

```text
Model,StockQty,PurchasedQty,ReceivedQty,ReservedQty,
TargetMultiplier,Source,Notes
```

- `StockQty`：本次采购前可用于调配的库存。
- `PurchasedQty`：本次去重后的已下单数量。
- `ReceivedQty`：已明确到货的本次数量；未知时留空，不能填成已采购数量。
- `ReservedQty`：必须留给上一套板、其他项目或样机的数量。
- `TargetMultiplier`：备料倍率，例如 `1.2`；按型号向上取整。
- 同一订单的采购表和发票不得重复累加。

计算：

```text
目标数量 = ceil(板上数量 × TargetMultiplier)
采购口径可用 = StockQty + PurchasedQty - ReservedQty
实物口径可用 = StockQty + (ReceivedQty 若明确，否则 0) - ReservedQty
```

实物数量未覆盖但采购口径覆盖时，状态必须写“采购数量覆盖，待到货清点”，不能写成库存足够。
