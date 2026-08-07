---
name: dida-task-capture
description: Capture a new task, idea, reminder, or project into 滴答清单, including inbox entry, concise title, useful body, parent relationship, list selection, and privacy-summary handling. Use for “记一下”, “加到滴答”, “放进收集箱”, or creating a new task. Do not deeply decompose, estimate, or schedule unless the user also invokes those workflows.
---

# Dida task capture

Create a clean Dida record without turning capture into a full planning session.

## Required reads

- Use `$dida-cli` to inspect available lists and possible parent tasks.
- Read only `系统协议｜标签与任务正文` and, when relevant, the current task's parent.
- Do not read the whole planning profile, memory store, or estimation history. Read only exact project memory when it can change capture content.

## Capture flow

1. Extract the smallest useful title: action + object, normally under 25 Chinese characters.
2. Determine destination:
   - Explicit list or parent wins.
   - Clear domain may be placed in its domain list.
   - Ambiguous items go to Dida inbox; do not auto-organize the inbox.
3. Decide role: `project`, `phase`, or `task`. Ordinary captures default to `task`. Never create work through a memory category; memory records belong to `$dida-planning-memory`.
4. Write current context, completion criteria, links, paths, decisions, and unresolved points. Keep natural text near 300 Chinese characters and below 500 when practical.
5. If the user says only a summary may be stored, set `privacy: summary_only` and omit sensitive details.
6. Add a minimal Planner block. Do not invent dates, dependencies, priority, estimate, reminders, recurrence, or progress.
7. If the user also states a durable project rule or explicitly asks to remember something, route that fact to `$dida-planning-memory`; do not duplicate it in every new task.
8. Create through `$dida-cli` and read back.

## Defaults

- `progress: 0`
- `date_semantics: none` unless the user supplied a real date meaning.
- `mobility: movable` for ordinary work; `fixed` for explicit meetings/appointments/travel; `protected` only for protected personal commitments such as fitness.
- No status tag for a new, unstarted task.
- Dida priority remains none unless urgency is clear or explicitly supplied.

## Parent and hierarchy

A long project is a parent task inside a domain list, not a new list. If an exact parent cannot be resolved, create in the correct list and report that parent assignment remains unresolved rather than guessing.

## Inbox rule

Only classify existing inbox items when the user explicitly says to organize the inbox. Capture alone never triggers bulk inbox cleanup.

## Output

Report the saved title, list, parent, date meaning, and any omitted uncertainty. Do not dump raw JSON.

## References

Read `references/capture-protocol.md` for field mapping and `references/examples.md` only when an example is needed.
