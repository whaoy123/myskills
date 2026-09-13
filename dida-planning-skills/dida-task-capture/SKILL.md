---
name: dida-task-capture
description: Classify, deduplicate, and capture a new task, idea, reminder, or project into 滴答清单. Decide destination, parent relationship, executable/waiting role, date semantics, and whether the item should be scheduled now. Prefer TickTick/滴答清单 MCP or connector tools for reads and writes; use dida-cli only as fallback. Do not deeply decompose, estimate, or schedule unless the user also invokes those workflows.
---

# Dida task capture

把用户的新事项整理成一条干净、可找到、不会和已有任务重复的 Dida 记录。

本 Skill 的核心价值是**分类和归档判断**，不是提供底层 API 能力。运行环境已有 TickTick/滴答清单 MCP 或连接器时，直接使用连接器完成搜索、创建和 read-back；只有没有连接器时才回退到 `dida-cli`。

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
2. **去重**：搜索语义或标题高度相近的已有任务。
   - 已有同一执行项 → 优先更新/补充，而不是重复创建；
   - 只是相关但不同 → 保留独立任务并挂到同一父项；
   - 无法判断是否重复 → 报出候选，不静默合并。
3. **确定归属**：
   - 用户明确指定 list/parent 时优先；
   - 明确属于现有项目时放入对应项目；
   - 归属不明才进入 Inbox；
   - 不为了“整理得漂亮”擅自新建 project/list。
4. **判断角色**：`project` / `phase` / `task`。
   - 普通事项默认 `task`；
   - 真正等待外部条件才能继续的事项应标记 waiting 语义，而不是伪装成当前 executable；
   - 长期规则交给 `dida-planning-memory`，不混入业务任务树。
5. **判断是否现在排日期**：
   - 用户明确给出日期/期限 → 按其语义记录；
   - 有真实外部日期约束 → 可以记录；
   - 只是“以后要做” → 不凭空 invent date；
   - 若存在明显截止链但不知道何时必须启动，可先保留 undated，并提示后续 planner 计算 `latest_safe_start`。
6. **写入必要上下文**：完成标准、链接/路径、关键决定、未决问题；自然文本保持紧凑。
7. **通过 MCP/连接器创建或更新并 read-back**。
8. 若只有 CLI 可用，才调用 `dida-cli` fallback。

## Defaults

- `progress: 0`
- `date_semantics: none`，除非用户提供真实日期含义。
- 普通工作默认 movable；会议/预约/出行等明确承诺可为 fixed；protected 只按运行态 profile 规则判断。
- 不自动发明 dependency、priority、estimate、reminder 或 recurrence。
- 不因为用户说“记一下”就触发完整日程规划。

## Parent and hierarchy

长项目优先作为现有 domain list 中的 parent task，而不是新建清单。父任务无法唯一解析时，宁可先放到正确 list 并报告 parent unresolved，也不要猜错父级。

## Inbox rule

只有当归属确实不清楚，或用户明确要求放 Inbox，才进入 Inbox。Capture 本身不触发批量 Inbox 清理。

## 与其他 Skill 的边界

- 任务太大/范围模糊 → `dida-task-breakdown`
- 用户问“大概多久” → `dida-task-estimator`
- 用户要求“今天/这周怎么安排” → `dida-manager` / `dida-daily-planner`，并执行全局扫描 Gate
- 用户汇报完成/耗时 → `dida-task-progress`
- 稳定规划偏好 → `dida-planning-profile`
- 跨项目长期规则 → `dida-planning-memory`

## Output

报告实际保存的标题、清单、父任务、日期语义，以及尚未解决的不确定点。不要输出原始 JSON。

## References

Read `references/capture-protocol.md` for field mapping and `references/examples.md` only when an example is needed.
