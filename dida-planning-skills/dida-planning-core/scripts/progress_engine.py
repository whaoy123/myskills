from __future__ import annotations

import argparse
from typing import Any

from common import is_work_item, read_json, write_json

ALLOWED = (0, 25, 50, 75, 90, 100)


def normalize_progress(value: float) -> int:
    return min(ALLOWED, key=lambda x: abs(x - value))


def parent_progress(children: list[dict[str, Any]]) -> dict[str, Any]:
    work_children = [c for c in children if is_work_item(c)]
    material = [c for c in work_children if c.get("required_for_parent", True)]
    if not material:
        return {"progress": 100, "method": "no_required_children"}
    estimated = [c for c in material if float(c.get("estimated_minutes") or 0) > 0]
    if len(estimated) == len(material):
        total = sum(float(c["estimated_minutes"]) for c in material)
        raw = sum(float(c["estimated_minutes"]) * float(c.get("progress", 0)) for c in material) / total
        method = "estimated_duration_weighted"
    else:
        raw = sum(float(c.get("progress", 0)) for c in material) / len(material)
        method = "equal_weight_missing_estimates"
    return {"progress": normalize_progress(raw), "raw_progress": round(raw, 2), "method": method, "required_children": len(material), "optional_children": len(work_children) - len(material), "ignored_non_work": len(children) - len(work_children)}


def completion_gate(children: list[dict[str, Any]]) -> dict[str, Any]:
    work_children = [c for c in children if is_work_item(c)]
    unfinished_required = [c for c in work_children if c.get("required_for_parent", True) and not c.get("completed")]
    unfinished_optional = [c for c in work_children if not c.get("required_for_parent", True) and not c.get("completed")]
    return {"can_complete_without_question": not unfinished_required and not unfinished_optional, "blocked": bool(unfinished_required), "ask_about_optional": not unfinished_required and bool(unfinished_optional), "unfinished_required": [c.get("id") for c in unfinished_required], "unfinished_optional": [c.get("id") for c in unfinished_optional]}


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--input", required=True); ap.add_argument("--mode", choices=["progress","completion"], default="progress"); ap.add_argument("--output")
    args = ap.parse_args(); data=read_json(args.input); result=parent_progress(data["children"]) if args.mode=="progress" else completion_gate(data["children"]); write_json(result,args.output)

if __name__ == "__main__": main()
