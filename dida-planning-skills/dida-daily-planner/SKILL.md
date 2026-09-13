---
name: dida-daily-planner
description: Build, revise, and optionally apply realistic Dida day/week plans. For global planning requests, first scan all unfinished TickTick tasks through the available MCP/connector, then check deadlines, latest-safe-start risk, dependencies, estimates, external lead times, capacity, fixed/protected commitments, energy preferences, and one-day exceptions. Generate exact clock blocks only when the user explicitly asks for them. Prefer MCP/connector reads and writes; use dida-cli only as fallback.
---

# Dida Daily Planner

把用户的任务池排成**现实可执行、容量不过载、依赖正确，而且不会因为只看近期任务而漏掉远期风险**的计划。

本 Skill 有两种工作模式：

1. **全局规划模式**：例如“帮我安排这周”“现在该做什么”“根据已有任务重新排一下”。先全量扫描，再按天/优先级安排。
2. **具体时间块模式**：例如“今天 14:00 到 18:00 怎么排”“把这些任务排成时间块”。只有这种明确需求才生成具体开始/结束时间。

普通单任务查询、单个日期修改、完成任务等局部 CRUD 不自动触发本 Skill。

## 职责边界

本 Skill 负责：

- 全局规划时读取全部未完成任务；
- 识别截止风险和 `latest_safe_start` 风险；
- 读取真实可用时间和 fixed/protected 承诺；
- 检查依赖、外部等待、估时和精力匹配；
- 从全局任务池挑选规划期内真正该做的工作；
- 用户明确要求时生成具体时间块；
- 用户要求应用时通过 MCP/连接器写回并 read-back；
- 实际执行偏离后重新规划 remaining work。

本 Skill 不负责：

- 自动给每天生成时钟日程；
- 自行改变硬截止；
- 只因为 due date 很远就忽略任务；
- 为范围不明的复杂任务凭空估一个确定时间；
- 把所有 backlog 塞满全天；
- 静默移动 fixed 承诺；
- 静默缩短 protected 活动；
- 把模型记忆当成完整任务数据库。

## Source of truth

### 任务事实

当前任务事实必须来自 TickTick/滴答清单运行态：

- 项目/清单；
- 未完成任务；
- 日期和优先级；
- 父子关系；
- recurrence；
- 评论/focus/估时等可用执行信息。

如果有可用 TickTick MCP/连接器，优先使用它。`dida-cli` 只在没有连接器的本地环境中回退使用。

### 规划配置

按需读取：

1. `规划偏好｜作息与容量`；
2. `规划偏好｜日程移动权限`；
3. `估时配置｜特征与风险缓冲`；
4. `系统协议｜依赖关系`；
5. 相关项目的长期规则；
6. 当前对话的一次性例外；
7. 当前时区和当前时间；
8. 天气仅在出行/户外等确实受影响时读取。

模型记忆可以帮助解释项目背景，但**不得用于判断“任务是否齐全”**。

## 固定工作流程

### Step 1 — Resolve planning horizon

先确定：

- 是今天、某一天、本周、下周还是更长窗口；
- 用户当前时区；
- 如果包含今天，当前时间；
- 用户要的是日级安排还是明确时钟块。

相对日期必须解析成绝对日期。

### Step 2 — Global inventory scan when required

如果用户要求全局规划，必须先做**完整任务盘点**，不能只查 `today` / `next7day`。

必须：

1. 枚举所有可访问项目/清单；
2. 读取全部未完成任务，处理分页；
3. 保留无日期任务、远期任务、waiting 任务、项目父节点的必要上下文；
4. 识别重复、已开始、等待中、blocked、active phase；
5. 不因为任务没有日期就默认它不重要。

只有明确的局部规划（例如“只排这三个任务”）才可以不做全量扫描。

### Step 3 — Read immutable and protected occupancy

读取规划窗口内不可随意覆盖的内容。

#### fixed

会议、预约、出行、用户明确指定不可移动事项、已经开始且必须连续完成的事项等。默认不移动。

#### protected

按当前 profile 定义的个人承诺/活动。只能在允许范围内移动，不能默认删除、跨天或缩短。

#### movable

普通任务根据容量、优先级和风险调整。

### Step 4 — Build actual capacity

从可用工作窗口中扣除 fixed/protected、通勤、休息、已过去时间和必要 buffer。

不能只看总小时数，还要看窗口形状：连续 3 小时与三个零散 1 小时不等价。

对周计划，计算每一天可用于不同类型工作的容量，不把未来所有空白都当作 100% 可用。

### Step 5 — Normalize task execution data

对可能进入规划的执行任务确认：

- remaining work；
- estimate confidence；
- hard/soft dependency；
- waiting/external dependency；
- hard deadline / due date；
- 是否可分段；
- 是否存在审核、采购、打样、物流、预约、反馈等 lead time。

没有可信 estimate 时调用 `dida-task-estimator`；范围过大或 DoD 不清时先退回 `dida-task-breakdown`。

### Step 6 — Compute deadline risk and latest safe start

对有交付/截止约束的任务，不仅看 due date，还要判断：

`latest_safe_start = 最晚仍能以可接受风险完成整条交付链的启动窗口`

至少考虑：

- 自身 remaining work；
- 必须串行的前置工作；
- 外部 lead time；
- 用户未来真实容量；
- 估时置信度；
- 风险 buffer。

例如：

```text
10/30 必须现场使用
← 物流 4 天
← 打样 7 天
← 审核 3 天
← 修改/出图 5 天
```

这种任务不能等到 10/29 才因“临近截止”变高优先级。

如果缺少足够信息，标记 `start-risk: unknown`，并优先安排一次澄清/估算，而不是默认安全。

### Step 7 — Build candidate pool

候选任务来自真实运行态数据，优先包括：

- 用户明确指定的任务；
- 已开始但未完成的任务；
- 规划期内已有日期的 executable task；
- `latest_safe_start` 已进入规划窗口的任务；
- 临近 hard deadline 的任务；
- active phase 中依赖已满足的下一步；
- 用户明确要求考虑的 backlog。

排除或降级：

- 纯 project/phase/config/memory 节点；
- hard dependency 未满足；
- waiting 且当前确实无法推进；
- 完全未知范围、无法形成执行 DoD 的任务。

waiting 任务本身可以不执行，但如果它的等待会威胁 latest safe start，需要显式暴露风险。

### Step 8 — Rank by risk, value and fit

优先级不是简单按 due date 排序。综合：

1. hard deadline / latest-safe-start 风险；
2. 是否已开始、切换成本；
3. 前置任务是否会解锁后续关键工作；
4. 用户明确优先级；
5. 任务价值；
6. 当前窗口和精力是否匹配。

高认知任务优先放连续高精力窗口；机械整理/沟通适合碎片或低精力窗口。

### Step 9 — Keep reserve and breaks

不把 free windows 100% 塞满。

- estimate confidence 越低，buffer 越大；
- 一天切换过多时少排任务；
- 容量不足时明确留下低优先任务，不偷偷压缩所有任务；
- AI 可并行执行的 elapsed time 不重复占用用户日历。

### Step 10 — Produce the right planning granularity

#### 用户只要求“安排今天/本周”

默认给日级或优先级安排，例如：

```text
周一：完成 A；开始 B
周二：B 主体工作；处理 C
周三：预留审核反馈 / buffer
```

不要自动创造具体时钟块。

#### 用户明确要求具体时间

才输出：

```text
14:00–15:30 任务 A
15:45–17:00 任务 B
```

### Step 11 — Optional deterministic scheduling engine

当用户明确需要具体时间块，且存在多个任务/复杂窗口时，可使用：

```bash
python dida-planning-core/scripts/scheduling_engine.py \
  --input day.json \
  --output schedule.json
```

脚本只负责确定性放置、buffer 和 overlap 检查；主代理仍负责风险、依赖、价值和语义判断。

### Step 12 — Apply through MCP/connector first

用户要求直接应用时：

1. 读取将修改对象当前状态；
2. 只修改用户已授权且规划需要的字段；
3. 保留未知字段和非冲突标签；
4. 写后 read-back；
5. 检查没有重复任务、重复 block、丢失任务或错误父子关系；
6. 如果发生超时/结果不明，先读回确认再决定是否重试。

有 MCP/连接器时禁止为了“沿用旧 Skill”而绕回 CLI。

没有 MCP/连接器时，才使用 `dida-cli` fallback，并遵循其安全协议。

### Step 13 — Replan after reality changes

实际执行偏离后：

- 已发生的事实不重写；
- 已完成任务移出 remaining pool；
- 超时任务重新估 remaining work；
- 新 fixed 事项先占容量；
- 重新计算 latest-safe-start 风险；
- 未完成任务重新判断，不自动全部顺延到明天。

## Capacity failure handling

如果规划期放不下，按顺序处理：

1. 保留 fixed；
2. 保留 hard deadline / latest-safe-start critical work；
3. 保留已开始且切换成本高的必要工作；
4. 保留 protected commitments；
5. 移出最低价值/最可移动任务；
6. 若仍不可行，明确指出需要用户决定的冲突。

不要通过压缩必要休息、伪造更短 estimate 或忽略 lead time 来制造容量。

## 完成 Gate

全局规划至少满足：

1. 已扫描全部未完成任务，并处理分页；
2. 无日期/远期任务没有被天然忽略；
3. 有交付约束的任务检查了 latest safe start；
4. hard dependency 均正确处理；
5. fixed/protected 权限未违反；
6. 总容量没有隐性超卖；
7. 所有安排任务有可信 duration 或明确探索 DoD；
8. 未安排任务有明确原因；
9. 用户未要求时没有擅自生成具体时钟块；
10. 若写回 Dida，read-back 与计划一致。

如果没有完成全量扫描，不得声称“所有任务都已安排到位”。

## References

- `references/daily-rules.md` — 通用日程原则与运行态读取规则。
- `references/weather.md` — 天气真正影响执行时再使用。
- `dida-task-estimator` — duration / confidence。
- `dida-task-breakdown` — 范围过大或不清时退回拆分。
- TickTick/滴答清单 MCP 或等价连接器 — 首选运行态读写。
- `dida-cli` — 无连接器环境下的 legacy/local fallback。
