# 数据手册指标读取指南

## 1. 先确定规格层级

依次记录：

- Typical：典型样品、特定条件下的代表值；
- Max/Min：数据手册保证边界，适合最坏预算；
- 3σ/六西格玛估计：统计值，不等于保证值；
- 全温区保证还是仅 25°C；
- 是否需特定供电、输入共模、频率和输出负载。

没有 Max 时，可做典型预算，但结果必须标为“估计”。

## 2. 常见指标与误差分类

| 数据手册参数 | 通常分类 | 常见单位 | 处理方式 |
|---|---|---|---|
| Gain error | 比例误差 | % | 当前读数 × 百分比 |
| Gain drift | 比例温漂 | ppm/°C | 读数 × ppm × 温差 |
| Offset voltage | 固定偏移 | µV/mV | 从所在节点折算 |
| Offset drift | 固定温漂 | µV/°C | 乘温差后折算 |
| INL/nonlinearity | 非线性 | LSB、%FS、% | 按定义折算，通常校准后仍保留 |
| DNL | 码宽误差 | LSB | 主要评估失码和小信号均匀性 |
| TUE | 组合静态误差 | LSB、%FS | 查清包含项，避免重复 |
| Input bias/leakage | 负载偏移 | nA/µA | 乘源阻抗 |
| CMRR | 共模耦合 | dB | 按共模刺激换算 |
| PSRR | 电源耦合 | dB | 按纹波换算 |
| Noise | 随机误差 | µV RMS、nV/√Hz | 统一带宽后 RSS |
| SNR/SINAD/ENOB | 动态性能 | dB/bit | 不与同一噪声重复计算 |
| THD | 失真 | dB/% | 判断对 RMS/基波测量的影响 |
| Bandwidth/settling | 动态误差 | Hz/s | 计算目标频率增益和建立残差 |
| Aperture jitter | 随机时间误差 | ps RMS | 按信号频率换算 |
| Reference accuracy | 比例误差 | %/ppm | 作为 ADC 比例误差 |
| Reference noise | 随机误差 | µVpp/µVrms | 按带宽和传递关系换算 |

## 3. 电阻数据手册

至少检查：

- tolerance；
- TCR；
- tracking TCR 或 ratio stability；
- VCR；
- maximum working voltage；
- power rating 与降额曲线；
- load-life / long-term stability；
- humidity；
- pulse/overload rating；
- 封装寄生参数。

“±0.1%”通常只表示初始容差，不代表全温区仍只有 ±0.1%。

## 4. ADC 数据手册

需要区分：

- offset/gain/INL/DNL 是典型还是最大；
- internal reference 是否启用；
- 外部 Vref 的允许范围和输入电流；
- acquisition time、source impedance 和推荐驱动电路；
- 单端、伪差分、全差分输入；
- input common-mode；
- `LSB = span/2^N` 的跨度定义；
- 码型是 offset binary 还是 two's complement；
- SNR/ENOB 的输入频率和采样率；
- 通道扫描时的建立时间和串扰。

## 5. 隔离放大器数据手册

除 gain/offset 外，还要检查：

- 输入范围是差分还是单端；
- 输入共模范围；
- 输入阻抗和偏置电流；
- 输出差分增益和输出共模；
- 输出是否可直接驱动 ADC；
- 带宽、群延迟和 THD；
- CMTI；
- 集成隔离电源的纹波和故障状态；
- 输出滤波条件，因为 SNR 和噪声会随带宽变化。

## 6. 典型重复计数检查

在正式合并前回答：

1. TUE 是否已经包含 offset、gain 和 INL？
2. ENOB/SINAD 是否已经包含 ADC 噪声和失真？
3. 外部基准误差是否已包含在 ADC 的 gain error 测试中？
4. 数据手册全温区最大误差是否已经包含 drift？
5. 标定是否已消除初始 offset/gain？
6. 噪声指标是否使用了相同带宽？

任何一项不确定，都应在结果中列为“可能重复计数/待确认”，不要静默相加。
