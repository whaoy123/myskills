# Frozen system contract v1.1

- Dida is the only task, profile, and durable planning-memory business source of truth.
- Lists are domains; projects are parent tasks.
- Four work levels: project, phase, task, block. Memory uses separate non-work roles: memory_category and memory.
- Native Dida fields own title, content, parent, priority, dates, recurrence, estimated duration, and completion.
- Planner body block owns progress, date semantics, mobility, privacy, confidence, dependencies, and memory metadata.
- Comments are append-only historical events.
- Stable planning preferences belong to `dida-planning-profile`; durable cross-project facts/rules belong to `dida-planning-memory`; task-local facts remain on the owning task; timing samples belong to estimator/progress.
- Explicit save/forget requests are honored. Stable, directly stated, low-sensitivity, future-useful facts may auto-save with visible confirmation. Inferred or sensitive facts require confirmation unless explicitly requested.
- Do not save temporary/trivial information or text supplied only for translation/rewriting.
- Hard deadlines are never changed automatically.
- Personal calendar occupancy cannot overlap.
- No abandoned state; unnecessary tasks may be deleted.
- Inbox is organized only on explicit request.
- Current-location timezone is used automatically.
