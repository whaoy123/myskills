---
name: research-understanding
description: Help the user understand a technical topic by bridging from their existing knowledge, maintaining a project-specific knowledge model, identifying prerequisite gaps and misconceptions, and iterating between explanation, questions, and targeted research. Use before or during engineering research when the user does not yet have a stable mental model of what the system is, how it works, or what they need to do.
---

# Research Understanding

Run the understanding loop for an `engineering-prestudy` project.

## Inputs

Read:

- unified user context from `user-context-profile`;
- `research_state/project.yaml`;
- `research_state/knowledge_model.yaml`;
- `research_state/research_questions.yaml`;
- `research_state/open_questions.yaml`;
- relevant existing evidence and user-provided materials.

## Core objective

Do not merely summarize a textbook. Build a mental model that connects the new topic to concepts the user already understands.

## Interaction pacing

Keep interactive explanations concise and locally focused.

- Each reply should primarily answer the question or conceptual gap that is most directly connected to the user's immediately previous message.
- Advance one useful conceptual step at a time; do not expand into downstream architecture, implementation details, alternatives, or future steps unless they are necessary to understand the current point or the user explicitly asks for them.
- Prefer a short explanation plus one next question over a complete lecture when the user is still building the mental model interactively.
- If a broader issue is relevant but not needed yet, keep it in project state/open questions instead of surfacing it immediately.
- Avoid repeating already-established background unless it is required to connect the next concept.
- When the user asks for more detail, deepen only that branch first before resuming the wider understanding loop.

## Understanding loop

1. Identify what the user already knows that can anchor the explanation.
2. Identify the smallest conceptual gap blocking the current goal.
3. Explain using existing knowledge, physical intuition, causal flow, concrete system behavior, and only then formulas when useful.
4. Let the user challenge the model or supply their own interpretation.
5. Record misunderstandings or gaps as project state, not global deficiencies.
6. If a factual question requires external evidence, create/activate a research question and hand it to `research-landscape`.
7. Update the project knowledge model when understanding changes.
8. Continue until the user can explain the relevant process well enough for the next engineering step.

## Knowledge categories

`knowledge_model.yaml` separates:

- `inherited`: relevant global knowledge brought in at project start;
- `known`: project-specific concepts currently understood;
- `current_beliefs`: tentative mental models or assumptions;
- `unclear`: unresolved conceptual gaps;
- `confirmed_updates`: newly established understanding;
- `promotion_candidates`: knowledge potentially reusable across projects.

## Promotion boundary

Do not directly edit the global user profile. Add a promotion candidate and let `user-context-profile` decide whether it becomes durable global knowledge.

## Output

Maintain project state and generate/update:

```text
reports/current_understanding.md
```

The human-readable report should contain:

1. what the system/topic is;
2. how it works step by step;
3. bridges to the user's existing knowledge;
4. what the user currently understands;
5. remaining conceptual gaps;
6. the next most useful concept/question.

Keep the report explanatory, not a dumping ground for source lists.

## Human-facing finalization

Before `reports/current_understanding.md` is treated as the current human-readable report or handed to another stage, run `no-negative-echo` on that report after its technical content is settled.

The finalization pass should describe the accepted current understanding directly and remove rejected session-only wording or stale conversational alternatives that no longer belong in the report.

Do **not** apply this cleanup to `knowledge_model.yaml`, `research_questions.yaml`, `open_questions.yaml`, evidence records, or other authoritative project state. Those files must preserve the real knowledge state, uncertainty, and history needed by the research workflow.
