---
name: dida-weekly-review
description: Review weekly deliverables against their original acceptance criteria and evidence, while checking all unfinished Dida tasks for deadline/start risks. Record delivered, not-delivered, blocked, cancelled or unverified outcomes. Preserve previous commitments before selecting the next week; no calendar scheduling or silent rollover.
---

# 滴答周验收与复盘

先看承诺的结果是否可验收，再看实际工作与偏差。努力记录要保留，但不能代替成果验收。

## 读取

1. 使用用户确认的时区/周边界；不因 VPN 地点静默切换。
2. 全局复盘枚举所有业务清单/未完成任务，处理分页；不只查近 7 天。
3. 读取本周已完成任务、owner 周合同及评论，避免遗漏已交付的 owner。
4. 读取本周 progress 事件、实际投入证据和 external wait；无起止时间不得编造精确专注记录。
5. 读取相关 profile、依赖及父子信息；停用日程清单不读取。

文件、记忆或本地缓存不替代运行态任务。未读全时明确本次覆盖范围。

## 验收

对照本周最初承诺，逐项列产物、标准、证据和剩余差距。

- delivered：标准满足且有明确用户确认或检查证据。
- not_delivered：有工作进展，但未满足完整约定。
- blocked：外部条件或前置工作未满足，记录具体对象和解除条件。
- cancelled：经用户确认取消，保留原承诺和原因。
- unverified：证据不足，不能判断是否交付。

不按百分比自动验收；不能把更宽的大项目同时完成。成果只按实际证据写，不声称看过未读取的文件。

## 与 progress 的分工

`dida-task-progress` 负责周中单次事实更新：完成了什么、实际投入、等待/恢复、证据、当前合同状态。weekly-review 不重写这些事实，而是把**一整周所有承诺**与原始验收合同对齐，做偏差分析、归档和换周决策。

若 progress 已把某合同标成 delivered，review 仍核对其证据是否与原 criteria 对应；不因为已有状态就跳过审计。

## 偏差分析

优先只指出 1–3 个影响下周选择的原因：范围偏大、估时偏低、外部等待、插入工作、同时推进过多或成果标准变化。

保持“原承诺 → 实际结果 → 剩余工作 → 下周决定”可追溯。部分完成如实记，不用“没交付”抹掉全部进展。

若本周没有 growth 交付，核对当周是否记录挤占原因和恢复条件；连续被挤占时把它作为 WIP/优先级风险显式带到下周选择，不自动假设“以后有空再做”。

## 风险检查

检查所有未完成工作中的硬截止、剩余工作、依赖、external lead time 与 Latest Safe Start。

- 到期但可延期的目标不等于硬截止。
- 未知 Latest Safe Start 不是安全；没有经过时间依据不能编日期。
- 只按用户提供的投入预算核对任务量，不读取日历容量。
- 必办节点和等待风险仍纳入判断。
- gate 未通过时，不把下游实现/原理图任务当成“已可执行”。

## 下周

由 `dida-weekly-delivery` 重新选 0–2 个核心交付物。

未完成项选择：保留原范围、缩小为新一周产物、改为 waiting、退回 backlog/future 或用户确认取消。不能一键把全部日期推到下周。

连续未交付时优先重估/缩范围，而不是再增加优先级。growth 被挤占时重新检查原因是否仍成立，并更新恢复条件。

## 写回顺序

读取原合同 → 追加验收历史并回读 → 清旧周标记 → 用户授权后写新合同 → 回读。

评论长度按实际接口拆分；operation_id 用于幂等核对。归档失败则不清原字段。不创建独立周总结任务或另一份可编辑 Markdown 周计划。

## 输出

通常只输出：核心交付验收结果及证据；关键偏差与必须处理风险；下周交付物建议与明确不纳入事项。

指标仅在有原承诺与证据时统计；不能用完成了多少条琐事替代周目标验收率。

## References

- `references/review-protocol.md`
- `dida-weekly-delivery`
