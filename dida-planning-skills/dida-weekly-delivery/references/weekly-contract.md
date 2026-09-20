# 周交付合同与数据协议

## 存储

当前约定只保存在 owner task/phase 的 Planner 区。自然语言可以是这一约定的简短展示，不另维护可编辑计划文件。历史在 owner 评论中。支撑任务保留原来的父子关系。

现有字段保留：`schema: 1`、周一 `week_start: YYYY-MM-DD`、`weekly_commitment: must|should|candidate`。新增一行 JSON `weekly_delivery`；使用 JSON 是为了和现有仅解析 dependencies 缩进的 Planner 解析器兼容，不引入新的 YAML 运行依赖。

```text
【Planner】
schema: 1
role: task
week_start: 2026-09-21
weekly_commitment: must
weekly_delivery: {"schema":1,"slot":"growth","outcome":"交付正常收发路径图并完成口述演示","artifact":"PCIe收发路径图","scope":"一次正常发送与接收，不含重传","criteria":["图中可追踪一条正常消息的完整路径","完成一次口述并记录未掌握项"],"verification":"对照图从头讲一遍，由用户确认","support_task_ids":[],"exclusions":["本周不实现RTL","本周不展开重传与流控"],"target_date":"2026-09-27","status":"planned","evidence":[]}
【/Planner】
```

真实运行时 artifact 应补实际文件、日志或演示记录位置，不能编造存在的链接/文件。上例不指向任何用户实际任务。

## 字段

| 字段 | 含义 |
|---|---|
| schema | 周合同版本，当前 1 |
| slot | work 或 growth；允许只有 work，但必须显式记录 growth 挤占原因与恢复条件 |
| outcome / artifact / scope | 本周结果、具体产物、范围；均为非空文本 |
| criteria | 非空的验收条件字符串数组 |
| verification | 如何验收及确认方式 |
| support_task_ids | 已读取的叶子 task ID 列表；task 自身即一个工作项时可为空，phase 必填 |
| exclusions | 本周不做的范围；无排除项时用空数组 |
| target_date | 本周内的内部目标日，不覆盖 owner 原生 dueDate |
| status | planned、delivered、not_delivered、blocked、cancelled、unverified |
| evidence | 对象数组：kind、detail；kind 为 user_report、artifact、test_log、tool_result、demonstration |

contract 内未知 JSON 字段保留，兼容未来扩展；错误版本拒绝。`weekly_delivery` 必须和有效的旧字段对同时出现，不允许放到 config/memory/legacy block。

`delivered` 必须有证据；实际验收由用户明确确认或逐条检查结果支持。字段校验通过不等于成果已被核验。

## 工作量快照

`weekly_delivery.py` 接收规范化的瞬时 JSON：

- `week_start`、`inventory_complete`、`tasks`；
- `effort_budget_minutes`：用户明确提供的该周总人力投入上限，可为 null；
- `obligation_task_ids`：本周必办但不占核心名额的叶子任务；
- `growth_deferral_reason` / `growth_resume_condition`：当本周没有 growth 核心交付时的挤占原因和重新评估条件；不要求创建额外持久任务；
- `tasks` 最少含 `id`、`role`、`completed`、`remaining_minutes`、`blocked`，以及可选的原样 Planner 字段。

适配层先根据实际 MCP schema 映射 camelCase/snake_case；不能把这个计算模型当成远端 API 参数。剩余投入不能由进度百分比机械生成。`blocked: false` 只有在相关硬依赖/外部等待核对过后才能填写；未核对则省略，脚本报告 unknown。单个必办节点的时间也要有依据。

校验区分结构错误和可行性：结构通过但没有投入预算，仍是 feasibility=unknown。纯等待任务不计本人的劳动分钟，但其阻塞风险仍然保留。先验手册阅读时长不是事实。

### owner 与支撑任务计数

- phase owner 必须列出真实支撑叶子，phase 本身的汇总估时不参与相加。
- task owner 的 `support_task_ids` 为空时，使用 owner 自身 `remaining_minutes`。
- task owner 的 `support_task_ids` 非空时，表示本周工作量由这些叶子完全代表；owner 汇总估时不再相加，避免双计。
- 同一个支撑叶子同时服务多个交付物/obligation 时只计一次，但每个交付物仍单独验收。

## 日期和风险

目标日不产生虚构 hard deadline。输入快照可含 `date_semantics`、`due_date`、`start_risk`、`latest_safe_start`；若最晚启动有值，还需 `latest_start_basis` 说明截止、经过时间和缓冲来源。脚本检查日期语义并列出本周之前必须启动的风险，不负责生成时钟排程。

最晚启动需要足够的经过时间依据，人力投入小时不等于自然日。缺关键周期时写 unknown；无截止约束的提醒写 not_applicable。未知不能被渲染为安全。

## 换周与授权

1. 读取旧合同和评论，保存原结果、标准、状态与证据。
2. 追加带 operation_id 的 weekly_review 历史；分段满足连接器的评论长度限制，并回读。
3. 历史记录成功后，才允许删除旧 `week_start`、`weekly_commitment`、`weekly_delivery` 字段。
4. 不改变 owner 的原生截止、状态、parentId 或其它 Planner 扩展。
5. 用户确认后才写新周合同；相同操作重试先核对 operation_id，不能重复归档。

`prepare_week_rollover` 仅给草案，不直接清数据；缺上周遗留合同、数据损坏时转人工确认，不能盲删。
