# Capture protocol

## Date semantics

- User says “周五必须交”：`hard_deadline` on the owning task.
- User says “周三下午做”：`execution_window` on an executable task. If the same outcome also owns a hard deadline, keep the deadline on the owner and create/use an execution child.
- User says “希望周五前弄完” without a true commitment：`target_date`.
- No date statement：`none`.

## Native Dida fields

Use native title, content, project/list, parent ID, tags, priority, start/due date, reminders, and recurrence when supported. Do not mirror native estimated duration in the Planner block.

## Minimal Planner block

```text
【Planner】
schema: 1
role: task
progress: 0
date_semantics: none
mobility: movable
privacy: normal
estimate_confidence: low
dependency_mode: all
dependencies:
【/Planner】
```

`estimate_confidence: low` means no reliable estimate yet; it does not require an estimated duration.

## Content boundary

Keep the durable conclusion, not the full conversation. Include enough context that a future planner can understand completion criteria without reopening the original chat.
