# Changelog

## 1.5.0 — 2026-09-20

- Make the task-only boundary executable, not just documentary: new Planner writes reject legacy `mobility`, `execution_window`, and `role: block` scheduling metadata while preserving old records for read/update compatibility.
- Replace calendar-occupancy calibration with canonical human-effort fields: `estimated_effort_minutes` for estimates and `actual_effort_minutes` for completion evidence; old `calendar_minutes` remains read-only migration input.
- Clarify ownership: manager orchestrates; breakdown owns durable hierarchy/gates; weekly-delivery owns the weekly contract; progress owns point-in-time facts/evidence; weekly-review owns end-of-week aggregate audit/archive; estimator owns effort only.
- Add growth anti-starvation metadata: busy weeks may omit a growth deliverable only with an explicit deferral reason and resume/re-evaluation condition.
- Add gate-driven hardware/design planning guidance: critical selection → datasheet constraints → external functional confirmation → requirements freeze → schematic/implementation.
- Remove scheduling/capacity/mobility routing from capture, profile/memory templates and shared user-context ownership.
- Extend regression tests for legacy-read/new-write boundaries, actual-effort migration, growth deferral and scheduling-residue checks.

## 1.4.0 — 2026-09-20

- Introduce dida-weekly-delivery on existing task/phase owners, with outcome, scoped acceptance and evidence.
- Default to at most two core weekly deliverables; retain growth trade-offs and count necessary obligations.
- Add pure weekly contract, reference, effort, deadline-risk, acceptance and rollover validation.
- Keep Planner schema 1 and existing week fields; support versioned JSON and preserve unknown metadata.
- Separate weekly-slice acceptance from whole-task completion; record user_report honestly.
- Archive before rollover; do not silently rewrite promises or dates.
- Carry forward the approved task-only boundary: remove calendar scheduler and clock-block workflows.
- Update research handoff routes and provide validated backup-first installation.

## 1.1.0 — 2026-08-06

- 新增 `dida-planning-memory`，负责长期项目规则、工具环境、工作方式和通用约定。
- 记忆采用独立原子子任务，不恢复单体 Markdown 记忆库。
- 明确“显式保存/遗忘必执行、稳定低敏信息可自动保存、推断和敏感信息需确认”的记忆边界。
- 新增记忆所有权路由，避免与 profile、任务正文和估时样本重复存储。
- 新增 `memory_policy.py` 及 5 项单元测试。
- Planner schema 增加 `memory_category`、`memory` 角色和记忆元数据字段。
- 更新全部技能的记忆读取边界、安装脚本、配置模板、审查代理与 README。


## 1.0.0 — 2026-08-06

- 将原 Markdown 单体规划系统拆成八个职责单一的 Skill。
- 以滴答清单作为任务、日期、状态、正文、评论和专注记录的唯一业务权威。
- 新增 Planner 机器区、结构化事件评论、依赖检查、三方冲突合并和待同步队列。
- 新增基于任务特征、相似历史和小样本收缩的估时引擎。
- 新增不重叠时间块排程器和旧 Markdown 迁移预览工具。
- 移除旧系统的快照、写锁、会话、日/周计划投影和 Markdown 双写机制。
