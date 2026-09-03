# Memory repository schema

```text
ai-memory/
├── PROFILE.md
├── CURRENT.md
├── projects/
│   └── <project-slug>/
│       ├── overview.md
│       ├── decisions.md
│       ├── status.md
│       └── test-results.md        # only when the project needs it
└── knowledge/
    └── <stable-topic>.md          # reusable, non-project-specific knowledge
```

`PROFILE.md` stores stable collaboration preferences and durable background that affects many projects. Do not put time-sensitive work state here.

`CURRENT.md` is a short index of active projects: current focus, blocking item, next action, and links to the project files. Remove completed one-off items instead of turning it into a history log.

`overview.md` states the project purpose, scope, canonical repositories/documents, and constraints. It should be readable by an agent with no chat history.

`decisions.md` is the authoritative decision ledger. Each entry has a date, decision, rationale/evidence, status, and a `Supersedes:` line when replacing an earlier entry.

`status.md` is the compact working handoff: completed work, current state, blockers, and next action. Keep it current rather than appending daily diaries.

`test-results.md` records measurements that need conditions to be interpretable: date, hardware/software revision, setup, inputs, results with units, and conclusion.

## Decision entry

```markdown
## BC retry policy — 2026-09-03

- Status: confirmed
- Decision: Retry count is register-configurable; reset default is 2.
- Rationale: allows mission-specific tuning while preserving a predictable default.
- Evidence: design review on 2026-09-03.
- Supersedes: none
```

Do not duplicate the same fact in `CURRENT.md`, `status.md`, and `decisions.md`: keep the authority in one place and link to it.
