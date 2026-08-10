---
name: engineering-prestudy
description: Orchestrate an engineering or technical prestudy from an initially unfamiliar topic through understanding, current-state research, evidence collection, design tradeoffs, and an implementation plan. Preserve changing goals, separate FACT/INFERENCE/DECISION, maintain open questions and stop conditions, reuse user context, and hand approved work packages to Dida planning without directly owning scheduling.
---

# Engineering Prestudy

This is the orchestration skill. It does not duplicate specialist logic.

## Subskills

- `user-context-profile` -> unified user background/knowledge/preferences.
- `research-understanding` -> understanding loop and project knowledge model.
- `research-landscape` -> current-state research, evidence, source library, reusable artifacts.
- `research-design-planning` -> trade studies, decisions, staged deliverables, Dida handoff.

## Fixed runtime project structure

```text
<project>/.prestudy/
├── research_state/
│   ├── project.yaml
│   ├── knowledge_model.yaml
│   ├── research_questions.yaml
│   ├── sources.csv
│   ├── evidence.jsonl
│   ├── open_questions.yaml
│   ├── decisions.yaml
│   ├── project_plan.yaml
│   └── dida_handoff.yaml
├── library/
│   ├── papers/
│   ├── datasheets/
│   ├── standards/
│   ├── repos/
│   ├── webpages/
│   └── other/
├── notes/
├── reports/
└── history/
```

`research_state/` is the authoritative project state. Reports are derived human-readable outputs.

## Minimal project input

Only two inputs are mandatory:

1. What the user wants to research/build/understand.
2. What the user already knows and approximate proficiency.

Optional:

- existing PDFs, code, repositories, notes, schematics, standards, datasheets, or webpages;
- constraints, purpose, target deliverable, budget, hardware, time, implementation requirements.

Do not demand a perfect research question up front. The research goal may evolve.

## Start workflow

1. Load unified user context from `user-context-profile`.
2. Separate stable global knowledge from topic/project-specific knowledge.
3. Create or load `.prestudy/research_state/`.
4. Record `initial_goal` and `current_goal` separately.
5. Inventory existing user-provided sources before browsing for duplicates.
6. Create the first research questions and open-question pool.
7. Produce `reports/research_brief.md` before broad research.
8. Enter the most appropriate state: `UNDERSTAND`, `RESEARCH`, or `DESIGN_PLAN`.

## State machine

```text
UNDERSTAND <-> RESEARCH <-> DESIGN_PLAN
```

The flow is intentionally reversible.

- If research exposes a prerequisite concept gap -> return to `UNDERSTAND`.
- If design reveals missing evidence -> return to `RESEARCH`.
- Do not force stage completion because the previous stage already ran once.

## Goal revision

Never overwrite the initial goal. When the practical problem changes, append a `goal_history` entry with:

- previous goal;
- new goal;
- reason;
- supporting evidence/decision IDs.

## Evidence classes

Keep these separate:

- `FACT`: externally supported statement traceable to a source locator.
- `INFERENCE`: conclusion derived from one or more facts.
- `DECISION`: project choice accepted or proposed from evidence, constraints, and tradeoffs.

Never present an inference as if the source explicitly stated it.

## Open questions

Every unresolved item belongs in `open_questions.yaml`.

Types:

- `MISSING_INFORMATION`
- `SOURCE_CONFLICT`
- `NEEDS_EXPERIMENT`
- `NEEDS_ENGINEERING_ANALYSIS`
- `NEEDS_USER_DECISION`

Impact may be `LOW|MEDIUM|HIGH|BLOCKING`.

Only actionable/blocking questions become Dida candidates.

## Stop conditions

Research questions may become `SATURATED` when their configured stop rule is met. Typical criteria:

- required primary source found;
- minimum independent-source count met;
- important contradictions resolved or explicitly documented;
- repeated searches no longer produce materially new information.

Do not equate saturation with certainty.

## Dida boundary

Research determines what should be done and what outputs/acceptance criteria are required. Dida owns task breakdown, estimation, scheduling, and progress.

Research writes `dida_handoff.yaml` only. It must not silently mutate the user's task plan.

If Dida skills are available, hand off approved work packages to:

1. `dida-task-breakdown`
2. `dida-task-estimator`
3. `dida-task-capture`
4. `dida-daily-planner`

Changes caused by a revised research conclusion require user approval before existing Dida tasks are removed, postponed, or materially changed.

## Distribution boundary

The skill package must never contain real `.prestudy/`, user context, downloaded libraries, Dida task data, credentials, or local project paths.
