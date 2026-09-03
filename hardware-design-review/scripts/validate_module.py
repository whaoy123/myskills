#!/usr/bin/env python3
"""Structural validator for hardware-design-review module.yaml files."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required to validate module.yaml") from exc
ALLOWED_TYPES = {"device", "interface", "power", "isolation", "pcb", "system"}
ALLOWED_STRENGTH = {"REQUIRED", "RECOMMENDED", "APP", "INFORMATIONAL", "UNCLEAR"}
RULE_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")
def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("module", type=Path)
    args = ap.parse_args()
    path = args.module.resolve()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if not isinstance(data, dict):
        fail(errors, "root must be a mapping")
        data = {}
    if data.get("schema_version") != 1:
        fail(errors, "schema_version must be 1")
    mod = data.get("module") or {}
    for key in ("id", "type", "name", "revision"):
        if not mod.get(key):
            fail(errors, f"module.{key} is required")
    if mod.get("type") not in ALLOWED_TYPES:
        fail(errors, f"module.type must be one of {sorted(ALLOWED_TYPES)}")
    files = data.get("files") or {}
    for key in ("usage_guide", "checklist", "provenance"):
        rel = files.get(key)
        if not rel:
            fail(errors, f"files.{key} is required")
        elif not (path.parent / rel).is_file():
            fail(errors, f"files.{key} does not exist: {rel}")
    checklist_text = ""
    checklist = files.get("checklist")
    if checklist and (path.parent / checklist).is_file():
        checklist_text = (path.parent / checklist).read_text(encoding="utf-8", errors="replace")
    seen: set[str] = set()
    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        fail(errors, "rules must be a non-empty list")
        rules = []
    for i, rule in enumerate(rules):
        where = f"rules[{i}]"
        if not isinstance(rule, dict):
            fail(errors, f"{where} must be a mapping")
            continue
        rid = rule.get("id")
        if not rid or not RULE_ID_RE.fullmatch(str(rid)):
            fail(errors, f"{where}.id is missing or invalid")
        elif rid in seen:
            fail(errors, f"duplicate rule id: {rid}")
        else:
            seen.add(rid)
            if checklist_text and not re.search(rf"(?<![A-Za-z0-9_.:-]){re.escape(rid)}(?![A-Za-z0-9_.:-])", checklist_text):
                fail(errors, f"rule {rid} is not found in checklist.md")
        if rule.get("strength") not in ALLOWED_STRENGTH:
            fail(errors, f"{where}.strength invalid")
        if not isinstance(rule.get("verification"), list) or not rule.get("verification"):
            fail(errors, f"{where}.verification must be a non-empty list")
        for key in ("required_facts", "dependency_keys"):
            if not isinstance(rule.get(key), list):
                fail(errors, f"{where}.{key} must be a list")
    if errors:
        print("INVALID")
        for e in errors:
            print(f"- {e}")
        return 1
    print(f"VALID: {mod.get('id')} ({len(rules)} rules)")
    return 0
if __name__ == "__main__":
    sys.exit(main())
