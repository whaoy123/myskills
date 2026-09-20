---
name: dida-planning-profile
description: Maintain Dida task-planning rules for estimation, dependencies, body protocol and weekly deliverable limits/effort budgets. No work schedules, calendar availability or clock blocks. Runtime configuration wins over repository templates; preserve existing user edits.
---

# 任务规划配置

稳定规划规则保存在滴答 `系统配置` NOTE 中；仓库模板只用于首次初始化。

## 配置所有权

| NOTE | 负责 |
|---|---|
| 估时配置｜特征与风险缓冲 | 估时口径、缓冲、历史策略 |
| 系统协议｜标签与任务正文 | role、日期语义、Planner 与周合同 |
| 系统协议｜依赖关系 | 依赖种类和约束 |
| 规划偏好｜周交付与任务投入 | 核心名额、长期发展偏好、用户给定的投入预算 |
| 系统状态｜Schema与迁移版本 | 版本与真实配置 ID |

所有配置 role=config，无执行估时、无截止日期，不计周交付数量。

不保存作息、可用时间段、Outlook/日历规则、日程移动权限。

## 初始化或更新

1. MCP/连接器精确解析现有配置，缺能力时用 CLI 回退。
2. 只用 assets/config-notes 创建缺失项；已有用户编辑内容不能由模板覆盖。
3. 新增周交付配置先复用已存在的等义 NOTE，避免再建一套重复配置。
4. 更新需要用户授权；写前读取、只改相应字段、写后回读。
5. 旧配置内容冲突时说明差异，不因软件升级静默改变用户规则。

## 默认周规则

核心交付上限 2，通常 work 和 growth 各一。允许 0 或 1；用户可调整上限并说明取舍。

只采纳用户给出的周投入预算；默认 unknown。预算是任务量判断，不是钟点排程。必办节点要计投入，不能把它们当作免费的第三条主线。

原生硬截止不随周模板改变。本周交付只对其验收范围负责。

## References

- `references/config-notes.md`
- `dida-weekly-delivery`
