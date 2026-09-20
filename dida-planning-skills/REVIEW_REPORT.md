# v1.5.0 发布审查

## 审查结论

v1.4.0 的周交付架构可以保留；主要问题不是重做结构，而是**边界没有完全落到协议实现**。本轮修复集中在旧调度字段、估时口径、模块职责和多主线防饥饿四处。

## 发现与处理

1. **旧调度语义仍能被新任务写入**：capture 仍使用 `execution_window`，Planner 新 block 默认带 `mobility`，profile/memory 模板也继续写 mobility。现在这些字段只保留历史读取兼容；新写入拒绝 `mobility`、`execution_window` 和 `role: block`，模板全部移除。
2. **估时仍混用 calendar occupancy**：estimator/progress/history 使用 `calendar_minutes`，与“纯任务规划”冲突。现在标准字段改为 `estimated_effort_minutes` / `actual_effort_minutes`；旧字段只作为重建历史时的兼容输入。
3. **progress 与 weekly-review 有职责重叠**：现在 progress 负责单次事实/证据/当前合同状态，weekly-review 负责整周所有承诺的审计、偏差、归档和换周。
4. **breakdown 与 weekly-delivery 都可能改范围**：现在 breakdown 只管持久层级、DoD、gate 和依赖；weekly-delivery 只定义本周切片，不为一周计划新建层级。
5. **长期发展可能被无限让位**：没有把 growth 设成硬性每周必选，而是增加 `growth_deferral_reason` 与 `growth_resume_condition`；忙周可以让位，但不能无记录地永久推迟。
6. **硬件真实流程缺少强 gate 表达**：增加通用“关键选型 → datasheet 约束 → 外部功能确认 → 需求冻结 → 原理图/实现”模式，并要求真正的 gate 用 hard `finish_to_start`，下游在 gate 前不视为 ready。

## 兼容性

Planner schema 与 weekly_delivery schema 都维持 1。旧任务可以继续读取并修改与旧调度字段无关的内容；升级不会自动远程清理历史 mobility/execution-window 配置，也不会迁移真实滴答任务。

旧 `calendar_minutes` 评论可由 `rebuild_history.py` 映射为 `actual_effort_minutes` 并保留 `actual_effort_source=legacy_calendar_minutes`，避免丢失历史校准数据。

## 验证

自动化覆盖核心解析、估时、依赖、周合同、WIP、obligation、growth 让位、验收、rollover、安装与退役旧 scheduler。最终精确测试数量、manifest 校验和示例 CLI 结果记录在 `VALIDATION_RESULTS.txt`。

本轮审查是本地代码/文档审查与自动化回归；没有把未执行的独立人工审阅冒充为已完成。

## GitHub 边界

已核对 `whaoy123/myskills` 的 GitHub 连接权限和默认分支。当前远端 `main` 仍包含旧 `dida-daily-planner`，因此 v1.5.0 必须提交到独立 review 分支；不直接覆盖或合并 main。远端是否真正同步以 GitHub 分支/提交回读为准。
