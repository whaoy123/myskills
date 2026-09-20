# Rebuildable estimation history

A sample comes from a completed task comment and Dida focus records. Example normalized record:

```json
{
  "task_id": "abc",
  "category": "writing",
  "mode": "modify",
  "familiarity": "partial",
  "clarity": "clear",
  "output_scale": 2,
  "validation": "medium",
  "ai_mode": "assist",
  "tool_switches": 2,
  "estimated_minutes": 90,
  "actual_effort_minutes": 110,
  "focus_minutes": 80,
  "other_active_minutes": 30,
  "ai_parallel_minutes": 40,
  "included": true
}
```

Use only samples with a reliable prior estimate, matching scope, and reliable actual-effort evidence. A completed task with unknown actual effort still gets a completion comment but `included: false`.

For backward compatibility, `rebuild_history.py` accepts old `calendar_minutes` events and canonicalizes them to `actual_effort_minutes` with source `legacy_calendar_minutes`. New events must write `actual_effort_minutes`.

The local history cache is an index, not a second source of truth. Rebuild it from a Dida task/comment JSON export with `dida-planning-core/scripts/rebuild_history.py` whenever stale or inconsistent.
