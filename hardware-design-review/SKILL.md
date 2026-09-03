---
name: hardware-design-review
description: Use when reviewing an electronic hardware design from schematic PDF, Altium netlist, BOM, datasheet-derived reference modules, project operating conditions, PCB screenshots/rules/exports, or a previous review state. Build a normalized design model, load only applicable device/interface/power/isolation/PCB rules, execute traceable checks and script-based calculations, evaluate complete signal chains, and report PASS/FAIL/UNCLEAR/N/A with evidence and incremental-review dependencies.
---
# Hardware Design Review

Review hardware as a traceable rule-execution problem, not as a visual plausibility check.

Core flow:

`inputs -> DesignFacts -> DesignGraph -> applicable Reference Modules -> checklist execution -> scripted calculations -> cross-device checks -> PCB checks -> PASS/FAIL/UNCLEAR/N/A -> ReviewState`

The core skill MUST remain device-independent. Never embed individual IC limits, pin rules, divider values, decoupling values, or layout requirements in this file. Those belong in `references/` modules generated from authoritative sources.

## 1. Inputs and evidence authority

Supported evidence includes:

- schematic PDF;
- Altium `.NET` or other netlist;
- BOM in XLSX/XLS/CSV;
- raw datasheets/application notes;
- datasheet-derived `usage-guide.md`, `checklist.md`, `PROVENANCE.md`, `module.yaml`;
- PCB screenshots, rules, fabrication/ODB/IPC exports, or PCB design files when readable;
- project operating conditions and external interface definitions;
- previous `.hardware-review/` state.

Use each source only for facts it can establish reliably:

1. Netlist: electrical connectivity.
2. BOM: installed value, MPN, package and population intent.
3. Schematic PDF: circuit intent, annotations, visible topology and design notes.
4. Project context: system operating assumptions, external voltage/current/frequency/temperature ranges.
5. Reference modules: engineering requirements and source provenance.
6. PCB design data: placement, routing, copper, layers, distances and rule values.
7. PCB screenshots: only what is visibly provable in the supplied view.

When sources conflict, record the conflict. Do not silently choose one. An affected rule is `UNCLEAR` unless one source is explicitly authoritative for that property.

## 2. Persistent project state

For a review that may be repeated, create or update beside the project:

```text
.hardware-review/
├── project-context.yaml
├── input-manifest.json
├── design-snapshot.json
├── design-graph.json
├── loaded-modules.json
├── calculations/
├── results.json
├── review-state.json
└── review-report.md
```

Do not store project-specific review state inside this Skill repository.

## 3. Phase A — Inventory the review inputs

Create `input-manifest.json` with file name, type, revision/hash when available, extraction status and known limitations.

Before final evaluation, determine whether the PDF/BOM/netlist/PCB evidence refer to the same design revision. Version mismatch is itself a review finding.

## 4. Phase B — Extract normalized DesignFacts

A DesignFact is one atomic statement about the actual design. Follow `schemas/design-fact.schema.json`.

Examples:

- `COMPONENT:R17:value = 200 kohm`
- `COMPONENT:U3:part_number = ...`
- `PIN:U3.4:net = NET_INP`
- `NET:+5V:nominal_voltage = 5 V`
- `PCB:U3:C17:edge_distance = 1.2 mm`

Every fact must retain its source/evidence location and confidence.

Never invent an unknown operating value. Missing required values remain unresolved and can cause `UNCLEAR`.

## 5. Phase C — Build the DesignGraph

Represent the design as:

`Component -> Pin -> Net -> Component -> Functional Block -> Power/Ground/Isolation Domain`

Annotate semantic roles only when supported by evidence, for example divider, filter, amplifier, isolation amplifier, ADC, regulator, DC/DC, shunt, connector, protection, reference or load.

The graph is required for cross-device checks and impact propagation.

## 6. Phase D — Resolve applicable Reference Modules

Read `references/README.md` and `schemas/reference-module.schema.json`.

Resolve modules from the actual design using, in order:

1. exact part number and orderable variant;
2. family/package-sensitive selector;
3. detected interface structure;
4. detected power topology;
5. detected isolation topology;
6. detected PCB/layout structure;
7. system-level signal-chain/power-budget rules.

Load only applicable modules. A datasheet being present does not prove the device is populated.

If an exact variant/package matters but cannot be resolved, mark the affected rule/module selection `UNCLEAR`.

Legacy device folders containing only `usage-guide.md`, `checklist.md` and `PROVENANCE.md` may be used through a compatibility adapter, but native `module.yaml` is preferred because it declares selectors, required facts and invalidation dependencies explicitly.

## 7. Phase E — Validate modules before execution

Before using a module:

- validate required top-level fields;
- require unique stable rule IDs;
- require the referenced guide/checklist/provenance files;
- verify every declared rule ID exists in `checklist.md`;
- verify declared source/provenance mapping is not missing;
- preserve module-declared ambiguities;
- do not silently turn an `UNCLEAR` source rule into a numeric limit.

Use `scripts/validate_module.py` when a native `module.yaml` is available.

## 8. Phase F — Determine rule scope

For every component instance, interface, power domain, isolation domain, layout structure and signal chain:

`selector -> applicability condition -> required facts -> required evidence -> required calculation -> dependencies`

A demonstrably inapplicable rule is `N/A`.

An applicable rule with missing evidence is `UNCLEAR`, not PASS.

## 9. Phase G — Connection checks first

Connectivity failures can invalidate later numerical analysis, so check them before parameter calculations.

Typical rule classes:

- required/forbidden/floating pin connections;
- supply, ground and reference pins;
- isolation-domain separation;
- differential polarity;
- mandatory external components and DC paths;
- connector pin mapping;
- return-path/domain connection requirements.

Prefer netlist evidence for connectivity. A drawing that looks connected does not override an unambiguous netlist.

## 10. Phase H — Electrical and peripheral checks

Apply only rules loaded from the relevant modules. Typical dimensions include:

- Recommended Operating Conditions;
- Absolute Maximum Ratings;
- differential/common-mode input range;
- output range and load;
- current, power, temperature, startup/brownout/fail-safe;
- divider, gain, RC, resistor power/working voltage, loading and bias-current error;
- shunt, bandwidth, slew rate and stability;
- decoupling value/count/ESR/dielectric/DC-bias;
- supply current and rail headroom.

Recommended Operating Conditions and Absolute Maximum Ratings are separate rule classes. Passing absolute maximum does not prove correct normal operation.

## 11. Phase I — Numerical calculation discipline

Any numerical result that can change `PASS` or `FAIL` MUST be produced by a script.

Each calculation record must preserve:

`input parameters -> units -> formula/model -> nominal result -> tolerance/worst-case -> sanity or inverse check -> compared limit -> assertion`

Use `templates/calculation-record.json` as the record shape. `scripts/engineering_calc.py` provides common divider/gain/RC/resistor-power helpers, but a project-specific script is allowed when the formula is different.

Rules:

- write the formula before accepting the result;
- reject incompatible units rather than silently convert dimensions;
- include tolerance/worst-case when it can change compliance;
- preserve RMS/peak/peak-to-peak and differential/common-mode semantics explicitly;
- perform an inverse, dimensional, limiting-case, or order-of-magnitude sanity check where practical;
- save the calculation record under `.hardware-review/calculations/`.

The script result alone is not evidence that the formula or source input was correct.

## 12. Phase J — Cross-device and signal-chain checks

Never conclude that a system is valid only because each IC passes its own checklist.

Trace every relevant chain:

`source -> protection/divider/filter -> device A -> interstage network -> device B -> ADC/load`

At every boundary compare upstream behavior with downstream requirements, including when applicable:

- output/input amplitude range;
- common-mode range;
- source/load impedance;
- gain and polarity;
- rail headroom and clipping;
- bandwidth and slew rate;
- reference/ground/isolation domain;
- fault and fail-safe propagation.

A chain passes only when the required boundaries close under the defined operating conditions and worst cases.

## 13. Phase K — Power/domain/system checks

Use the DesignGraph to aggregate rather than inspect devices in isolation.

Examples:

- rail load -> source capability -> efficiency/derating -> margin;
- isolated-side load -> isolated converter capability;
- reference-source loading -> all dependent loads;
- fault path -> protection element -> device absolute maximum;
- isolation domain -> all conductive crossings.

Rules may come from device modules and from generic `power/`, `isolation/` or `system/` modules.

## 14. Phase L — PCB checks

Load only applicable PCB/layout rules. Typical classes:

- decoupling placement and loop;
- feedback loop;
- sensitive trace routing;
- differential symmetry;
- Kelvin routing;
- return current;
- keepout;
- creepage/clearance;
- isolation barrier;
- copper/trace/via under a component when restricted.

Evidence limits are strict. A top-layer screenshot cannot prove that an isolation keepout is clear on all copper layers. If a rule requires information not visible or extractable, return `UNCLEAR` and state exactly what PCB evidence is missing.

## 15. Result state

Only these final states are allowed:

- `PASS`: evidence demonstrates compliance.
- `FAIL`: evidence demonstrates violation.
- `UNCLEAR`: applicable but insufficient or conflicting evidence prevents a reliable decision.
- `N/A`: demonstrably not applicable.

Every `UNCLEAR` must state the missing/conflicting information and what would resolve it.

Never promote uncertainty to PASS.

## 16. Result record

Every evaluated rule must preserve:

- result ID;
- rule ID and module ID/version;
- affected component/net/block/PCB region;
- actual design fact(s);
- rule/limit;
- calculation record when applicable;
- status;
- evidence/source location;
- modification recommendation for FAIL;
- missing evidence for UNCLEAR;
- dependency keys;
- review revision.

Use namespaced rule IDs in stored results, for example `device:<module-id>:<rule-id>` or `pcb:<module-id>:<rule-id>`.

## 17. Incremental review

Follow `schemas/review-state.schema.json`.

Every stored result must list the DesignFacts, assumptions, calculation model and reference-module version that can invalidate it.

Example dependency keys:

- `COMPONENT:R17:value`
- `COMPONENT:U3:part_number`
- `PIN:U3.4:net`
- `NET:+5V:nominal_voltage`
- `PCB:U3:C17:edge_distance`
- `ASSUMPTION:VIN_MAX`
- `REFERENCE:device:manufacturer:part:revision`
- `CALC_MODEL:resistor-divider:v1`

For a new revision:

`previous snapshot -> current snapshot -> changed facts -> impacted rules -> transitive dependent rules -> affected signal chains`

Use `scripts/diff_design.py` to identify directly changed facts. Re-run transitive dependents through the DesignGraph/review dependency graph.

A previous result may be retained only if all of its dependency facts, reference versions and calculation models are unchanged.

Do not reset an entire board review because one unrelated component changed.

## 18. Final report

Begin with blocking findings, then unresolved items, then concise retained-pass information.

For each non-PASS finding include:

| ID | Actual design | Datasheet / Rule | Calculation | Status | Evidence | Required change / missing evidence |
|---|---|---|---|---|---|---|

Also report:

- PASS / FAIL / UNCLEAR / N/A counts;
- modules loaded;
- changed DesignFacts since the previous revision;
- checks re-opened because of those changes;
- previous results retained without re-review;
- unresolved source ambiguities.

Do not call a design fully verified while any applicable `REQUIRED` rule remains `FAIL` or `UNCLEAR`.

## 19. Self-check before delivery

- Device-specific requirements came from reference modules, not generic memory.
- Connectivity was checked before dependent calculations.
- Every decision-changing calculation was script-produced and recorded.
- Absolute maximum and normal operating ranges were not conflated.
- Cross-device boundaries and complete signal chains were checked.
- PCB claims do not exceed the available PCB evidence.
- Every UNCLEAR names the exact missing evidence.
- Incremental results are reused only when their dependency keys remain unchanged.
