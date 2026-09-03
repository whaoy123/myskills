#!/usr/bin/env python3
"""Check that module.yaml rule IDs and companion files are consistent."""
from __future__ import annotations
import argparse, re
from pathlib import Path
try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required") from exc
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("module", type=Path); args=ap.parse_args(); p=args.module.resolve(); d=yaml.safe_load(p.read_text(encoding="utf-8")) or {}; errors=[]
    files=d.get("files") or {}; paths={}
    for key in ("usage_guide","checklist","provenance"):
        rel=files.get(key)
        if not rel: errors.append(f"missing files.{key}"); continue
        fp=p.parent/rel; paths[key]=fp
        if not fp.is_file(): errors.append(f"missing companion file: {rel}")
    text=paths.get("checklist").read_text(encoding="utf-8",errors="replace") if paths.get("checklist") and paths["checklist"].is_file() else ""
    seen=set()
    for i,rule in enumerate(d.get("rules") or []):
        rid=rule.get("id") if isinstance(rule,dict) else None
        if not rid: errors.append(f"rules[{i}] missing id"); continue
        if rid in seen: errors.append(f"duplicate rule id: {rid}")
        seen.add(rid)
        if text and not re.search(rf"(?<![A-Za-z0-9_.:-]){re.escape(rid)}(?![A-Za-z0-9_.:-])", text): errors.append(f"module rule missing from checklist: {rid}")
    if errors:
        print("INVALID")
        for e in errors: print(f"- {e}")
        return 1
    print(f"VALID: {len(seen)} rule IDs consistent"); return 0
if __name__=="__main__": raise SystemExit(main())
