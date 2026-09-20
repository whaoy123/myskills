---
name: dida-task-capture
description: Classify, deduplicate, and capture a new task, idea, reminder, or project into 滴答清单. Decide destination, parent relationship, executable/waiting role and true date semantics. Prefer TickTick/滴答清单 MCP or connector tools for reads and writes; use dida-cli only as fallback. Do not deeply decompose, estimate, schedule, or promote a new item into a weekly core deliverable unless the user invokes those workflows.
---

# Dida task capture

把用户的新事项整理成一条干净、可找到、不会和已有任务重复的 Dida 记录。Capture 负责**分类和归档**，不负责日程排程。

## Capture 前最小读取

不要为了记录一个小任务扫描整个任务库，但必须读取足够信息避免放错位置或重复：

1. 用户明确指定的项目/父任务；
2. 与新事项高度相似的任务标题/关键词；
3. 相关父任务及必要项目上下文；
4. `系统协议｜标签与任务正文` 等直接影响归档的配置；
5. 只有当项目长期规则会改变归类时才读取对应 memory。

模型记忆可以提示可能归属，但不能替代运行态任务搜索。

## Capture flow

1. **提炼最小可执行标题**：动作 + 对象，通常控制在 25 个中文字符左右。
2. **去重**：已有同一执行项优先更新/补充；只是相关但不同则保留独立任务；无法判断时报告候选，不静默合并。
3. **确定归属**：用户明确指定 list/parent 时优先；明确属于现有项目时挂入对应项目；归属不明才进入 Inbox；不为整理外观擅自新建 project/list。
4. **判断角色**：`project / phase / task`。普通事项默认 `task`；真正等待外部条件才能继续的事项记录 waiting 语义；长期规则交给 `dida-planning-memory`。
5. **判断日期语义**：
   - “周五必须交”这类真实承诺 → `hard_deadline`；
   - “希望周五前完成”这类目标 → `target_date`；
   - 仅说“周三下午做”属于执行意图，不是任务规划约束；除非用户明确要 Dida 原生提醒，否则不把它转换成 Planner 日期语义；
   - 没有可靠日期 → `none`；
   - 若存在明显截止链但不知道何时必须启动，保持 undated，后续由 manager/estimator 在依据充分时计算 `latest_safe_start`。
6. **写入必要上下文**：完成标准、链接/路径、关键决定、未决问题；自然文本保持紧凑。
7. **通过 MCP/连接器创建或更新并 read-back**；只有无连接器时才回退 CLI。

## Defaults

- `progress: 0`
- `date_semantics: none`，除非用户提供真实日期含义。
- 不新写 `mobility` 或 `execution_window`；旧任务中的这些字段仅由核心协议兼容读取。
- 不自动发明 dependency、priority、estimate、reminder 或 recurrence。
- 不因为用户说“记一下”就触发完整任务规划。

## Parent and hierarchy

长项目优先作为现有 domain list 中的 parent task，而不是新建清单。父任务无法唯一解析时，宁可先放到正确 list 并报告 parent unresolved，也不要猜错父级。

## Inbox rule

只有当归属确实不清楚，或用户明确要求放 Inbox，才进入 Inbox。Capture 本身不触发批量 Inbox 清理。

## 与其他 Skill 的边界

- 任务太大/范围模糊 → `dida-task-breakdown`
- 用户问“大概多久” → `dida-task-estimator`
- 用户要求“这周怎么安排” → `dida-manager` / `dida-weekly-delivery`，并执行全局扫描 Gate
- 用户汇报完成/耗时 → `dida-task-progress`
- 稳定任务规划偏好 → `dida-planning-profile`
- 跨项目长期规则 → `dida-planning-memory`

## 新任务与本周承诺

默认新收集项先归类，不自动成为第三个核心交付物。紧急事项纳入本周时说明被替换/缩小的承诺，必办项仍计投入；由用户确认取舍。

## Output

报告实际保存的标题、清单、父任务、日期语义，以及尚未解决的不确定点。不要输出原始 JSON。

## References

Read `references/capture-protocol.md` for field mapping and `references/examples.md` only when an example is needed.
