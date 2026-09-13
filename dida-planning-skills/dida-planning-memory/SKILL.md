---
name: dida-planning-memory
description: Save, retrieve, update, or forget durable planning-related rules and background without duplicating current task state or stable scheduling profile settings. Use for explicit long-term project rules, tool/environment facts, reusable workflow conventions, and cross-project agreements. Current task facts belong to TickTick tasks; stable planning preferences belong to dida-planning-profile. Prefer TickTick/滴答清单 MCP or connector tools for storage; use dida-cli only as fallback.
---

# Dida planning memory

Maintain only the durable information that materially improves future planning. This Skill is deliberately narrow: **it is not a second task database and not a substitute for TickTick task inventory.**

## Authority boundary

- Current task existence, status, dates, parent/child relationships, progress and completion state → owning TickTick task.
- Stable scheduling/energy/capacity/mobility preferences → `dida-planning-profile`.
- Estimate and actual-time evidence → `dida-task-estimator` / `dida-task-progress` / focus records.
- Cross-project durable rule, tool/environment fact, reusable workflow convention or long-lived agreement → this Skill.
- Project-specific durable rule → explicit memory/config record scoped to that project, not a duplicate of live task state.

Model-native memory may provide background, but higher-level planning Skills must never use it as proof that the current task list is complete.

## Storage path

When a TickTick/滴答清单 MCP or connector is available, use it for searching, creating, updating and verifying durable memory records. `dida-cli` is used only when no connector is available.

Do not create a parallel editable Markdown/SQLite memory database.

## Save policy

1. Explicit “记住/保存/加入记忆” request → route to the correct owner and save if appropriate.
2. Stable low-sensitivity fact that is clearly durable and future-useful → may be saved when the environment/policy permits, but report what was stored.
3. Ambiguous persistence intent → ask once before saving.
4. Inferred pattern, uncertain stability or possible conflict → do not silently persist.
5. Temporary details, one-day exceptions, ordinary task status, copied text being transformed, and facts already owned by a task/profile → do not store here.
6. Sensitive personal facts → store only on explicit request and minimize wording.

## Ownership routing

Before every write, ask “哪个对象才是真正 owner？”

- “以后周三晚上不要安排科研” → profile
- “这个 PCB 已经布完线” → PCB task/progress
- “这个项目所有原始设计方案都不能覆盖，只改修改稿” → durable project rule
- “Windows + WSL，某工具只在 WSL 中可用” → tool/environment memory when genuinely reusable
- “今天做到 22:00” → one-day exception, not memory

Never duplicate one fact across owners just for convenience.

## Recommended storage structure

If the existing runtime schema uses `系统配置` memory categories, keep using them:

- `长期记忆｜项目规则`
- `长期记忆｜工具与环境`
- `长期记忆｜工作方式`
- `长期记忆｜通用约定`

Each memory should be a small independent NOTE/task record with:

- concise `记忆｜...` title;
- current fact and applicability;
- no execution date or estimate;
- explicit scope/source/confidence where the runtime schema supports it;
- change history in comments rather than duplicate records.

This structure is optional compatibility with the existing system; do not create memory categories inside business task trees.

## Save / update

1. Search only the relevant category/project scope for semantically equivalent records.
2. If equivalent, update the existing record rather than create a duplicate.
3. If contradicted, preserve a short change-history comment when useful, then update the current fact.
4. Write through MCP/connector and read back.
5. Only after successful read-back report the durable rule as stored.

## Retrieve

Retrieve the smallest relevant scope. Ordinary task operations should not load all memory categories.

When a memory rule materially changes a plan, higher-level Skills may mention it, but the live task inventory still comes from TickTick.

## Forget / change

Resolve the exact owner first.

- If the information is owned by a live task → update/delete there.
- If owned by profile → route to `dida-planning-profile`.
- If owned by this Skill → update/delete the exact durable memory record.

Do not “forget” a fact by merely adding a contradictory memory.

## Global planning interaction

This Skill does **not** participate in completeness checks by returning “everything remembered”. For global daily/weekly planning, `dida-manager` / `dida-daily-planner` must first enumerate all unfinished TickTick tasks. Memory is loaded only afterward when a specific project rule is relevant.

## Initialize

If the runtime already has memory categories, reuse them. If initialization is genuinely needed:

1. resolve/create the configured system list through MCP/connector;
2. create only missing category parents;
3. preserve user-edited category notes;
4. use CLI only as fallback when no connector is available.

## References

Read `references/memory-policy.md` for policy boundaries and `references/memory-format.md` for record fields and examples.
