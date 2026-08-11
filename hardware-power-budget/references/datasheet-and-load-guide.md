# Datasheet and Load Guide

## 1. 常见电流字段

优先寻找：

- Supply current / supply current per channel
- Quiescent current (IQ)
- Operating current / active current
- IDD / ICC / IVDD / IAVDD / IDVDD
- No-load input current（电源模块）
- Shutdown / standby current（若场景使用）
- Output current（注意这往往是能力，不是器件自身消耗）

必须确认参数是：

- 每颗器件还是每通道；
- 单 rail 还是正负 rail 合计；
- 典型还是最大；
- 在什么 VCC、温度、输出负载、采样率、通信速率、工作模式下测得。

## 2. 隔离放大器/隔离器

特别检查：

- low-side supply current；
- high-side supply current；
- 是否集成隔离 DC/DC；
- 高侧电源是内部生成还是外部供电。

如果高侧由器件内部隔离 DC/DC 生成，通常其能量已经反映到低侧输入电流中。不要再把内部高侧输出作为板级独立外部 rail 重复计入。

如果高侧需要外部独立供电，则 high-side 与 low-side 分别计在各自 rail。

## 3. 运放/模拟器件

除了 quiescent current，还要检查实际输出是否带显著负载：

```text
Iout_load ≈ Vout / Rload
```

若输出只接高阻 ADC，常常可忽略；若驱动低阻、终端、LED 或其他电路，必须额外计入。不要把器件“最大输出驱动能力”直接当作持续消耗，除非电路确实在该负载下工作。

## 4. 数字器件和收发器

电流可能强烈依赖：

- 时钟频率；
- 数据速率；
- GPIO 翻转；
- PHY link state；
- TX dominant/recessive 状态；
- FPGA 利用率；
- MCU 外设开启情况。

只有 datasheet 静态电流而动态占主导时，不应声称预算已经完整。需要厂商功耗工具、实测或明确的保守工作模式。

## 5. 容易漏掉的非 IC 负载

逐项扫描：

- 电源 LED + 限流电阻；
- pull-up / pull-down；
- bleeder / preload；
- 从 rail 到地的分压器；
- relay / contactor / solenoid coil；
- optocoupler LED；
- 电阻加热/偏置网络；
- 传感器激励；
- ADC/DAC voltage reference 及其负载；
- 本板对外接口提供的 3.3/5/12/24/28 V；
- 风扇、蜂鸣器等附件。

分压/bleeder：

```text
I = V / R_total
P = V² / R_total
```

## 6. 数据手册没有 Maximum 怎么办

允许三种状态：

1. `current_max_a`：数据手册最大值，可用于保证；
2. `current_design_a`：用户或工程师明确给出的保守值，只能标成工程假设；
3. 只有 `current_typ_a`：只能给典型估算，最坏预算标 `INCOMPLETE`。

禁止自动把 Typical 乘某个系数并伪装成 Maximum。

## 7. 来源记录

每个主要电流项至少记录：

```text
Part number
Parameter name
Value
Typ/Max
Condition
Datasheet revision/date if relevant
Page/table/section or official URL
```

当多个料号后缀有不同温度等级或规格时，必须匹配原理图/BOM 中实际型号。
