---
name: dida-task-breakdown
description: Split Dida projects or oversized work by observable deliverables, scope, acceptance and dependencies. Reuse the existing hierarchy; weekly commitments are metadata rather than new parent trees. Prefer MCP/connectors; use dida-cli only as fallback. Do not create execution time blocks.
---

# 任务拆分

产物 → 验收条件 → 必要工作 → 依赖。先定义成果，再决定是否需要新任务。

## 读取范围

局部拆分先读取 owner、children、同级节点、DoD 和相关依赖/项目规则。全局重排才通过 `dida-manager` 的完整扫描。

MCP/连接器优先，文件和记忆不替代当前任务结构。

## 层级

project 是长期项目；phase 是阶段；task 是可执行且可验收的工作。

旧 `block` 只为历史兼容保留，不再创建。周承诺不是新层级，不新增周计划父任务。

## 是否拆分

- 多个独立产物、明显串行依赖、范围难以一句话界定时拆分。
- 同一动作内部“打开文件/修改/保存”不要拆成任务。
- 简单检查点用原 task 的 checklist，不堆微任务。
- 现有结构能复用就复用，不静默重命名或跨项目移动。

## 按产物切分

每个 task 至少有：具体输出、范围、可判定 DoD、验收方式和必要前置。

“看完全部手册”往往太宽，可拆成“一组已选器件的供电/接口约束表及未决项”。“继续写代码”应明确哪个模块、哪些场景通过验证。

用真实产物判断大小，不按“项目名相同”合并两个独立工作量。只有一个共用产物时可以跨项目引用支撑任务，保留原 parentId 并按实际工作去重。

## Gate 驱动拆分

当后续工作必须等前一阶段结论冻结时，用持久依赖表达 gate，而不是靠周计划文字记住顺序。

典型主干：关键器件/方案确认 → 手册约束核对 → 外部/老师功能确认 → 需求冻结 → 原理图/实现。

- gate 本身必须有可验收产物，例如“需求冻结清单 + 未决项归零/明确延期”。
- 下游 task 用 hard `finish_to_start` 指向 gate；gate 未满足时不视为 ready。
- 只有真实约束才设 hard；“最好先做”仍是 soft。
- 下游日期不要因为一个乐观估时提前生成；已有外部 hard deadline 保持原样。

## 依赖

- finish_to_start：前置成果完成才开始。
- start_to_start：前置已开始即可。
- external_wait：等物料、反馈、审批等明确条件。
- not_before：不能早于指定日期。

只有真实限制才设 hard dependency；建议顺序写 soft。写前检测环路，缺前置 ID 时记录未决项，不猜 ID。

## 周交付切片

若总任务适合跨周保留，可在其上记录本周范围和标准，不要求拆出同名副本。

达到本周标准不等于整个 task/phase 完成。周交付所需的支撑工作必须与本周范围一致；引用整项估时会明显过大时，先明确本周剩余工作量，不能默默打折。

只有当本周切片需要形成长期可复用的独立任务/依赖时才改持久层级；否则由 `dida-weekly-delivery` 只写周合同。

## 估时和写回

范围明确后调用 `dida-task-estimator`。未知流程先定义可验收的一轮探索，再估这一轮，不承诺整个设计周期。

只讨论方案时不写；用户要求拆到滴答时：读取 → 去重 → 仅改授权字段 → 写回 → 重新读取 owner/children。

保留日期、内容、附件及未知字段；CHECKLIST 的 desc/items 按实际 schema 更新。不为凑格式删除原任务。

## 验收

子任务覆盖阶段成果、每项有 DoD、依赖无环、无重复、估时有依据或标 unknown、实际写入已回读。

## References

- `references/hierarchy-and-dependencies.md`
- `dida-task-estimator`
- `dida-weekly-delivery`
