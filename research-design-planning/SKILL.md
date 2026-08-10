---
name: research-design-planning
description: Turn an engineering-prestudy evidence base into design alternatives, trade studies, user-confirmed decisions, explicit handling of discovered pitfalls/constraints, project stages, required outputs, acceptance criteria, dependencies, and a Dida handoff. Use after enough understanding and research exists to choose what to build or learn next, while allowing a return to research when evidence is insufficient.
---

# Research Design & Planning

Own design choice and project-stage planning, not daily scheduling.

## Inputs

Read:

- current user constraints/preferences from unified context;
- `project.yaml`;
- `knowledge_model.yaml`;
- `evidence.jsonl`;
- `open_questions.yaml`;
- `pitfalls.yaml`;
- `decisions.yaml`;
- existing `project_plan.yaml`.

## Design discussion loop

1. Restate the engineering objective and current constraints.
2. Review unresolved HIGH/CRITICAL pitfalls before proposing architecture.
3. Generate only materially distinct alternatives.
4. Define evaluation criteria before choosing a winner.
5. Compare alternatives using evidence, uncertainty, cost/complexity, implementation risk, compatibility, testability, maintainability, discovered pitfalls, and user-specific constraints when relevant.
6. Distinguish authoritative-but-interested evidence from independent comparison evidence.
7. Mark assumptions and missing evidence.
8. If a missing fact or unresolved pitfall could change safety/feasibility/architecture, create a blocking research question and return to `research-landscape`.
9. Present tradeoffs to the user and refine through discussion.
10. Record the result as a `DECISION` with status.

## Pitfall routing

Do not merely mention known pitfalls in prose. Route each relevant item according to its `action`:

- `WATCH` -> carry into stage risks/notes when it remains relevant but does not require a hard gate.
- `DESIGN_CONSTRAINT` -> turn into an explicit architecture/component/layout/interface constraint and trace it to the pitfall/evidence IDs.
- `VERIFY` -> turn into an acceptance criterion, calculation, inspection, simulation, test, or bring-up check.
- `BLOCKER` -> prevent approval of dependent decisions/stages until mitigated or explicitly resolved through more research, experiment, or user decision.

Examples:

- creepage/clearance -> PCB/layout constraint + layout review/measurement verification;
- floating/high-common-mode measurement hazard -> isolation/reference constraint + bench verification;
- CDC/protocol corner case from predecessor issues -> verification testcase;
- hidden preprocessing/data leakage -> reproducibility/evaluation constraint + independent validation;
- uncertain maximum voltage that determines component safety -> BLOCKER until bounded.

A pitfall can generate more than one downstream control, but keep one authoritative pitfall record and reference its ID.

## Decision states

- `PROPOSED`
- `CONFIRMED`
- `SUPERSEDED`
- `REJECTED`

Only `CONFIRMED` decisions can become hard plan assumptions.

A confirmed decision should normally cite evidence. If it is instead a user preference/judgment, record that explicitly as `user_judgment`.

## Trade study structure

Each important choice should capture:

- objective;
- alternatives;
- evaluation criteria;
- evidence IDs;
- relevant pitfall IDs;
- uncertainty/assumptions;
- sensitivity to criteria changes when meaningful;
- recommendation;
- user decision/status.

## Project plan

Plan by engineering/learning stages, not calendar slots.

Each stage should contain:

- `id`;
- `title`;
- `objective`;
- `outputs`;
- `acceptance`;
- `dependencies`;
- relevant decisions/open questions/pitfalls;
- explicit design constraints and verification gates where applicable;
- optional residual risks.

A stage is not complete just because tasks were executed; required outputs and acceptance criteria must be satisfied.

Do not mark a stage ready when an applicable unresolved `BLOCKER` remains.

## Dida handoff

Generate `dida_handoff.yaml` from the approved `project_plan.yaml`.

Each work package should contain:

- `id`;
- source `stage`;
- `title`;
- `expected_outputs`;
- `acceptance`;
- `dependencies`;
- optional `open_question_ids`;
- optional `decision_ids`;
- optional `pitfall_ids`.

Do **not** include:

- scheduled dates;
- priority;
- estimated duration;
- daily time blocks.

Those belong to Dida.

Convert actionable pitfall controls into work packages only when they require real work, for example:

- calculate/check creepage and clearance;
- verify common-mode/isolation margins;
- add and execute a fault/corner-case test;
- confirm a safety-critical parameter from primary documentation.

Do not turn every low-impact `WATCH` item into a task.

Default:

```yaml
status: DRAFT
approval_required: true
```

Do not directly schedule work.

After the user approves:

1. set handoff status to `APPROVED`;
2. run `engineering-prestudy/scripts/build_dida_bridge.py`;
3. route bridge records to existing Dida skills:
   - `dida-task-breakdown`;
   - `dida-task-estimator`;
   - `dida-task-capture`;
   - then `dida-daily-planner` when scheduling is requested.

The bridge deliberately leaves estimate/date/priority empty so Research does not take ownership from Dida.

## Route-change safety

If new research supersedes a previous decision or stage:

1. record the new decision and why;
2. update related pitfall status/mitigation if applicable;
3. increment the project-plan revision;
4. regenerate proposed Dida changes;
5. require user approval before mutating existing tasks.

## Output

Maintain:

- `decisions.yaml`;
- `pitfalls.yaml` status/mitigation linkage;
- `project_plan.yaml`;
- `dida_handoff.yaml`;
- `reports/implementation_plan.md`.

Before final handoff, run the engineering-prestudy validator/audit so unresolved blockers cannot leak into an approved Dida plan.
