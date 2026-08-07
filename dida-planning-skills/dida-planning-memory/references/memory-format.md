# Memory record format

## Category parent

A category parent uses:

```text
role: memory_category
required_for_parent: false
progress: 0
date_semantics: none
mobility: fixed
privacy: normal
estimate_confidence: high
```

## Memory item

```text
记忆｜原始方案文档不得覆盖

适用范围：南航航空发电机项目。
规则：只修改“设计方案_修改稿.docx”，保留原始“设计方案.docx”。

【Planner】
schema: 1
role: memory
required_for_parent: false
progress: 0
date_semantics: none
mobility: fixed
privacy: normal
estimate_confidence: high
dependency_mode: all
dependencies:
memory_scope: project
memory_kind: project_rule
memory_source: explicit
memory_confidence: high
applies_to: PROJECT_TASK_ID
【/Planner】
```

Allowed memory fields:

- `memory_scope`: global or project
- `memory_kind`: project_rule, tool_environment, workflow, convention
- `memory_source`: explicit, durable_fact, confirmed_inference
- `memory_confidence`: high or medium
- `applies_to`: `all` or an exact project/task ID
- `review_after`: optional ISO date for facts likely to become stale
- `supersedes`: optional previous memory task ID

Use comments for updates:

```text
[planner-event:v1]
event: memory_updated
operation_id: ...
reason: user changed the default rule
note: old value replaced after explicit instruction
```
