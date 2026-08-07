---
name: dida-task-estimator
description: Estimate or re-estimate the calendar occupancy of a Dida task using task features, bottom-up scope, similar completed tasks, confidence shrinkage, and risk coverage. Use for “大概多久”, “估时”, “重新估计剩余时间”, or before scheduling an unestimated task. Do not schedule dates or treat AI-parallel elapsed time as personal calendar occupancy.
---

# Dida task estimator

Produce one practical estimated duration for Dida while retaining internal uncertainty and evidence.

## Required reads

1. Read the exact task, body, children, existing estimate, and relevant completion comments. Refuse `role: config|memory_category|memory`; these records have no estimated duration.
2. Read only `估时配置｜特征与风险缓冲`.
3. Query similar completed tasks or the rebuildable local history cache. Read a tool/environment memory only when it materially changes effort; never scan all memories.
4. Use `dida-planning-core/scripts/estimation_engine.py`; do not hand-calculate a category multiplier.

## Estimate target

The Dida estimated duration is **calendar occupancy including normal short rests**. It excludes AI-parallel time when the user can work on something else.

Internally distinguish:

- calendar occupancy;
- Dida focus time;
- other necessary active effort;
- AI-parallel time;
- end-to-end elapsed time.

The user may provide these separately. Never infer overlap that the user did not state.

## Feature model

Classify the task by:

- one of eight coarse categories;
- work mode: create, modify, verify, research, communicate, travel, routine;
- familiarity;
- scope clarity;
- output scale;
- validation/rework burden;
- AI participation mode;
- tool/context switching;
- external uncertainty.

Use bottom-up steps or three-point estimates for broad/uncertain work. Historical samples modify the base only through similarity weighting and small-sample shrinkage toward no correction.

## Risk target

- ordinary movable task: about 70% coverage;
- hard-deadline task: about 85%;
- travel, queue, appointment, or fixed commitment: about 90%.

Round small tasks to 5 minutes and larger tasks to 15 minutes.

## Writeback

1. Write only the final duration to Dida native estimated duration.
2. Patch `estimate_confidence: low|medium|high` in the Planner block.
3. Keep a short current rationale in the body.
4. Add an event comment only when changing an existing estimate materially.
5. Read back the saved value.

## No reliable estimate

Low-confidence estimates are allowed. State the uncertainty and use a larger buffer rather than refusing to estimate.

## References

Read `references/estimation-model.md` for features and `references/history-format.md` for sample records.
