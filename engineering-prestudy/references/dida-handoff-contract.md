# Research -> Dida Handoff Contract

## Ownership boundary

Research owns:

- why work is needed;
- engineering/learning work packages;
- expected outputs;
- completion/acceptance criteria;
- dependencies;
- traceability to decisions, open questions, and pitfalls.

Dida owns:

- final task hierarchy in Dida;
- duration estimates;
- scheduling/date semantics;
- daily time blocks;
- priority/status/progress;
- task IDs and dependency edges after Dida records exist.

## Handoff lifecycle

```text
project_plan.yaml
    ↓
dida_handoff.yaml (DRAFT)
    ↓ user approves
dida_handoff.yaml (APPROVED)
    ↓ build_dida_bridge.py
dida_bridge.jsonl
    ↓
dida-task-breakdown
    ↓
dida-task-estimator
    ↓
dida-task-capture
    ↓
dida-daily-planner (only when scheduling is wanted)
```

`build_dida_bridge.py` refuses non-APPROVED handoff by default.

## Work-package fields

Required:

- id
- stage
- title
- expected_outputs
- acceptance
- dependencies

Optional traceability:

- open_question_ids
- decision_ids
- pitfall_ids

Do not put estimated duration, date, priority, schedule, or time blocks into research-owned handoff.

## Bridge output

Each JSONL row is deliberately neutral:

- `role: task`
- title/body from work package
- dependency references preserved
- `estimated_duration: null`
- `date: null`
- `priority: null`
- `schedule: null`
- flags indicating Dida breakdown/estimation are still required

The bridge is not a direct Dida API import format. It is an explicit interface object for the Dida skills to consume without duplicating responsibility.

## Revision safety

If research changes a previously approved route:

1. update decisions/pitfalls;
2. increment `project_plan.revision`;
3. regenerate `dida_handoff.yaml`;
4. present changes;
5. require user approval before modifying existing Dida tasks.
