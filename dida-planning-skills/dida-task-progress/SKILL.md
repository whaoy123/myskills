---
name: dida-task-progress
description: Start, pause, wait, resume, update progress, complete, or delete Dida tasks; record focus and actual-time evidence; update parent progress; and append estimation-calibration comments. Use for execution updates such as “开始了”, “做到一半”, “等反馈”, “完成了”, or “删掉这个任务”. Do not replan an entire day unless requested.
---

# Dida task progress and completion

Keep current state in Dida fields/body and history in append-only comments. If completion reveals a durable reusable rule, route it to `$dida-planning-memory` rather than burying it only in the completion comment.

## State rules

Status labels are mutually exclusive:

- `状态/进行中`
- `状态/等待`
- `状态/暂停`

No state label means not started. Completion uses Dida native completion. There is no abandoned state; an unnecessary task may be deleted.

Use progress only from `0, 25, 50, 75, 90, 100`. Configuration and memory records are not executable work; update them only through their owner skills and exclude them from parent progress/completion gates. User statements override automated inference. AI may infer a level from completed children or conversation, but should avoid false precision.

## Start, pause, wait, resume

1. Resolve and read the task.
2. Check hard dependencies before starting.
3. Replace any existing state label with exactly one new state label.
4. Patch progress if supported by evidence.
5. Add a short event comment when the reason matters.
6. Read back.

## Block completion

Completing an execution block:

- completes that block;
- updates the owner task's weighted progress;
- does not automatically complete the owner;
- records the session's actual time when available.

## Task completion

1. Verify completion criteria and required children.
2. If required children remain, do not complete. If only optional children remain, ask.
3. Read Dida focus summaries.
4. Ask once for actual calendar time and any separately known focus, other active, AI-parallel, or end-to-end time.
5. If the user says unknown, prepare `included: false` and do not ask again.
6. Generate an idempotent completion event with the prior estimate preserved.
7. Complete the native Dida task first.
8. Append the completion comment; if this write fails, queue only the missing comment operation.
9. Update ancestors and the rebuildable local estimation index.

Never append a `completed` event before native completion succeeds; otherwise history could claim a completion that Dida rejected.

## Delete

Any task may be deleted when the user clearly requests it. Before deleting a task with children, comments, or focus records, state the impact. Verify afterward. Do not invent an abandoned substitute.

## Time accounting

Personal calendar occupancy and focus time cannot be double-counted across simultaneous tasks. The user may separately supply overlapping AI elapsed times; store them without treating them as personal occupancy.

## References

Read `references/progress-and-completion.md` for event fields and parent progress.
