# 官方资料索引

技能不硬编码某个器件的永久参数。每次正式预算应读取用户提供的数据手册或制造商当前版本。

以下资料用于建立本技能的方法框架，检索日期：2026-08-07。

1. Texas Instruments, **AMC3330 Precision, ±1-V Input, Reinforced Isolated Amplifier With Integrated DC/DC Converter**, SBASA34B, revised August 2024. 重点指标包括 gain error、gain drift、input offset、offset drift、nonlinearity、bias current、noise、CMRR、PSRR、bandwidth 和 THD。  
   https://www.ti.com/lit/ds/symlink/amc3330.pdf

2. Texas Instruments, **ADC Input Circuit Evaluation for C2000 MCUs**, SPRACT6A. 重点说明 SAR ADC 采样电容、源阻抗和 acquisition settling。  
   https://www.ti.com/lit/spract6

3. Texas Instruments, **SAR ADC input driver / reference droop and settling modeling**, SBAA531. 重点说明输入建立、参考下垂、参考噪声和 ADC 时序的共同影响。  
   https://www.ti.com/document-viewer/lit/html/SBAA531

4. Analog Devices, **The ABCs of Analog to Digital Converters: How ADC Errors Affect System Performance**. 重点说明 offset、gain、INL、DNL、reference、temperature 和 AC performance。  
   https://www.analog.com/en/resources/technical-articles/the-abcs-of-analog-to-digital-converters-how-adc-errors-affect-system-performance.html

5. Analog Devices, **Understanding AC Behaviors of High Speed ADCs**. 重点说明 quantization、SNR、SINAD、ENOB、jitter、THD 和 SFDR。  
   https://www.analog.com/en/resources/technical-articles/understanding-ac-behaviors-of-high-speed-adcs.html

使用规则：

- 技术问题优先采用制造商数据手册和应用笔记；
- 用户给出具体料号时，读取对应 revision，不从相似型号迁移参数；
- 数据手册冲突时，以最新正式 PDF 的参数表和测试条件为准；
- 输出中注明参数是 typical 还是 maximum。
