# 误差折算与合并规则

## 1. 统一报告端

设最终被测输入为 `X`，某节点信号为：

```text
V_node = G_node × X
```

节点处固定电压误差 `e_node` 折算到输入端：

```text
e_input = e_node / |G_node|
```

例如分压比 `K=0.0035307`，AMC 输入失调 `0.3 mV`：

```text
e_input = 0.0003 / 0.0035307 = 0.08497 V
```

这是原始物理输入等效偏移。必须继续根据结果算法转换：瞬时/峰值可直接使用；原始完整周期 RMS 用平方和；去均值 RMS 中固定偏移贡献近似为零。

## 2. 百分比读数误差

比例误差：

```text
e_input = X × p / 100
```

也可以先在局部节点计算再除以 `G_node`：

```text
(G_node × X × p) / G_node = X × p
```

因此 AMC 增益误差 ±0.2% 在 115 V 输入下等效为：

```text
115 × 0.2% = 0.23 V
```

## 3. 满量程误差

若指标为 `%FS`：

```text
e_input = X_FS × p_FS / 100
```

它与当前读数无关。不能用当前 115 V 乘 `%FS`，除非 115 V 就是满量程。

## 4. 温漂

比例温漂：

```text
e_input = X × TC_gain(ppm/°C) × |ΔT| × 1e-6
```

固定失调温漂位于节点处：

```text
e_input = TC_offset(V/°C) × |ΔT| / |G_node|
```

数据手册若已经给出全温区最大误差，不要再重复把温漂加一次。

## 5. 电阻分压比

```text
K = R_L / (R_H + R_L)
```

若高低臂容差分别为 `t_H`、`t_L`：

```text
K_max = R_L(1+t_L) / [R_H(1-t_H) + R_L(1+t_L)]
K_min = R_L(1-t_L) / [R_H(1+t_H) + R_L(1-t_L)]
```

分压比最坏相对误差：

```text
max(|K_max/K-1|, |K_min/K-1|)
```

当 `R_H >> R_L` 时可近似：

```text
ΔK/K ≈ ΔR_L/R_L - ΔR_H/R_H
```

所以两边各 ±0.1% 时，最坏比例误差接近 ±0.2%，不是 ±0.1%。

### TCR 匹配

温差 `ΔT` 下，最坏比例温漂近似：

```text
(|TCR_H| + |TCR_L|) × |ΔT|
```

若数据手册提供 tracking TCR，应优先使用 tracking TCR，不再用两颗绝对 TCR 最坏相加。

### VCR、自热和长期漂移

将它们转换成电阻相对变化，再按分压比公式重新求 `K`。上下臂相同方向同幅变化时，比例可能几乎不变；不同方向或不同温升才会改变比例。

## 6. 偏置电流和漏电

局部误差：

```text
e_node = I_leak × R_source_eq
```

再折算：

```text
e_input = I_leak × R_source_eq / |G_node|
```

必须使用器件看到的等效源阻抗，而不是简单使用整个高压臂阻值。

## 7. CMRR 和 PSRR

若 CMRR 以 dB 给出，共模刺激为 `V_CM`：

```text
e_local = V_CM / 10^(CMRR/20)
```

PSRR 同理：

```text
e_local = V_ripple / 10^(PSRR/20)
```

注意很多数据手册给的是 input-referred CMRR/PSRR，此时不要再次除以器件增益。

## 8. ADC 量化、LSB 和 INL

ADC 输入跨度 `V_span`、位数 `N`：

```text
1 LSB = V_span / 2^N
```

理想量化最大误差：

```text
±0.5 LSB
```

理想均匀量化噪声 RMS：

```text
1 LSB / √12
```

若 INL 为 ±2 LSB，输入端等效：

```text
e_input = 2 × LSB / |G_ADC_input|
```

不要把 ADC 的 TUE 与已包含的 offset/gain/INL 重复相加。

## 9. ADC 基准源

理想换算通常与 `Vref` 成比例，因此基准初始误差和温漂通常是比例误差：

```text
e_input = X × e_Vref(relative)
```

基准噪声应按 ADC 的参考噪声传递和带宽换算，不能一律按满幅比例处理。

## 10. 一阶 RC 幅值误差

低通幅值：

```text
|H(f)| = 1 / √[1 + (f/fc)^2]
```

如果理想目标是单位增益：

```text
比例误差 = |1 - H(f)|
```

RC 衰减是确定性的动态比例误差。若软件在同一频率准确补偿，可去除标称衰减，但元件容差、频率变化和模型误差仍保留。

## 11. 采样抖动

对正弦信号，抖动导致的近似噪声比：

```text
σ_relative ≈ 2π f_in t_jitter,rms
```

输入端 RMS 噪声近似：

```text
σ_input ≈ X_rms × 2π f_in t_jitter,rms
```

400 Hz 下通常很小，但多通道相位测量还需检查通道时间偏差。

## 12. RMS 与固定偏移

若采样信号：

```text
y(t) = x(t) + V_os
```

完整周期且 `x(t)` 零均值：

```text
RMS(y) = √[RMS(x)^2 + V_os^2]
```

固定偏移不会按线性方式直接变成同值 RMS 误差。若先减去周期平均值，固定偏移基本被消除。峰值检测、半波整流或非整周期窗口则可能受到更明显影响。

## 13. 合并规则

### 最坏情况

对有界、可能同向的系统误差：

```text
E_WC = Σ |e_i|
```

用于保证设计。

### RSS

对合理独立、零均值或方向随机的误差：

```text
E_RSS = √Σ(e_i²)
```

RSS 是统计估计，不是保证边界。相关项先在线性域合并，再与其他独立组 RSS。

### 随机噪声

随机 RMS 噪声：

```text
σ_total = √Σ(σ_i²)
```

保守总界限可写：

```text
E_conservative = E_systematic_WC + k × σ_total
```

默认 `k=3`，必须声明。

## 14. 最终表达

推荐保留：

```text
±(a% × 读数 + b% × 满量程 + c V) + 随机噪声 σ
```

在给定工作点 `X0` 下再计算：

```text
E(X0) = aX0 + bXFS + c
```

不要只给一个工作点数字而丢失误差模型，否则无法判断低电压和高电压时的表现。
