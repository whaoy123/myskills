---
name: research-landscape
description: Research the current technical landscape for an engineering-prestudy project with an engineering-prestudy bias: find enough authoritative evidence and representative predecessor implementations to understand what exists, what has been achieved, what is worth borrowing, what predecessors got wrong, and what remains blocking; use iterative search, seed selection, limited snowballing, source/evidence/search logging, pitfall discovery, and selective retention of usually only 1–2 core artifacts instead of building an exhaustive literature collection.
---

# Research Landscape

Own the evidence-gathering and current-state phase.

## Core principle

This is **engineering pre-study, not an exhaustive systematic review**.

Optimize for **decision sufficiency**, not maximum source count.

The phase is successful when the user can answer:

- what this thing is and how the relevant process/architecture works;
- what representative approaches currently exist;
- how predecessors actually implemented it;
- what predecessors discovered can go wrong;
- what is worth borrowing for the current project;
- what important trade-offs or risks remain;
- whether enough is known to move into design/planning.

Read:

- `references/search-and-retention-policy.md`
- `references/source-quality-policy.md`

## Inputs

Read:

- `project.yaml` and current goal;
- `research_questions.yaml`;
- `sources.csv`, `search_log.csv`, and `evidence.jsonl`;
- `open_questions.yaml` and `pitfalls.yaml`;
- user-provided files/links/code before searching for duplicates;
- relevant unified user context when it affects source selection or explanation depth.

Existing user material gets priority: first determine what it already answers before adding new sources.

## Search logging

Every meaningful search pass must be logged in `search_log.csv`.

Record:

- `SearchID`
- `QuestionID`
- timestamp
- phase (`orientation|seed|snowball|contrarian|pitfall`)
- query / search expression
- scope or source class
- short result summary
- whether a new route appeared
- whether the pass produced materially new information
- next action

Do not create a row for every trivial browser click. Log a coherent search pass.

## Default research funnel

### 1. Orientation search

Search broadly enough to build a landscape map before deep reading.

Use applicable perspectives such as:

- principles / architecture;
- standards and official documentation;
- representative commercial implementations;
- academic papers / reviews;
- open-source projects;
- failure modes / limitations;
- alternatives;
- test and verification methods.

Default guidance:

- inspect roughly **6–12 promising candidates**;
- normally do **not** download them during this pass;
- record useful candidates and why they matter;
- prefer source diversity over many near-duplicates.

These are guidance values, not quotas.

### 2. Select strong seed sources

Choose only **2–4 seed sources** for deeper inspection.

Prefer:

- primary/authoritative sources for factual specifications;
- original papers for novel methods;
- original repositories/projects for implementation details;
- strong review/textbook material when it improves understanding efficiently.

For each seed, extract:

- the problem it solves;
- architecture / method;
- implementation choices;
- important constraints and limitations;
- what is reusable;
- what is not directly transferable;
- evidence locators for important claims.

### 3. Limited snowballing

Expand strong seeds through:

- backward/forward citations;
- referenced standards or app notes;
- related repositories;
- issues/discussions with concrete engineering evidence;
- related implementations.

Default: **one expansion round**.

Continue beyond one round only if:

- a blocking question remains unresolved; or
- a materially different route appears that could change the engineering decision.

### 4. Contrarian check

Before stopping, actively look for one credible challenge to the emerging conclusion when relevant:

- alternative architecture;
- known failure case;
- important limitation;
- newer revision;
- contradictory evidence.

The purpose is to avoid premature convergence, not restart the whole research effort.

### 5. Mandatory pitfall / hazard pass

This is separate from the contrarian check.

Actively search for **unknown unknowns**: things a newcomer may not know to ask about but that can cause rework, bad measurements, latent failures, unsafe behavior, or invalid conclusions.

Applicable engineering categories include:

- electrical absolute maximums, transients, surge, derating;
- creepage / clearance / insulation;
- grounding, floating domains, common-mode, shielding;
- measurement loading or measurement changing the original circuit;
- abnormal/open/short/fault states;
- connector, trace, via, current, thermal constraints;
- EMC/EMI/filtering/bandwidth interactions;
- startup/shutdown/bring-up order;
- clock/reset/CDC and protocol corner cases;
- hidden preprocessing/data leakage/evaluation mismatch in algorithms;
- dependencies, toolchain versions, undocumented assumptions;
- manufacturing/test/calibration/serviceability;
- standards, regulatory, safety, or certification constraints.

Search sources particularly useful for pitfalls:

- standards / safety/application guides;
- datasheet absolute-maximum and application sections;
- errata;
- GitHub issues/discussions;
- engineering postmortems;
- implementation notes;
- verification/test documentation;
- forum reports only when they contain concrete reproducible evidence.

Record important findings in `pitfalls.yaml`, not only prose.

## Source quality: authority != independence

Track both dimensions.

`Authority` answers:

> How qualified/direct is this source for this factual claim?

`Independence` answers:

> How independent is this source from the product/method being evaluated?

Examples:

- vendor datasheet for pinout/rating: `Authority=HIGH`, `Independence=LOW`;
- original paper for its own method: `Authority=HIGH`, `Independence=LOW` for superiority claims;
- independent replication: often `Authority=HIGH|MEDIUM`, `Independence=HIGH`;
- forum anecdote: usually lower authority, but may reveal a failure mode worth verifying.

Do not use source tier as a substitute for these two dimensions.

## Download and retention policy

### Default: retain only 1–2 core artifacts

A normal pre-study may inspect and cite many sources, but should normally **download/retain only 1–2 artifacts** for later reading or reuse.

Preferred pair:

1. `REFERENCE` — strongest principle/specification/authoritative understanding source.
2. `IMPLEMENTATION` — strongest predecessor example showing how the work was actually done.

A third retained item requires an explicit exception reason and project policy override.

A source marked `RETAINED` must have:

- a `LocalPath`;
- a `RetentionRole`;
- `notes/<SourceID>.md`;
- a real locally retained artifact;
- an explanation of why it beat other candidates.

Stable official webpages may remain URL-only when downloading adds little future value.

## Retained-source notes

Every retained artifact must get `notes/<SourceID>.md` containing:

- why this source was selected over alternatives;
- what to read first;
- key sections/files/pages;
- what can be borrowed;
- what cannot be copied directly or does not fit the project;
- which research questions it answers;
- relevant pitfall/evidence IDs.

For repositories, identify specific directories/files worth reading.

## Evidence model

Write one record per line in `evidence.jsonl`.

FACT:

```json
{"id":"F001","type":"FACT","statement":"...","source_id":"S001","locator":"page 6 / section X","confidence":"HIGH"}
```

INFERENCE:

```json
{"id":"I001","type":"INFERENCE","statement":"...","basis":["F001","F009"],"confidence":"MEDIUM"}
```

Every FACT must have a traceable locator when the source format supports one.

Do not convert an inference into a FACT merely because several secondary sources repeat it.

## Pitfall model

Important pitfall records should contain:

- `id`
- `title`
- `category`
- `why_it_happens`
- `consequence`
- `impact: LOW|MEDIUM|HIGH|CRITICAL`
- `action: WATCH|DESIGN_CONSTRAINT|VERIFY|BLOCKER`
- `mitigation`
- optional `verification`
- `evidence`
- `status: OPEN|MITIGATED|ACCEPTED|RESOLVED`

`HIGH` and `CRITICAL` items need evidence and mitigation.

A `CRITICAL` item cannot be left as `WATCH`.

## Contradictions

If credible sources conflict:

- do not silently choose one;
- create a `SOURCE_CONFLICT` open question;
- record conditions, publication dates/versions, and why the conflict may exist;
- resolve only when evidence supports a resolution.

## Stop conditions

A research question may move to `SATURATED` only when all applicable stop-condition flags are explicitly true:

- `mechanism_understood`
- `landscape_known`
- `predecessor_known_or_not_applicable`
- `evidence_adequate`
- `tradeoffs_visible`
- `blocking_unknowns_handled`
- `low_marginal_value`

`low_marginal_value` should be supported by the search log: the latest relevant pass should not reveal a new route, materially alter the recommendation, or resolve a blocking issue.

Do **not** require every open question to be closed. Non-blocking unknowns remain recorded.

Continue researching when:

- safety/feasibility/architecture is blocked;
- primary sources materially disagree;
- a preferred route depends on an unverified assumption;
- a credible alternative could materially change cost/performance/safety/feasibility/schedule;
- the pitfall pass exposes a critical unknown;
- the user explicitly requests deeper coverage.

## Output

Update:

- `sources.csv`;
- `search_log.csv`;
- `evidence.jsonl`;
- `research_questions.yaml`;
- `open_questions.yaml`;
- `pitfalls.yaml`;
- project library and selected source notes;
- `reports/research_landscape.md`.

The report should be selective and action-oriented:

1. 当前已经做到什么
2. 1–3 条代表性路线
3. 前辈怎么做
4. 哪些最值得借鉴
5. 前人踩过的坑与注意事项
6. 最终保留的 1–2 份资料 + 阅读指南
7. 不能直接照搬的地方
8. 仍未解决的阻塞问题
9. 是否已足够进入 design/planning

Avoid long catalogues unless comparison itself is the research goal.
