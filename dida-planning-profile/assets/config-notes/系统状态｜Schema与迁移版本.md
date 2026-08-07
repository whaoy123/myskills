# 系统状态｜Schema与迁移版本

- system_version: 1.1.0
- planner_schema: 1
- planner_event_schema: 1
- migration_status: not_started
- memory_schema: 1
- dida_cli_version_last_verified: null

## 配置 NOTE IDs

- availability_note_id: null
- mobility_note_id: null
- estimation_note_id: null
- body_protocol_note_id: null
- dependency_note_id: null
- system_state_note_id: null
- memory_project_rules_id: null
- memory_tool_environment_id: null
- memory_workflow_id: null
- memory_convention_id: null

本 NOTE 只保存协议版本、配置与记忆分类任务 ID 及迁移状态，不保存任务或记忆副本。

【Planner】
schema: 1
role: config
progress: 0
date_semantics: none
mobility: fixed
privacy: normal
estimate_confidence: high
dependency_mode: all
dependencies:
【/Planner】
