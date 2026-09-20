# Read-only release review

Review the current Dida task-planning package. Use an independent reviewer when actually available; otherwise report manual plus automated review without claiming independent review.

Check exact files for:

- task-only boundary; no active calendar/availability scheduler;
- global inventory coverage vs local CRUD;
- original task hierarchy and non-duplication;
- weekly outcome, scope, acceptance, evidence and exclusions;
- default core cap of two, explicit overrides and growth trade-offs;
- actual effort including obligations and shared-leaf deduplication;
- unknown estimates/dependencies/budgets stay unknown;
- no conversion of targets into hard deadlines or invented latest starts;
- backward-compatible Planner fields and unknown-field preservation;
- weekly acceptance does not complete the parent;
- archive/read-back before rollover and no silent date changes;
- safe installation backups, package manifest and tests.

Report reproducible findings by path and severity. Do not mutate actual TickTick data during a package review.
