---
name: dida-weekly-review
description: Review a week of Dida tasks and focus records, identify overdue and deadline risks, stalled parents, waiting dependencies, estimation performance, capacity, and the next-week task pool. Use for 周复盘, 下周规划, or checking project/task-system health. Do not create a separate Markdown weekly plan or silently reschedule fixed commitments.
---

# Dida weekly review

Produce a source-backed weekly review from Dida and write only durable task/profile changes back to Dida.

## Required reads

1. Determine the local week boundaries in the user's current timezone.
2. Read completed, incomplete, overdue, waiting, and upcoming-hard-deadline work tasks. Exclude `role: config|memory_category|memory` from task counts, capacity, overdue, and completion metrics.
3. Read focus records in windows supported by the installed CLI.
4. Read parent/child structures for active projects and the relevant configuration NOTE sections.
5. Read the rebuildable estimation index or reconstruct missing samples from comments. Review memory only for stale/conflicting rules explicitly implicated by the week; never dump the whole memory store.

## Review sections

1. **Outcome:** meaningful completed deliverables, not raw task count alone.
2. **Plan reliability:** planned versus completed/moved work and recurring misses.
3. **Deadline risk:** hard deadlines, remaining estimated occupancy, and last viable execution days.
4. **Stalled work:** active parents without progress, waiting dependencies, and orphan tasks.
5. **Capacity:** focus/occupancy patterns, important-task load, and protected commitments.
6. **Estimation:** absolute error, typical multiplicative error, underestimation rate, coverage, and buffer cost.
7. **Next-week pool:** recommended tasks, dependencies, and why each fits.

## Write behavior

- Do not create a weekly-plan document or summary task.
- Write date/time changes only when the user asks to apply the proposed next-week plan.
- Update incorrect progress, dependencies, estimates, or profile rules only with supporting evidence.
- Add comments to affected tasks when a review decision materially changes them.
- Keep unfinished daily tasks in the pool for fresh judgment; do not auto-roll all forward.

## Saturday preference

The default weekly review day is Saturday. This is a preference, not a requirement to create an automation unless the user requests one.

## Output

Lead with risks and decisions, then concise metrics. Clearly separate observations from proposed writes and completed writes.

## References

Read `references/review-protocol.md` for metrics and checks.
