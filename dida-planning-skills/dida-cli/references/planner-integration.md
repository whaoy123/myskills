# Planner-managed Dida content

## Single source of truth

Dida owns all task business facts. Local files may contain only rebuildable model/cache data, a pending operation queue, or migration previews.

## Body update

A Planner-managed task body contains:

1. Natural-language current context, completion criteria, links, and unresolved points; normally within 300 Chinese characters and no more than 500 unless technically necessary.
2. One `【Planner】` block ending at `【/Planner】`.

Use `dida-planning-core/scripts/planner_block.py` to patch the machine block without discarding unknown keys or the natural body.

## Comment event

Use append-only comments beginning with `[planner-event:v1]`. Generate and parse them with `planner_event.py`. Do not treat comments as the current state; current state belongs in native Dida fields and the current body.

## Idempotency

Each comment or queued write may include `operation_id`. Before retrying an ambiguous write, search current comments or read current task state for the same operation ID.

## Estimated duration

Planner estimated duration means calendar occupancy including normal short rests. Focus minutes, other active effort, AI-parallel time, and end-to-end elapsed time are recorded separately in completion comments.
