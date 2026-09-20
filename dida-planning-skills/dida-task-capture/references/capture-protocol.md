# Capture protocol

## Date semantics

- User says “周五必须交”：`hard_deadline` on the owning task.
- User says “希望周五前弄完” without a true commitment：`target_date`.
- User says “周三下午做”：this is an execution intention, not a Planner date semantic. Keep `date_semantics: none`; only create a native Dida reminder/date when the user explicitly asks for that reminder behavior.
- No reliable date statement：`none`.

`execution_window` is legacy-read-only and must not be written by capture.

## Native Dida fields

Use native title, content, project/list, parent ID, tags, priority, start/due date, reminders, and recurrence when the user actually requests or supplies them and the connector supports them. Do not mirror native estimated duration in the Planner block.

## Minimal Planner block

```text
【Planner】
schema: 1
role: task
progress: 0
date_semantics: none
privacy: normal
estimate_confidence: low
dependency_mode: all
dependencies:
【/Planner】
```

`estimate_confidence: low` means no reliable estimate yet; it does not require an estimated duration.

## Content boundary

Keep the durable conclusion, not the full conversation. Include enough context that a future planner can understand completion criteria without reopening the original chat.
