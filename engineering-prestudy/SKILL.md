---
name: engineering-prestudy
description: Orchestrate an engineering or technical prestudy from an initially unfamiliar topic through understanding, current-state research, evidence collection, predecessor/pitfall analysis, design tradeoffs, and an implementation plan. Preserve changing goals, separate FACT/INFERENCE/DECISION, maintain open questions and stop conditions, reuse user context, and hand approved work packages to Dida planning without directly owning scheduling.
---

# Engineering Prestudy

This is the orchestration skill. It does not duplicate specialist logic.

## Subskills

- `user-context-profile` -> unified user background/knowledge/preferences.
- `research-understanding` -> understanding loop and project knowledge model.
- `research-landscape` -> current-state research, evidence, predecessor implementations, pitfalls, and retained source library.
- `research-design-planning` -> trade studies, decisions, staged deliverables, pitfall routing, and Dida handoff.

## Fixed runtime project structure

```text
<project>/.prestudy/
├── research_state/
│   ├── project.yaml
│   ├── knowledge_model.yaml
│   ├── research_questions.yaml
│   ├── sources.csv
│   ├── search_log.csv
│   ├── evidence.jsonl
│   ├── open_questions.yaml
│   ├── pitfalls.yaml
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
│   ├── research_brief.md
│   ├── current_understanding.md
│   ├── research_landscape.md
│   ├── implementation_plan.md
│   └── FINAL.md
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

Use `scripts/init_project.py` for deterministic state/report scaffolding.

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

## Pitfalls

`pitfalls.yaml` is the authoritative register for discovered predecessor failures, hidden constraints, novice traps, safety hazards, integration risks, and verification-sensitive conditions.

A pitfall is not just prose. It must be routed later as one or more of:

- `WATCH`
- `DESIGN_CONSTRAINT`
- `VERIFY`
- `BLOCKER`

Important pitfalls must remain traceable from evidence -> pitfall -> design/verification control -> project stage/work package.

## Search log and saturation

`search_log.csv` records what was searched, for which research question, what changed, and whether the latest pass produced materially new information.

A `SATURATED` research question must explicitly record all applicable stop-condition flags. It is not enough to simply set `status: SATURATED`.

Do not equate saturation with certainty.

## Reports

Fixed report roles:

- `research_brief.md` -> initial framing and known/unknown boundary.
- `current_understanding.md` -> current mental model and remaining conceptual gaps.
- `research_landscape.md` -> current state, predecessor implementations, borrowable patterns, pitfalls, retained 1–2 core references.
- `implementation_plan.md` -> selected route, stages, outputs, acceptance, design constraints, verification gates.
- `FINAL.md` -> compact final overview for the user; never use it as the authoritative state database.

Use `scripts/build_final.py` to regenerate `FINAL.md` from current state/reports.

## Human-facing report finalization

All files under `reports/` are human-facing derived outputs. Before a report is treated as the current formal version, apply its domain/style rules first and run `no-negative-echo` last.

At minimum this applies to:

- `research_brief.md`;
- `current_understanding.md`;
- `research_landscape.md`;
- `implementation_plan.md`;
- `FINAL.md`.

`no-negative-echo` must regenerate or clean the report from the accepted current state, while preserving real current risks, unresolved questions, comparison results needed for a decision, safety/compatibility constraints, and required audit facts.

Do **not** apply this cleanup to `research_state/`, `history/`, retained-source notes, search/evidence logs, decision history, pitfall history, or Dida machine handoff state. Those artifacts intentionally preserve process and provenance.

For `FINAL.md`, the order is:

```text
validate/audit current state
→ regenerate FINAL.md
→ apply document/style rules
→ run no-negative-echo
→ final read-back
```

## Dida boundary

Research determines what should be done and what outputs/acceptance criteria are required. Dida owns task breakdown, estimation, scheduling, and progress.

Research writes `dida_handoff.yaml` only. It must not silently mutate the user's task plan.

If Dida skills are available, hand off approved work packages to:

1. `dida-task-breakdown`
2. `dida-task-estimator`
3. `dida-task-capture`
4. `dida-daily-planner`

`dida_handoff.yaml` must not pre-invent calendar dates, priorities, or estimated durations. Those belong to Dida.

Use `scripts/build_dida_bridge.py` only after handoff status is `APPROVED`; it emits a neutral bridge record with no schedule/estimate fields populated.

Changes caused by a revised research conclusion require user approval before existing Dida tasks are removed, postponed, or materially changed.

## Quality gates

Before calling a prestudy complete:

1. Run `scripts/validate_state.py`.
2. Run `scripts/prestudy_audit.py`.
3. Resolve all ERRORs.
4. Review WARNs; do not ignore safety/feasibility warnings.
5. Regenerate `FINAL.md`.
6. Run the human-facing finalization sequence above on `FINAL.md`.
7. If handing off to Dida, export the bridge only after user approval.

The audit checks include:

- state/schema integrity;
- duplicate IDs;
- FACT/INFERENCE traceability;
- explicit saturation evidence;
- retained-source budget;
- retained-source reading notes and local-file presence;
- HIGH/CRITICAL pitfall evidence/mitigation;
- blocker leakage into approved handoff;
- pitfall -> project-plan traceability;
- confirmed-decision evidence;
- final report scaffolding.

## Distribution boundary

The skill package must never contain real `.prestudy/`, user context, downloaded libraries, Dida task data, credentials, or local project paths.

Run the existing distribution audit before publishing or sharing the skill package.
