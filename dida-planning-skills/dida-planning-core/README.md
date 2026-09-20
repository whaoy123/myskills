# DIDA Task Planning Core

Deterministic helpers for task contracts, dependencies, estimates, progress, conflict merges, weekly delivery checks and history. Not a second task database or calendar scheduler.

New module: `scripts/weekly_delivery.py` validates a complete, normalized task snapshot; checks weekly scope/acceptance, the core cap, task references, obligations, unique effort and unknown risk inputs. It produces no remote mutations. `prepare_week_rollover` prepares an archive and a conditional clear patch; execution still requires an authorized connector operation.

Planner schema 1 remains compatible; `weekly_delivery` is an optional versioned JSON extension. Unknown fields survive read/patch/render.

```bash
python scripts/package_validator.py --root .. --strict-manifest
python -m unittest discover -s tests -v
```
