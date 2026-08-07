---
name: dida-planning-profile
description: Initialize, inspect, or update Dida “系统配置” NOTE tasks for work hours, energy, mobility permissions, estimation coverage, task-body/tag protocol, dependency protocol, timezone behavior, weather, fitness, and schema version. Use when the user changes a stable planning preference or asks to initialize/configure the planning system. Do not load or rewrite all configuration during ordinary task operations.
---

# Dida planning profile

Maintain stable planning rules as several small NOTE tasks in the Dida list `系统配置`.

## Configuration NOTE set

- `规划偏好｜作息与容量`
- `规划偏好｜日程移动权限`
- `估时配置｜特征与风险缓冲`
- `系统协议｜标签与任务正文`
- `系统协议｜依赖关系`
- `系统状态｜Schema与迁移版本`

Long-term memories are not stored in these six profile NOTE tasks; `$dida-planning-memory` owns separate atomic memory entries.

Each NOTE has `role: config`, no estimated duration, no status label, and no scheduling date unless a configuration reminder is intentionally created.

## Initialize

1. Use `$dida-cli` to find or create the exact `系统配置` list.
2. Inspect existing NOTE titles before creating anything.
3. Create only missing NOTE tasks from `assets/config-notes/`.
4. Read back all created NOTE IDs.
5. Add their IDs to `系统状态｜Schema与迁移版本` so other skills can resolve exact notes without broad searches.

Initialization must be idempotent. Never overwrite an existing user-edited NOTE with a template.

## Update a preference

1. Resolve the one relevant NOTE; do not read all six unless the change crosses domains.
2. Distinguish stable planning preference from a one-day exception or a non-planning memory. Route project/tool/workflow facts to `$dida-planning-memory`.
3. Stable explicit preference may be written immediately.
4. If it conflicts with an existing explicit rule, show the conflict before replacement.
5. Preserve unrelated sections and append a Planner event comment describing the change.
6. Read back.

## Current defaults

- Current-location timezone updates automatically.
- No personal calendar occupancy overlap.
- Work normally ends by 21:00; Sunday is light/no work unless approved.
- Weather task update target is about 08:30.
- Fitness defaults to protected and may move within the same day.
- Hard deadlines cannot be changed by AI.
- Inbox organization occurs only on explicit request.

## Memory boundary

Do not absorb general memory into profile. Scheduling/energy/mobility behavior belongs here; project rules, tool environments, and cross-project workflow agreements belong to `$dida-planning-memory`.

## References

Read `references/config-notes.md` for ownership and template rules.
