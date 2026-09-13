---
name: dida-weekly-review
description: Review TickTick/Dida task-system health using a full unfinished-task inventory, completed work and focus records. Identify overdue work, hard-deadline and latest-safe-start risks, stalled parents, waiting dependencies, estimation performance, capacity, and the next-week task pool. Prefer TickTick/滴答清单 MCP or connector tools; use dida-cli only as fallback. Do not create a separate Markdown weekly plan or silently reschedule fixed commitments.
---

# Dida weekly review

Produce a source-backed weekly review from Dida. The review is also a **task-system safety check**: it must catch work whose due date may still be far away but whose latest safe start is already approaching.

## Source of truth

Current task state comes from TickTick/滴答清单 runtime data, preferably through the available MCP/connector. Model memory and conversation context can explain background but cannot establish inventory completeness.

Use `dida-cli` only when no first-class connector is available.

## Required reads

1. Determine local week boundaries in the user's current timezone.
2. **Enumerate all accessible projects/lists and all unfinished tasks, handling pagination.**
   - Do not limit the inventory to this week or next 7 days.
   - Include undated and far-future tasks in the risk pass.
   - Exclude config/memory records from workload counts, but keep project/phase context needed to interpret executable descendants.
3. Read completed tasks for the review week.
4. Read focus/actual-time records for the review week when available.
5. Read active parent/child structures and relevant planning-profile sections.
6. Read exact project memory only when a durable project rule materially affects the review; never load all memory by default.

## Risk pass

For every unfinished executable task that has, or may imply, a delivery constraint, check:

- hard deadline / due date;
- remaining estimate and confidence;
- hard/soft dependencies;
- external waits;
- review/procurement/fabrication/shipping/appointment/feedback lead times;
- future available capacity;
- **latest safe start**.

If the information needed to determine latest safe start is missing, record `start-risk: unknown`; do not classify the task as safe merely because its due date is far away.

Waiting tasks also matter: an external wait can consume delivery margin even when the waiting item itself is not executable.

## Review sections

1. **Outcome** — meaningful completed deliverables, not raw task count alone.
2. **Plan reliability** — planned versus completed/moved work, recurring misses and stale dates.
3. **Deadline / start risk** — overdue work, hard deadlines, latest-safe-start windows and unknown start risk.
4. **Stalled work** — active parents without progress, waiting dependencies, blocked tasks and orphans.
5. **Capacity** — actual focus/occupancy, important-task load, protected commitments and next-week realistic capacity.
6. **Estimation** — estimate vs actual evidence, systematic underestimation, confidence and buffer quality.
7. **Next-week pool** — recommended executable tasks, dependencies, why each belongs now, and what remains outside the week.

## Next-week planning rule

The next-week pool is selected only after the full risk pass.

A task may enter next week even if its due date is weeks away when:

- latest safe start falls in or before next week;
- it unlocks a critical downstream chain;
- an external lead time requires action now;
- waiting/approval risk needs to be started early.

Conversely, an overdue but low-value task does not automatically outrank every strategically important task; surface the conflict explicitly.

## Write behavior

- Do not create a separate weekly-plan Markdown document or summary task.
- Write schedule/date changes only when the user asks to apply the proposal.
- Use MCP/connector writes first and read back all applied changes.
- Do not automatically roll every unfinished daily task into the next week; re-evaluate it.
- Update incorrect progress, dependencies, estimates or profile rules only with evidence.
- Add comments when a review decision materially changes a task's interpretation or next action.
- Never silently move fixed commitments or hard deadlines.

If the user wants concrete clock blocks, route to `dida-daily-planner`. A weekly review itself normally stays at day/pool granularity.

## Weekly review preference

If the runtime profile specifies a preferred review day, use it. A repository example such as Saturday is only a default suggestion, not a hard-coded user fact and not a request to create an automation.

## Completion Gate

Before claiming the system is reviewed:

1. all unfinished tasks across all projects were included in the inventory pass;
2. pagination was handled;
3. undated and far-future work was checked for hidden start risk;
4. latest-safe-start or `start-risk: unknown` was considered for delivery-constrained work;
5. waiting dependencies and external lead time were checked;
6. next-week capacity was not oversold;
7. proposed writes are clearly separated from writes actually performed.

## Output

Lead with risks and decisions, then concise metrics. Explicitly call out:

- tasks that must start sooner than their due dates suggest;
- tasks whose start risk is unknown because information is missing;
- tasks intentionally not scheduled next week and why.

## References

Read `references/review-protocol.md` for metrics and checks. Use TickTick/滴答清单 MCP or an equivalent connector as the preferred runtime I/O path; `dida-cli` is fallback only.
