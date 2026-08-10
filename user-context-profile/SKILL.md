---
name: user-context-profile
description: Build, load, update, promote, and forget durable user context for other skills. Use when a skill needs the user's background, knowledge level, learning preferences, long-term goals, or reusable constraints. Prefer Dida-owned planning/profile facts when available, keep local private user context outside distributable skill packages, and never mix project-specific state into the global user profile.
---

# User Context Profile

Provide a stable, privacy-safe user context layer shared by research and other skills.

## Core boundary

The skill package is stateless and distributable. Runtime user data must live outside the skill directory.

Default local runtime root:

```text
~/.prestudy/user-context/
├── profile.yaml
├── knowledge.yaml
├── preferences.yaml
└── context_meta.yaml
```

Never commit this runtime directory into a skill repository.

## Ownership rules

A fact has one owner only.

- Planning schedule, energy, mobility, timezone, work-capacity rules -> Dida `dida-planning-profile` when available.
- Durable tool/environment facts, workflow conventions, reusable agreements -> Dida `dida-planning-memory` when available.
- General background, long-term goals, knowledge levels, learning/explanation preferences -> local user context.
- Project-specific understanding, misconceptions, open questions, project decisions -> the project's `research_state/`, never global user context.

Do not duplicate a fact merely for convenience.

## Operations

### INIT

Use when the local context does not exist.

1. Check whether Dida profile/memory are available.
2. Reuse those facts first.
3. Ask only for missing information needed for the current task.
4. The user must provide what they already know and approximate proficiency in natural language.
5. Map natural-language proficiency into `unknown|beginner|foundational|intermediate|advanced`, while preserving the original wording.
6. It is acceptable to remain `PARTIAL`; never force a long questionnaire.

### LOAD

Return a unified view for the requesting skill. The caller should request a scope such as `research`, `planning`, or `coding`.

The unified view may include:

- background;
- long-term goals;
- relevant knowledge and gaps;
- learning/explanation preferences;
- tools and reusable constraints;
- planning constraints when Dida is available;
- provenance/owner for each imported field.

Other skills should consume this unified view rather than independently reading all backing stores.

### UPDATE

Update stable user information only.

- A one-project fact stays in project state.
- A temporary preference stays in the current interaction.
- A stable fact can update its true owner.
- If a new fact conflicts with an explicit existing fact, surface the conflict before replacement.

### PROMOTE

Project knowledge must never silently become global knowledge.

Promotion is allowed when either:

- the user explicitly confirms durable mastery; or
- the knowledge has been demonstrated consistently across multiple contexts and confidence is high.

Create a promotion candidate first, then update global context only after the promotion condition is satisfied.

### FORGET

Remove or correct the exact owned fact. Do not mask it by writing a contradictory copy elsewhere.

## Knowledge boundary test

Use this rule:

- "Would this still describe the user if they switched to a different project?" -> global knowledge/profile.
- "Does this make sense only inside this project/topic?" -> project knowledge model.

Examples:

- `Can write synthesizable Verilog independently` -> global knowledge.
- `Understands 1553B command/status word format` -> project knowledge until promoted.
- `Does not yet understand AVRplus Field loop` -> project knowledge only.
- `Prefers physical intuition before formulas` -> global preference.

## Required local schemas

### `profile.yaml`

```yaml
schema_version: 1
identity: {}
roles: []
long_term_goals: []
resources: {}
constraints: []
```

### `knowledge.yaml`

```yaml
schema_version: 1
domains: {}
```

Each domain may contain:

```yaml
level: intermediate
self_report: "会写项目，但工程写法还不确定"
confidence: high
known: []
gaps: []
evidence: []
```

### `preferences.yaml`

```yaml
schema_version: 1
explanation:
  preferred: []
  avoid: []
response: {}
research: {}
```

### `context_meta.yaml`

```yaml
schema_version: 1
initialized: true
state: PARTIAL
sources: {}
pending_promotions: []
```

Allowed states: `PARTIAL|COMPLETE_ENOUGH`.

## First-use user input

Do not require a rigid form. Ask the user to describe:

1. what they already know;
2. approximate proficiency for those areas;
3. only when relevant, their long-term goal or preferred explanation style.

Example acceptable input:

```text
数电比较熟，Verilog能自己写项目，SystemVerilog会一些，模拟电路基础，Python比较弱。
```

## Privacy and distribution

The distributable skill directory must contain only method, schemas, scripts, templates, examples, and tests. It must not contain real user context, project state, Dida task data, downloaded research libraries, local absolute paths, credentials, email addresses, or tokens.
