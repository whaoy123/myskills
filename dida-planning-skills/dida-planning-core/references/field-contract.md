# Planner field contract

Allowed values:

- role: project, phase, task, block, config, memory_category, memory
- required_for_parent: true or false; omitted means true
- progress: 0, 25, 50, 75, 90, 100
- date_semantics: hard_deadline, execution_window, target_date, none
- week_start: Monday ISO date for the current weekly mainline commitment; work roles only
- weekly_commitment: must, should, candidate; only valid together with week_start
- mobility: fixed, protected, movable
- privacy: normal, summary_only
- estimate_confidence: low, medium, high
- dependency_mode: all, any

Memory-only fields:

- memory_scope: global, project
- memory_kind: project_rule, tool_environment, workflow, convention
- memory_source: explicit, durable_fact, confirmed_inference
- memory_confidence: high, medium
- applies_to: `all` or exact owning project/task ID
- review_after: optional ISO date
- supersedes: optional previous memory task ID

Memory records always use `required_for_parent: false`, no estimate/date/status, and must not block parent completion.

Dependency item fields:

- type: finish_to_start, start_to_start, not_before, external_wait
- task_id: required for task-based dependency; optional for external_wait
- external_ref: external person/event identifier when external_wait has no task ID
- not_before: required for date dependency
- strength: hard or soft
- note: optional short reason
