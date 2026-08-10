---
name: research-landscape
description: Research the current technical landscape for an engineering-prestudy project with an engineering-prestudy bias: find enough authoritative evidence and representative predecessor implementations to understand what exists, what has been achieved, what is worth borrowing, and what remains blocking; use iterative search, seed selection, limited snowballing, source/evidence tracking, and selective retention of usually only 1–2 core artifacts instead of building an exhaustive literature collection.
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
- what is worth borrowing for the current project;
- what important trade-offs or risks remain;
- whether enough is known to move into design/planning.

Do not keep searching simply because more papers, products, repositories, or webpages exist.

Read `references/search-and-retention-policy.md` for the detailed v1 search funnel, retained-download budget, and stop conditions.

## Inputs

Read:

- `project.yaml` and current goal;
- `research_questions.yaml`;
- existing `sources.csv` and `evidence.jsonl`;
- user-provided files/links/code before searching for duplicates;
- relevant unified user context when it affects source selection or explanation depth.

Existing user material gets priority: first determine what it already answers before adding new sources.

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

These are guidance values, not quotas. Stop the orientation pass early when the important routes are already visible.

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

When a strong seed source exists, expand through its:

- backward/forward citations;
- referenced standards or app notes;
- related repositories;
- issues/discussions that contain concrete engineering evidence;
- related implementations.

Default: **one expansion round**.

Continue beyond one round only if:

- a blocking question remains unresolved; or
- a materially different route appears that could change the engineering decision.

Do not snowball merely to increase source count.

### 4. Contrarian check

Before stopping, actively look for one credible challenge to the emerging conclusion when relevant:

- alternative architecture;
- known failure case;
- important limitation;
- newer revision;
- contradictory evidence.

The purpose is to avoid premature convergence, not to restart the whole research effort.

## Source tiers

Default source tiers:

- `L1`: standards, official manuals/datasheets, original project/repository, official product documentation, original paper.
- `L2`: reputable secondary technical analysis, review papers, textbooks, authoritative tutorials.
- `L3`: community implementation, engineering blog, forum, issue/discussion with useful practical evidence.
- `L4`: weakly sourced aggregation or discovery-only material; do not use as final support when a stronger source exists.

Source tier and usefulness are different. An L1 source can still be irrelevant to the active question.

## Download and retention policy

### Default: retain only 1–2 core artifacts

A normal pre-study may inspect and cite many sources, but should normally **download/retain only 1–2 artifacts** for later reading or reuse.

Preferred pair when available:

1. **Reference source** — strongest material for principle/specification/authoritative understanding.
2. **Implementation source** — strongest predecessor example showing how the work was actually done.

Examples:

- official standard/manual + open-source repository;
- datasheet/application note + implementation project;
- strong review/foundational paper + source code;
- official architecture guide + detailed engineering paper.

One retained item is enough when one artifact already covers both roles or only one source is genuinely worth future reading.

A third retained artifact requires an explicit reason, such as:

- mandatory standard + implementation + separate verification/test reference;
- two fundamentally different routes both remain viable;
- the extra artifact resolves a blocking question.

Do not download a large collection merely because it appeared in search.

Stable official webpages may remain URL-only when downloading adds little future value.

### Retained-source notes

Every retained artifact must get `notes/<SourceID>.md` containing:

- why this source was selected over alternatives;
- what to read first;
- key sections/files/pages;
- what can be borrowed;
- what cannot be copied directly or does not fit the project;
- which research questions it answers;
- related evidence IDs.

For repositories, identify specific directories/files worth reading rather than saying only "look at this repo".

## Evidence model

Write one record per line in `evidence.jsonl`.

FACT example:

```json
{"id":"F001","type":"FACT","statement":"...","source_id":"S001","locator":"page 6 / section X","confidence":"HIGH"}
```

INFERENCE example:

```json
{"id":"I001","type":"INFERENCE","statement":"...","basis":["F001","F009"],"confidence":"MEDIUM"}
```

Every FACT must have a traceable locator when the source format supports one.

Do not convert an inference into a FACT merely because several secondary sources repeat it.

## Contradictions

If credible sources conflict:

- do not silently choose one;
- create a `SOURCE_CONFLICT` open question;
- record conditions, publication dates/versions, and why the conflict may exist;
- resolve only when evidence supports a resolution.

## Stop conditions

A research question may move to `SATURATED` when the applicable conditions are met:

1. **Mechanism understood** — enough is known to explain the relevant process/architecture and continue design discussion.
2. **Landscape known** — the main representative routes are identified; obscure variants are unnecessary.
3. **Predecessor known** — at least one credible example shows how predecessors actually did it, when such an example exists.
4. **Evidence adequate** — important factual claims have sufficiently strong support.
5. **Trade-offs visible** — the major reasons to choose between viable routes are known.
6. **Blocking unknowns handled** — blocking questions are resolved or explicitly routed to experiment/user decision/future investigation.
7. **Low marginal value** — the most recent search/snowball pass did not reveal a new route, materially alter the likely recommendation, or resolve a blocking issue.

Do **not** require every open question to be closed. Non-blocking unknowns remain in `open_questions.yaml`.

Continue researching despite the default stop rule when:

- architecture/safety/feasibility is blocked by an unanswered question;
- primary sources materially disagree;
- the preferred route depends on an unverified assumption;
- a credible alternative could materially change cost, performance, safety, feasibility, or schedule;
- the user explicitly requests deeper literature coverage.

## Output

Update:

- `sources.csv`;
- `evidence.jsonl`;
- `research_questions.yaml`;
- `open_questions.yaml`;
- project library and selected source notes;
- `reports/research_landscape.md`.

The report should be selective and action-oriented. Prefer:

1. **当前已经做到什么** — concise landscape summary.
2. **1–3 条代表性路线** — not a long catalogue.
3. **前辈怎么做** — concrete implementation patterns/examples.
4. **哪些最值得借鉴** — and why.
5. **最终保留的 1–2 份资料** — with a reading guide.
6. **不能直接照搬的地方**.
7. **仍未解决的阻塞问题**.
8. **是否已足够进入 design/planning**.

Avoid long lists of similar papers/products/projects unless comparison itself is the research goal.
