# 滴答任务规划 v1.5.0：周交付 + 纯任务门控

## 主线

v1.4.0 已把“这周推进什么”改成“这周交付什么”；v1.5.0 继续解决两个实际问题：一是旧日程/容量语义仍残留在字段和估时口径里，二是硬件/求职多线并行时容易把所有事情同时激活。

现在的流程固定为：

全量未完成任务 → hard deadline / Latest Safe Start / 依赖与 external lead time → 已有承诺与 obligation → 0–2 个核心周交付 → 支撑叶子 → 证据验收 → 周末归档并重选。

它只回答“做什么、先后关系、需要多少人工投入、什么算完成”，不回答“周二 19:00–21:00 做什么”。

## 1. 周交付物是临时切片，不是新层级

周合同继续写在现有 task/phase owner 上，必须包含产物、范围、验收标准、验收方式、支撑任务和本周不做项。`dida-task-breakdown` 只在需要长期有效的独立 task/gate 时修改项目树；`dida-weekly-delivery` 不为了本周计划再造一棵任务树。

默认核心 WIP 上限 2，可以 0 或 1。一次性的板测、出差、采购、问老师、现场检查属于 obligation：它们消耗投入并影响可行性，但不会因为重要就自动变成第三条主线。

## 2. 长期发展防饥饿，但不和硬截止硬碰硬

默认尽量保留一个小型 growth 交付，例如一张 PCIe 数据流图、一个 RTL 小模块及验证结果、一次 CPU/Cache 设计说明。

忙周可以只保留工作交付，但必须写：

- `growth_deferral_reason`：本周为什么让位；
- `growth_resume_condition`：什么条件触发重新选择 growth。

这两个字段不会把 growth 变成硬截止，也不会自动创建提醒任务；作用是让周复盘能够发现连续数周的隐性延期。

## 3. 硬件项目按 gate 推进

对“器件已经选完，但还没到画原理图”的项目，真正的主干是：

关键器件/方案确认 → datasheet 约束核对 → 外部/老师功能确认 → 需求冻结 → 原理图/实现 → PCB/投板。

`dida-task-breakdown` 把真实 gate 做成持久 task/phase 与 hard `finish_to_start`。例如需求冻结没有通过时，原理图可以留在 backlog/future，但不能因为“月底想开始画”就被标成 ready 或塞进本周核心承诺。

这种模型同时适合两块独立硬件：它们可以各自有 gate；如果某项工作确实共享（例如同一份接口规范），只对那个真实共享叶子去重，不能把“两块板都属于硬件”当成一条工作量。

## 4. 估时 = 人工投入，不是日历占用

v1.5.0 的标准输出：

- `estimated_effort_minutes`：预计人工投入；
- `actual_effort_minutes`：完成后的实际人工投入；
- `focus_minutes` / `other_active_minutes`：可选拆分；
- `ai_parallel_minutes`：AI 独立并行时间；
- `end_to_end_minutes`：端到端经过时间。

纯等待、物流、老师回复等属于 external lead time / elapsed time，不直接加到人工投入。Latest Safe Start 只有在“人工投入如何转换为经过时间”也有可靠依据时才能计算；否则就是 unknown。

历史 `calendar_minutes` 仍可读，用来迁移旧校准样本，但新事件拒绝再写该字段。

## 5. 旧调度字段只读兼容

为避免升级时破坏历史任务，解析器仍能读取：`role: block`、`date_semantics: execution_window`、`mobility`。但新 `patch_body` 不允许创建或修改它们；新 Planner block 也不包含 mobility。

Capture 遇到“周三下午做”时不再写 execution window。只有用户明确需要滴答原生提醒时，才通过真实连接器写原生 reminder/date；这不进入 Planner 的任务规划语义。

## 6. 模块边界

| 模块 | 负责 | 不负责 |
|---|---|---|
| manager | 全量扫描、风险检查、路由 | 重复实现各子模块规则 |
| breakdown | 长期层级、DoD、gate、dependency | 本周临时切片 |
| estimator | 人工投入、剩余工作、置信度 | 日历容量、钟点排程 |
| weekly-delivery | 本周交付选择和合同 | 改造长期任务树 |
| progress | 当前进度/等待/证据/实际投入 | 整周换周决策 |
| weekly-review | 整周验收、偏差、归档、重选建议 | 篡改原合同使其“看起来完成” |

## 7. 发布验收

回归测试必须覆盖：旧字段可读、新字段不可再写；人工投入新字段；旧 `calendar_minutes` 迁移；WIP 上限；growth 让位原因/恢复条件；obligation 计入；共享叶子去重；gate/依赖风险；周切片不误完成 owner；归档后才清旧周字段；配置模板不再含 mobility/execution_window。

实际任务写入仍由 MCP/连接器完成，CLI 只是 fallback。包验证、GitHub 同步和真实滴答任务修改是三个独立动作，不能把其中一个成功说成另外两个成功。
