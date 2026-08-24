---
name: dida-task-estimator
description: Estimate or re-estimate Dida executable work using task scope, familiarity, validation burden, AI participation, external uncertainty, and reliable historical samples. Use for 大概多久、估时、重新估计剩余时间、任务大小判断. Produce calendar occupancy plus confidence, keep AI-parallel elapsed time separate, and route oversized or unclear work back to dida-task-breakdown instead of inventing a precise tag.
---

# Dida Task Estimator

给 Dida 中的可执行任务估算**用户真正需要占用的日历时间**，并给出置信度。

本 Skill 不靠固定“任务类型 → 时间”的经验表直接拍数字。估时应来自：

```text
任务范围
+ 用户熟悉度
+ 验证/返工负担
+ AI 参与方式
+ 外部不确定性
+ 历史同类任务误差
```

## 职责边界

本 Skill 负责：

- 首次估时；
- 任务范围变化后的重新估时；
- 执行一部分后的剩余时间估计；
- 判断任务是否过大、是否应该退回 Breakdown；
- 计算日历占用与置信度；
- 记录用于后续校准的估时依据。

本 Skill 不负责：

- 把项目/phase/config/memory 当成可执行任务估时；
- 创建具体开始/结束钟点；
- 把 AI 后台/并行运行时间全部算成用户日历占用；
- 为范围不清的工作给出看起来精确的确定时间；
- 用静态示例覆盖已经存在的历史数据和用户配置。

## Required reads

对一个普通任务，只读取真正相关的内容：

1. 目标 task 的标题、正文、DoD、依赖、当前 progress 和已有 estimate；
2. `估时配置｜特征与风险缓冲`；
3. 如果会改变熟悉度判断，读取相关用户/项目记忆；
4. rebuildable estimation history 中与当前任务相似的可靠样本；
5. 重新估时时读取该任务已有 focus / completion / progress 证据。

不要为了估一个任务加载整个 Dida 历史。

## Estimation model

读取：

- `references/estimation-model.md`
- `references/history-format.md`

规范化特征至少包括：

```text
category
mode
familiarity: familiar | partial | unfamiliar
clarity: clear | partial | unclear
output_scale
validation: low | medium | high
ai_mode: none | assist | parallel | review_only
tool_switches
external_uncertainty: low | medium | high
```

类别只是特征之一，不允许写成：

```text
写文档 = 1h
RTL = 2h
PCB = 3h
```

同一个类别在不同熟悉度、范围、验证要求下可以差很多。

## 时间口径

Dida 的预计时长默认表示：

> 用户为完成这个任务实际需要占用的日历时间，包含正常的短切换/短休息成本。

内部必须区分：

- `calendar_minutes`：真正占用用户日程的时间；
- `focus_minutes`：专注投入；
- `other_active_minutes`：沟通、切工具、等待但仍需人在场等主动时间；
- `ai_parallel_minutes`：AI 可独立运行且用户可以同时做别的工作的时间；
- `end_to_end_minutes`：从开始到全部结束的墙钟时间。

`ai_parallel_minutes` 不得重复算进用户日历占用。

## 固定工作流程

### Step 1 — Check estimability

先判断任务是否已经可以估。

至少需要知道：

- 要产出什么；
- 做到什么算完成；
- 主要范围是否可见。

如果 `clarity=unclear`，并且探索本身会决定最终工作量：

- 可以估“第一轮探索/调研”本身；
- 不要直接估整个未知项目；
- 必要时退回 `dida-task-breakdown` 把探索和实现拆开。

### Step 2 — Choose base method

根据任务形态选择基础估时方式。

#### Direct / analogous

适合小而熟悉、已有高度相似历史样本的任务。

#### Bottom-up components

适合可以拆成几个明确组成部分的任务，例如：

```text
理解现状 20m
修改 40m
验证 30m
整理结果 10m
```

这些是估时组件，不一定要变成 Dida 子任务。

#### PERT

范围有不确定性时给：

```text
optimistic
most_likely
pessimistic
```

由确定性脚本计算 Beta-PERT，而不是人工取平均。

#### Travel / queue

路程、排队、办事类任务拆为：

```text
去程 + 等待 + 现场处理 + 回程 + 不确定性
```

### Step 3 — Assess features

根据当前任务和用户真实上下文设置特征。

重点判断：

- `familiarity`：工具和流程是否已经做过；
- `clarity`：DoD 和范围是否清楚；
- `validation`：是否要仿真、复核、跑测试、交叉检查；
- `ai_mode`：AI 是辅助、并行执行还是主要起草后用户审核；
- `external_uncertainty`：是否依赖设备、网络、他人回复、排队或未知环境。

不要为了让结果“更合理”事后反调特征。

### Step 4 — Use deterministic engine

正式估时优先使用：

```bash
python dida-planning-core/scripts/estimation_engine.py \
  --task task.json \
  --history history.json \
  --output estimate.json
```

脚本负责：

- component / PERT 基础时间；
- familiarity / clarity / validation / AI mode 等特征修正；
- 工具切换和外部不确定性；
- 相似历史样本校正；
- 风险覆盖；
- 时间取整；
- confidence。

不要在 Skill 里重新手算另一套公式。

### Step 5 — Historical correction

历史数据是校准证据，不是死规则。

只使用：

- 有真实 prior estimate；
- actual calendar time 可信；
- scope 与当前任务可比；
- `included=true` 的样本。

本地 history cache 只是可重建索引。与 Dida comment / focus 事实冲突时，以 Dida 为准并重新构建索引。

样本少时允许使用，但必须向无修正方向收缩并降低 confidence，不要因为一次历史任务超时就永久把某类工作翻倍。

### Step 6 — Check task size

估时完成后检查任务尺度。

如果任务明显超过单个自然执行单元，而且内部存在独立产出或依赖：

```text
Estimator → dida-task-breakdown → 拆分 → 分别重估
```

`3h` 可以作为一个实用提醒线，但不是硬性上限。

- 4h 的连续实验可能仍是一个自然任务；
- 3h 的“调研 + 设计 + 编码 + 验证”通常应该拆。

判断依据是可独立验收性，不是单纯数字。

### Step 7 — Map to Dida

优先使用 Dida native estimated duration。

如果当前系统协议仍保留半小时标签，则同步对应可见标签，但**标签只是展示层，不是估时真值源**。

不要维护一张静态“典型场景 → 标签”表作为核心算法。

估时依据只写一行最有用的信息，例如：

```text
## 估时依据
90min；范围清楚，流程部分熟悉，需要一次完整仿真验证；历史同类样本 3 个，置信度 medium。
```

不要把全部内部 feature JSON 塞进任务正文。

## Re-estimation

以下情况触发重新估时：

- DoD 或范围发生实质变化；
- 完成一部分后剩余工作与原估计明显不同；
- 新 blocker / 外部依赖出现；
- 原来 unfamiliar 的流程已经跑通；
- 用户明确说“剩下大概要多久”；
- 实际执行证据显示旧估计已经失效。

重新估时必须保留原始 prior estimate 作为历史证据，不要覆盖得无法追踪。

对于进行中任务：

> 估计剩余工作，不要简单用 `原估时 × (1-progress)`。

先看已经完成了哪些部分、剩余 DoD 是什么，再重新建模。

## Confidence

输出至少分：

- `high`
- `medium`
- `low`

高置信通常意味着：范围清楚、流程熟悉、存在多个相似可靠样本。

低置信通常意味着：范围不清、新领域、外部依赖多、没有可比历史数据。

低 confidence 不等于不能安排；它意味着 Daily Planner 应留更多弹性，而不是伪装成一个精确数字。

## Write and verify

用户要求实际更新 Dida 时：

1. `dida-cli` 读取任务当前值；
2. 运行估时模型；
3. 仅更新 estimate 及必要的估时依据；
4. 保留原任务其它字段；
5. read back；
6. 确认 native duration、展示标签和正文依据没有互相冲突。

## 完成 Gate

只有满足以下条件才算估时完成：

1. 时间口径是 calendar occupancy，不与 AI parallel 重复；
2. 任务范围足够清楚，或明确标记为低置信探索估计；
3. 使用了合适的 base method；
4. 可用时已使用可靠历史样本；
5. 给出 confidence；
6. 过大/混合任务已回到 Breakdown 或明确说明为何保持整体；
7. 若写入 Dida，已 read-back 验证。

## Output

默认简短输出：

```text
预计：1.5h
置信度：medium
依据：范围清楚，但需要完整验证；历史相似样本较少。
```

用户只问“大概要多久”时，不展开内部模型。
