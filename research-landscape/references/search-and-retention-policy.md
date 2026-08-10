# Research Landscape v1 — Search, Pitfall, and Retention Policy

## Purpose

This is an engineering pre-study workflow, not an exhaustive systematic review.

The goal is **decision sufficiency**:

- understand what the thing is and how predecessors usually do it;
- understand the representative approaches and trade-offs;
- identify credible predecessor implementations worth borrowing from;
- identify known pitfalls, hidden constraints, and novice traps before design;
- know what still blocks the next engineering decision;
- stop before research time grows faster than decision value.

Do not optimize for maximum source count, paper count, or download count.

## Search log

Record each coherent search pass in `search_log.csv`.

Log:

- active research question;
- phase;
- query;
- scope/source type;
- short result summary;
- whether a new route appeared;
- whether materially new information appeared;
- next action.

Do not log every click.

The search log is part of the evidence for `low_marginal_value` when closing a question as `SATURATED`.

## Default search funnel

### Phase A — Orientation

Cover applicable perspectives:

- principles / architecture;
- standards / official docs;
- representative products;
- papers/reviews;
- open source;
- known limitations;
- alternatives;
- test / verification.

Default: inspect roughly 6–12 promising candidates, usually without downloading.

### Phase B — Seed selection

Choose 2–4 strong seeds.

Prefer:

- primary/authoritative factual sources;
- original papers for methods;
- original repositories/projects for implementation;
- high-value review/textbook material when it accelerates understanding.

Extract problem, architecture, implementation choices, constraints, limitations, reusable content, non-transferable assumptions, and evidence locators.

### Phase C — Limited snowballing

Expand strong seeds through citations, standards/app notes, related repos, issues/discussions, and linked implementations.

Default: one round.

Continue only when a blocking question remains or a materially different route appears.

### Phase D — Contrarian check

Actively seek one credible challenge:

- alternative architecture;
- failure case;
- limitation;
- newer revision;
- conflicting evidence.

This prevents premature convergence; it does not restart the whole search.

### Phase E — Mandatory pitfall / hazard pass

Search specifically for things a newcomer may not know to ask.

Use topic-relevant categories such as:

- absolute max / transient / surge / derating;
- creepage / clearance / insulation;
- grounding / floating / common-mode / shielding;
- measurement loading;
- abnormal open/short/fault states;
- thermal/current/connector/trace/via limits;
- EMC/filtering/bandwidth;
- startup/shutdown/bring-up;
- reset/clock/CDC/protocol corner cases;
- algorithm preprocessing/data leakage/evaluation mismatch;
- toolchain/dependency/version assumptions;
- manufacturing/test/calibration/serviceability;
- safety/standards/regulatory requirements.

Useful sources include standards, datasheet application/absolute-max sections, errata, original repo issues, postmortems, verification docs, and reproducible engineering discussions.

Record important findings in `pitfalls.yaml`.

## Source quality

Track `Authority` and `Independence` separately.

- Authority is claim-specific technical/direct authority.
- Independence is independence from the product/method being evaluated.

Vendor/original-author sources may be HIGH authority but LOW independence for superiority claims.

## Download / retention budget

Normal pre-study retained budget: **1–2 core artifacts**.

Preferred pair:

1. `REFERENCE` — strongest source for principle/specification/authoritative understanding.
2. `IMPLEMENTATION` — strongest predecessor implementation/example.

A third retained artifact requires:

- explicit `EXCEPTION` role/reason; and
- `project.research_policy.allow_extra_retained: true`.

Many sources may be inspected/cited without being retained.

A retained source requires:

- `LocalPath`;
- retained artifact actually present;
- `notes/<SourceID>.md`;
- retention role;
- selection rationale.

## Retained-source note

Each retained source note should say:

- why this source beat alternatives;
- what to read first;
- key pages/sections/files;
- what can be borrowed;
- what should not be copied directly;
- research questions answered;
- relevant evidence/pitfall IDs.

## Stop conditions

A question can become `SATURATED` only when all applicable flags are true:

- mechanism understood;
- landscape known;
- predecessor known or not applicable;
- evidence adequate;
- trade-offs visible;
- blocking unknowns handled;
- low marginal value.

Low marginal value should be supported by recent search-log evidence.

Do not require every open question to close. Non-blocking unknowns may remain.

## Continue triggers

Continue when:

- safety/feasibility/architecture is blocked;
- primary sources materially disagree;
- current recommendation depends on an unverified assumption;
- a credible alternative materially changes cost/feasibility/safety/performance/schedule;
- the pitfall pass reveals a critical unknown;
- the user explicitly requests deeper coverage.
