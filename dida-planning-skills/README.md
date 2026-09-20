# DIDA 任务规划 Skills v1.5.0

滴答清单保存真实任务状态。Skill 只负责任务范围、归属、依赖、人工投入估时、截止风险、周交付和验收；MCP/连接器优先执行真实读写，`dida-cli` 仅作无连接器时的 fallback。

## 主流程

全量未完成任务 → hard deadline / Latest Safe Start / 依赖与 external lead time → 本周已有承诺与必办节点 → 0–2 个核心周交付物 → 支撑任务 → 执行证据 → 周验收 → 重新选择下周。

- **纯任务规划**：不读取 Outlook/日历，不生成小时级时间块，不维护个人可用时段、精力窗口或 weekly capacity。
- **周交付物**：必须有产物、范围、验收标准、验收方式、支撑任务和明确不做项；默认最多两个，可以只有一个或零个。
- **长期发展防饥饿**：没有 growth 交付的忙周必须记录挤占原因和恢复/重新评估条件。
- **真实门控**：硬件/设计项目用持久依赖表达“关键选型 → datasheet 约束 → 功能确认 → 需求冻结 → 原理图/实现”，不提前承诺尚未 ready 的下游工作。
- **估时口径**：估计人工任务投入；新输出 `estimated_effort_minutes`，完成事实用 `actual_effort_minutes`。外部等待和端到端周期单独记录。
- **日期边界**：目标日期、硬截止和 Latest Safe Start 分开；缺可靠经过时间依据时 Latest Safe Start 为 unknown。

## 职责

| 模块 | 唯一职责 |
|---|---|
| dida-manager | 总入口、全量扫描、风险检查和路由 |
| dida-weekly-delivery | 选择本周 0–2 个交付切片并定义验收合同 |
| dida-weekly-review | 整周验收、偏差分析、归档与换周 |
| dida-task-breakdown | 持久项目层级、阶段 gate 与依赖 |
| dida-task-estimator | 人工投入、剩余工作和估时置信度 |
| dida-task-progress | 当前进度/等待/完成、证据和实际投入事实 |
| dida-task-capture | 新事项分类、去重、归属和真实日期语义 |
| dida-planning-profile | 稳定的任务规划规则 |
| dida-planning-memory | 跨项目长期规则与背景，不替代任务事实 |
| dida-planning-core | 确定性解析、校验、估算、依赖与周合同辅助 |
| dida-cli | 无可用连接器时的本地回退 |

## 兼容边界

历史任务中的 `role: block`、`execution_window`、`mobility` 仍可读取，避免修改其它字段时破坏旧数据；v1.5.0 新写入拒绝这些字段。旧完成记录里的 `calendar_minutes` 可迁移为实际投入样本，但新事件不再写它。

## 读写规则

修改 Skill/讨论方案不触发实际任务写入。局部操作只读相关对象；全局周规划必须枚举全部可访问业务清单和未完成任务，包括 undated、future、waiting，并处理分页。

实际写回采用：读取 → 比较/去重 → 仅修改授权字段 → 回读。超时先核对结果，不盲目重试；不无痕移动硬截止或修改旧验收标准。

## 验证

```bash
python dida-planning-core/scripts/package_validator.py --root . --strict-manifest
python -m unittest discover -s dida-planning-core/tests -v
python dida-planning-core/scripts/weekly_delivery.py --input dida-weekly-delivery/assets/example-plan.json
python install.py --dry-run
```

这些 JSON/本地历史仅用于瞬时计算或可重建校准，不是第二份可编辑任务库。
