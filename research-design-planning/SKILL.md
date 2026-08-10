---
name: research-design-planning
description: Turn an engineering-prestudy evidence base into design alternatives, trade studies, user-confirmed decisions, project stages, required outputs, acceptance criteria, dependencies, and a Dida handoff. Use after enough understanding and research exists to choose what to build or learn next, while allowing a return to research when evidence is insufficient.
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
- `decisions.yaml`;
- existing `project_plan.yaml`.

## Design discussion loop

1. Restate the engineering objective and current constraints.
2. Generate only materially distinct alternatives.
3. Define evaluation criteria before choosing a winner.
4. Compare alternatives using evidence, uncertainty, cost/complexity, implementation risk, compatibility, testability, maintainability, and user-specific constraints when relevant.
5. Mark assumptions and missing evidence.
6. If a missing fact could change the decision, create a blocking research question and return to `research-landscape`.
7. Present tradeoffs to the user and refine through discussion.
8. Record the result as a `DECISION` with status.

## Decision states

- `PROPOSED`
- `CONFIRMED`
- `SUPERSEDED`
- `REJECTED`

Only `CONFIRMED` decisions can become hard plan assumptions.

## Trade study structure

Each important choice should capture:

- objective;
- alternatives;
- evaluation criteria;
- evidence IDs;
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
- relevant decisions/open questions;
- optional risks.

A stage is not complete just because tasks were executed; its required outputs and acceptance criteria must be satisfied.

## Dida handoff

Generate `dida_handoff.yaml` from the approved `project_plan.yaml`.

Each work package should contain:

- source stage;
- title;
- expected outputs;
- acceptance criteria;
- dependencies;
- relevant blocking question/decision IDs.

Default:

```yaml
status: DRAFT
approval_required: true
```

Do not directly schedule work. Once the user approves the handoff, route to the existing Dida skills for breakdown, estimation, capture, and scheduling.

## Route-change safety

If new research supersedes a previous decision or stage:

1. record the new decision and why;
2. increment the project-plan revision;
3. generate proposed Dida changes;
4. require user approval before mutating existing tasks.

## Output

Maintain:

- `decisions.yaml`;
- `project_plan.yaml`;
- `dida_handoff.yaml`;
- `reports/implementation_plan.md`.
