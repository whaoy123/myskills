---
name: dida-daily-planner
description: Build, revise, and write a Dida daily schedule with non-overlapping time blocks, fixed/protected/movable mobility, dependency checks, current-location timezone, weather task update, capacity, breaks, and rescheduling. Use for “安排今天/明天”, “重新排日程”, or “看看今天做什么”. Do not modify hard deadlines or decide how to handle an already-started task that no longer fits without asking.
---

# Dida daily planner

Create a real Dida schedule, not a separate Markdown daily plan.

## Runtime requirement

- All Dida CLI reads and writes for this skill must run outside the default sandbox, using an approved non-sandbox execution path.
- The Dida CLI stores its access token under the user's profile (`%USERPROFILE%\\.config\\dida-cli\\config.json`); a sandboxed run may falsely report that the account is unauthenticated.
- If non-sandbox execution is unavailable or rejected, report the execution blocker. Do not infer that the user is logged out or ask them to re-authenticate solely from the sandboxed status result.

## Required reads

1. Determine current date, location timezone, and requested planning date.
2. Read Dida tasks/events for that date, nearby hard deadlines, current focus/started state, and unscheduled candidates. Read the open-task set carrying the exact tag `今天` for reconciliation. Exclude `role: config|memory_category|memory` from capacity and scheduling. Treat `project` as deadline/context only and `phase` as hierarchy context only; only `task`/`block` (or a verified unlabelled leaf) may occupy personal capacity.
3. Read only `规划偏好｜作息与容量`, `规划偏好｜日程移动权限`, and `估时配置｜特征与风险缓冲`. Do not load general memory unless an exact task references a scheduling constraint not already in profile/task data.
4. Update the weather task for the current day when making the daily plan.
5. Run dependency checks and the shared scheduling engine.

## Mobility

- `fixed`: never move; meetings, appointments, travel, and already-started tasks.
- `protected`: move within the same day but do not delete, shorten, or move across days; fitness defaults here.
- `movable`: may move in time or date automatically.
- Repeating tasks carry their own mobility; recurrence alone does not imply fixed.

## Capacity

Account for lunch, nap, commute, focus breaks, and task-switch buffer even when they are not Dida tasks. Personal calendar occupancy must never overlap. AI-parallel elapsed time may overlap but cannot duplicate personal occupancy or focus minutes.

## Scheduling rules

- A project with a long hard-deadline range may be returned by a date query. Do not schedule it or display it as an execution row. Show only the target-week `phase` and its in-scope descendants; use the project solely as a breadcrumb and deadline context.
- Never place a weekly execution window on a project. Reuse or create a dated weekly phase under it; that phase may have any number of selected child tasks.
- Use the exact Dida tag `今天` as the daily execution-view marker. After selecting today's executable tasks, add `今天` to those `task`/`block` records and remove it from open executable records no longer selected today; preserve all other tags.
- Do not put `今天` on a `project`, weekly `phase`, configuration/memory record, weather reminder, or other non-work context. The daily view should filter by the native tag `今天` (normally with open status), not by every task whose date range happens to overlap today.
- Use Dida native start/end times for actual work blocks.
- A one-session task is its own block only when its Dida dates do not represent a hard deadline.
- If a task owns a hard deadline, schedule a child execution task/block so the deadline remains intact.
- Multi-session work uses explicit block children created jointly with the user or by breakdown logic.
- Re-evaluate unfinished tasks during the next planning session; do not auto-roll them forward blindly.
- Never change a hard deadline.
- If an already-started task no longer fits, ask whether to extend, split, or move the remainder.
- Default to no work after 21:00 and light/no work Sunday; ask before breaking these rules.
- Limit the day to at most three important tasks unless the user deliberately overrides.

## Weather

At about 08:30, update today's recurring weather instance title, for example `今日天气：24–31℃，下午有雨，记得带伞`. Prefer a single-instance edit. If the CLI cannot safely edit one occurrence, update a long-lived weather task's title, body, and date instead.

## Write sequence

1. Show a concise preview only when material judgment or a fixed conflict exists.
2. Write fixed/protected-safe changes first, then movable tasks.
3. Re-read the day and verify no personal occupancy overlaps and no hard deadline changed.
4. Report scheduled, moved, and unscheduled tasks separately.

## References

Read `references/daily-rules.md` and `references/weather.md` when those branches apply.
