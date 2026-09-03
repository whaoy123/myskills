#!/usr/bin/env python3
"""Compare two design snapshots and emit changed DesignFact IDs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
def load(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    facts = raw.get("facts", raw) if isinstance(raw, dict) else raw
    if not isinstance(facts, list):
        raise ValueError("snapshot must be a list or {'facts': [...]} object")
    out = {}
    for fact in facts:
        fid = fact.get("fact_id")
        if not fid:
            raise ValueError("every fact requires fact_id")
        out[fid] = fact
    return out
def comparable(fact: dict | None):
    if fact is None:
        return None
    return {"entity": fact.get("entity"), "property": fact.get("property"), "value": fact.get("value"), "unit": fact.get("unit"), "confidence": fact.get("confidence")}
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("previous", type=Path)
    ap.add_argument("current", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    prev, cur = load(args.previous), load(args.current)
    changed = []
    for fid in sorted(set(prev) | set(cur)):
        a, b = prev.get(fid), cur.get(fid)
        if comparable(a) != comparable(b):
            changed.append({"fact_id": fid, "change": "added" if a is None else "removed" if b is None else "modified", "previous": comparable(a), "current": comparable(b)})
    if args.json:
        print(json.dumps({"changed_facts": changed}, ensure_ascii=False, indent=2))
    else:
        for item in changed:
            print(f"{item['change'].upper()}\t{item['fact_id']}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
