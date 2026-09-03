---
name: datasheet-to-design-guide
description: Use when the user provides an IC/component datasheet and wants a traceable engineering usage guide and design-review checklist, or wants to review a schematic/PCB against the datasheet. Extract requirements from the source rather than relying on generic electronics knowledge. Every requirement must be traceable to the datasheet.
---
# Datasheet to Design Guide

Turn a component datasheet into an engineering artifact that can be used both to design with the part and to review a design later.

Input: one datasheet, preferably the exact revision used by the design.

Output:

```text
<part-number>/
├── usage-guide.md
├── checklist.md
└── PROVENANCE.md
```

The goal is not to summarize the datasheet. The goal is to answer two questions:

1. How should this part be used in a real design?
2. What must be checked before the schematic and PCB can be considered compliant with the datasheet?

<master_rules>
## Rules that hold across all phases

1. **No requirement without a source anchor.** Every extracted design requirement must include a short verbatim source anchor and a location: PDF page plus section/table/figure/note when available.
2. **Do not infer missing requirements.** Generic engineering knowledge may be used to explain a datasheet rule, but it must never be presented as a datasheet requirement unless the source states it.
3. **Conditions belong to the requirement.** A limit without its test condition, operating condition, mode, temperature range, supply range, or footnote is incomplete.
4. **Exact device identity matters.** Verify part number, grade, package, revision, and variant. Do not silently mix limits from related devices.
5. **Notes and footnotes are first-class source material.** Scan table notes, figure notes, equation notes, pin descriptions, application sections, and layout sections deliberately. Many design-breaking constraints live there.
6. **Separate fact from calculation.** Datasheet values are source facts. Derived resistor values, gains, currents, powers, margins, and tolerances are calculations and must show inputs and formula.
7. **Unknown is allowed.** If the datasheet is ambiguous or the source is incomplete, mark the item `UNCLEAR` rather than filling the gap from intuition.
8. **Design review must be scoped.** Once a checklist item has been verified, later changes reopen only the checklist items that depend on the changed nets/components/parameters unless a newly discovered requirement expands the scope.
</master_rules>

<phase_0>
## Phase 0 — Establish the source

Before extraction, record:

- exact part number and orderable variant if visible;
- datasheet title;
- document revision/date;
- package(s) relevant to the user's design;
- whether the source appears complete and readable.

If the source is truncated, corrupted, or the device variant cannot be identified when the distinction affects limits, stop and report the uncertainty.

Write this information to `PROVENANCE.md`.
</phase_0>

<phase_1>
## Phase 1 — Extract requirements

Read `references/01-extraction.md` before extracting.

Run separate passes for these requirement classes:

A. Power, grounding, bias, startup, shutdown, sequencing, UVLO and supply current.
B. Input/output electrical limits, source/load impedance, bias current, common-mode/differential range and drive capability.
C. External components and equations: resistor/capacitor/inductor/transformer values, gain networks, filters, compensation and protection.
D. Functional behavior: modes, timing, clocks, interfaces, logic thresholds, enable/fault behavior and state transitions.
E. Absolute maximum, recommended operating conditions, thermal, reliability, isolation, creepage/clearance and protection limits.
F. PCB/layout/placement/routing/decoupling/thermal/EMI guidance that can change implementation.
G. **Hidden conditional constraints:** table footnotes, figure notes, pin-description caveats, test conditions, application-section restrictions, maximum current through external networks, source-resistance limits, settling constraints, startup exceptions, and requirements stated only in prose.

Do not merge passes A–G mentally. The G pass is mandatory even when earlier passes look complete.

Each candidate must use the schema in `references/01-extraction.md`.
</phase_1>

<phase_2>
## Phase 2 — Validate the extracted set

Read `references/02-validation.md`.

Validation must be performed as a separate pass from extraction. Prefer a different agent/model when available.

For every candidate:

1. mechanically verify the source anchor exists;
2. verify the stated condition and units;
3. verify it applies to the exact part/variant/package;
4. check whether another datasheet section narrows, overrides, or qualifies it;
5. classify it as `REQUIRED`, `RECOMMENDED`, `INFORMATIONAL`, or `UNCLEAR`;
6. merge true duplicates without losing stricter conditions.

Then run a **coverage challenge**: search specifically for constraints not yet represented in the candidate set, especially words and structures such as `must`, `should`, `do not`, `maximum`, `minimum`, `recommended`, `required`, `only`, `when`, `unless`, `note`, `see`, footnote markers, equation conditions, and layout callouts.
</phase_2>

<phase_3>
## Phase 3 — Build the usage guide and checklist

Read `references/03-output-format.md`.

### `usage-guide.md`

Organize by engineering task, not by datasheet chapter. Typical routing:

- Device role and signal path
- Power and grounding
- Input/front-end design
- Output/interface design
- External component calculations
- Protection and abnormal conditions
- Timing/control behavior
- PCB/layout/thermal/isolation

Only include material that changes how the device is designed or reviewed.

### `checklist.md`

Every actionable requirement becomes one checklist row/item with a stable ID.

A checklist item must tell a reviewer:

- what must be true;
- under what condition;
- where the requirement came from;
- what schematic/PCB object it applies to;
- how to verify it;
- what other items must be reopened if this item changes.

Do not create a separate “notes” or “attention points” document. If a note matters to design, it belongs in the checklist or usage guide.
</phase_3>

<phase_4>
## Phase 4 — Calculation discipline

Calculations are allowed only after the source facts have been extracted.

For each engineering calculation record:

1. input variables and source anchors;
2. formula before code;
3. units for every input and result;
4. script result;
5. at least one independent sanity check: inverse calculation, limiting-case check, dimensional check, or order-of-magnitude check.

The script is not evidence that the formula or inputs are correct. The calculation is accepted only when source inputs and formula have both been reviewed.

When reviewing an existing design, report the minimum human-review surface first: source inputs, formula/criterion, and PASS/FAIL. Do not require the user to redo arithmetic that has already passed automated and independent checks.
</phase_4>

<phase_5>
## Phase 5 — Review a schematic or PCB with the generated checklist

When a schematic/PCB is supplied later:

1. map each relevant checklist ID to concrete nets, pins, components, values, and layout regions;
2. mark `PASS`, `FAIL`, `N/A`, or `UNCLEAR` with evidence;
3. do not mark the whole design “verified” while any applicable `REQUIRED` item is `FAIL` or `UNCLEAR`;
4. after a change, reopen only dependent checklist IDs plus any newly discovered requirement.

If a new valid datasheet requirement is discovered during review, add a new stable checklist ID and record why it was previously absent. Do not silently rewrite old review history.
</phase_5>

<self_check>
## Check before delivering

- Every `REQUIRED`/`RECOMMENDED` checklist item has a source anchor and exact location.
- No value is detached from its condition or footnote.
- A dedicated hidden-constraint pass was completed.
- Absolute maximum ratings are not presented as normal design targets.
- Recommended operating conditions and electrical-characteristic test conditions are distinguished.
- Related device variants have not been mixed.
- All derived values show inputs, formula, units, and a sanity check.
- `usage-guide.md` tells an engineer how to use the part; it does not retell the datasheet.
- `checklist.md` is sufficient to review a schematic/PCB without rereading the entire datasheet for already-extracted requirements.
</self_check>

## Attribution

This skill is adapted from the workflow ideas in `book-to-skill` by Sergey Lebedev / Londeren, especially source anchoring, independent validation, task-oriented output routing, and provenance tracking. The upstream project is MIT licensed. See `LICENSE` and `NOTICE.md`.
