# POR A-N voltage acquisition 误差预算

- 工作点：115.0 Vrms input-equivalent
- 校准模式：two_point
- 结果算法：rms_mean_removed
- 温度：25.0°C → 75.0°C

## 误差明细

| 来源 | 类型 | 原始输入等效 | 对结果的误差 | 合并 | 校准后保留 | 公式 |
|---|---|---:|---:|---|---|---|
| 分压比初始误差 | percent_reading | 0.23 Vrms input-equivalent | 0.23 Vrms input-equivalent | systematic | 否 | 115 × 0.2% |
| 分压器比例温漂 | ppm_per_c_reading | 0.14375 Vrms input-equivalent | 0.14375 Vrms input-equivalent | systematic | 是 | 115 × 25 ppm/°C × 50°C |
| AMC3330 初始增益误差 | percent_reading | 0.23 Vrms input-equivalent | 0.23 Vrms input-equivalent | systematic | 否 | 115 × 0.2% |
| AMC3330 增益温漂 | ppm_per_c_reading | 0.25875 Vrms input-equivalent | 0.25875 Vrms input-equivalent | systematic | 是 | 115 × 45 ppm/°C × 50°C |
| AMC3330 输入失调 | local_offset_v | 0.0849689863 Vrms input-equivalent | 0 Vrms input-equivalent | systematic | 否 | 0.0003 V at divider_output ÷ 0.0035307; fixed offset removed before RMS |
| AMC3330 失调温漂 | local_offset_uv_per_c | 0.0566459909 Vrms input-equivalent | 0 Vrms input-equivalent | systematic | 是 | 4 µV/°C × 50°C ÷ 0.0035307; fixed offset removed before RMS |
| ADC/基准初始增益误差 | percent_reading | 0.115 Vrms input-equivalent | 0.115 Vrms input-equivalent | systematic | 否 | 115 × 0.1% |
| ADC/基准增益温漂 | ppm_per_c_reading | 0.0575 Vrms input-equivalent | 0.0575 Vrms input-equivalent | systematic | 是 | 115 × 10 ppm/°C × 50°C |
| ADC INL | lsb | 0.0177018721 Vrms input-equivalent | 0.0177018721 Vrms input-equivalent | systematic | 是 | 2 LSB × 6.25e-05 V/LSB ÷ 0.0070614 |
| ADC 量化噪声 | lsb | 0.00255504516 Vrms input-equivalent | 0.00255504516 Vrms input-equivalent | random | 是 | 0.288675 LSB × 6.25e-05 V/LSB ÷ 0.0070614 |
| 校准源不确定度 | percent_reading | 0.0575 Vrms input-equivalent | 0.0575 Vrms input-equivalent | systematic | 是 | 115 × 0.05% |
| 一阶模拟低通标称衰减 | first_order_lowpass_attenuation | 0.198447085 Vrms input-equivalent | 0.198447085 Vrms input-equivalent | systematic | 否 | 115 × \|1 - 1/sqrt(1+(400/6800)²)\| |

## 合并结果

| 场景 | 系统最坏值 | 系统 RSS | 随机 RMS | 系统最坏+kσ | 相对保守误差 |
|---|---:|---:|---:|---:|---:|
| 未校准 | 1.30864896 Vrms input-equivalent | 0.502939089 Vrms input-equivalent | 0.00255504516 Vrms input-equivalent | 1.31631409 Vrms input-equivalent | 1.14462% |
| 校准后 | 0.535201872 Vrms input-equivalent | 0.307475985 Vrms input-equivalent | 0.00255504516 Vrms input-equivalent | 0.542867008 Vrms input-equivalent | 0.472058% |

## 主导误差

1. AMC3330 增益温漂：0.25875 Vrms input-equivalent
2. 分压比初始误差：0.23 Vrms input-equivalent
3. AMC3330 初始增益误差：0.23 Vrms input-equivalent
4. 一阶模拟低通标称衰减：0.198447085 Vrms input-equivalent
5. 分压器比例温漂：0.14375 Vrms input-equivalent
