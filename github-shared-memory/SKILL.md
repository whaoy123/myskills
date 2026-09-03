---
name: github-shared-memory
description: Maintain and compact a GitHub-backed Markdown memory repository shared by ChatGPT and coding agents. Use when continuing a long-running project, recording confirmed decisions or status, or organizing cross-agent project context.
---

# GitHub Shared Memory

Treat the configured ai-memory Git repository as the source of truth for durable cross-agent context. It records confirmed facts, decisions, current status, and active next actions; it is not a chat-log archive, a replacement for project source documentation, or a store for secrets.

## Start work

1. Locate the configured memory repository. If none is configured, ask for its local path or GitHub URL; do not create a remote repository or infer one.
2. Before reading, inspect git status --short. Pull only when the worktree is clean. If it is dirty or pull produces a conflict, preserve local work and ask the user how to resolve it.
3. Read PROFILE.md and CURRENT.md, then read only the project files relevant to the task. Project-local facts take precedence over general profile notes.

## Synchronize current work

Normal synchronization is incremental. Read the relevant project record, then make the smallest edit that records only durable new information:

- confirmed architecture, parameter, interface, or policy decisions;
- measured test results with conditions and units;
- completed milestones, current blocking issue, and the next concrete action;
- corrections that supersede earlier recorded facts.

Never rewrite unrelated files or summarize the complete repository during ordinary synchronization. Do not write tentative ideas, whole conversation summaries, credentials, raw personal data, or implementation details that already belong in the project repository. Keep one active statement per decision and mark replaced decisions as superseded with the date and link to the new entry.

Use the repository structure and file responsibilities in [the memory schema](references/memory-schema.md). Add a new project folder only when the work is a distinct long-running project; otherwise update the closest existing project.

## Maintain and compact memory

Use maintenance mode only when the user requests a cleanup, or when an active memory file exceeds 300 lines, has duplicate/conflicting statements, or contains stale handoff state. It is a controlled rewrite of the affected scope, never a blind whole-repository rewrite.

A maintenance pass must:

1. Read every file in the affected project plus the linked entries in CURRENT.md.
2. Classify each statement as current fact, superseded decision, historical test evidence, stale work state, duplicate, or unsupported.
3. Keep one canonical current statement in its authoritative file: decisions in decisions.md, current handoff in status.md, and stable scope in overview.md.
4. Merge duplicates; move superseded decisions and historical evidence to archive/ with a date and source link instead of deleting them.
5. Remove stale items from CURRENT.md and keep only active projects, blockers, and next actions.
6. Preserve uncertainty rather than silently resolving a conflict. Ask the user when evidence cannot determine the canonical fact.
7. Review and report the exact diff before committing.

The outcome is a compact current context plus traceable history, not a shorter but lossy summary.

## Synchronize safely

After updating, inspect git diff. State precisely what will be committed. Commit and push only when the user has authorized that external write or the current task explicitly includes synchronization. Use a focused commit message such as memory(1553b): record BC retry defaults.

When two agents edited the same fact, do not silently choose one. Compare the evidence, keep the currently confirmed value, and record the replacement history when a decision genuinely changed.

## Agent integration

For each agent environment, add a short pointer in its project/global instruction file so it discovers this skill and the memory repository. Use the template in [agent integration](references/agent-integration.md). The pointer must require relevant reads at task start and prohibit automatic pushes without authorization.
