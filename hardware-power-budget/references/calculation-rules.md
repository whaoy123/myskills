# Calculation Rules

## 1. 基础公式

对每个负载行：

```text
Ityp_total = quantity × Ityp_each
Ibudget_total = quantity × Imax_each
```

若没有 datasheet Max，但有明确工程设计值：

```text
Ibudget_total = quantity × Idesign_each
```

该行必须标记为 estimate，不能写成 datasheet maximum。

对每条 rail：

```text
Ityp_rail = Σ Ityp_total
Ibudget_rail = Σ Ibudget_total
Ptyp_rail = |Vrail| × Ityp_rail
Pbudget_rail = |Vrail| × Ibudget_rail
```

设计余量：

```text
Idesign_min = Ibudget_rail × (1 + margin%)
Pdesign_min = |Vrail| × Idesign_min
```

默认 margin = 30%。

## 2. 为什么用“预算/最坏”而不是只有一个电流

三个数必须分开：

- Typical：热估算、正常工作估计；
- Budget/Worst：基于 datasheet Max 或明确工程保守值；
- Design minimum：Budget/Worst 加一次设计余量，用于选电源。

最终商业模块的额定值通常再向上取标准档，但这叫 `selected rating`，不是再次加百分比。

## 3. 负电源轨

`-15 V` 的功耗仍为正：

```text
P = |-15 V| × I
```

双电源器件若 datasheet 给的是每 rail supply current，则正负轨各计一次。若 datasheet 明确给的是整个器件总电源功耗或 total supply current，先确认定义，不能机械复制到两轨。

## 4. DCDC 回推

对 DC/DC：

```text
Pin = Pout / η
Iin = Pin / |Vin| + Iq_input
```

最坏输入电流优先使用 `η_min`。只有 `η_typ` 时，只能标记为估计。

多输出：

```text
Pout = Σ |Vout_i| × Iout_i
```

既要检查单路电流，也要检查总输出功率。

## 5. LDO / 线性稳压器

近似：

```text
Iin ≈ Iout + Iq
Pin = |Vin| × Iin
Pout = |Vout| × Iout
Pdiss = Pin - Pout
```

单输出、同极性时常见近似：

```text
Pdiss ≈ (|Vin| - |Vout|) × Iout + |Vin| × Iq
```

必须检查热耗散和结温，不能只检查“电流够不够”。

## 6. 级联电源与避免重复计数

若：

```text
VIN → DCDC → +5V → LDO → +3V3
```

整机 VIN 功耗不能简单把 `VIN + 5V + 3V3` 三个 rail 功耗相加，否则会把下游功耗重复统计。

正确方法是：

1. 下游负载先在自己的 rail 汇总；
2. 通过转换器效率回推为上游输入电流；
3. 整机输入功耗只看最上游 root rail。

脚本采用该逻辑。

## 7. 峰值、浪涌和工作模式

连续供电预算与瞬态能力分开：

- Continuous / worst steady-state：用于额定功率；
- Peak / inrush：用于瞬态、储能、电流限制和启动可靠性；
- Fault：如果系统要求故障不断电，单独做 fault scenario。

多个互斥工作模式不要强行塞进一个“全都同时最大”的数字。分别建立 `idle / normal / worst-active / startup / fault` 输入文件，再选择真正需要覆盖的设计场景。

## 8. 总功耗的两个口径

### 实际最坏负载

```text
P_worst_actual = root rail 的 Pbudget
```

用于估算真实输入需求和热负载。

### 最终额定容量

如果每条输出 rail 已选标准额定值：

```text
P_selected_capacity = Σ |Vrail| × Iselected
```

这是“配置的电源容量”，通常大于实际最坏负载。不要把它写成“板子实际耗电”。
