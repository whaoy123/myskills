---
name: dida-task-breakdown
description: Decompose a Dida project, phase, or oversized task into executable child work with clear outputs, completion criteria, dependencies, and clean hierarchy. Use for 拆任务、细化项目、建立子任务、整理任务池、识别前置依赖. Read the current Dida tree and relevant project rules instead of hard-coding project structure. Route duration estimation to dida-task-estimator and clock scheduling to dida-daily-planner.
---

# Dida Task Breakdown

把一个过大的项目、阶段或任务拆成**可执行、可验收、依赖关系清楚**的子工作。

本 Skill 只负责回答：

> 这件事应该拆成哪些工作，做到什么算完成，它们之间什么先做、什么后做。

它不负责估时和具体排钟点。

## 职责边界

本 Skill 负责：

- 判断当前节点应保持为 `project`、`phase` 还是拆成 `task`；
- 从最终产出和完成标准反推合理子任务；
- 保持父子层级清楚；
- 建立必要的硬/软依赖；
- 发现缺失的前置工作和阻塞项；
- 在用户要求写入 Dida 时创建或调整对应子任务；
- 将叶子任务交给 `dida-task-estimator` 估时。

本 Skill 不负责：

- 根据某个用户当前项目硬编码固定任务树；
- 自己决定 `#0.5h/#1.0h/...`；
- 生成每天几点到几点的执行块；
- 因为“拆得更细”就机械创建大量微任务；
- 静默删除、改名或重排用户已有的重要任务。

## 运行态真值源

项目结构和命名规则必须从当前运行态读取，不写死在 Skill 中。

优先读取：

1. 当前目标父任务及其 body / Planner block；
2. 当前父任务已有 children 和同级节点；
3. `系统协议｜标签与任务正文`；
4. `系统协议｜依赖关系`；
5. 与当前项目直接相关的 `dida-planning-memory`，仅在它会改变拆分结果时读取；
6. 如果任务来自 `engineering-prestudy`，读取已批准 handoff 中的 outputs / acceptance / dependencies。

不要为了拆一个任务加载整个 Dida、全部记忆或全部 profile。

## 层级模型

读取 `references/hierarchy-and-dependencies.md`。

基本角色：

```text
project  → 长期结果 / 大项目
phase    → 一个明确阶段或主要交付物
task     → 可执行工作，有独立完成标准
block    → 某次实际执行时段，由日程规划阶段按需产生
```

Breakdown 默认只创建 `phase` 和 `task`。

不要在这里预先创建具体钟点 `block`；当用户要求排日程时交给 `dida-daily-planner`。

## 固定工作流程

### Step 1 — Resolve target

先通过 `dida-cli` 唯一解析目标父任务并读取当前状态。

确认：

- 当前目标是什么；
- 它现在是 `project / phase / task` 中哪一类；
- 已经有哪些 children；
- 哪些工作已经完成、正在进行或等待；
- 是否存在用户已经明确的交付物、截止或外部依赖。

已有结构能复用就复用，不要每次从零重建。

### Step 2 — Decide whether decomposition is needed

满足任一条件时通常需要继续拆：

- 一个节点包含多个可独立验收的交付物；
- 完成标准无法一句话判断；
- 内部存在明确前后依赖；
- 任务太大，无法作为一次或少数几次连续工作完成；
- 当前标题只是“继续做 / 完善 / 学一下 / 处理一下”这类无法直接执行的描述。

下面情况不要继续拆：

- 一个动作已经有单一输出和明确 DoD；
- 再拆只会得到机械步骤，例如“打开文件 / 修改 / 保存”；
- 小步骤更适合放在 task body checklist，而不是独立任务。

### Step 3 — Decompose from outputs, not activity words

优先按**可交付结果**拆，不按过程动作堆任务。

推荐：

```text
完成 RX 接口定义并确认握手语义
完成 RX RTL 并通过 Pre-TB Review
完成 RX Verification Plan
完成 RX TB 与回归
```

避免：

```text
看代码
想方案
写一点
再检查
继续优化
```

每个叶子任务至少包含：

- 一个明确动作；
- 一个主要输出；
- 简短完成标准 DoD；
- 必要时的依赖或阻塞条件。

### Step 4 — Keep the hierarchy shallow enough

默认优先：

```text
project
└─ phase
   └─ task
```

只有真实工程结构需要时才增加层级。

不要为了形式整齐给每个 project 强行创建同样数量的 phase，也不要为了“原子化”把一个自然任务拆成十几个子任务。

### Step 5 — Name from current context

命名规则由 `系统协议｜标签与任务正文` 决定。

如果当前协议要求 `父任务简称｜具体任务`：

- 父任务简称从当前父任务标题或已有同级命名中动态推导；
- 已有项目简称优先复用；
- 不在 Skill 中维护 1553B、AVRplus、PCIe 等固定映射表。

标题应该描述可执行动作或交付物，避免只有抽象名词。

### Step 6 — Add DoD and dependency

DoD 回答：

> 什么证据出现后，这个任务可以完成？

例如：

```text
## 完成标准
- 接口表已更新；
- 关键握手时序已确认；
- 不存在待确认的 Blocking 接口问题。
```

依赖只记录会真实影响执行顺序的关系。

- 必须完成前一任务才能开始 → hard finish-to-start；
- 等外部回复/物料/审批 → external wait；
- 只是推荐顺序 → 不要伪造成 hard dependency。

新增 task-based dependency 前检查环路。

### Step 7 — Route estimation

Breakdown 不自己猜时间。

对子任务结构稳定后调用 `dida-task-estimator`：

```text
Breakdown → 明确工作内容和 DoD
Estimator → 计算预计日历占用和置信度
```

如果 Estimator 判断某个叶子任务仍然明显过大或范围不清，回到 Breakdown 再拆一次。

一般优先让叶子任务落在可独立执行的尺度；`3h` 不是绝对硬上限，但超过这个量级且存在自然拆点时应优先继续拆。

### Step 8 — Preview vs write

如果用户只是讨论“应该怎么拆”，只给方案，不写 Dida。

如果用户明确要求“拆到滴答 / 帮我把这个任务拆开 / 直接改任务”等，则视为授权创建必要 children。

以下变化即使在 apply 模式也不要静默执行：

- 删除已有任务；
- 把已有重要任务移到别的项目；
- 改变硬截止；
- 大范围重命名现有任务树；
- 用新结构覆盖用户已经进行中的结构。

这些先给出最小变更方案再执行。

### Step 9 — Write and read back

通过 `dida-cli` 写入时：

1. 先读取当前对象；
2. 只创建/更新这次拆分需要的字段；
3. 保留用户已有正文、日期、标签和未知字段；
4. 防止重复创建同名同义 child；
5. 写入后重新读取 parent + children；
6. 检查层级、标题、DoD、依赖和估时字段是否实际保存。

## 完成 Gate

Breakdown 完成至少满足：

1. 父任务的主要交付物已经被 children 覆盖；
2. 每个叶子任务都有可判定 DoD；
3. 没有明显“继续做/完善一下”式不可执行叶子；
4. 必要依赖已经表达且无环；
5. 没有因为拆分制造重复任务；
6. 叶子任务已估时，或明确记录为何暂时无法估时；
7. 若实际写入 Dida，已完成 read-back 验证。

## 输出

默认只给用户：

- 新增 / 调整了哪些 phase 或 task；
- 关键依赖；
- 哪些任务因范围过大继续拆分；
- 仍存在的真正 blocker。

不要把完整 Planner block 或内部 JSON 全部打印出来。

## References

- `references/hierarchy-and-dependencies.md` — role、依赖和环路规则。
- `dida-task-estimator` — 叶子任务估时。
- `dida-cli` — 实际读写与 read-back。
