# Research Landscape v1 — Search and Retention Policy

## Purpose

This is an engineering pre-study workflow, not an exhaustive systematic review.

The goal is to reach **decision sufficiency**:

- understand what the thing is and how predecessors usually do it;
- understand the current representative approaches and their trade-offs;
- identify one or more credible examples worth borrowing from;
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
- what is reusable in the current project;
- what is not directly transferable;
- evidence locators for important claims.

### Phase C — One-round snowballing

Use backward/forward citation expansion, referenced standards/app notes, related repositories, issues, or linked implementations only from strong seed sources.

Default limit: **one expansion round**.

Continue beyond one round only when a blocking research question remains unresolved or the expansion reveals a materially different route that could change the engineering decision.

Do not snowball merely to increase source count.

### Phase D — Contrarian check

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

1. **Reference source** — the strongest source for understanding the principle/specification, such as an official standard/manual/datasheet, a strong review, or a foundational paper.
2. **Implementation source** — the strongest predecessor example, such as an original open-source repository, complete engineering project, detailed implementation paper, application note, or teardown/design document.

One artifact is enough when it already covers both roles or when only one item is truly worth future reading.

A third download requires an explicit reason, such as:

- a mandatory standard plus a separate implementation plus a separate test/verification reference;
- two fundamentally different routes both remain viable and both must be compared;
- the extra artifact resolves a blocking question that the selected pair cannot answer.

### Selection criteria

Prefer an artifact when several of these are true:

- directly relevant to the current goal;
- primary or authoritative;
- contains enough detail to teach from later;
- contains concrete implementation details, code, schematics, test methods, or parameters;
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
- which research questions it answers;
- related FACT / INFERENCE IDs.

For a repository, name concrete files/directories.

## Stop conditions — decision sufficiency

A research question can move to `SATURATED` when all applicable conditions are met:

1. **Mechanism understood** — the project can explain the relevant process/architecture well enough to continue design discussions.
2. **Current landscape known** — the main representative approaches are identified; obscure edge variants are not required.
3. **Predecessor known** — at least one credible predecessor/example shows how the work is actually done, when such an example exists.
4. **Evidence adequate** — important factual claims have sufficiently strong support, preferably primary sources where available.
5. **Trade-offs visible** — the major reasons to choose between viable routes are known.
6. **Blocking unknowns handled** — blocking questions are resolved or explicitly routed to experiment/user decision/future investigation.
7. **Low marginal value** — the latest search/snowball pass did not reveal a new route, materially change the recommendation, or resolve a blocking issue.

Do not require every open question to be closed. Non-blocking unknowns may remain recorded.

## Continue-research triggers

Continue despite the normal stopping rule when:

- a blocking question prevents architecture or safety decisions;
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
- what is worth borrowing;
- the selected 1–2 retained materials and a reading guide;
- remaining blocking questions;
- what information is now sufficient to enter design/planning.

Avoid long catalogues of similar papers/products/projects unless comparison itself is the research goal.
