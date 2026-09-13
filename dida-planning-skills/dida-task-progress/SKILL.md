---
name: dida-task-progress
description: Start, pause, wait, resume, update progress, complete, or delete Dida tasks; record focus and actual-time evidence; update parent progress; and append estimation-calibration comments. Use for execution updates such as “开始了”, “做到一半”, “等反馈”, “完成了”, “花了两个点”, or “删掉这个任务”. Prefer TickTick/滴答清单 MCP or connector tools for runtime reads/writes; use dida-cli only as fallback. Do not replan an entire day unless requested.
---

# Dida task progress and completion

把用户实际发生的执行事实写回 Dida：**当前状态属于任务，历史证据属于评论/focus，实际耗时用于后续估时校准。**

如果完成过程中暴露出稳定、可复用的长期规则，才路由到 `dida-planning-memory`；不要把普通进度事实塞进 memory。

## Runtime I/O

有 TickTick/滴答清单 MCP 或一等连接器时，优先使用它完成：

- task read/update/complete/delete；
- comment；
- focus/actual-time 记录；
- parent/child read-back。

只有没有连接器时才使用 `dida-cli` fallback。

所有写操作遵循：

```text
resolve/read → apply intended change → read-back → report actual saved state
```

超时或结果不明确时先读回，不盲目重复写。

## State rules

如果当前运行态协议使用状态标签，状态互斥：

- `状态/进行中`
- `状态/等待`
- `状态/暂停`

No state label 表示未开始；完成使用 Dida native completion。

如果当前连接器/运行态支持更直接的状态字段，以运行态协议为准，不为了兼容旧标签制造重复状态源。

Progress 只在有证据时更新。用户明确陈述优先于自动推断；避免虚假精度。

配置和 memory 记录不是 executable work，不参与父任务进度/完成 Gate。

## Start / pause / wait / resume

1. 唯一解析并读取任务；
2. 开始前检查 hard dependency；
3. 更新当前状态；
4. 有证据时更新 progress；
5. reason 有长期执行意义时加一条短 comment；
6. read-back。

`wait` 应记录等待对象/条件；如果等待可能吞噬交付余量，后续 planner/review 应重新评估 `latest_safe_start`。

## Progress update

用户说“做到一半”“主体做完了但还没验证”等时：

- 优先记录实际完成的交付物/剩余 DoD；
- progress 数字只是摘要，不替代 remaining work 描述；
- 如果范围改变导致旧 estimate 失效，调用 `dida-task-estimator` 估 remaining work。

不要因为一个子步骤完成就误把整个任务完成。

## Block completion

完成 execution block：

- 完成该 block；
- 更新 owner task 的合理进度；
- 不自动完成 owner；
- 有实际时间时记录本次 session evidence。

## Task completion

1. 读取任务、required children 和 DoD；
2. 若 required children 未完成，不直接 complete；
3. 读取可用 focus/actual-time evidence；
4. 用户报告“花了 X 个点/小时”时按用户陈述记录 calendar/focus 语义；若语义不清且影响统计，只做最小必要澄清；
5. 保存 prior estimate 作为校准证据；
6. 先完成 native Dida task；
7. 再追加 completion / actual-time comment；
8. read-back；
9. 更新必要 ancestors 和可重建估时索引。

永远不要在 native completion 成功前先写一个“completed”历史事件。

## Actual-time accounting

区分：

- `calendar_minutes`：用户真正被占用的日历时间；
- `focus_minutes`：专注时间；
- `other_active_minutes`：沟通、切工具、现场等待但人在参与；
- `ai_parallel_minutes`：AI 可独立运行、用户可以同时干别的；
- `end_to_end_minutes`：墙钟总跨度。

同一用户同时发生的 calendar occupancy 不可跨任务重复计算。AI parallel 可以与用户工作重叠，但不能再算一次用户占用。

当用户说“两个点/三个点”且当前对话约定其含义为小时，可以按对应小时记录；不要制造比用户陈述更高的时间精度。

## Delete

用户明确要求删除时可以删除唯一解析的任务。

如果该任务有 children、重要 comments 或 focus history，删除前说明影响。删除后 read-back/刷新确认。

## Interaction with planning

本 Skill 负责**事实更新**，不自动重排整天/整周。

但是以下变化应触发“需要重新规划”的信号：

- 实际耗时显著超出 estimate；
- 新 external wait；
- hard dependency 发生变化；
- scope/DoD 增大；
- 任务完成后释放了大量容量；
- latest-safe-start 风险可能变化。

只有用户要求重新安排时，再路由到 `dida-manager` / `dida-daily-planner`。

## Completion Gate

一次进度操作完成至少满足：

1. 修改的是唯一解析的正确任务；
2. 状态/progress 与用户陈述一致；
3. actual time 没有重复计入 calendar occupancy；
4. prior estimate 没被无痕覆盖；
5. parent completion 没有越过 required children；
6. 写操作已经 read-back；
7. 若 estimate 已明显失效，remaining work 已重估或明确标记需要重估。

## References

Read `references/progress-and-completion.md` for event fields and parent progress. TickTick/滴答清单 MCP or an equivalent connector is the preferred runtime I/O layer; `dida-cli` is fallback only.
