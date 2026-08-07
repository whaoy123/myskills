from __future__ import annotations

import argparse
import json
import re
import uuid
from pathlib import Path
from typing import Any


def first_heading(body: str) -> str | None:
    m = re.search(r"^#\s+(.+)$", body, re.M)
    return m.group(1).strip() if m else None


def build(scan: dict[str, Any]) -> dict[str, Any]:
    actions = []; ambiguities = []
    for rec in scan.get("records", []):
        fm = rec.get("frontmatter", {}); typ = rec.get("type")
        if typ not in {"task", "project", "recurring-rule"}: continue
        title = fm.get("title") or fm.get("name") or first_heading(rec.get("body", ""))
        if not title:
            ambiguities.append({"source": rec["decoded_path"], "reason": "missing title"}); continue
        action = {
            "operation_id": str(uuid.uuid4()),
            "source": rec["decoded_path"],
            "entity_type": typ,
            "title": title,
            "legacy_id": fm.get("id"),
            "target_list": None,
            "target_parent_legacy_id": fm.get("project") or fm.get("parent_id"),
            "status": fm.get("status"),
            "hard_deadline": fm.get("hard_deadline"),
            "target_date": fm.get("target_date"),
            "estimated_minutes": fm.get("estimated_minutes"),
            "actual_minutes": fm.get("actual_minutes"),
            "preview_only": True,
        }
        if not action["target_list"]: ambiguities.append({"source": rec["decoded_path"], "reason": "domain list mapping required"})
        actions.append(action)
    return {"actions": actions, "ambiguities": ambiguities, "writes_performed": False}


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("scan_json"); ap.add_argument("--output", required=True)
    args = ap.parse_args(); scan = json.loads(Path(args.scan_json).read_text(encoding="utf-8")); result = build(scan); Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"); print(f"actions={len(result['actions'])} ambiguities={len(result['ambiguities'])}")

if __name__ == "__main__": main()
