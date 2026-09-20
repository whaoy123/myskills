---
name: dida-manager
description: Manage TickTick/Dida tasks, classification, hierarchy, dependencies, effort estimates, deadline risks and weekly deliverables. Route weekly outcome planning to dida-weekly-delivery. Use for 滴答清单、整理任务、这周交付什么、任务进度. Task planning only; no calendar scheduling. Prefer available MCP/connectors and use dida-cli only as fallback.
---

# 滴答任务总控

目标：项目知道最终做成什么，本周知道验收什么，现在知道下一步做什么。

## 边界

- 当前任务事实从滴答运行态读取；聊天补背景，用户最新陈述可纠正旧状态。
- 只做任务规划：归属、依赖、优先级、投入估时、目标日期、硬截止与最晚启动风险。
- 不恢复日程清单、不读写 Outlook/日历、不生成钟点时间块，不保存个人可用时段或日历容量。
- 用户给出的“周三下午做”属于日程信息，不转换成 Planner execution window；任务侧只保留确有意义的目标日/硬截止或原文备注。
- 讨论方法或修改 Skill 不等于授权修改滴答，不必全库扫描。
- 局部操作局部读取；全局安排必须通过下面的完整扫描。

## 全局扫描

1. 枚举所有可访问业务清单，处理分页；同时检查原生 Inbox 和用户自建收集箱。
2. 获取全部未完成任务及必要父任务，不漏无日期、远期和 waiting 项。
3. config、memory、模板不计入执行工作；保留实际待办与必要上下文。
4. 核对 hard deadline、剩余工作、依赖、external lead time 和 Latest Safe Start。
5. 统计当前周已有承诺和必须处理的一次性节点，再决定是否新增/替换承诺。
6. 读取失败、分页未完或父任务缺失时列出范围，不能声称全库完整。

停用日程清单只跳过，不再读取内容。不要为了一个局部修改重复全量审计。

## 周交付流程

全量扫描 → 风险与必办节点 → 选择核心交付 → 定义验收合同 → 关联支撑任务 → 执行 → 证据验收。

- 路由至 `dida-weekly-delivery`，默认每周 0–2 个核心交付物。
- 通常保留工作和长期发展两个方向，但不是强制凑满；忙周允许只有一个核心交付物。
- 先限定产物和范围，再由 estimator 核投入；不把所有高优先级项都叫主线。
- 两块板同属硬件不意味着工作量可合并；共享工作也只能按真实共享叶子任务去重。
- 板测、出差、采购、问老师等一次性事项默认是 obligation，不因“很重要”自动升级成第三条主线。
- 没有 growth 交付时必须说明本周挤占原因和恢复/重新评估条件，不能默默长期延期。
- 今天做什么：从已承诺交付物选择最小可执行下一步，再列必要节点；不重新开启新的主线。

## Gate 驱动项目

对“选型 → 手册核对 → 功能确认 → 需求冻结 → 原理图/实现”这类有明确前置关口的项目：

- `dida-task-breakdown` 负责把 gate 做成持久阶段/任务和真实依赖；
- manager 只选择当前最近可验收的 gate，不提前把下游原理图/PCB 等承诺进本周；
- gate 未通过时，下游日期只保留已有外部硬截止，不根据乐观估时重新推算。

## 日期语义

- 目标日期是内部希望完成日；硬截止需要用户或外部明确依据。
- Latest Safe Start 需要截止、剩余工作、依赖链、外部经过时间和缓冲。
- 小时投入不能直接从日期相减。缺少“投入 → 经过天数”的可靠依据时记 unknown。
- 建议启动日不冒充 Latest Safe Start；提醒无交付链时可记不适用。
- 不依据旧标签或过时估时断言“只有几小时，所以你肯定有空”。

## 职责路由

| 请求 | owner |
|---|---|
| 录入/分类/去重 | dida-task-capture |
| 持久拆分、阶段 gate、依赖 | dida-task-breakdown |
| 投入估时/剩余工作 | dida-task-estimator |
| 本周交付/这周优先做什么 | dida-weekly-delivery |
| 日常进度/完成/实际投入/证据 | dida-task-progress |
| 周末整体验收、偏差、归档/换周 | dida-weekly-review |
| 唯一任务日期/归属调整 | 相关对象局部读写 |

manager 负责总控和路由，不重复实现 breakdown、estimator、progress 或 weekly-review 的细节规则。

## 写回

读取 → 比较 → 保留未指定字段 → 操作 → 回读。

- 不凭名称猜 ID、上下级或完成状态。
- 周承诺优先复用现有任务，不另建周总结任务。
- 写入时按真实 schema 选 content/desc；CHECKLIST 内容不能写到不可见字段后就称成功。
- 原生估时字段不存在时，不发明 API 参数；按运行态约定保留正文/标签中的估时及来源。
- 超时先查写入结果，不盲目重试。
- 最终只报告回读确认的变化，区分建议、已保存、失败和未处理。

## 完成检查

能回答：扫描范围、核心产物、验收方法、阻塞、工作量未知项、未纳入项及原因。

没有完整资料时给限定范围的可用结论，不假装所有任务都已安排妥当。
