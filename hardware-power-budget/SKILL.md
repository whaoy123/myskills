---
name: hardware-power-budget
description: Calculate, audit, and size board-level or system-level power rails from schematics/netlists/BOMs plus component datasheets. Use whenever the user asks for 整机电流、功耗、电源预算、各电源轨电流、DCDC/LDO 选型容量、输入电流、功率余量、rail load、power budget, or wants to know how much current/power to reserve for a PCB. Build a traceable load inventory per rail, distinguish typical/max/estimated/peak current, propagate converter efficiency upstream, apply design margin exactly once, and output a rail current-and-power table suitable for power-supply selection.
---

# Hardware Power Budget

为 PCB、调理板、控制板或整机建立**可追溯、可复算、可用于 DCDC/LDO 选型**的电流与功耗预算。默认中文简要输出，但内部必须完成器件计数、数据手册依据核验和确定性脚本计算。

## 何时调用

以下任一请求均调用本技能：

- “整板/整机要多少电流、多少瓦”；
- “每个电源轨留多少电流/功率”；
- “28 V 输入最后需要多大输入电流”；
- “这个 DCDC/LDO 够不够”；
- “根据原理图和芯片手册算功耗”；
- “给电源页/DCDC 选型做预算”；
- 检查别人给出的 rail current / power budget 是否漏算或重复加余量。

## 输入优先级

用户可以给任意组合：

1. **Netlist / pin-net / BOM / 原理图工程文件**：优先作为器件数量与电源网络真值源；
2. **原理图 PDF**：可用于识别拓扑、器件与电源轨；
3. **器件官方数据手册**：电流规格真值源；
4. 用户明确给出的工作模式、负载电流、DCDC 效率、余量策略。

若既有 Netlist/BOM 又有 PDF，数量和网络连接以 Netlist/BOM 为主，PDF 用于语义复核。只有截图或 PDF 时可以继续做，但必须把“器件计数/网络识别风险”标成待核验，不能假装与 Netlist 同等可靠。

## 随包文件

按需读取：

- 计算规则：`references/calculation-rules.md`
- 数据手册取值与常见漏项：`references/datasheet-and-load-guide.md`
- DCDC/LDO 选型检查：`references/power-supply-selection.md`
- 规范化输入模板：`templates/input-template.json`
- 确定性计算器：`scripts/power_budget.py`
- 回归测试：`tests/test_power_budget.py`

## 核心原则

### 1. 先建立电源轨，再数器件

先列清楚：

```text
rail 名称 / 电压 / 电气域 / 来源 / 是否隔离
```

例如 `+5_SEC`、`+15_SEC`、`-15_SEC`、`+12_PRI_POR`、`+12_PRI_Field`。

**同电压不等于同一电源轨。** 不同隔离域、不同 DC/DC 输出、不同高侧供电必须分开。不能因为都是 `12 V` 就合并。

### 2. 一个“器件-电源轨关系”一行

规范化负载时，每行只描述某器件在某一条 rail 上的电流：

```text
reference / component / quantity / rail /
Ityp_each / Imax_each(or Idesign_each) / Ipeak_each /
basis / source / notes
```

双电源运放若同时从 `+15 V` 和 `-15 V` 取电，就写两行。隔离器高侧与低侧来自不同 rail，也写两行。

### 3. Typical、Maximum、工程估计严格分开

优先级：

```text
Datasheet Maximum > 用户确认的工程设计值 > Datasheet Typical
```

- 有 Max：`current_max_a`；
- 无 Max，但用户/工程上明确采用保守值：写 `current_design_a`，并标注“工程假设”；
- 只有 Typical：可以计算典型功耗，但**不能给出可保证的最坏预算**。

绝不静默用 `Typical × 1.5` 之类规则伪造 Max。

### 4. 余量只加一次

默认：

```text
I_design_min = I_budget × (1 + margin)
P_design_min = |Vrail| × I_design_min
```

默认 `margin = 30%`，用户另有要求时按用户要求。

区分：

- `I_budget / P_budget`：器件数据形成的实际最坏负载；
- `I_design_min / P_design_min`：加设计余量后的**最低选型需求**；
- `selected rating`：实际选中的标准 DCDC/LDO 额定值。

不要在器件电流上先放大 30%，选 DCDC 时又再放大 30%。

## 固定工作流程

### Step 1 — 识别电源拓扑

从原理图/Netlist 提取：

- 输入电源；
- 每条稳压/隔离后的 rail；
- DCDC/LDO 的输入 rail 与输出 rail；
- 正负轨；
- 不同隔离域；
- 外部负载是否由本板供电。

画成逻辑关系：

```text
VIN → DCDC_A → +5V
    → DCDC_B → +15V / -15V
    → isolated converter → isolated +12V
```

### Step 2 — 统计 rail 上的全部负载

优先用 Netlist/BOM 自动统计 reference 与数量；再用原理图核对用途。

不仅统计 IC。按 `references/datasheet-and-load-guide.md` 检查：

- IC 静态/工作供电电流；
- LED、继电器/线圈、上拉/下拉、bleeder、分压器；
- 基准源和参考输入负载；
- 运放/驱动器的外部输出负载；
- 通信收发器不同工作状态；
- DCDC/LDO 自身静态电流；
- 本板给外部接口供电的负载。

### Step 3 — 查官方数据手册

对每个主要负载记录：

- 参数名；
- Typ / Max；
- 测试条件、供电电压、温度；
- 是每颗、每通道还是整芯片；
- 是否含内部隔离 DC/DC；
- 来源链接/PDF 页码/表格。

同一器件若 datasheet 中有多个工作模式，选择与当前方案匹配的模式；不确定时采用能覆盖目标工作状态的保守模式并标注。

### Step 4 — 规范化为 JSON

按 `templates/input-template.json` 生成输入。

关键规则：

- 电流单位统一为 A；
- 电压统一为 V；
- 功率由脚本计算，不手填；
- 负电源轨写负电压，例如 `-15`，功率使用 `|V| × I`；
- `source` 尽量写到 datasheet 页/章节；
- DCDC 最坏输入回推优先使用 `efficiency_min`；只有典型效率时只能算估计值。

### Step 5 — 必须运行确定性脚本

```bash
python scripts/power_budget.py input.json --format markdown -o power_budget_report.md
```

脚本负责：

1. 器件数量 × 单颗电流；
2. 按 rail 汇总 Ityp / Ibudget；
3. 计算 `P = |V| × I`；
4. 加一次设计余量；
5. 对级联 DCDC/LDO 向输入 rail 回推电流；
6. 区分最坏负载与选型容量；
7. 检查缺失 Max、缺失来源和额定值不足；
8. 输出 Markdown 或 JSON。

### Step 6 — DCDC/LDO 选型

若用户需要具体电源型号，再使用 `references/power-supply-selection.md`。

选型时至少满足：

```text
额定输出电流 >= I_design_min
额定总输出功率 >= P_design_min
输入工作范围覆盖真实 VIN min~max
温度降额后仍满足
```

双路/多路输出模块还要检查**每路额定电流 + 总功率限制**，不能只看包装上的总瓦数。

### Step 7 — 审核

提交前主代理完整自审一次。若环境支持子代理，再做两个独立完整审核：

- Reviewer A：只看原理图/Netlist，核对 rail、reference、数量、是否漏负载；
- Reviewer B：只看 datasheet 与计算输入，核对 Typ/Max、单位、条件、余量、效率和 DCDC 选型。

发现任何问题后修改输入并**重新运行脚本**；旧审核结果作废，重新完整审核。

## 默认输出

首先给用户一个紧凑的电源轨表：

| 电源轨 | 电压 | 负载组成 | 典型电流 | 最坏/预算电流 | 最坏功率 | 加余量后最低电流 | 加余量后最低功率 | 最终建议额定值 |
|---|---:|---|---:|---:|---:|---:|---:|---|

然后给：

- 实际最坏总功耗；
- 加余量后的最低设计容量；
- 如果已选标准模块：各 rail 最终额定电流/功率与利用率；
- 如果有输入电源和 DCDC 效率：整板输入最坏电流；
- 仅列真正影响选型的警告。

用户只问“最终留多少”时，不展开长篇推导；表格 + 结论即可。用户追问时再展开负载明细和数据手册依据。

## 强制检查清单

交付前逐项确认：

- Netlist/BOM 数量与手工统计一致；
- 同电压不同隔离域没有误合并；
- 双电源器件在正负 rail 上均计入；
- 隔离器高侧/低侧供电没有混淆；
- 内置隔离 DC/DC 的器件没有把内部输出再次当外部 rail 重复计功耗；
- Typical 没被冒充 Maximum；
- 每通道/每芯片电流没有乘错数量；
- LED、继电器、分压/bleeder、输出驱动等非 IC 静态负载没有漏掉；
- `P = |V| × I`，负 rail 没算成负功率；
- DCDC 回推使用效率，LDO 另算压差损耗；
- 30% 等设计余量只加一次；
- 启动/浪涌/峰值与连续功耗分开；
- 选型同时检查电流、功率、输入范围、温度降额和多输出总功率限制；
- 每个关键电流都有来源或明确标注“工程假设”。

## Human-facing finalization

当生成 `power_budget_report.md` 或其他正式给人阅读的功耗预算报告时，先完成数据手册核验、确定性脚本计算和审核，再运行 `no-negative-echo` 做最终文档清理。

该步骤只处理表达层，不允许改变计算结果、来源、工程假设、Typ/Max 区分、设计余量、风险警告或选型结论。报告应直接描述当前采用的电源拓扑、预算结果和选型要求，不保留已经被本轮核算否决的会话方案残影。

规范化 JSON、脚本输入输出、计算中间数据、审核记录和来源证据属于可追溯计算/审计材料，不执行该清理。
