---
name: github-shared-memory
description: Maintain a GitHub-backed Markdown memory repository shared by ChatGPT and coding agents. Use when continuing a long-running project, recording confirmed decisions or status, or setting up cross-agent project context.
---

# GitHub Shared Memory

Treat the configured `ai-memory` Git repository as the source of truth for durable cross-agent context. It records confirmed facts, decisions, current status, and active next actions; it is not a chat-log archive, a replacement for project source documentation, or a store for secrets.

## Start work

1. Locate the configured memory repository. If none is configured, ask for its local path or GitHub URL; do not create a remote repository or infer one.
2. Before reading, inspect `git status --short`. Pull only when the worktree is clean. If it is dirty or pull produces a conflict, preserve local work and ask the user how to resolve it.
3. Read `PROFILE.md` and `CURRENT.md`, then read only the project files relevant to the task. Project-local facts take precedence over general profile notes.

## Record durable context

Update memory only for information that remains useful after the current chat:

- confirmed architecture, parameter, interface, or policy decisions;
- measured test results with conditions and units;
- completed milestones, current blocking issue, and the next concrete action;
- corrections that supersede earlier recorded facts.

Do not write tentative ideas, whole conversation summaries, credentials, raw personal data, or implementation details that already belong in the project repository. Keep one active statement per decision and mark replaced decisions as superseded with the date and link to the new entry.

Use the repository structure and file responsibilities in [the memory schema](references/memory-schema.md). Add a new project folder only when the work is a distinct long-running project; otherwise update the closest existing project.

## Synchronize safely

After updating, inspect `git diff`. State precisely what will be committed. Commit and push only when the user has authorized that external write or the current task explicitly includes synchronization. Use a focused commit message such as `memory(1553b): record BC retry defaults`.

When two agents edited the same fact, do not silently choose one. Compare the evidence, keep the currently confirmed value, and record the replacement history when a decision genuinely changed.

## Agent integration

For each agent environment, add a short pointer in its project/global instruction file so it discovers this skill and the memory repository. Use the template in [agent integration](references/agent-integration.md). The pointer must require relevant reads at task start and prohibit automatic pushes without authorization.
