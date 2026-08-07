---
name: dida-planning-memory
description: Save, retrieve, update, or forget durable planning-related memory in Dida without duplicating task state or profile settings. Use when the user says 记住/保存到记忆/忘掉, when a directly stated stable low-sensitivity fact will materially improve future work, or when another Dida skill needs project rules, tool/environment facts, workflow conventions, or cross-project agreements. Route planning preferences to dida-planning-profile and task-local facts to the owning task.
---

# Dida planning memory

Maintain durable memory as small Dida records. Dida remains the only business source of truth; never create a parallel editable Markdown memory database.

## Ownership routing

Before saving, choose the true owner:

- Stable scheduling, energy, fitness, mobility, timezone, or planning behavior → `$dida-planning-profile`.
- Current task/project context, progress, completion criteria, or decisions → owning task body/comment.
- Estimate samples and timing evidence → `$dida-task-estimator` / `$dida-task-progress`.
- Cross-project rule, tool/environment fact, reusable workflow, or durable agreement → this skill.
- Project-specific durable rule → a `role: memory` child under the exact project parent.

Never duplicate one fact across owners merely for convenience.

## Save policy

1. Explicit “记住/保存/加入记忆” request: save it. If sensitive, store only the minimum wording requested and set `privacy: summary_only` when appropriate.
2. If wording is ambiguous about whether the user wants persistence, ask once before saving.
3. Explicit “忘掉/删除这条记忆”: resolve the exact owner and delete/update it. Do not merely add a contradictory memory.
4. Directly stated, stable, future-useful, low-sensitivity fact: may be saved automatically, then report what and where was saved.
5. Inferred pattern, uncertain stability, or possible conflict: ask before saving.
6. Do not save temporary details, trivial facts, one-day exceptions, copied text being translated/rewritten, or information already owned by a task/profile/estimate record.
7. Do not automatically save sensitive personal attributes or health/private-life details. Save them only on an explicit request and minimize content.

Use `dida-planning-core/scripts/memory_policy.py` for the final save/ask/route/skip decision after the semantic owner is identified.

## Storage structure

Global memory categories live as parent NOTE tasks in `系统配置`:

- `长期记忆｜项目规则`
- `长期记忆｜工具与环境`
- `长期记忆｜工作方式`
- `长期记忆｜通用约定`

Each memory is a separate child task/NOTE with:

- concise title beginning `记忆｜`;
- current fact and applicability in the natural body, normally under 300 Chinese characters;
- `role: memory`, `required_for_parent: false`, no dates, no estimate, no status;
- source/confidence/scope fields in the Planner block;
- change history in comments.

Project-specific memory is created under the exact project parent, not copied into a global category.

## Initialize

1. Resolve or create `系统配置` through `$dida-cli`.
2. Create only missing category parents from `assets/memory-categories/`.
3. Read back IDs and write them into `系统状态｜Schema与迁移版本`.
4. Never overwrite user-edited category notes.

## Save or update

1. Search the exact project/category and semantically similar memory titles before creating.
2. If equivalent, update the existing record rather than duplicate it.
3. If contradicted, preserve a comment explaining the change, then replace the current body.
4. Use `memory_source: explicit|durable_fact|confirmed_inference` and `memory_confidence: high|medium`.
5. Read back and report the saved memory and owner. Never say “记住了” before the write is verified.

## Retrieve

Read only the exact project memories and relevant global category. Do not load all memory categories for ordinary operations. State which remembered rule materially affected the action when helpful.

## Forget

Resolve by ID, exact title, owner, and content. Delete the exact memory when authorized. If the fact is owned by profile/task/estimate data, route the deletion to that owner. When several candidates match, ask which one rather than deleting broadly.

## References

Read `references/memory-policy.md` for policy boundaries and `references/memory-format.md` for record fields and examples.
