---
name: dida-daily-planner
description: Build, revise, and optionally apply a realistic Dida day plan only when the user explicitly asks for concrete schedule planning. Read current availability, fixed/protected commitments, mobility permissions, dependencies, estimates, deadlines, energy preferences, and one-day exceptions from Dida/runtime context. Use capacity-aware time blocks, preserve hard commitments, keep buffer and breaks, and verify all applied changes through dida-cli.
---

# Dida Daily Planner

把用户已经决定要规划的一天排成**现实可执行、容量不过载、依赖正确**的时间块。

本 Skill 只在用户明确要求排具体日程时触发，例如：

- “帮我排一下今天”；
- “明天具体怎么安排”；
- “把这些任务排到时间块里”；
- “今天剩下的时间重新排一下”。

普通任务查询、任务拆解、估时或 backlog 整理不自动触发 Daily Planner。

## 职责边界

本 Skill 负责：

- 读取当天真实可用时间；
- 保护 fixed / protected 承诺；
- 从候选任务中选择当天能容纳的工作；
- 检查依赖、截止、估时和精力匹配；
- 生成具体开始/结束时间；
- 必要时把大任务拆成当天执行 block；
- 当用户要求应用时写回 Dida 并 read back；
- 已经执行偏离计划后重新规划剩余时间。

本 Skill 不负责：

- 自动给每天生成日程；
- 自行改变硬截止；
- 为没有估时的复杂任务凭空塞一个时间块；
- 把所有 backlog 塞满全天；
- 静默移动 fixed 承诺；
- 静默缩短 protected 活动；
- 把并行 AI 时间重复占用用户日历。

## Runtime source of truth

具体作息和个人偏好属于运行态，不写死在 Skill 中。

每次规划按需读取：

1. 当天已有 Dida 任务、日程块和状态；
2. `规划偏好｜作息与容量`；
3. `规划偏好｜日程移动权限`；
4. `估时配置｜特征与风险缓冲`；
5. `系统协议｜依赖关系`；
6. 相关项目任务树和必要 project memory；
7. 用户在当前对话给出的 one-day exception，例如“今天可以做到 22:00”；
8. 当前时区和当前时间；
9. 天气只在出行、户外、通勤、运动等会受天气实质影响时读取。

运行态 Dida NOTE 一旦存在，就是权威值。仓库模板只用于首次初始化，不周期性覆盖运行态配置。

## 任务与时间块角色

```text
project / phase → 只提供上下文，不占当天容量
task            → 可执行工作和总估时
block           → 某一天中 task 的一次实际执行时段
```

一个 2h task 可以今天排 60min block、明天再排 60min block，只要任务本身允许分段。

不要为了排日程把所有 task 永久拆成 block；只有确实需要跨时段执行或保留当天计划痕迹时才创建 block。

## 固定工作流程

### Step 1 — Resolve day and current time

先确定：

- 规划日期；
- 用户当前时区；
- 如果是今天，当前时间；
- 当前已经过去的时间不能重新安排。

相对日期必须解析为绝对日期。

### Step 2 — Read immutable and protected occupancy

先放入当天不可随意覆盖的内容。

#### fixed

例如：

- 会议；
- 预约；
- 出行；
- 已经开始且必须连续完成的事项；
- 用户明确指定不能移动的时间块。

默认不移动。

#### protected

例如运行态配置中标成 protected 的健身、个人承诺等。

可以只按当前 profile 允许的范围移动；不能默认删除、跨天或缩短。

#### movable

普通任务可以根据容量和优先级调整。

具体权限以 `规划偏好｜日程移动权限` 为准，不在 Skill 中硬编码某项活动永远属于哪个类别。

### Step 3 — Build actual free windows

从当天可用窗口中减去 fixed / protected occupancy，形成 free windows。

同时考虑：

- 已经过掉的时间；
- 午饭、休息、通勤等运行态约束；
- 用户当前的一次性例外；
- 必要 buffer；
- 连续高认知工作上限；
- 任务之间的切换成本。

不能只算“还有 5 小时空白”，还要看它是否被切成多个小窗口。

### Step 4 — Build candidate pool

候选任务优先从真实 Dida 数据中产生，而不是根据项目名称猜。

读取：

- 用户明确指定今天要做的任务；
- 已经开始但未完成的任务；
- 当天已有 date / `今天` 标记的 executable task；
- 临近硬截止且已经进入有效执行窗口的任务；
- 当前 active phase 下依赖已满足的下一批任务；
- 用户明确要求考虑的 backlog。

排除：

- `project / phase / config / memory`；
- hard dependency 未满足；
- 明确 waiting 且当前无法推进；
- 没有足够信息估时的复杂任务。

不要因为父项目重要就把所有 children 都拉进今天。

### Step 5 — Ensure estimates are usable

每个候选执行单元必须有可用预计时长。

- 已有可信 estimate → 使用；
- estimate 已因范围变化失效 → 调用 `dida-task-estimator` 重估；
- 大任务只计划其中一段 → 明确该 block 的目标和时长；
- 完全未知范围 → 只排一个有明确 DoD 的探索 block，或先退回 Breakdown。

AI 可并行运行的 elapsed time 与用户 calendar occupancy 分开。

### Step 6 — Check dependencies and deadlines

依赖检查优先于“看起来很重要”。

- hard dependency 未满足 → 不排执行块；
- external wait 未解除 → 不假装可以推进；
- soft dependency → 可以排，但要知道风险。

硬截止不能由 Planner 修改。

对临近截止任务，使用**有效执行截止**：根据剩余估时和未来真实容量反推最后可执行窗口，而不是等到 deadline 当天才变高优先级。

### Step 7 — Fit work to energy and window shape

结合运行态 profile 中的精力偏好：

- 高认知任务优先放高精力窗口；
- 低精力窗口放机械、整理、沟通或 AI-parallel 工作；
- 需要连续上下文的任务尽量使用较完整窗口；
- 很短窗口只放真的能在该窗口结束的工作。

不要把 profile 中的“下午最好”“60min 一块”等某个用户值写成通用 Skill 常量。

### Step 8 — Keep reserve and breaks

日程不是装箱问题，不能把 free windows 100% 塞满。

保留多少 buffer、连续工作多久、休息多久，以当前 profile 为准。

额外原则：

- 不把任务的 nominal estimate 当成零误差；
- confidence 低的任务留更多弹性；
- 一天中任务切换过多时，宁可少排一个任务；
- 如果容量明显不足，明确把低优先候选留在 pool，不偷偷压缩所有任务。

### Step 9 — Use deterministic scheduling engine

当日程包含多个任务、fixed 块或复杂窗口时，优先使用：

```bash
python dida-planning-core/scripts/scheduling_engine.py \
  --input day.json \
  --output schedule.json
```

脚本负责：

- 从 availability 中扣除 fixed occupancy；
- 检查 dependencies ready；
- 按 duration 放置；
- 加 buffer；
- 输出未安排任务及原因；
- 检查 overlap。

主代理仍负责：

- 正确构造输入；
- 判断 mobility；
- 判断任务的 energy / priority / deadline 语义；
- 检查输出是否符合用户真实意图。

不要把 scheduling engine 的简单排序逻辑当成完整规划判断。

### Step 10 — Present plan before destructive changes

普通“帮我排今天”默认先给紧凑日程方案。

如果用户明确说“直接写到滴答 / 直接调整”，可以直接应用可逆、范围清楚的日期/时间块更新。

以下变化需要特别谨慎：

- 移动 fixed；
- 跨天移动 protected；
- 删除已有 block；
- 改硬截止；
- 把已经开始的工作强行换到别的任务；
- 大范围改动用户已经手排的日程。

不要为了得到一个无冲突表格而破坏真实承诺。

### Step 11 — Apply through dida-cli

应用时：

1. 读取每个将修改的 task/block 当前状态；
2. 创建或更新时间字段；
3. 保留未知字段和原有非冲突标签；
4. 按系统协议维护可见 `今天` 标记（如果当前运行态采用该机制）；
5. 不给 project/phase 父节点因为日期窗口重叠就加 `今天`；
6. 写后重新读取当天视图；
7. 检查无 overlap、无重复 block、无丢失任务。

### Step 12 — Replan after reality changes

如果当天执行偏离计划：

- 当前时间以前的记录保持事实，不重写历史；
- 已完成任务直接移出剩余容量；
- 实际超时的进行中任务先重新估计 remaining work；
- 新出现的 fixed 事项先占位；
- 对剩余 free windows 重新运行规划；
- 未完成任务重新判断，不自动全部顺延到明天。

## Capacity failure handling

如果今天放不下，不通过压缩休息或缩短 protected 承诺来制造容量。

按顺序处理：

1. 保留 fixed；
2. 保留 hard-deadline critical work；
3. 保留已经开始且切换成本高的必要工作；
4. 保留运行态定义的 protected commitments；
5. 移出最低价值/最可移动任务；
6. 如果仍然不可行，明确指出冲突并给出需要用户决定的选项。

## 完成 Gate

日程完成至少满足：

1. fixed / protected 权限没有被违反；
2. 没有时间 overlap；
3. 所有安排任务都有可信 duration；
4. hard dependency 均已满足；
5. 用户日历占用没有重复计算 AI parallel time；
6. 留有符合当前 profile 的休息和 buffer；
7. 当天总容量没有被隐性超卖；
8. 未安排任务有明确原因；
9. 若已写回 Dida，read-back 与建议日程一致。

## 输出

默认直接给紧凑时间表，例如：

```text
17:40–18:30 任务 A
18:30–19:10 晚饭 / 休息
19:10–20:10 任务 B
20:20–21:00 任务 C
```

然后只补充：

- 哪些任务今天没排进去；
- 为什么；
- 真正需要用户决定的冲突。

不要把内部 scoring、JSON 或 Planner block 全部展示出来。

## References

- `references/daily-rules.md` — 通用日程原则与运行态读取规则。
- `references/weather.md` — 天气真正影响执行时再使用。
- `dida-task-estimator` — duration / confidence。
- `dida-task-breakdown` — 范围过大或不清时退回拆分。
- `dida-cli` — 实际写入和 read-back。
