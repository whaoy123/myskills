# Frozen system contract v1.2

- Dida is the only task, profile, and durable planning-memory business source of truth.
- Lists are domains; projects are parent tasks.
- Four work levels: project, phase, task, block. Memory uses separate non-work roles: memory_category and memory.
- Native Dida fields own title, content, parent, priority, dates, recurrence, estimated duration, and completion.
- Planner body block owns progress, date semantics, weekly mainline commitment, mobility, privacy, confidence, dependencies, and memory metadata.
- Weekly mainlines are 2–4 user-selected work tasks, classified as must, should, or candidate. Their task-local Planner fields are the only current-week commitment state; no weekly summary task or local editable plan is created.
- A weekly commitment is a pair on a work role only: Monday `week_start: YYYY-MM-DD` and `weekly_commitment: must|should|candidate`. On a week roll, stale or malformed work-task pairs are cleared from the owning Dida task's Planner block; native dates, especially hard deadlines, are untouched.
- Movable work is assessed as weekly total occupancy. Exact day/hour blocks are reserved for fixed items, started tasks, explicit requests, or deadline rescue.
- Comments are append-only historical events.
- Stable planning preferences belong to `dida-planning-profile`; durable cross-project facts/rules belong to `dida-planning-memory`; task-local facts remain on the owning task; timing samples belong to estimator/progress.
- Explicit save/forget requests are honored. Stable, directly stated, low-sensitivity, future-useful facts may auto-save with visible confirmation. Inferred or sensitive facts require confirmation unless explicitly requested.
- Do not save temporary/trivial information or text supplied only for translation/rewriting.
- Hard deadlines are never changed automatically.
- Personal calendar occupancy cannot overlap.
- No abandoned state; unnecessary tasks may be deleted.
- Inbox is organized only on explicit request.
- Current-location timezone is used automatically.
