---
name: datasheet-to-design-guide
description: Use when the user provides an IC/component datasheet and wants a traceable engineering usage module. Convert the exact datasheet/variant into usage-guide.md, checklist.md, PROVENANCE.md, and machine-readable module.yaml for direct loading by hardware-design-review. Extract requirements from the source rather than generic electronics knowledge; every requirement must remain traceable to the datasheet and preserve conditions, ambiguity and applicability.
---
# Datasheet to Design Guide

Turn one component datasheet into a reusable engineering Reference Module.

This Skill extracts device knowledge. Concrete board-level schematic/PCB review should use the generated module with `hardware-design-review`.

Input: one datasheet, preferably the exact revision used by the design.

Output:

```text
<part-number>/
├── usage-guide.md
├── checklist.md
├── PROVENANCE.md
└── module.yaml
```

The four files form one interface:

- `usage-guide.md`: how to use the part correctly;
- `checklist.md`: stable executable engineering review rules;
- `PROVENANCE.md`: exact source locations, extraction decisions and unresolved ambiguity;
- `module.yaml`: machine index used by `hardware-design-review` to select the module and map rules to required facts/evidence/dependencies.

`module.yaml` MUST NOT become a second full copy of the datasheet rules.

<master_rules>
## Rules that hold across all phases

1. **No requirement without a source anchor.** Every extracted design requirement must include a short verbatim source anchor and a location: PDF page plus section/table/figure/note when available.
2. **Do not infer missing requirements.** Generic engineering knowledge may explain a datasheet rule, but must never be presented as a datasheet requirement unless the source states it.
3. **Conditions belong to the requirement.** A limit without its test condition, mode, temperature, supply range or footnote is incomplete.
4. **Exact device identity matters.** Verify part number, grade, package, revision and variant. Do not silently mix related devices.
5. **Notes and footnotes are first-class source material.** Scan table notes, figure notes, equation notes, pin descriptions, application sections and layout sections deliberately.
6. **Separate source fact from derived calculation.** Datasheet values are facts. Derived resistor values, gains, currents, powers, margins and tolerances are calculations and must show inputs and formula.
7. **Unknown is allowed.** Ambiguous or incomplete source material becomes `UNCLEAR`; never fill it from intuition.
8. **Stable IDs are part of the public interface.** Do not renumber existing checklist IDs merely because wording changes. Add a new ID when a genuinely new requirement is discovered.
9. **Machine metadata never outranks provenance.** `module.yaml` indexes the rule; `checklist.md` and `PROVENANCE.md` remain the human-readable requirement and authority record.
10. **Design-review dependencies must be declared.** Each actionable rule should identify the design facts that can invalidate a future PASS result.
</master_rules>

<phase_0>
## Phase 0 — Establish the source and module identity

Before extraction, record exact part number/orderable variant, manufacturer, datasheet title, revision/date, package scope, package/grade differences, and source completeness. Write these facts to `PROVENANCE.md` and use them to populate `module.yaml` selectors.

If the source is truncated/corrupted or the applicable variant cannot be identified when it changes limits, stop and report the uncertainty.
</phase_0>

<phase_1>
## Phase 1 — Extract requirements

Read `references/01-extraction.md`. Run separate passes for A power/ground/startup, B I/O electrical limits, C external components/equations, D functional/timing/interface behavior, E absolute max/recommended/thermal/isolation, F PCB/layout/decoupling/EMI, and G hidden conditional constraints/footnotes. Pass G is mandatory.
</phase_1>

<phase_2>
## Phase 2 — Validate the extracted set

Read `references/02-validation.md`. Validation is a separate pass. For every candidate verify the source anchor, conditions/units, exact variant/package applicability, qualifiers/overrides, Strength (`REQUIRED`, `RECOMMENDED`, `APP`, `INFORMATIONAL`, `UNCLEAR`), required future DesignFacts/evidence, and invalidation dependencies. Then run a coverage challenge for missed constraint language and footnotes.
</phase_2>

<phase_3>
## Phase 3 — Build human-readable files

Read `references/03-output-format.md`.

`usage-guide.md` is task-oriented engineering guidance. `checklist.md` contains every actionable rule with stable ID, Strength, condition, source, applies-to, verification and `UNVERIFIED` source status. `PROVENANCE.md` records source identity, scope, extraction passes, validation method, ambiguities, application-vs-specification decisions and later rule additions.
</phase_3>

<phase_4>
## Phase 4 — Compile module.yaml

Read `references/04-module-interface.md` and create `module.yaml` only after checklist IDs are stable.

For every checklist rule declare: matching `id`, category/Strength, verification methods, required DesignFacts, required evidence types, affected object categories, invalidation dependency keys, and rule-to-rule dependencies where needed.

Do not duplicate full requirement prose, numeric limits or source quotations in `module.yaml` merely for convenience. Selectors must be conservative and cover only verified part/package variants.
</phase_4>

<phase_5>
## Phase 5 — Calculation discipline

Calculations are allowed only after source facts are extracted. Preserve inputs/source anchors, formula before code, units, script result and an inverse/limiting/dimensional/order-of-magnitude sanity check. Concrete design PASS/FAIL calculations belong to `hardware-design-review`.
</phase_5>

<phase_6>
## Phase 6 — Interface consistency check

Before delivery:

1. every `module.yaml` rule ID exists in `checklist.md`;
2. every actionable checklist rule is represented unless explicitly human-only;
3. companion file paths resolve;
4. selectors match `PROVENANCE.md` scope;
5. unresolved ambiguity is not converted to an unqualified machine rule;
6. dependencies are specific enough for incremental review.

Run `scripts/check_module_consistency.py`; when the sibling `hardware-design-review/scripts/validate_module.py` is available, run that validator too.
</phase_6>

<concrete_design_review>
## When a schematic/PCB is supplied together with the datasheet

First generate/update the four-file Reference Module, then use `hardware-design-review` for board-level review. That shared review engine owns DesignFacts, DesignGraph, script calculation records, PASS/FAIL/UNCLEAR/N/A and incremental ReviewState.

If board review discovers a valid missing datasheet rule, add a new stable checklist ID, update `module.yaml`, and record why it was added in `PROVENANCE.md`. Do not renumber historical IDs.
</concrete_design_review>

<self_check>
## Check before delivering

- Exact part/variant/package/revision is identified or explicitly unresolved.
- Every design rule has source anchor and exact location.
- No value is detached from its condition or footnote.
- Hidden-constraint pass completed.
- Absolute maximum is not treated as a normal design target.
- Application examples are not silently upgraded to component specifications.
- Related variants are not mixed.
- Derived values retain inputs, formula, units and sanity check.
- Checklist IDs are stable.
- `module.yaml` contains selectors/dependencies without duplicating the full rule corpus.
- All four files agree on scope.
</self_check>

## Attribution

This skill is adapted from workflow ideas in `book-to-skill` by Sergey Lebedev / Londeren, especially source anchoring, independent validation, task-oriented output routing and provenance tracking. The upstream project is MIT licensed. See `LICENSE` and `NOTICE.md`.
