---
name: dida-planning-profile
description: Initialize, inspect, or update Dida “系统配置” NOTE tasks for stable planning preferences and planning-system protocols: availability/capacity, mobility permissions, estimation policy, task-body/tag protocol, dependencies, timezone behavior, and schema version. Keep concrete user values in runtime Dida NOTE tasks, not in the distributable Skill or repository templates. Use when the user changes a stable planning preference or asks to initialize/configure the planning system.
---

# Dida Planning Profile

维护 Dida `系统配置` 中的稳定规划规则。

核心原则：

> Skill 只定义“有哪些配置、谁负责、怎么读写”；具体作息、精力、活动偏好等用户值只存在运行态 Dida NOTE 中。

## Configuration NOTE set

- `规划偏好｜作息与容量`
- `规划偏好｜日程移动权限`
- `估时配置｜特征与风险缓冲`
- `系统协议｜标签与任务正文`
- `系统协议｜依赖关系`
- `系统状态｜Schema与迁移版本`

Long-term project/tool/workflow memory 不放进这六个 NOTE，由 `dida-planning-memory` 单独负责。

每个 NOTE：

- `role: config`；
- 不作为可执行工作估时；
- 不进入普通任务容量统计；
- 默认无 status；
- 除非它本身就是一个配置提醒，否则不设置调度日期。

## Ownership

### `规划偏好｜作息与容量`

负责稳定的：

- 常规可用工作窗口；
- 固定休息/不可用窗口；
- 高低精力规律；
- 偏好的专注块与休息长度；
- 连续认知工作上限；
- 每日容量、reserve、重要任务数量等偏好；
- 稳定的 deadline 提前量偏好。

### `规划偏好｜日程移动权限`

负责：

- `fixed / protected / movable` 定义；
- 哪些活动属于哪种 mobility；
- 可否同日移动、跨天、缩短、删除；
- 已开始任务的移动规则；
- hard deadline 修改权限。

### `估时配置｜特征与风险缓冲`

负责：

- 估时口径；
- 风险覆盖；
- 取整；
- 历史样本使用策略；
- calendar / focus / AI parallel 时间区分。

### `系统协议｜标签与任务正文`

负责：

- task role；
- 标题/正文协议；
- Planner block；
- 可见标签；
- 任务命名约定。

### `系统协议｜依赖关系`

负责 dependency schema 和语义。

### `系统状态｜Schema与迁移版本`

只负责 schema / migration / exact config IDs 等系统状态。

## Initialize

1. 使用 `dida-cli` 解析或创建 `系统配置`；
2. 检查六个 NOTE 是否已经存在；
3. 只从 `assets/config-notes/` 创建缺失项；
4. 模板只提供字段骨架和通用协议，不应包含真实用户作息或项目状态；
5. 对需要用户具体值的配置，允许保持 `未设置 / PARTIAL`，不要为了“初始化完整”伪造默认值；
6. read back 新建 NOTE；
7. 把 exact IDs 写入 `系统状态｜Schema与迁移版本`。

初始化必须幂等。已有用户编辑过的 NOTE 绝不由模板覆盖。

## Read behavior

普通 Dida 操作只读取相关 NOTE，不加载整套 profile。

例如：

- Daily Planner → 作息与容量 + 移动权限 + 必要估时/依赖协议；
- Estimator → 估时配置；
- Breakdown → 标签与任务正文 + 依赖协议；
- Capture → 标签与任务正文。

运行态 NOTE 一旦存在，就是当前用户配置真值源。

仓库里的 `assets/config-notes/` 只是首次初始化模板，不能在后续运行时当作 fallback 用户事实。

## Update a preference

1. 唯一解析负责该事实的 NOTE；
2. 区分稳定偏好和 one-day exception；
3. 稳定且用户明确的新偏好可以直接更新；
4. 一天的例外只保留在当前 planning interaction / task comment，不写入 stable profile；
5. 如果新值与已有明确规则冲突，指出冲突后替换，不保留两套同时生效的规则；
6. 保留无关 section；
7. 用 comment 记录实质配置变化；
8. read back。

## Generic invariants

以下属于规划系统方法规则，可以保留在 Skill，而不是用户个性化值：

- Dida 当前运行态配置优先于仓库模板；
- hard deadline 不由 AI 静默修改；
- 同一用户的真实日历占用不能重叠；
- AI parallel 时间可以与用户工作重叠，但不能重复算成用户 occupancy；
- current-location timezone 应使用运行时实际时区，不硬编码 UTC offset；
- inbox bulk organization 只有用户明确要求时才执行；
- one-day exception 不自动晋升为 stable preference。

不要在 Skill 中写诸如“默认 21:00 下班”“周日不工作”“某项运动默认 protected”“固定 08:30 做天气任务”这样的当前用户值。

## Memory boundary

- scheduling / energy / mobility → 本 Profile；
- 项目规则、工具环境、跨项目工作方式 → `dida-planning-memory`；
- 当前任务范围、进度和决策 → owning task；
- estimation samples → estimator / progress 历史机制。

一个事实只保留一个 owner，不为了方便重复存储。

## References

读取 `references/config-notes.md` 获取 NOTE ownership 和 template/runtime 规则。
