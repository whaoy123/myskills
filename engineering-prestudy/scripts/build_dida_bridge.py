#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def build_bridge(handoff_path: Path, output_path: Path, allow_draft: bool = False) -> Path:
    handoff = load_yaml(handoff_path)
    status = handoff.get("status")
    if status != "APPROVED" and not allow_draft:
        raise ValueError(
            f"dida handoff status is {status}; APPROVED is required before bridge export"
        )

    rows = []
    seen = set()
    for wp in handoff.get("work_packages", []):
        wid = wp.get("id")
        if not wid:
            raise ValueError("work package missing id")
        if wid in seen:
            raise ValueError(f"duplicate work package id: {wid}")
        seen.add(wid)
        for field in ["stage", "title", "expected_outputs", "acceptance", "dependencies"]:
            if field not in wp:
                raise ValueError(f"work package {wid} missing {field}")

        body_lines = []
        if wp.get("expected_outputs"):
            body_lines.append("预期产出：")
            body_lines.extend(f"- {x}" for x in wp["expected_outputs"])
        if wp.get("acceptance"):
            body_lines.append("完成标准：")
            body_lines.extend(f"- {x}" for x in wp["acceptance"])
        refs = []
        for key in ["open_question_ids", "decision_ids", "pitfall_ids"]:
            if wp.get(key):
                refs.append(f"{key}: {', '.join(wp[key])}")
        if refs:
            body_lines.append("Research refs：")
            body_lines.extend(f"- {x}" for x in refs)

        rows.append({
            "source_work_package_id": wid,
            "source_stage": wp["stage"],
            "title": wp["title"],
            "role": "task",
            "body": "\n".join(body_lines),
            "dependencies": wp.get("dependencies", []),
            "estimated_duration": None,
            "date": None,
            "priority": None,
            "schedule": None,
            "requires_dida_breakdown": True,
            "requires_dida_estimation": True,
            "requires_user_approved_capture": status == "APPROVED",
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return output_path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("handoff_path", type=Path)
    p.add_argument("output_path", type=Path)
    p.add_argument("--allow-draft", action="store_true")
    args = p.parse_args()
    print(build_bridge(args.handoff_path, args.output_path, args.allow_draft))


if __name__ == "__main__":
    main()
