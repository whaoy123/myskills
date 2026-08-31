# 示例：隔离调理板审核

以下示例用于说明本技能如何区分“确定错误 / 需确认 / 可优化”。

## 1. 隔离域误连 — P0

背景：Field 与 POR 是两个独立高压测量域。

发现：Field 的隔离 12V 已以 `Field -` 为返回端，但指示 LED 仍回到 `POR Neutral`。

判断：LED 电阻虽然很大，仍形成两个隔离域之间的实际电气连接。

修改：

`+12_PRI_Field → R → LED → Field -`

而不是：

`+12_PRI_Field → R → LED → POR Neutral`

## 2. PDF 看似连接，但 NET 未连接 — P0

PDF 中连接器 pin 3、5、13 显示了 Field 信号标签，但 Netlist 中 pin 3/5/13 未进入任何 Net。

判断：以 Netlist 为准，标签很可能未吸附到引脚。

修改：重新吸附 Net Label，Compile 后重新导出 NET，再检查：

`U46-3 → Field_I_Out_High1`

`U46-5 → Field Out`

`U46-13 → Field_I_Out_High2`

## 3. 参数相同但用了两个型号 — P2

发现：两种 1µF / ±20% / 50V 贴片铝电解，尺寸均为 D4×L5.4mm，只是厂家/纹波电流略有不同。

处理：先比较 ESR、纹波、寿命、温度；若均满足当前 DC/DC Cin2 使用条件，可统一为一个型号，减少采购种类。

输出：

`型号 A + 型号 B → 统一型号 B → C34/C42/C240`

## 4. 型号封装与 Footprint 不一致 — P0/P1

发现：某 470pF C0G 的 MPN 是 0603，但 PCB Footprint 为 0805。

判断：制造风险，必须确认是否为故意兼容焊盘；若不是，统一型号或 footprint。

优先建议：保持 PCB footprint，选择相同参数的 0805 MPN。

## 5. Footprint 名称误导但尺寸兼容 — P2

发现：4.7µH 电感实际 MPN 为 2.5×2.0mm，Footprint 名称中写着另一颗 15µH 电感的型号，但实际焊盘尺寸也是 2.5×2.0mm。

判断：电气/制造上可用，但命名容易导致后续误采购。

建议：重命名 footprint 或在 BOM 中明确实际 MPN。

## 6. 参数计算示例

Field 输入 300VDC：

- 高边：5×200kΩ
- 低边：32.4kΩ

`Vchip = 300 × 32.4k / (1000k + 32.4k) ≈ 9.41V`

若隔离放大器输入范围为 ±12V，则量程成立；再继续检查每颗 200kΩ 的工作电压与功耗。

## 7. 最终判断示例

**当前版本：修正后可投板。**

P0：隔离域 LED 回错地；连接器 3 个引脚在 NET 中未入网。

P1：BOM/NET/PDF 需统一版本重新导出。

P2：统一重复 MPN、清理误导性 Footprint 名称。