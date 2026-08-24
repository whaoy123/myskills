---
name: rtl-design-flow
description: RTL 模块开发总流程索引。负责判断当前阶段、调用对应 Skill、检查阶段输入输出和 Gate，不复制各子 Skill 的详细规则。
---

# RTL Design Flow

## 目标

这个 Skill 不负责替代具体设计、编码或验证 Skill。

它只负责四件事：

1. 判断当前模块处于哪个阶段；
2. 确定当前阶段应该读取什么输入；
3. 调用对应 Skill 完成当前阶段；
4. 检查当前阶段是否满足进入下一阶段的 Gate。

原则：

> 顶层流程只做索引和编排，具体规则放在对应子 Skill 中。

---

# 总流程

```text
需求 / 项目上下文
      ↓
1. Module Contract
      ↓
2. RTL Design
      ↓
3. RTL Coding
      ↓
4. Pre-TB Review
      ↓
5. Verification Plan
      ↓
6. TB Implementation
      ↓
7. Simulation / Debug / Regression
      ↓
8. Verification Complete
```

阶段输出默认作为下一阶段输入，不要求用户重复说明已经确定的内容。

---

# Skill 路由

| 阶段 | 主要 Skill | 主要输出 |
|---|---|---|
| Module Contract | `rtl-module-contract` | `module_contract.md` |
| RTL Design | `rtl-design-doc` | `rtl_design.md` |
| RTL Coding | `synthesizable-human-rtl` | RTL 文件 |
| Coding 过程中的关键决策确认 | `grill-me` | 用户确认后的设计决策 |
| Pre-TB Review | `rtl-pre-tb-review` | PASS / FAIL + Blocking / Warning |
| Verification | `rtl-verification` | TB、`verification_plan.md`、`debug_record.md`、仿真脚本 |
| Questa 波形布局 | `questa-wave-layout` | Questa `.do` / 波形脚本 |
| 工程文档写作 | `engineering-doc-style` | 作为文档类 Skill 的最终风格层 |

如果某个通用 Skill 尚未完善，不阻塞流程本身；先按当前规则工作，后续再替换或增强。

---

# 阶段 1：Module Contract

调用：`rtl-module-contract`

输入：

- 用户需求；
- 现有项目文档；
- 上下游接口；
- 已有 RTL；
- 协议资料；
- 项目规则。

输出：

```text
module_contract.md
```

Gate：

1. Interface 确定；
2. Purpose 清楚；
3. Capabilities 可明确判断是否实现。

Contract 只冻结模块边界，不要求此时把所有内部时序、FSM 和实现结构定死。

---

# 阶段 2：RTL Design

调用：`rtl-design-doc`

输入：

- 已确认的 `module_contract.md`；
- 项目上下文；
- 协议资料；
- 现有模块关系；
- 已有 RTL（如果是改造现有模块）。

输出：

```text
rtl_design.md
```

Gate：

1. 职责划分清楚；
2. 主数据流 / 主流程清楚；
3. 关键状态或存储需求清楚；
4. 关键时序和关键设计语义清楚。

这里冻结的是行为和关键设计决策，不是具体 RTL 结构。

---

# 阶段 3：RTL Coding

调用：`synthesizable-human-rtl`

输入：

- `module_contract.md`；
- `rtl_design.md`；
- 项目现有 RTL、宏、参数、package、上下游接口；
- 项目代码风格和工具链约束。

优先级：

```text
Contract / Design  → 决定做什么
Coding Skill       → 决定怎么写
```

AI 可以自行决定：

- FSM 具体拆几个状态；
- 中间寄存器和信号名；
- 条件如何拆分；
- `always_ff / always_comb` 组织；
- 局部实现结构；
- 不改变设计语义的综合友好写法。

如果实现过程中发现某个问题满足以下任一条件，并且原设计文档没有定死，必须停止并询问用户：

- 功能语义；
- 模块职责；
- 接口；
- 关键时序；
- 错误处理；
- 数据语义；
- 重要优先级；
- 缓存满、超时、覆盖等策略。

不要为了继续编码而静默猜测关键设计决策。

RTL 阶段输出保持最小：

- 最终 RTL；
- 简短修改说明；
- 如果仍有未决关键项，明确列出。

---

# 阶段 4：Pre-TB Review

调用：`rtl-pre-tb-review`

输入：

- `module_contract.md`；
- `rtl_design.md`；
- 当前 RTL。

目标：

> 在写 TB 前拦住明显问题，不替代正式仿真验证。

Gate：

```text
Blocking = 0
```

Warning 可以带入下一阶段，但必须记录并让用户知道。

---

# 阶段 5～8：Verification

调用：`rtl-verification`

输入：

1. `module_contract.md`；
2. `rtl_design.md`；
3. 通过 Pre-TB Review 的 RTL；
4. 后续生成并经用户确认的 `verification_plan.md`。

验证权威顺序：

```text
Contract / Design
      ↓
Verification Plan
      ↓
TB
      ↓
RTL observed behavior
```

TB 不允许从 RTL 反推出“正确答案”。

验证阶段包含：

```text
verification_plan.md
      ↓
TB implementation
      ↓
compile / simulate
      ↓
FAIL classification
      ↓
RTL / TB / Design
      ↓
fix wrong side
      ↓
local regression
      ↓
full regression
```

如果 FAIL 暴露出新的关键设计歧义，回到 Design，由用户确认后再继续。

最终验证文档只保留：

```text
verification_plan.md
debug_record.md
```

TB、终端运行脚本、Questa 波形脚本作为工程文件保留。

验证完成条件由 `rtl-verification` 定义。

---

# 文档同步规则

开发中允许先修改 RTL、跑仿真、确认方案稳定，再同步设计文档。

需要回写文档的是稳定的设计决策变化，例如：

- 接口变化；
- 模块职责变化；
- Capability 变化；
- 关键时序变化；
- 错误处理语义变化；
- 数据语义变化；
- 关键存储或提交规则变化。

纯实现 Bug、状态数变化、内部表达式变化、局部重构通常不回写设计文档。

---

# 人工验收点

AI 可以自动完成大量编码、仿真和 Debug，但以下位置默认需要用户确认：

1. `module_contract.md` 的模块边界；
2. `rtl_design.md` 的关键设计语义；
3. 实现过程中出现的未定义关键决策；
4. `verification_plan.md` 的关键时序和预期行为；
5. 首次 TB 验收时，确认关键 Checker 的时间基准没有错拍；
6. Debug 发现设计语义需要改变时。

原则：

> AI 可以替用户执行 Debug，但不能替用户决定尚未定义的重要设计语义。

---

# 进入流程时的处理方式

用户给出一个新的 RTL 模块任务时：

1. 先读取已有项目上下文；
2. 判断已有文件覆盖到哪个阶段；
3. 不重复已经通过的阶段；
4. 从第一个未通过 Gate 的阶段继续；
5. 如果用户明确要求跳过某个阶段，可以跳过，但要说明失去的约束或验证依据；
6. 不把整套流程一次性重新输出给用户，只汇报当前阶段和下一步。

如果是已有 RTL 的维护任务，也不要求机械地从 Contract 重写一遍。先检查现有 Contract / Design 是否足够支撑修改；只有缺失会影响当前修改的关键内容时才补。

---

# 核心原则

```text
先定模块边界
再定关键设计语义
再写 RTL
先做轻量 Review
再定义验证预期
TB 按预期验证 RTL
失败先判错在哪一侧
稳定后再同步文档
```

不要让文档变成第二份 RTL，也不要让 TB 变成 RTL 的自我证明。
