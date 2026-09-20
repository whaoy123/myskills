---
name: dida-weekly-delivery
description: Select and define 0–2 verifiable weekly deliverables on existing TickTick tasks. Use for 每周交付物、本周成果、周承诺、这周做什么. Specify artifact, scope, acceptance, evidence, supporting tasks and exclusions. Preserve career/growth work without hiding workload or scheduling calendar time blocks.
---

# 周交付规划

周目标是一个可验收结果，不是“推进到某处”的活动记录。

## 先读什么

- 全局选择必须先通过 `dida-manager` 的完整任务扫描及截止/Latest Safe Start 检查。
- 局部修改一个已选交付物，只读取 owner、支撑任务、原承诺和相关依赖。
- 读取 `规划偏好｜周交付与任务投入`；未初始化时使用默认上限 2，但不假定周投入预算。
- 配置、模板和记忆不算工作。运行态任务优先于静态例子。

## 选择流程

1. 列必须处理的节点、真实硬截止、启动风险、外部等待和当前已有承诺。
2. 默认选 0–2 个核心周交付物，通常工作/课题一个、求职/长期发展一个。
3. 明确单一产物和本周范围；多个无关产物不能用一个大标题伪装成一个。
4. 从范围反推需要的叶子任务；需要新增持久层级或 gate 时交给 `dida-task-breakdown`。
5. 由 `dida-task-estimator` 核剩余投入与不确定性；重用已有任务，不为适配预算反调估时。
6. 核对用户明确给出的投入预算。未知就标 unknown，不从日历推算，也不硬套固定小时数。
7. 放不下时先缩小范围、替换或取消本周承诺；不要无限叠加主线。

2 个是可覆盖的默认上限，不要求凑满。例外需记录原因、用户同意及被挤出的工作。

## 六项验收合同

- **产物**：文件、表、代码+验证结果、测量记录或口述演示。
- **范围**：哪些器件/功能/场景包含在本周，哪些不包含。
- **完成标准**：逐项可判断的条件，不能只有“基本掌握”。
- **验收方式**：怎样查看、演示或测试；谁确认。
- **支撑任务**：运行态真实 ID；不改变这些任务的项目归属。
- **本周不做**：防止范围持续增长的边界。

格式及示例见 `references/weekly-contract.md`。

## 工作量、名额与防饥饿

- 默认尽量保留一个 growth 交付；工作挤占时必须写明 `growth_deferral_reason` 与 `growth_resume_condition`，至少在本次计划输出中可追溯。
- 板测、出差、沟通、采购、预约仍计入投入，默认作为 obligation，不统一视作免费“小节点”。
- 同一叶子只计一次；父阶段与子任务不重复估时。
- 两个项目任务相似，只能复用真正相同的工作，不能把名称合并后当成减负。
- 未知环节可先交付“探索结论 + 未决项”，不把“完整设计”承诺成几小时。
- 全部支撑任务并不同时标为进行中；通常一次推进一个上下文。

## 与 breakdown / progress / review 的边界

- weekly-delivery 只定义**本周切片**；持久项目层级、长期 DoD、阶段 gate 和依赖由 `dida-task-breakdown` 管。
- `dida-task-progress` 在周中记录事实、证据和当前合同状态，不做整周重新选择。
- `dida-weekly-review` 在周末对所有承诺做汇总验收、偏差分析、归档和换周；它不修改旧合同来“补成完成”。

## 原地写回

优先选一个已有 task/phase 作为 owner：

- 沿用 `week_start`、`weekly_commitment: must|should|candidate`。
- 增加 `weekly_delivery` JSON 对象；结构版本为 1，Planner schema 仍为 1。
- 支撑任务放在 owner 的引用列表，保持原 parentId。
- `must/should` 是周承诺等级，不改变原生硬截止；candidate 不算核心承诺。
- task owner 的 `support_task_ids` 非空时，工作量由这些引用叶子代表；不能再把 owner 的汇总估时重复相加。
- 不生成“本周计划”父任务、执行块或另一份持久 Markdown 任务库。
- 纯建议不写入；“安排/更新到滴答”等授权后才操作并回读。

结构化校验可使用：

```bash
python dida-planning-core/scripts/weekly_delivery.py --input dida-weekly-delivery/assets/example-plan.json
```

该脚本只处理瞬时快照并给校验结果，不直接操作滴答。

## 验收和换周

交给 `dida-task-progress` / `dida-weekly-review`：delivered、not_delivered、blocked、cancelled、unverified。

- 用户明确确认完整合同范围可以记 user_report；未查看文件不得写成工具验证通过。
- 本周子范围交付不自动完成 owner 大任务。
- 换周先归档原承诺及证据，再清理旧周字段；是否承接下周重新选择。
- 不静默降低旧验收条件，也不把每个未完成项自动滚到下周。

## 输出

默认只给：核心交付物及验收；必办节点/阻塞；明确不纳入项。没有 growth 时同时给挤占原因和恢复条件。

不要再输出完整长期任务清单；只有用户要求时才展开。
