---
name: dida-task-progress
description: Record actual Dida task progress, completion, waits and human effort; assess a current weekly delivery slice against its criteria without turning partial progress into parent/native completion. Prefer MCP/connectors and read-write-read-back; never invent timestamps, effort, or measured results.
---

# 任务事实与当前验收

Progress owns **point-in-time facts**: what changed on a task now, what evidence exists, whether the current weekly slice presently meets its acceptance contract, and how much human effort was actually spent. Weekly review owns the end-of-week aggregate audit, archive and rollover decision.

## 读取与更新

唯一解析 task，读取自然语言、Planner、required children、DoD 和本周合同。只修改本次陈述涉及的字段。

用户最新陈述优先于自动推断。状态标签沿运行态约定，完成使用原生状态；不能因 status 与旧 completedTime 矛盾就猜已完成。

有 MCP/连接器就优先用它；超时先查结果，写后回读。

## 进度

记录“完成了什么 / 剩什么 / 被什么阻塞”。百分比只是摘要，不生成假精度；旧估时不再适用时交给 estimator 重估。

开始/暂停/等待/恢复保留原因和解除条件。硬依赖未满足不能当作已可执行。进度更新不自动重排整周，也不重新选择核心周交付物。

## 当前周交付切片验收

1. 对照当前 owner 上的本周范围和全部验收条件。
2. 明确的用户完成确认可作为 `user_report`，保留原意。
3. 工具读取/测试结果和用户陈述分开标来源；不能把未看过的文件说成已核验。
4. 当前可判定 `delivered / not_delivered / blocked / cancelled / unverified`。
5. 周交付只完成了大任务的切片时，原生大任务继续未完成。

活动陈述“干了三小时”“看了一半”不自动成为 delivered。周末跨全部核心交付物的验收、原因归因、归档和下周处理交给 `dida-weekly-review`。

## 原生任务完成

完整 DoD 与 required children 满足，或用户明确确认这一完整任务已经完成，才执行 native complete。存在矛盾时指出，不越过剩余条件。

先原生完成成功，再追加 completed 事件；不能把失败的写入记成完成。周合同验收结果可以独立记录，但不自动传播为父项目完成。

## 实际投入记录

`actual_effort_minutes` = 用户为该任务实际投入的人工工作量，包括专注工作和必要的主动沟通/操作，但不包含纯等待，也不等于某个日历时间段的长度。

用户说约 3 小时就记录约 180 分钟及不确定性；不知道起止时间时不虚构时间戳。“早九到晚十一”只是端到端经过时间，不能自动记成 14 小时投入。

可分开记录 `focus_minutes`、`other_active_minutes`、`ai_parallel_minutes` 和 `end_to_end_minutes`；不要重复计数。新事件写 `actual_effort_minutes`；旧事件中的 `calendar_minutes` 只作历史读取兼容，不再新写。

不因消息时间间隔推算用户持续工作。保留 prior estimate 与实际证据，供 estimator 校准。

## 范围改变和换周

不能把旧合同改小后回称本周已交付。先保存原合同与变更原因，再记录新的约定；重大替换需用户确认。

换周归档由 weekly-review 处理，历史成功后才清旧周标记。默认不滚动日期、不另建周计划任务。

## 安全写回

读取 → 比较 → 仅改必要字段 → 写入 → 回读。

保留未知 Planner 字段、正文、清单项、父任务与硬截止。CHECKLIST 使用实际可见的 desc/items。删除有子任务/历史的任务前说明影响。

## References

- `references/progress-and-completion.md`
- `dida-weekly-delivery`
- `dida-weekly-review`
