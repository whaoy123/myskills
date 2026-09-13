---
name: dida-cli
description: Legacy/local fallback execution adapter for 滴答清单/Dida365. Use only when the runtime does not provide a first-class TickTick/滴答清单 MCP or connector tool and a planning skill still needs verified reads or writes through the local DIDA CLI. Do not use this Skill when an MCP/connector is available. Do not make planning, prioritization, decomposition, or estimation decisions.
---

# DIDA CLI fallback execution layer

This Skill is a **compatibility fallback**, not the preferred runtime path.

Higher-level planning skills decide what should happen. When a first-class TickTick/滴答清单 MCP or connector is available, they must use that connector directly for reads, writes, and verification. Only when such a connector is unavailable should this Skill act as a thin, verifiable adapter around the installed `dida` command.

## Routing rule

Use this order:

```text
1. TickTick / 滴答清单 MCP or connector available?
   yes → use it directly; do not invoke dida-cli
   no  → use dida-cli fallback
```

Do not route through CLI merely because older Skill text, scripts, or examples mention it.

The CLI remains useful for:

- local Codex/agent environments without MCP support;
- offline development/testing of the planning package;
- migration utilities that explicitly depend on local CLI behavior;
- compatibility with older workflows.

## Runtime requirement

These requirements apply **only when the fallback path is actually needed**:

- Never run Dida CLI commands in the default sandbox. Use an approved non-sandbox execution path for authentication, reads, writes, and verification.
- The CLI stores its access token under the user's profile (`%USERPROFILE%\\.config\\dida-cli\\config.json`); sandbox isolation can make a valid token appear absent and produce a false unauthenticated result.
- If non-sandbox execution is unavailable or rejected, report the blocker and do not claim the account is logged out based only on a sandboxed result.

## Start of a fallback Dida session

1. Confirm that no usable TickTick/滴答清单 MCP or connector exists in the current runtime.
2. Run `dida --version` and `dida auth status`.
3. If unavailable, explain that Node.js 20+ and `npm install -g @suibiji/dida-cli` are required for this fallback path. Install only when requested or approved.
4. If unauthenticated, use `dida auth login`. Never request tokens, cookies, or credentials in chat.
5. Before an unfamiliar command or flag, run the relevant `--help`. Installed help is authoritative; bundled references are only a baseline.

## Resolve before writing

- Prefer `--json` for machine-read operations.
- Resolve lists with `dida project list --json`.
- Resolve tasks from exact title plus project, parent, date, tags, or status.
- Never invent IDs or silently select the first fuzzy match.
- Keep `projectId` and `taskId` together.
- If several candidates remain, return the short candidate set rather than writing.

## Write protocol

For create, update, move, complete, delete, comment, or focus changes:

1. Read the current object.
2. Preserve unspecified fields.
3. Execute only the intended fields.
4. Read back the object or destination list.
5. Report actual saved values.

After timeout or ambiguous network failure, read before retrying to prevent duplicate tasks or comments.

## Batch helper

For several related fallback reads, or a pre-reviewed set of creates, updates, parent assignments, and comments, `scripts/dida_batch.py` may be used instead of spawning many individual shell commands.

- Run `python scripts/dida_batch.py --help` before the first use in a session.
- Use `scheduled` for a date-window read and `search` for project-scoped title/body lookup.
- Put writes in a JSON plan and run `plan --input <file>` first; it is dry-run by default.
- Use `--apply` only after resolving IDs and confirming the write scope.
- If a plan fails midway, do not rerun it blindly. Read the reported objects, then prepare a narrowed follow-up plan.

For **global planning**, a date-window query alone is insufficient. The higher-level planner must enumerate all unfinished tasks across all projects, including pagination and undated/future tasks. The CLI adapter must not silently downgrade that requirement to a `today` or `next7day` view.

## Dates and time

- Resolve relative dates to absolute timestamps using the user's current local timezone.
- Do not hard-code UTC+8 when the user is elsewhere.
- Preserve date-only tasks as all-day when supported.
- Never change a hard deadline unless the user explicitly directs it.

## Destructive operations

An exact request to delete a uniquely resolved task authorizes that deletion. Before deleting a task with children, comments, or focus history, show the impact. Vague requests such as “清理旧任务” require a preview. Verify deletion afterward.

## Planner integration

When used as fallback by planning skills:

- Preserve natural-language body and unknown fields in planner-managed regions.
- Add history through task comments; do not rewrite old comments.
- Use Dida native estimated duration, priority, dates, parent IDs, tags, recurrence, and completion state where supported.
- Do not treat model memory or local SQLite/cache as more authoritative than the remote Dida objects read through the CLI.
- For global planning, return enough data for the planner to evaluate deadlines, dependencies and latest-safe-start risk; do not filter only to recent tasks unless the caller explicitly requested a local view.
- Inspect `references/planner-integration.md` before modifying Planner-managed content.

## Failure handling

- `command not found`: report missing fallback CLI; do not imply TickTick itself is unavailable.
- HTTP 401/auth failure: check CLI auth and request browser login for the fallback path.
- Unknown option: inspect help and adapt once.
- Not found: refresh before concluding.
- Malformed JSON: retain diagnostic stderr but redact credentials or headers.

## Deprecation status

`dida-cli` is **not deleted** because it still supports local/legacy environments. New planning logic must not depend on it as the only execution mechanism. New documentation and higher-level Skills should describe MCP/connector tools as the primary runtime I/O layer.

## References

- `references/commands.md` — CLI command baseline for fallback environments.
- `references/workflows.md` — ID resolution and write verification.
- `references/planner-integration.md` — Planner body/comment rules.
