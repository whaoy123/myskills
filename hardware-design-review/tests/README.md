# Tests

Use datasheet-derived device folders as external fixtures. Do not copy a real device's rules into `SKILL.md`.

Minimum acceptance test for a fixture:

1. `module.yaml` passes `scripts/validate_module.py`.
2. Every declared rule ID is present in `checklist.md`.
3. A one-fact snapshot change is detected by `scripts/diff_design.py`.
4. Only rules whose dependency keys intersect the changed facts, plus transitive dependents, are reopened by the review workflow.
