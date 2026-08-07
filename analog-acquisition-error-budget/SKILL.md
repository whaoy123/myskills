---
name: analog-acquisition-error-budget
description: Calculate, combine, audit, or explain errors in an analog measurement and ADC acquisition chain. Use whenever the user asks about 误差、精度、准确度、温漂、偏移、增益误差、INL/DNL、量化、噪声、误差合并、误差预算, or wants to evaluate a divider, shunt, isolation amplifier, op-amp, filter, multiplexer, ADC, voltage reference, clock, PCB, RMS algorithm, or calibration. Normalize every source to one reporting point, distinguish percent-of-reading, percent-of-full-scale, fixed offset, drift, dynamic error, and random noise, then report worst-case and RSS separately.
---

# Analog acquisition error budget

为完整模拟采集链建立可审查、可复算的误差预算。默认使用中文简要输出，但计算过程必须完整、单位一致。

## 何时调用

只要任务涉及以下任一内容，就调用本技能：

- 计算“测量值最多偏多少”；
- 判断某 ADC、隔离放大器、分压器或运放精度是否足够；
- 合并电阻、隔离、ADC、基准源和滤波器误差；
- 比较校准前后精度；
- 从器件数据手册提取误差参数；
- 为电压闭环、保护阈值或测试设备建立误差预算；
- 解释百分比误差、固定偏移、满量程误差、温漂、RSS 等概念。

不要只在用户明确说“误差预算”时触发；“这个测 115 V 能偏多少”“ADC 会不会不准”同样属于本技能。

## 随包文件

按需要读取：

- 全部潜在误差源：`references/error-source-catalog.md`
- 公式和合并规则：`references/calculation-rules.md`
- 数据手册指标映射：`references/datasheet-field-guide.md`
- 校准与输出规则：`references/calibration-and-reporting.md`
- 官方资料索引：`references/source-notes.md`
- 确定性计算器：`scripts/error_budget.py`
- JSON 模板：`templates/input-template.json`

## 工作流程

### 1. 明确被测量和报告端

先固定：

- 被测量，例如 `POR A-N 电压`；
- 报告端，默认折算到被测输入端；
- 数值形式：DC、峰值、峰峰值或 RMS；
- 结果算法：瞬时/峰值、原始 RMS，还是去均值后的 RMS；
- 正常值、测量范围、过载范围；
- 信号频率和波形；
- 环境温度范围；
- 校准条件。

用户资料不足时不要停在空泛提问。先列出缺失项，采用清晰的保守假设继续计算，并标注“待替换”。

### 2. 建立节点与传递比例

把链路写成：

```text
被测输入 → 分压/传感器 → 隔离 → 运放/滤波 → ADC 输入 → ADC 码 → 软件结果
```

为每个节点定义：

```text
G_node = 节点电压 / 被测输入值
```

局部电压误差折算到输入端：

```text
E_input = E_local / |G_node|
```

百分比读数误差可直接作用于最终读数，因为线性比例会约掉。

### 3. 从数据手册提取规格

每项必须记录：

- 参数名称；
- 典型值还是最大值；
- 测试条件；
- 参考温度和工作温度；
- 是 `% of reading`、`%FS`、电压、LSB、ppm/°C、噪声 RMS 还是频域指标；
- 位于哪个电路节点；
- 是否可通过零点或增益校准消除。

不得把 Typical 当作 Max。没有最大值时，明确写“仅典型估计，不能用于保证”。

### 4. 分类

至少分成：

1. 比例/增益误差；
2. 固定偏移误差；
3. 满量程相关误差；
4. 温漂和长期漂移；
5. 非线性；
6. 动态幅值/相位/建立误差；
7. 随机噪声；
8. 校准参考和算法误差。

### 5. 统一折算

先统一成被测输入端物理等效量，再根据结果算法转换成“对最终报告值的误差”。固定 DC offset 在去均值 RMS 中可为零，在原始 RMS 中应按平方和计算。禁止直接把 `%`、`mV`、`LSB` 和 `ppm/°C` 混在一起相加。

常用形式：

```text
±(a% × 读数 + b × 满量程 + c V)
```

如果满量程项已换算成输入端固定电压，可简化为：

```text
±(a% 读数 + d V)
```

### 6. 分开计算校准前后

至少考虑：

- 未校准；
- 零点校准；
- 单点增益校准；
- 两点校准。

初始失调和初始增益可被相应校准消除，但必须新增：

- 校准源不确定度；
- 校准重复性；
- 校准温度与使用温度之间的漂移；
- 非线性和长期漂移。

### 7. 合并

默认同时输出：

- **最坏情况**：有界系统误差绝对值线性相加；
- **RSS 估计**：仅对合理独立的误差平方和开方；
- **随机噪声 RMS**：随机项单独 RSS；
- **保守总值**：系统最坏值 + `k × 随机 RMS`，默认 `k=3`。

相关误差不得直接当作独立项 RSS。共享同一基准、同一电阻网络、同一温度梯度或同一校准系数时，应注明相关性。

### 8. 输出

默认输出五部分：

1. **结论**：在指定输入下，未校准和校准后的最大偏差；
2. **假设与传递比例**；
3. **误差明细表**：器件、参数、局部值、折算公式、输入端误差、是否可校准；
4. **合并结果**：最坏值、RSS、随机 RMS；
5. **主导项和改进建议**。

表格至少包含：

| 来源 | 指标 | 类型 | 折算到输入端 | 校准后是否保留 |
|---|---|---|---:|---|

## 强制检查

提交前确认：

- 峰值、峰峰值和 RMS 没有混用；
- 百分比是相对读数还是满量程；
- 温漂已乘温差，且没有把正负温差抵消；
- 电阻容差与 TCR/VCR/自热没有混为一个指标；
- ADC 基准源误差没有漏算或与 ADC 增益误差重复计算；
- 量化误差、INL、噪声没有重复计入同一个“总未调整误差”；
- 模拟滤波器在目标频率处的幅值衰减已检查；
- SAR ADC 的采样建立误差已检查；
- 校准没有错误地消除非线性、温漂和长期漂移；
- 最坏值与 RSS 没有混成一个数字；
- 所有结果都能追溯到公式或数据手册参数。

## 计算器

当来源超过 5 项、存在多个节点或需同时比较校准前后时，优先使用：

```bash
python scripts/error_budget.py input.json --format markdown
```

脚本结果是计算辅助，不替代对指标含义、重复计数和相关性的工程判断。
