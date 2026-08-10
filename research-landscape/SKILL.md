---
name: research-landscape
description: Research the current technical landscape for an engineering-prestudy project: find authoritative sources, papers, standards, datasheets, commercial implementations, open-source projects, patents or other relevant artifacts; download and organize valuable material; maintain source and evidence registers; use iterative search and citation/snowball expansion; and identify what is worth borrowing without mixing fact with inference.
---

# Research Landscape

Own the evidence-gathering and current-state phase.

## Inputs

Read:

- `project.yaml` and current goal;
- `research_questions.yaml`;
- existing `sources.csv` and `evidence.jsonl`;
- user-provided files/links/code before searching for duplicates;
- relevant unified user context when it affects source selection or explanation depth.

## Research strategy

Use a layered search strategy rather than one broad query.

1. Clarify the active research question.
2. Search from multiple perspectives: principles, current implementations, standards, products, academic work, open source, failure modes, alternatives, tests, and constraints as applicable.
3. Prefer primary/authoritative sources for factual technical claims.
4. When a strong seed source is found, expand backward/forward or through referenced standards, app notes, repositories, related implementations, and citations when useful.
5. Run a contrarian pass for important conclusions: actively look for contradictory evidence, failure cases, limitations, and viable alternatives.
6. Stop when the configured research question reaches saturation rather than browsing indefinitely.

## Source tiers

Suggested default:

- `L1`: standards, official manuals/datasheets, original project/repository, official product documentation, original paper.
- `L2`: reputable secondary technical analysis, review papers, textbooks, authoritative tutorials.
- `L3`: community implementation, engineering blog, forum, issue/discussion with useful practical evidence.
- `L4`: weakly sourced aggregation or discovery-only material; do not use as final support when a stronger source exists.

## Download and library handling

For material worth reusing, preserve it under the project `.prestudy/library/` tree when tooling and licensing permit.

Record every retained item in `sources.csv` with:

- unique source ID;
- type/title/publisher/year;
- URL or origin;
- local path if downloaded;
- source tier;
- why it is useful;
- reading priority;
- status.

Do not download a large collection merely because it appeared in search. Retain material that supports an active question or is clearly valuable for implementation/reference.

## Source notes

Create `notes/<SourceID>.md` for important sources. The note should answer:

- why this source matters;
- what to read first;
- key sections/files/pages;
- what can be borrowed;
- what cannot be copied directly or does not fit the project;
- related evidence IDs.

For repositories, identify the specific directories/files worth reading rather than saying only "look at this repo".

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

## Contradictions

If credible sources conflict:

- do not silently choose one;
- create an `SOURCE_CONFLICT` open question;
- record conditions, publication dates/versions, and why the conflict may exist;
- resolve only when evidence supports a resolution.

## Output

Update:

- `sources.csv`;
- `evidence.jsonl`;
- `research_questions.yaml`;
- `open_questions.yaml`;
- project library and source notes;
- `reports/research_landscape.md`.

The landscape report should answer what exists now, what has been achieved, what is worth borrowing, the strongest source for each important claim, important gaps/controversies, and what should be investigated next.
