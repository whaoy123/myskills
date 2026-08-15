# DIDA Planning Core

This directory is shared deterministic support code for the nine user-facing skills. It is intentionally not a skill and has no `SKILL.md`.

Scripts read JSON from files/stdin and write JSON to stdout. They do not persist Dida task copies. The only persistent local state allowed is:

- rebuildable estimation index;
- pending sync operation queue;
- migration preview/mapping files.

Run:

```bash
python scripts/package_validator.py --root ..
python -m unittest discover -s tests -v
```

Memory support includes `memory_policy.py` for deterministic save/ask/route/skip policy and `migration/classify_legacy_memory.py` for preview-only legacy memory classification.

Weekly mainline support is provided by `weekly_capacity.py`. It evaluates selected task-local weekly commitments against weekly capacity and a reserve ratio, reports estimate/dependency/deadline risks, and returns stale commitment clear patches without storing Dida data locally. Run `python scripts/weekly_capacity.py --help` for the authoritative CLI.
