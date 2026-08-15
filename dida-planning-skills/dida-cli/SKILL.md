---
name: dida-cli
description: Execute safe individual or batched reads and writes through the local DIDA CLI for 滴答清单/Dida365. Use when another planning skill or the user needs to list, resolve, create, update, move, complete, delete, comment on, or inspect Dida tasks, lists, tags, focus records, habits, or countdowns. Do not make planning, prioritization, decomposition, or estimation decisions.
---

# DIDA CLI execution layer

Act as a thin, verifiable adapter around the installed `dida` command. Higher-level skills decide what should happen; this skill resolves IDs, executes the exact change, and verifies the saved state.

## Runtime requirement

- Never run Dida CLI commands in the default sandbox. Use an approved non-sandbox execution path for authentication, reads, writes, and verification.
- The CLI stores its access token under the user's profile (`%USERPROFILE%\\.config\\dida-cli\\config.json`); sandbox isolation can make a valid token appear absent and produce a false unauthenticated result.
- If non-sandbox execution is unavailable or rejected, report the blocker and do not claim the account is logged out or request another login based only on the sandboxed result.

## Start of a Dida session

1. Run `dida --version` and `dida auth status`.
2. If unavailable, explain that Node.js 20+ and `npm install -g @suibiji/dida-cli` are required. Install only when requested or approved.
3. If unauthenticated, use `dida auth login`. Never request tokens, cookies, or credentials in chat.
4. Before an unfamiliar command or flag, run the relevant `--help`. Installed help is authoritative; bundled references are only a baseline.

## Resolve before writing

- Prefer `--json` for all machine-read operations.
- Resolve lists with `dida project list --json`.
- Resolve tasks from exact title plus project, parent, date, tags, or status.
- Never invent IDs or select the first fuzzy match silently.
- Keep `projectId` and `taskId` together.
- If several candidates remain, return the short candidate set rather than writing.

## Write protocol

For create, update, move, complete, delete, comment, or focus changes:

1. Read the current object.
2. Preserve unspecified fields.
3. Execute only the intended fields.
4. Read back the object or destination list.
5. Report actual saved values.

After timeout or ambiguous network failure, read before retrying to prevent duplicate tasks or comments. Higher-level skills may add an operation to the shared pending-sync queue.

## Batch helper

For several related reads, or a pre-reviewed set of creates, updates, parent assignments, and comments, use `scripts/dida_batch.py` instead of spawning many individual shell commands.

- Run `python scripts/dida_batch.py --help` before the first use in a session.
- Use `scheduled` for a date-window read and `search` for project-scoped title/body lookup. Require an explicit project unless a broad search is genuinely needed.
- Put writes in a JSON plan and run `plan --input <file>` first. It is dry-run by default; use `--apply` only after resolving IDs and confirming the write scope.
- A plan can create tasks, use `@key` to attach later tasks to newly created parents, update native dates/estimates/parent IDs, and append idempotent comments. The helper reads each updated task first and verifies every saved result.
- Keep delete, completion, and cross-project move operations on the normal CLI path; inspect their impact individually.
- If a plan fails midway, do not rerun it blindly. Read the reported objects, then prepare a narrowed follow-up plan.

## Dates and time

- Resolve relative dates to absolute timestamps using the user's current local timezone.
- Do not hard-code UTC+8 when the user is elsewhere.
- Preserve date-only tasks as all-day when supported.
- Never change a hard deadline unless the user explicitly directs it.

## Destructive operations

An exact request to delete a uniquely resolved task authorizes that deletion. Before deleting a task with children, comments, or focus history, show the impact. Vague requests such as “清理旧任务” require a preview. Verify deletion afterward.

## Planner integration

When called by the planning skills:

- Preserve the natural-language body and unknown fields in `【Planner】...【/Planner】`.
- Add history through task comments; do not rewrite old comments.
- Use Dida native estimated duration, priority, dates, parent IDs, tags, recurrence, and completion state where supported. Treat `role: memory_category|memory` records as ordinary Dida objects with no scheduling/estimate side effects.
- For daily execution views, use the exact visible tag `今天`: resolve it with `tag list`, create it only if missing, and update exact task IDs with `--tags` while preserving existing tags. The higher-level planner decides the tag membership; never tag project/phase parents merely because their date range overlaps today.
- Inspect `references/planner-integration.md` before modifying Planner-managed content.

## Failure handling

- `command not found`: report missing CLI; do not substitute another product.
- HTTP 401/auth failure: check auth and request browser login.
- Unknown option: inspect help and adapt once.
- Not found: refresh before concluding.
- Malformed JSON: retain diagnostic stderr but redact credentials or headers.

## References

- Read `references/commands.md` for command baselines.
- Read `references/workflows.md` for ID resolution and write verification.
- Read `references/planner-integration.md` for Planner body/comment rules.
