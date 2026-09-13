---
name: dida-task-estimator
description: Estimate or re-estimate Dida executable work using task scope, familiarity, validation burden, AI participation, external uncertainty, and reliable historical samples. Produce calendar occupancy plus confidence, keep AI-parallel elapsed time separate, and route oversized or unclear work back to dida-task-breakdown. Prefer TickTick/滴答清单 MCP or connector tools for runtime data and writes; use dida-cli only as fallback.
---

# Dida Task Estimator

给 Dida 中的可执行任务估算**用户真正需要占用的日历时间**，并给出置信度。

估时来自：

```text
任务范围
+ 用户熟悉度
+ 验证/返工负担
+ AI 参与方式
+ 外部不确定性
+ 历史同类任务误差
```

而不是固定“任务类型 → 时间”的拍脑袋表。

## 职责边界

负责：首次估时、范围变化后的重估、remaining work、任务尺度判断、calendar occupancy、confidence 和校准依据。

不负责：给 project/phase/config/memory 估执行时间、创建具体钟点、把 AI 并行时间重复算入用户日历、给范围不清的工作伪造精确数字。

## Required reads

只读取真正相关的数据：

1. 目标 task 的标题、正文、DoD、依赖、progress 和已有 estimate；
2. `估时配置｜特征与风险缓冲`；
3. 会改变 familiarity 判断的相关项目/用户规则；
4. 可重建历史中与当前任务相似的可靠样本；
5. 重估时的 focus / completion / progress 证据。

有 TickTick/滴答清单 MCP 或连接器时优先从它读取；只有没有连接器时才用 `dida-cli` fallback。

不要为了估一个局部任务扫描全部 Dida；全量扫描属于 manager/planner 的全局规划 Gate。

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

类别只是特征之一，同类工作在不同熟悉度、范围和验证要求下可以差很多。

## 时间口径

预计时长默认表示用户真正占用的日历时间。

内部区分：

- `calendar_minutes`
- `focus_minutes`
- `other_active_minutes`
- `ai_parallel_minutes`
- `end_to_end_minutes`

`ai_parallel_minutes` 不得重复算进用户 calendar occupancy。

## 固定工作流程

### Step 1 — Check estimability

至少需要知道产出、DoD 和主要范围。

如果 `clarity=unclear`，可以估第一轮探索本身，但不要直接估整个未知项目；必要时退回 `dida-task-breakdown`。

### Step 2 — Choose base method

根据任务形态选择：

- **Direct / analogous**：小而熟悉、历史样本高度相似；
- **Bottom-up components**：几个明确组成部分；
- **PERT**：范围有明显不确定性；
- **Travel / queue**：路程、排队、现场处理等。

估时组件不一定要变成 Dida 子任务。

### Step 3 — Assess features

重点判断 familiarity、clarity、validation、ai_mode、tool_switches、external_uncertainty。不要为了让结果“更合理”事后反调特征。

### Step 4 — Use deterministic engine when useful

复杂估时优先使用：

```bash
python dida-planning-core/scripts/estimation_engine.py \
  --task task.json \
  --history history.json \
  --output estimate.json
```

脚本负责基础时间、特征修正、历史校正、风险覆盖、取整和 confidence；不要在 Skill 中再手算一套冲突公式。

### Step 5 — Historical correction

历史数据是校准证据，不是死规则。

只使用有可信 prior estimate、actual calendar time、可比 scope 且 `included=true` 的样本。

本地 history cache 只是可重建索引。与 TickTick task/comment/focus 事实冲突时，以远端运行态事实为准并重建索引。

### Step 6 — Check task size

如果估时结果说明任务明显包含多个独立可验收单元：

```text
Estimator → Breakdown → 拆分 → 分别重估
```

`3h` 只是实用提醒线，不是硬上限。依据是可独立验收性，不是单纯数字。

### Step 7 — Map to Dida

优先使用 TickTick/Dida native estimated duration；半小时标签如仍存在，只是展示层，不是估时真值源。

正文只写最有用的一行依据，不塞完整 feature JSON。

### Step 8 — Re-estimation

以下情况触发重估：

- DoD 或范围实质变化；
- remaining work 与旧估计明显不符；
- 新 blocker / external dependency；
- unfamiliar 流程已经跑通；
- 用户问“剩下多久”；
- 实际证据显示旧 estimate 失效。

进行中任务重新建模 remaining work，不使用 `原估时 × (1-progress)` 的机械公式。

### Step 9 — Write and verify

用户要求实际更新时：

1. 通过 MCP/连接器读取任务当前值；
2. 运行估时模型；
3. 只更新 estimate 和必要依据；
4. 保留其它字段；
5. read-back；
6. 检查 native duration、展示标签和正文依据无冲突。

只有没有 MCP/连接器时才交给 `dida-cli` fallback。

## Confidence

至少输出 `high / medium / low`。

低 confidence 不代表不能安排，而是 planner 应留更多 buffer；如果低置信来自范围未知，优先拆出明确探索任务。

## 完成 Gate

1. 时间口径是 calendar occupancy；
2. 没有重复计算 AI parallel；
3. 范围足够清楚或明确标记探索估计；
4. 使用合适 base method；
5. 有可用可靠历史时已使用；
6. 给出 confidence；
7. 过大/混合任务已回到 Breakdown 或说明为何保持整体；
8. 若写入 Dida，已 read-back。

## Output

默认简短：

```text
预计：1.5h
置信度：medium
依据：范围清楚，但需要完整验证；历史相似样本较少。
```
