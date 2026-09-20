---
name: dida-task-estimator
description: Estimate task effort and remaining work from scope, acceptance, familiarity, validation, AI participation and reliable history. Separate human effort from external elapsed lead time. Identify uncertainty before weekly commitments; do not assume calendar capacity or derive precise dates from ungrounded hours.
---

# 任务投入估时

估的是完成指定产物所需的**人力投入**，不是替用户排钟点。采购、物流、等反馈等另外记录经过时间。

## 读取

读取目标任务范围、DoD、支撑叶子任务、剩余工作、相关历史和 `估时配置｜特征与风险缓冲`。局部估时不全库扫描；全局承诺交给 manager。

## 方法

- 熟悉的小任务可用同类历史；多部分工作自下而上累加。
- 陌生设计或调试先给范围/置信度，必要时定义一轮探索的交付。
- 估时必须包含实际查证、整理结论、验证和合理返工，不只算“看文档”或“写代码”。
- 不为迎合本周预算反调估时，不把固定小时范围当作任何交付物的保证。
- 用户明确提供的投入预算可用于周承诺校验；没有预算就不能断言有足够时间。

参考 `references/estimation-model.md` 和 `references/history-format.md`。

## 确定性辅助

```bash
python dida-planning-core/scripts/estimation_engine.py --task task.json --history history.json --output estimate.json
```

输出主字段为 `estimated_effort_minutes`。输入是当前读取的瞬时计算快照；输出是估算，不是外部事实，本地历史只是可重建索引。

## 口径

- `actual_effort_minutes`：用户为该任务实际投入的总人力时间；是新写入的标准字段。
- `focus_minutes`：可确认的专注工作时间。
- `other_active_minutes`：沟通、现场处理、必要切换等仍占用用户的主动参与时间。
- `ai_parallel_minutes`：AI 独立并行运行时间，不重复计入人的投入。
- `end_to_end_minutes`：从开始到结果产生的整体经过时间；纯等待不当作劳动投入。
- 旧 `calendar_minutes` 只在读取历史时作为兼容别名，不再用于新事件或新估时输出。

同一共享叶子工作只计一次，父任务总估时与 children 不重复累加。大出差/板测即使是一次性节点，也要计本人实际投入。

## 剩余工作和日期

进行中任务按剩余验收条件重估，不机械用“旧估时 × (1-progress)”。旧标签不等于可靠估时；发现低估需保留原值作为校准记录。

Latest Safe Start 需要把剩余劳动转为有依据的经过时间，加 external lead time 和缓冲。没有吞吐/经过天数依据，就输出 unknown，不从截止日期直接减小时数得某一天。

## 写入

0.5h 是预计投入的默认展示粒度；实际用户时间不按这个粒度伪造。

优先 native estimated duration；接口未提供此字段时，不发明参数，使用已确认的正文/标签约定并说明表示限制。该字段只表达任务投入估计，不代表日历时间块或可用时段。

写前读取，保留 prior estimate；仅修改授权字段并回读。没有可靠估计时保留 unknown，而不是写 0。

## 输出

范围、预计投入、置信度、主要不确定性，通常一段足够。若仍过大，交回 breakdown 缩小为可验收范围。
