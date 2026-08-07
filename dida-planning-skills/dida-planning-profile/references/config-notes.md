# Configuration NOTE ownership

| NOTE | Read by |
|---|---|
| 作息与容量 | daily planner, weekly review |
| 日程移动权限 | daily planner |
| 特征与风险缓冲 | estimator, daily planner, progress, weekly review |
| 标签与任务正文 | capture, breakdown, progress |
| 依赖关系 | breakdown, daily planner, progress |
| Schema与迁移版本 | all skills only when resolving IDs/version or migrating |

## Template rule

Templates are first-run defaults, not authoritative files after initialization. The Dida NOTE becomes authoritative once created. Never periodically sync a template over the NOTE.

## One-time exception

A one-day request such as “今天可以做到22点” belongs to that planning interaction or affected task comment, not the stable profile, unless the user says this should be the new default.

## Long-term memory boundary

These six notes do not own project rules, tool environments, or general workflow memories. Route those facts to `dida-planning-memory`, which stores atomic child memory records. Do not duplicate the same fact in profile and memory.
