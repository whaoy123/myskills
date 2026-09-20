# Hierarchy and dependency rules

## Role meanings

- `project`: long-lived outcome, such as a research or hardware project.
- `phase`: major deliverable or stage.
- `task`: executable work with a completion criterion.
- `block`: legacy historical session only; do not create new blocks.
- `required_for_parent`: omitted/true means it blocks parent completion; false means optional and triggers a completion question rather than a block.

## Good executable task

A good child states one observable output, such as “完成 PMG 上电电压测试表并核对量程”, rather than “继续做项目”.

## Gate pattern

Use a hard `finish_to_start` edge when a downstream artifact is invalid until an upstream decision or freeze is accepted. Examples: requirements freeze before schematic implementation, interface definition before RTL integration, approved BOM choice before layout constraints.

Do not convert a preferred order into a hard gate. A gate must name the acceptance artifact and the condition that releases downstream work.

## Dependency representation

```text
 dependency_mode: all
 dependencies:
   - type: finish_to_start
     task_id: abc123
     strength: hard
   - type: external_wait
     task_id: reply-from-reviewer
     strength: soft
```

For `not_before`, use `not_before: YYYY-MM-DDTHH:MM:SS±HH:MM` instead of `task_id`. For an external reply or event without its own task, use `external_ref` plus `resolved: false`; a task ID is not required.

## Cycle check

Build a directed graph for task-based dependencies. Reject an edge if the target can already reach the source. Date and external-event dependencies do not create graph cycles unless linked to another task ID.

## Progress

Use only 0, 25, 50, 75, 90, 100. Parent progress is weighted by child estimated effort when estimates exist; otherwise use equal weight.

## Weekly delivery

Weekly contracts are metadata on existing tasks/phases. Supporting task IDs are references, not a reason to reparent work. Count actual shared leaf work once; do not collapse unrelated outputs into one commitment merely by naming.
