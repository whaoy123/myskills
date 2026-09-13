---
name: dida-task-breakdown
description: Decompose a Dida project, phase, or oversized task into executable child work with clear outputs, completion criteria, dependencies, and clean hierarchy. Use for 拆任务、细化项目、建立子任务、整理任务池、识别前置依赖. Read the current Dida tree and relevant project rules instead of hard-coding project structure. Route duration estimation to dida-task-estimator and schedule planning to dida-daily-planner. Prefer TickTick/滴答清单 MCP or connector tools for runtime reads/writes; use dida-cli only as fallback.
---

# Dida Task Breakdown

把一个过大的项目、阶段或任务拆成**可执行、可验收、依赖关系清楚**的子工作。

本 Skill 回答：

> 这件事应该拆成哪些工作，做到什么算完成，它们之间什么先做、什么后做。

它不负责估时和具体排钟点。

## 职责边界

负责：

- 判断当前节点应保持为 `project`、`phase` 还是拆成 `task`；
- 从最终产出和完成标准反推合理子任务；
- 保持父子层级清楚；
- 建立必要的 hard / soft / external-wait 依赖；
- 发现缺失前置工作和阻塞项；
- 用户授权时创建或调整子任务；
- 将稳定的叶子任务交给 `dida-task-estimator`。

不负责：

- 根据静态 Skill 硬编码当前用户项目树；
- 自己拍一个估时数字；
- 生成每天几点到几点的执行块；
- 机械创建大量微任务；
- 静默删除、改名、移动或重排用户已有重要任务。

## 运行态真值源

项目结构必须从当前 TickTick/滴答运行态读取。

优先读取：

1. 当前目标父任务及其正文/Planner 信息；
2. 已有 children 和同级节点；
3. 与拆分直接相关的标签/正文协议；
4. 依赖协议；
5. 会改变拆分结果的项目规则；
6. 已批准的工程 handoff（如果存在）。

有 MCP/连接器时直接使用它；没有时才使用 `dida-cli` fallback。

不要为了拆一个局部任务加载全部 Dida、全部 memory 或全部 profile。只有用户同时要求“全局整理/安排”时，才由 `dida-manager` 触发全量扫描 Gate。

## 层级模型

```text
project  → 长期结果 / 大项目
phase    → 一个明确阶段或主要交付物
task     → 可执行工作，有独立完成标准
block    → 某次实际执行时段，由 planner 按需产生
```

Breakdown 默认只创建 `phase` 和 `task`。

## 固定工作流程

### Step 1 — Resolve target

通过 MCP/连接器唯一解析目标父任务并读取当前状态：

- 当前目标是什么；
- 当前角色；
- 已有哪些 children；
- 哪些已完成、进行中、waiting；
- 是否已有截止、交付物或外部依赖。

已有结构能复用就复用，不从零重建。

### Step 2 — Decide whether decomposition is needed

满足任一条件时通常需要继续拆：

- 包含多个可独立验收交付物；
- 完成标准无法一句话判断；
- 内部存在明确前后依赖；
- 任务太大，无法作为少数自然执行单元完成；
- 标题只是“继续做 / 完善 / 学一下 / 处理一下”。

不要继续拆的情况：

- 一个动作已有单一输出和明确 DoD；
- 再拆只会得到“打开文件 / 修改 / 保存”这类机械步骤；
- 小步骤更适合 task body checklist。

### Step 3 — Decompose from outputs

按**可交付结果**拆，不按活动词堆任务。

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

每个叶子任务至少有：明确动作、主要输出、可判定 DoD，以及必要依赖/阻塞条件。

### Step 4 — Keep hierarchy shallow

默认优先：

```text
project
└─ phase
   └─ task
```

只有真实工程结构需要时才增加层级。

### Step 5 — Name from runtime context

命名规则从当前系统协议和现有同级任务动态读取。如果当前约定是 `父任务简称｜具体任务`，复用已有简称，不在 Skill 中维护固定项目映射表。

### Step 6 — Add DoD and dependency

DoD 回答“什么证据出现后可以完成”。

依赖只记录真正影响执行顺序的关系：

- 必须先完成 → hard finish-to-start；
- 等外部回复/物料/审批 → external wait；
- 只是推荐顺序 → 不伪造成 hard dependency。

新增依赖前检查环路。

### Step 7 — Route estimation

Breakdown 不自己猜时间：

```text
Breakdown → 明确内容和 DoD
Estimator → 计算 calendar occupancy + confidence
```

Estimator 判断范围仍然过大时，再回来拆。

### Step 8 — Preview vs write

用户只是讨论“应该怎么拆” → 只给方案。

用户明确说“拆到滴答 / 直接改任务” → 授权创建必要 children。

以下变化不要静默执行：删除已有任务、跨项目移动重要任务、改硬截止、大范围重命名、覆盖进行中的结构。

### Step 9 — Write and read back

应用时：

1. MCP/连接器读取当前对象；
2. 只创建/更新本次拆分需要的字段；
3. 保留用户已有正文、日期、标签和未知字段；
4. 防止重复创建同名同义 child；
5. 写入后重新读取 parent + children；
6. 检查层级、标题、DoD、依赖和估时信息是否保存。

只有没有 MCP/连接器时，才把同一流程交给 `dida-cli` fallback。

## 完成 Gate

1. 父任务主要交付物已被 children 覆盖；
2. 每个叶子任务有可判定 DoD；
3. 没有明显不可执行的“继续做/完善一下”叶子；
4. 必要依赖已表达且无环；
5. 没制造重复任务；
6. 叶子已估时，或明确为何暂时无法估；
7. 若写入 Dida，已 read-back 验证。

## References

- `references/hierarchy-and-dependencies.md`
- `dida-task-estimator`
- TickTick/滴答清单 MCP 或等价连接器 — 首选读写
- `dida-cli` — 无连接器环境下 fallback
