---
name: dida-planning-profile
description: Initialize, inspect, or update Dida “系统配置” NOTE tasks for stable planning preferences and planning-system protocols: availability/capacity, mobility permissions, estimation policy, task-body/tag protocol, dependencies, timezone behavior, and schema version. Keep concrete user values in runtime Dida NOTE tasks, not in the distributable Skill or repository templates. Prefer TickTick/滴答清单 MCP or connector tools for runtime reads/writes; use dida-cli only as fallback.
---

# Dida Planning Profile

维护 Dida `系统配置` 中的稳定规划规则。

核心原则：

> Skill 只定义“有哪些配置、谁负责、怎么读写”；具体作息、精力、活动偏好等用户值只存在运行态 Dida NOTE 中。

当前任务事实不属于 Profile；全局任务完整性也不能通过读取 Profile 或模型记忆来判断。

## Configuration NOTE set

- `规划偏好｜作息与容量`
- `规划偏好｜日程移动权限`
- `估时配置｜特征与风险缓冲`
- `系统协议｜标签与任务正文`
- `系统协议｜依赖关系`
- `系统状态｜Schema与迁移版本`

长期项目/工具/工作方式记忆不放进这六个 NOTE，由 `dida-planning-memory` 负责。

每个 NOTE：

- `role: config`；
- 不作为可执行工作估时；
- 不进入普通任务容量统计；
- 默认无 status；
- 除非本身就是配置提醒，否则不设置调度日期。

## Ownership

### `规划偏好｜作息与容量`

负责稳定的：

- 常规可用工作窗口；
- 固定休息/不可用窗口；
- 高低精力规律；
- 偏好专注块与休息长度；
- 连续认知工作上限；
- 每日/每周容量和 reserve；
- 稳定的 deadline 提前量 / 风险缓冲偏好。

注意：具体任务的 `latest_safe_start` 由 planner 根据任务链动态计算，不写成 Profile 中的固定日期。

### `规划偏好｜日程移动权限`

负责：

- `fixed / protected / movable` 定义；
- 同日移动、跨天、缩短、删除权限；
- 已开始任务的移动规则；
- hard deadline 修改权限。

### `估时配置｜特征与风险缓冲`

负责：

- 估时口径；
- 风险覆盖；
- 取整；
- 历史样本策略；
- calendar / focus / AI parallel 区分。

### `系统协议｜标签与任务正文`

负责 task role、标题/正文协议、Planner block、可见标签、命名约定。

### `系统协议｜依赖关系`

负责 dependency schema 和语义。

### `系统状态｜Schema与迁移版本`

只负责 schema / migration / exact config IDs 等系统状态。

## Runtime I/O

有 TickTick/滴答清单 MCP 或一等连接器时，必须优先通过连接器解析、创建、更新和 read-back 配置 NOTE。

`dida-cli` 仅用于没有可用连接器的本地 fallback 环境。

## Initialize

1. 通过 MCP/连接器解析或创建 `系统配置`；
2. 检查六个 NOTE 是否已存在；
3. 只从 `assets/config-notes/` 创建缺失项；
4. 模板只提供字段骨架和通用协议，不包含真实用户作息或项目状态；
5. 需要用户具体值但当前未知的配置允许保持 `未设置 / PARTIAL`；
6. read-back 新建 NOTE；
7. 需要时把 exact IDs 写入 `系统状态｜Schema与迁移版本`。

初始化必须幂等。已有用户编辑过的 NOTE 绝不由模板覆盖。

只有没有 MCP/连接器时，才由 `dida-cli` 执行同一初始化流程。

## Read behavior

普通操作只读取相关 NOTE，不加载整套 Profile：

- Planner → 作息/容量 + 移动权限 + 必要估时/依赖协议；
- Estimator → 估时配置；
- Breakdown → 标签正文 + 依赖协议；
- Capture → 标签正文。

运行态 NOTE 一旦存在，就是当前用户配置真值源。仓库 `assets/config-notes/` 只是首次初始化模板，不能当作 fallback 用户事实。

## Update a preference

1. 唯一解析负责该事实的 NOTE；
2. 区分 stable preference 与 one-day exception；
3. 稳定且用户明确的新偏好可以直接更新；
4. 一天例外只保留在当前 planning interaction / task comment，不写 stable profile；
5. 新值与旧规则冲突时，替换真实 owner 中的旧值，不保留两套同时生效规则；
6. 保留无关 section；
7. 用 comment 记录实质配置变化；
8. read-back。

## Generic invariants

可保留在 Skill 的通用方法规则：

- 运行态配置优先于仓库模板；
- hard deadline 不由 AI 静默修改；
- 同一用户真实日历占用不能重叠；
- AI parallel 时间可与用户工作重叠，但不重复算 occupancy；
- timezone 使用运行时实际时区，不硬编码 UTC offset；
- Inbox bulk organization 只有用户明确要求时才执行；
- one-day exception 不自动晋升为 stable preference；
- 全局规划必须由 manager/planner 从 TickTick 全量未完成任务开始，Profile 不替代该扫描。

不要在 Skill 中写死“默认 21:00 下班”“周日不工作”等当前用户值。

## Memory boundary

- scheduling / energy / mobility → Profile；
- 项目规则、工具环境、跨项目工作方式 → `dida-planning-memory`；
- 当前任务范围、进度、决策 → owning task；
- estimation samples → estimator / progress；
- 当前任务库存 → TickTick runtime inventory。

一个事实只保留一个 owner。

## References

读取 `references/config-notes.md` 获取 NOTE ownership 和 template/runtime 规则。
