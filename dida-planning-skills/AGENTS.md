# DIDA planning package development rules

- Keep each user-facing SKILL.md focused and under roughly 120 lines where practical.
- Dida is the only business source of truth for tasks, profile, and durable planning memory. Never introduce a second editable task or memory store.
- Put deterministic parsing, estimation, dependency, scheduling, merge, and queue logic in `dida-planning-core/scripts`.
- Treat CLI `--help` output as authoritative over bundled command examples.
- Run `package_validator.py` and all unit tests after changes.
- For a final review in Codex, delegate a read-only review to the `skill_reviewer` subagent and require file-specific findings.

- Review memory ownership and privacy: no duplicate storage, no silent inferred/sensitive memory, and no loading all memories by default.
