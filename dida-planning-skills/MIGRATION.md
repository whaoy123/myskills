# v1.5.0 迁移说明

## 兼容策略

Planner schema 仍为 1，`week_start + weekly_commitment` 与 `weekly_delivery` v1 不改结构。v1.5.0 收紧的是**新写入语义**，不是强制批量改历史任务。

旧任务中的以下字段仍可读取并在修改其它字段时原样保留：

- `role: block`
- `date_semantics: execution_window`
- `mobility: fixed|protected|movable`
- 完成事件中的 `calendar_minutes`

新代码不再创建或更新这些日程时代字段；显式迁移时可以删除。新的估时输出写 `estimated_effort_minutes`，新的完成事件写 `actual_effort_minutes`。历史 `calendar_minutes` 只作为重建估时样本时的兼容输入，并标注来源。

## 运行态任务

安装不会扫描、删除或迁移实际滴答任务。启用周规划时：

1. 保留现有正确父子归属，不按周重挂任务；
2. 旧 must/should 承诺缺少交付合同时只标“待补定义”，不猜验收标准；
3. 周交付复用现有 task/phase owner，不默认创建“本周计划”或执行块；
4. 换周先归档原合同与证据，回读成功后才清旧周字段；
5. 目标日期、硬截止和 Latest Safe Start 保持不同语义，不因换周自动移动。

## 配置与记忆

仓库模板不覆盖用户已编辑的运行态 NOTE。v1.5.0 的新模板不再写 mobility、执行窗口、作息、日历可用性或个人容量模型。

如果旧配置 NOTE 中仍有这类字段，安装本身不会远程删除；只有用户明确授权迁移时才清理。周投入预算只接受用户直接提供的任务投入上限，不从日历反推。

## 周交付新增字段

忙周没有 growth 核心交付时，规划快照应记录：

- `growth_deferral_reason`
- `growth_resume_condition`

这两个字段用于防止长期发展线被无限默默延期，不要求额外创建一条“提醒任务”。

## 发布基线

本次 v1.5.0 以用户上传并已通过 v1.4.0 回归的 weekly-delivery 包为本地基线，同时核对了当前 GitHub `whaoy123/myskills` 的默认分支结构。远端 `main` 仍是更早的日程版，因此同步必须走独立分支/提交，不直接覆盖 `main`。
