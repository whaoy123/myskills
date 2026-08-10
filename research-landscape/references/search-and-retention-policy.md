# Research Landscape v1 — Search and Retention Policy

## Purpose

This is an engineering pre-study workflow, not an exhaustive systematic review.

The goal is to reach **decision sufficiency**:

- understand what the thing is and how predecessors usually do it;
- understand the current representative approaches and their trade-offs;
- identify one or more credible examples worth borrowing from;
- surface the mistakes, hidden constraints, safety issues, and redesign traps that predecessors or newcomers commonly encounter;
- know what still blocks the next engineering decision;
- stop before research time grows faster than decision value.

Do not optimize for maximum source count, paper count, or download count.

## Default search funnel

### Phase A — Orientation search

Search broadly enough to build the landscape before deep reading.

Cover applicable perspectives such as:

- principles / architecture;
- standards and official documentation;
- representative products or commercial implementations;
- academic papers or review papers;
- open-source projects;
- known limitations / failure modes;
- competing or alternative approaches;
- test and verification methods.

Default behavior:

- inspect roughly 6–12 promising candidates;
- usually do not download them yet;
- record useful candidates and the reason they matter;
- prefer diversity of source type over many near-duplicate results.

These counts are guidance, not quotas. Stop the orientation pass early when the landscape is already clear.

### Phase B — Seed selection and deep reading

Choose only the few sources that best explain the important routes.

Default target:

- 2–4 seed sources for deeper inspection;
- at least one primary/authoritative source when the question has factual technical specifications;
- at least one concrete implementation/example when the project needs to learn how predecessors actually built it.

For each seed source, extract:

- what problem it solves;
- architecture / method;
- key implementation choices;
- constraints and limitations;
- warnings / errata / known problems / important boundary conditions;
- what is reusable in the current project;
- what is not directly transferable;
- evidence locators for important claims.

### Phase C — One-round snowballing

Use backward/forward citation expansion, referenced standards/app notes, related repositories, issues, errata, troubleshooting material, or linked implementations only from strong seed sources.

Default limit: **one expansion round**.

Continue beyond one round only when a blocking research question remains unresolved, a high-impact pitfall remains unclear, or the expansion reveals a materially different route that could change the engineering decision.

Do not snowball merely to increase source count.

### Phase D — Mandatory pitfall / hazard discovery

Do not assume that understanding a working implementation is enough.

Explicitly ask:

> If a competent newcomer follows the obvious design path, what are they likely to overlook, violate, mis-measure, damage, or discover only after a redesign?

This pass searches for **unknown unknowns** and hidden engineering constraints.

Select relevant lenses based on the project domain.

For hardware/electrical work, common lenses include:

- voltage/current/power extremes and transients;
- creepage, clearance, insulation, isolation and environmental assumptions;
- floating systems, common-mode, ground/shield/chassis relationships and ground loops;
- measurement loading and unsafe probing/reference choices;
- transformer/CT/sensor failure states;
- startup/shutdown/hot-plug/inrush/surge behavior;
- overvoltage/overcurrent/reverse-polarity/fault protection;
- connector/trace/via current and heating;
- thermal derating and lifetime;
- EMC, signal integrity and filter-bandwidth side effects;
- manufacturing, assembly, test access and bring-up hazards;
- standards/certification/safety requirements.

For FPGA/software/algorithm work, common lenses include:

- clock/reset/CDC and boundary conditions;
- protocol corner cases and interoperability;
- resource, latency and memory limits;
- numerical overflow, quantization and precision;
- data leakage and train/deploy mismatch;
- dependency/toolchain/version incompatibility;
- error handling, recovery and observability;
- incomplete verification and happy-path-only tests.

Preferred evidence sources for pitfalls:

1. official warnings, safety sections, standards, errata and application notes;
2. original repository issues/discussions/changelogs with reproducible detail;
3. failure-analysis reports, engineering postmortems and credible case studies;
4. community reports as discovery leads.

A community anecdote may identify a risk, but high-impact safety/feasibility constraints should be confirmed with stronger evidence when reasonably available.

Record relevant items in `pitfalls.yaml`, not as an unbounded generic checklist.

Each pitfall should capture:

- failure mode / mistake;
- why it happens;
- consequence;
- scope/trigger/conditions;
- mitigation/prevention;
- supporting FACT/INFERENCE IDs;
- impact;
- action type: design constraint, verification item, blocker, or watch item;
- current status.

### Phase E — Contrarian check

Before declaring the landscape sufficient, actively search for one of the following when relevant:

- a credible alternative architecture;
- a failure case;
- a known limitation;
- a newer revision that invalidates an older source;
- evidence contradicting the current preferred interpretation.

The purpose is to prevent premature convergence, not to restart the whole research process.

## Download / retention policy

### Default retained-download budget

For a normal pre-study topic, retain/download **1–2 core artifacts**.

Do not treat this as 1–2 sources total. Many sources may be inspected and cited without being downloaded.

Preferred pair when both exist:

1. **Reference source** — the strongest source for understanding the principle/specification and important constraints, such as an official standard/manual/datasheet, a strong review, or a foundational paper.
2. **Implementation source** — the strongest predecessor example, such as an original open-source repository, complete engineering project, detailed implementation paper, application note, or teardown/design document.

Prefer retained artifacts that also preserve high-value warnings or practical lessons.

One artifact is enough when it already covers both roles or when only one item is truly worth future reading.

A third download requires an explicit reason, such as:

- a mandatory standard plus a separate implementation plus a separate test/safety reference;
- two fundamentally different routes both remain viable and both must be compared;
- the extra artifact resolves a blocking question or high-impact pitfall that the selected pair cannot answer.

### Selection criteria

Prefer an artifact when several of these are true:

- directly relevant to the current goal;
- primary or authoritative;
- contains enough detail to teach from later;
- contains concrete implementation details, code, schematics, test methods, parameters, warnings or boundary conditions;
- representative rather than unusual;
- current enough for the topic;
- likely to be reused during implementation;
- difficult to reconstruct later from a short citation alone.

Do not retain locally merely because the source is good. Stable official webpages can remain URL-only when offline preservation adds little value.

### Mandatory note for retained artifacts

Every retained artifact gets `notes/<SourceID>.md` containing:

- why it was selected over other candidates;
- what to read first;
- key pages / sections / files;
- what can be borrowed;
- what should not be copied directly;
- warnings / pitfalls / boundary conditions worth remembering;
- which research questions it answers;
- related FACT / INFERENCE / PITFALL IDs.

For a repository, name concrete files/directories.

## Stop conditions — decision sufficiency

A research question can move to `SATURATED` when all applicable conditions are met:

1. **Mechanism understood** — the project can explain the relevant process/architecture well enough to continue design discussions.
2. **Current landscape known** — the main representative approaches are identified; obscure edge variants are not required.
3. **Predecessor known** — at least one credible predecessor/example shows how the work is actually done, when such an example exists.
4. **Pitfalls surfaced** — high-impact hidden constraints and likely mistakes have been actively searched for and either handled or explicitly recorded.
5. **Evidence adequate** — important factual claims have sufficiently strong support, preferably primary sources where available.
6. **Trade-offs visible** — the major reasons to choose between viable routes are known.
7. **Blocking unknowns handled** — blocking questions are resolved or explicitly routed to experiment/user decision/future investigation.
8. **Low marginal value** — the latest search/snowball/pitfall pass did not reveal a new route, materially change the recommendation, surface a new high-impact risk, or resolve a blocking issue.

Do not require every open question or pitfall to be closed. Non-blocking unknowns and watch items may remain recorded.

## Continue-research triggers

Continue despite the normal stopping rule when:

- a blocking question prevents architecture or safety decisions;
- a potentially critical pitfall has not been bounded;
- primary sources materially disagree;
- the current recommendation depends on an unverified assumption;
- a credible alternative route could change cost, feasibility, safety, performance, or schedule materially;
- the user explicitly asks for deeper literature coverage.

## Output bias

The final landscape report should be selective and action-oriented.

Prefer:

- 1–3 representative routes;
- what predecessors did;
- why each route works;
- what predecessors/newcomers commonly get wrong;
- high-impact hidden constraints that must be carried into design;
- what is worth borrowing;
- the selected 1–2 retained materials and a reading guide;
- remaining blocking questions and risks;
- what information is now sufficient to enter design/planning.

Avoid long catalogues of similar papers/products/projects unless comparison itself is the research goal.
