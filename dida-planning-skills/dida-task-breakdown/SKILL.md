---
name: dida-task-breakdown
description: Decompose a Dida parent task into phases, executable child tasks, completion criteria, and enforceable dependencies. Use when the user asks to 拆任务, 细化项目, 建立子任务, sequence work, or identify prerequisites. Do not choose daily time blocks or perform a full estimate review unless needed for decomposition.
---

# Dida task breakdown

Turn an oversized task into a usable four-level hierarchy while keeping every durable action in Dida.

## Required reads

1. Resolve and read the exact parent through `$dida-cli`.
2. Read its existing children to prevent duplicates. Treat `role: memory` children as project context only; never count or rewrite them as work breakdown items.
3. Read `系统协议｜标签与任务正文`, `系统协议｜依赖关系`, and only the exact parent project memories that constrain decomposition.
4. Use the shared dependency checker before writing dependency edges.

## Hierarchy

Use at most:

```text
project → phase/deliverable → executable task → execution block
```

- Do not create a separate Dida list for a project.
- Create all useful confirmed steps directly as child tasks; there is no candidate status.
- Prefer executable children with a visible deliverable and completion criterion.
- A child should normally fit one focused session or one coherent multi-session unit.

## Execution blocks

- If a task can finish in one sitting and does not itself own a hard deadline, the task itself becomes the time block later.
- If the owning task uses its Dida date as a hard deadline, create a child execution task/block even for one sitting; never overwrite the deadline with an execution window.
- Otherwise create block children only when the work must be advanced across multiple sessions.
- Completing a block increases the owning task's progress; it never automatically completes the owner.

## Dependencies

Support finish-to-start, start-to-start, not-before, external wait, all-of, any-of, soft, and hard dependencies.

- Hard unsatisfied dependencies prevent scheduling unless the user explicitly overrides.
- Soft dependencies allow scheduling with a warning.
- Detect self-dependencies and cycles before writing.
- Store task IDs, not titles, in the Planner block.
- Use the single state tag `状态/等待` when work is currently unable to proceed.

## Write sequence

1. Present a compact hierarchy when decomposition contains material judgment.
2. Create/update phases before their children.
3. Create children with parent IDs and minimal Planner blocks.
4. Patch dependencies after all required IDs exist.
5. Add a `[planner-event:v1]` decomposition comment to the parent.
6. Read back the complete child set and verify no duplicate or orphan exists.

## Completion rule

A parent with unfinished required children cannot be completed. If only optional children remain, ask before completing. This system has no “abandoned” state; unnecessary tasks may be deleted.

## References

Read `references/hierarchy-and-dependencies.md` for decomposition and dependency details.
