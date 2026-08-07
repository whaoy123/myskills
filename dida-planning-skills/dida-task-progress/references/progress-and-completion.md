# Progress and completion details

## Progress meanings

- 0: not started.
- 25: meaningful start.
- 50: about half the weighted work remains/completed.
- 75: main body complete.
- 90: only validation, feedback, or closing work remains.
- 100: completion criteria met.

## Parent progress

Use `dida-planning-core/scripts/progress_engine.py`. Required children use `sum(child_estimate * child_progress) / sum(child_estimate)` when all estimates exist; otherwise equal weighting is used. Optional children do not affect parent progress. Deleted children are absent from the calculation.

## Completion event fields

```text
[planner-event:v1]
event: completed
operation_id: <uuid>
prior_estimate_minutes: 90
calendar_minutes: 110
focus_minutes: 80
other_active_minutes: 30
ai_parallel_minutes: 40
end_to_end_minutes: 150
included_in_estimation: true
note: final review took longer than expected
```

Unknown numeric values are omitted or written `null`; never fabricate them. `included_in_estimation: true` requires a reliable prior estimate, matching task scope, and reliable calendar occupancy.

## Rounding

Use 5-minute increments for small tasks and 15-minute increments for larger tasks. Preserve raw Dida focus seconds in the source read, but normalized comments may use rounded minutes.
