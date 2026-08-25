---
name: rtl-verification
description: 从已确认的 module_contract.md、rtl_design.md 和通过轻量 Review 的 RTL 出发，生成可审核的 verification_plan.md、SystemVerilog TB、自动仿真脚本、Questa 波形脚本和 debug_record.md，并按“验证计划→TB→仿真/Debug→局部回归→全量回归”完成 RTL 模块验证。强调周期级时序、TB 判定依据、人机验收点，以及 RTL/TB/Design 三类问题的严格区分。
---

# RTL Verification

## 目标

验证阶段的目标不是“让仿真 PASS”，而是证明：

> `module_contract.md` 和 `rtl_design.md` 中已经定义的行为，在当前验证计划覆盖范围内被正确实现。

本技能覆盖：

1. `verification_plan.md`
2. TB 编写
3. 自动检查
4. 终端仿真脚本
5. Questa 波形脚本
6. Debug
7. 局部回归与全量回归
8. 验证完成判定
9. `debug_record.md`

不额外生成独立 signoff 文档。

---

# 1. 输入与权威关系

进入本技能前，至少需要：

1. 已确认的 `module_contract.md`
2. 已确认的 `rtl_design.md`
3. 已通过 `rtl-pre-tb-review` 的 RTL
4. 项目上下文：时钟、复位、依赖文件、参数、仿真器和目录结构

验证行为的权威顺序固定为：

```text
module_contract.md / rtl_design.md
            ↓
verification_plan.md
            ↓
TB 的预期行为与检查逻辑
            ↓
RTL 实际输出
```

**禁止从 RTL 反推“正确答案”再写 TB。**

原因：错误 RTL 不能成为 TB 的预期行为来源，否则可能出现 RTL 与 TB 同时错误但仍然 PASS。

---

# 2. 设计歧义处理

如果写验证计划或 TB 时发现一个关键行为没有在 Contract / Design 中定死，并且会影响：

- 功能；
- 接口；
- 周期级时序；
- 错误处理；
- 数据语义；
- 优先级；
- 超时起点；
- 握手完成条件；

则停止替用户做决定，返回设计阶段确认。

典型例子：

- `valid` 是 C+1 还是 C+2；
- timeout 从 `busy`、`valid` 还是 handshake 开始计；
- 错误字丢弃还是仍然上报；
- FIFO 满时 drop-new、drop-old 还是停止接收；
- 同周期两个关键事件谁优先。

如果只是 TB 组织方式、task 名称、局部变量、随机数产生方式等，不需要询问用户。

---

# 3. verification_plan.md

验证计划只保留三部分：

```markdown
# <Module> Verification Plan

## 验证目标
...

## 验证表格
...

## 验证结果
...
```

## 3.1 验证目标

只写 1～2 句话，说明要证明哪些外部行为和关键设计语义。

不要重复模块背景、接口说明和 RTL 实现。

## 3.2 组织方式

按“验证点 → 测试用例”组织。

```text
验证点
└── 测试用例
    ├── simple
    ├── boundary
    ├── continuous
    └── abnormal
```

上面的 simple / boundary / continuous / abnormal 只是常见思路，不要求每个验证点机械凑齐四类。

### 验证点

回答：

> 要证明什么？

例如 RX：

1. 数据接收正确；
2. 字类型输出正确；
3. `valid` 时序正确；
4. 反压时输出保持正确。

### 测试用例

回答：

> 具体用什么条件去证明这个验证点？

一个具体激励可以同时覆盖多个验证点，但验证计划仍按验证点组织，便于发现遗漏。

## 3.3 测试用例固定字段

每个测试用例只要求五项：

| 字段 | 含义 |
|---|---|
| 用例 ID | 如 `V1-1` |
| 激励 / 前置条件 | DUT 接收什么、起始状态是什么 |
| 时序要求 | 周期级或协议级时间要求 |
| 预期结果 | 功能结果 |
| 检查方式 | TB 如何自动判定 PASS/FAIL |

默认不要再增加“测试目的、详细步骤、备注、风险等级”等重复字段。

推荐形式：

| ID | 激励 / 前置条件 | 时序要求 | 预期结果 | 检查方式 |
|---|---|---|---|---|
| V1-1 | 合法数据字，`ready=1` | `C0` 字完成；`C+1` `valid=1` | `data` 正确，`error=0` | 直接比对 |
| V4-1 | `valid=1` 后令 `ready=0` | `C0` 进入反压；`C+1...Cn` 保持，直到 handshake | 结果包稳定 | Assertion |

---

# 4. 时序要求必须明确

## 4.1 周期级时序

只要可以用时钟描述，必须使用：

```text
C0
C+1
C+N
until
```

定义：

```text
C0    = 触发事件所在周期
C+1   = 触发后的下一个有效周期
C+N   = 触发后第 N 个有效周期
until = 一直保持到指定条件成立
```

禁止只写：

- 随后；
- 之后；
- 稍后；
- 保持一段时间；
- 若干周期后。

### RX 示例

```text
C0：一个字完成
C+1：valid_o = 1，data/type/error 有效
```

反压：

```text
C0：valid_o = 1 且 ready_i = 0
C+1...Cn：valid/data/type/error 保持
until：valid && ready 完成握手
```

### AXI4-Lite 示例

```text
C0：AW handshake
C+k：W handshake
C0...C+(k-1)：不得发生内部写
C+k 或设计规定周期：发起内部写
```

## 4.2 协议绝对时间

协议本身定义的物理时间范围继续使用时间单位，例如：

```text
RT response：4~12us
```

不要为了统一格式把协议物理时间强行换成周期描述；可以在需要时同时给出其对应周期数。

## 4.3 时序未确定时禁止猜

如果设计只写“完成后拉高 valid”，但没有说明 C+1 还是 C+2，而这个差异会影响 TB 判定，则先回到 `rtl_design.md` 确认。

---

# 5. 自动检查方式

默认只分三类。

## 5.1 直接比对

用于检查某个时刻的明确值：

- data；
- type；
- error；
- count；
- address；
- response code。

示例：

```systemverilog
if (data_o !== expected_data)
    $error("V1-1: data mismatch, expected=%h actual=%h", expected_data, data_o);
```

## 5.2 Assertion（时序断言）

用于检查跨周期关系和持续约束：

- `valid` 在反压时保持；
- data 与 valid 同步保持；
- 请求后 N 周期必须出现响应；
- 某状态下禁止写；
- handshake 后才能释放当前结果。

原则：

> 直接比对主要检查“值”；Assertion 主要检查“时序关系和持续约束”。

## 5.3 参考模型比对

TB 根据输入独立计算期望值，再与 DUT 比较。

适用于：

- CRC；
- 编解码；
- Cache 地址/替换结果；
- 数据变换；
- 复杂打包/解包。

参考模型必须来自协议/设计定义，不得复制 DUT 的内部算法结构作为“独立模型”。

---

# 6. 人工验收点

AI 可以自动完成大部分 TB 编写和回归，但有两个点默认需要用户确认。

## 6.1 verification_plan.md 时序审核

用户重点确认：

- `C0` 定义是否正确；
- `C+1 / C+N` 是否符合设计；
- timeout 起点是否正确；
- handshake 和 hold 条件是否正确；
- 协议绝对时间是否正确。

不要求用户逐行审核 TB。

## 6.2 首次 TB 可信度检查

TB 首次完成后，人工重点审：

- 关键 checker 在哪一拍采样；
- Assertion 的前因和后果是否错一拍；
- wait / handshake 条件是否正确；
- 参考模型的输入采样点是否正确。

首次 bring-up 建议查看 1～3 个最关键波形，确认 TB 对时序的整体理解没有偏移。

之后正常回归以自动检查为准，不要求每次人工看波形。

---

# 7. TB 编写规则

TB 必须能自动判定 PASS/FAIL。

要求：

- 每个测试用例能够映射回 `verification_plan.md` 的用例 ID；
- FAIL 日志必须打印用例 ID；
- 检查逻辑与激励逻辑尽量分开；
- 周期边界必须明确，避免依赖模糊的 `#delay` 猜测 DUT 时序；
- 时钟同步接口优先在明确 clock edge 驱动和采样；
- 必须有全局超时保护，避免 TB 永久挂死；
- 测试结束输出总用例数、PASS、FAIL；
- 全部通过时输出明确的 `ALL PASS` 或项目约定等价标记。

如果独立 Assertion 文件更清晰，可以生成：

```text
<module>_assertions.sv
```

简单模块也可以直接把少量断言放在 `<module>_tb.sv` 中，不为拆文件而拆文件。

---

# 8. 仿真运行脚本

TB 阶段至少保留两类运行入口。

## 8.1 终端自动回归脚本

用于：

- 编译；
- elaboration；
- 无 GUI 运行；
- 收集 PASS/FAIL；
- Debug 后快速重跑；
- 全量回归。

文件名遵循项目现有习惯，例如：

```text
run_sim.bat
run_sim.ps1
run_sim.sh
run_sim.do
```

不要把工具生成目录和临时日志当作正式交付物。

仿真器优先级不写死为全局固定顺序，应先读取项目现有工具链。若当前项目环境明确为 Questa/Vivado，则优先兼容这两套工具。

## 8.2 Questa 波形脚本

必须额外保留一份可以直接打开关键波形的 Questa 脚本，例如：

```text
questa_wave.do
run_questa_wave.do
```

要求：

- 自动加载 DUT/TB 需要观察的信号；
- 按功能分组；
- 排列顺序面向人工阅读；
- 用户打开后无需重新手工逐个添加信号。

具体分组、排序和命名规则交给 `questa-wave-layout` Skill，不在本技能中重复定义。

本技能负责告诉 `questa-wave-layout`：

> 哪些信号与哪些验证点、时序关系和 Debug 目标有关。

---

# 9. 波形使用规则

正常验证以 TB 自动检查为准。

波形主要用于：

1. 首次确认 TB 的时间基准和 checker 没有整体错拍；
2. Debug 时定位 FAIL 从哪一拍开始、为什么发生。

不要把“每个验证点都人工看波形”作为通过条件。

---

# 10. 仿真 / Debug 闭环

固定流程：

```text
运行全部 TB
    ↓
得到 FAIL 用例
    ↓
按 verification_plan 定位预期
    ↓
分类：RTL / TB / Design
    ↓
修正确认错误的一侧
    ↓
局部回归
    ↓
全量回归
    ↓
稳定后同步必要文档
```

## 10.1 第一次失败时先分类

### RTL

Contract / Design / Verification Plan 明确，TB 判定也正确，DUT 实际行为不符合预期。

→ 只修 RTL。

### TB

Contract / Design / Verification Plan 明确，RTL 行为符合预期，但 TB 激励、采样、等待、checker 或参考模型错误。

→ 只修 TB。

### Design

失败暴露出关键行为原本没有定义，或现有文档相互矛盾。

→ 不继续猜，回到设计阶段让用户决定。

## 10.2 禁止为了 PASS 同时改 RTL 和 TB

除非已经分别确认两边都有独立问题，否则不能通过“RTL 改一点 + TB 改一点”让结果重新 PASS。

原则：

> 先根据 Contract / Design / Verification Plan 判断哪一侧错，再只修错误的一侧。

## 10.3 局部回归

修复后先运行：

- 直接失败的测试用例；
- 与修改逻辑强相关的相邻用例。

局部 PASS 后再运行全量回归。

## 10.4 全量回归

模块验证结束前必须完整跑一遍当前 `verification_plan.md` 对应的所有用例。

---

# 11. debug_record.md

所有发现的问题都记录，不只记录重大 Bug。

它是工程日志，不是长篇 Debug 报告。

固定表格：

| ID | 时间 | 关联验证点 | 现象 | 分类 | 根因 | 修改 | 回归结果 | 状态 |
|---|---|---|---|---|---|---|---|---|
| D001 | 2026-08-23 | V2-3 | `valid_o` 晚 1 拍 | RTL | 完成条件判断晚一拍 | 修正完成条件 | 局部 PASS，全量 PASS | CLOSED |

分类固定为：

```text
RTL
TB
Design
```

状态固定为：

```text
OPEN
CLOSED
```

同一个问题经历多次修改时，不删除历史信息。可在同一行的“修改/回归结果”中追加简短版本记录，或新增关联记录；不要覆盖掉导致问题演进信息丢失。

---

# 12. 文档同步

Debug 过程中不要每试一个修改就同步 `rtl_design.md`。

推荐顺序：

```text
改 RTL / TB
→ 仿真
→ 确认根因与稳定方案
→ 局部回归
→ 全量回归
→ 再同步设计文档
```

只有真正改变设计语义时才回写 `rtl_design.md`，例如：

- timeout 起点改变；
- 错误字处理规则改变；
- 模块职责改变；
- 数据提交时机改变；
- 同周期事件优先级改变。

纯实现 Bug 修复不需要把修复过程写进 `rtl_design.md`，但必须留在 `debug_record.md`。

如果接口、Purpose 或 Capability 改变，则还需要同步 `module_contract.md`。

---

# 13. 验证完成条件

只有同时满足以下四条，模块才算在当前验证计划范围内验证完成。

## 1. verification_plan 全部有执行结果

每个测试用例都真正运行过，不能只写在计划中。

## 2. 所有自动检查通过

包括适用的：

- 直接比对；
- Assertion；
- 参考模型比对。

## 3. TB 已完成一次可信度验收

至少确认：

- 关键 checker 时间基准正确；
- Assertion 没有明显错拍；
- 首次关键波形与设计定义一致。

这不是每次回归都要重复做。

## 4. 所有 Debug 闭环

- 已知 FAIL 都有根因；
- `debug_record.md` 中没有未解释的失败；
- 修复后局部回归通过；
- 最终全量回归通过。

最终结论应表述为：

> 当前版本 RTL 在当前 Verification Plan 覆盖范围内验证完成。

不要扩张成“模块绝对正确”。

---

# 14. 正式保留的输出

推荐结构：

```text
<module>_tb/
├── <module>_tb.sv
├── <module>_assertions.sv      # 有需要才有
├── run_sim.*                   # 终端自动回归
├── run_questa_wave.do          # Questa 波形入口
├── verification_plan.md
└── debug_record.md
```

工具产生的以下内容默认不作为正式交付物：

- 临时编译目录；
- 可重新生成的 `.wlf`；
- 大量中间日志；
- 临时缓存；
- 仿真器工作库。

如果项目已有固定目录结构，以项目为准，不强制迁移。

---

# 15. 与其他 Skill 的配合

## `rtl-module-contract`

提供外部接口、Purpose 和 Capabilities，是验证目标的第一来源。

## `rtl-design-doc`

提供职责、数据流、关键状态/存储、关键时序和关键设计语义，是周期级预期行为的主要来源。

## `rtl-pre-tb-review`

只有 Blocking 已清零的 RTL 才进入正式 TB 阶段。

## `synthesizable-human-rtl`

用于理解 RTL 结构、发现潜在时序/握手风险；不能用 RTL 内部实现替代 Contract / Design 作为正确性标准。

## `questa-wave-layout`

负责 Questa 信号选择后的分组、排序和可读布局。本技能提供“需要观察什么”，该 Skill 决定“怎么摆给人看”。

## `engineering-doc-style`

如果可用，应用于 `verification_plan.md` 和 `debug_record.md`：保持工程化、简短、直接，不扩写成报告。

---

# 16. Human-facing finalization

`verification_plan.md` 和最终验证结论属于正式的人类可读验证产物。它们的技术内容确认后运行 `no-negative-echo`，使当前计划和结论只表达现行验证目标、时序要求、检查方式、执行结果和仍然有效的限制。

最终化顺序：

```text
确认 Contract / Design / Plan 一致
→ 完成 TB 与回归
→ 写入当前验证结果
→ 应用工程文档风格
→ run no-negative-echo
→ final read-back
```

必须明确豁免以下内容：

- `debug_record.md`；
- FAIL 日志；
- 仿真原始日志；
- 历史 Review / Audit；
- 需要保留的问题演进事实。

这些记录的职责就是保存失败、根因、修改和回归历史，不能因为最终版本已经 PASS 就清除或改写。

`no-negative-echo` 也不能删除 `verification_plan.md` 中仍然有效的异常用例、边界条件、风险说明、协议限制或必要的比较依据。

---

# 17. 核心原则

```text
设计文档定义正确行为。
Verification Plan 把正确行为变成可检查要求。
TB 负责执行检查，不负责重新定义设计。
AI 可以自动执行 Debug，但不能替用户决定未定义的关键设计语义。
首次人工验的是“TB 这把尺子准不准”，之后回归以自动检查为主。
正式计划和最终结论可以清理会话残影；Debug 与失败历史必须保留。
```
