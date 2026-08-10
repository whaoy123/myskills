#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import yaml

TEMPLATES = {
    "project.yaml": {"schema_version": 1, "project_id": "", "title": "", "initial_goal": "", "current_goal": "", "current_stage": "UNDERSTAND", "goal_history": [], "purpose": "", "constraints": [], "existing_assets": []},
    "knowledge_model.yaml": {"schema_version": 1, "inherited": [], "known": [], "current_beliefs": [], "unclear": [], "confirmed_updates": [], "promotion_candidates": []},
    "research_questions.yaml": {"schema_version": 1, "questions": []},
    "open_questions.yaml": {"schema_version": 1, "questions": []},
    "decisions.yaml": {"schema_version": 1, "decisions": []},
    "project_plan.yaml": {"schema_version": 1, "revision": 1, "stages": []},
    "dida_handoff.yaml": {"schema_version": 1, "source_plan_revision": 1, "status": "DRAFT", "approval_required": True, "work_packages": []},
}


def dump_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def init(root: Path) -> Path:
    base = root / ".prestudy"
    state = base / "research_state"
    for d in [state, base / "notes", base / "reports", base / "history"]:
        d.mkdir(parents=True, exist_ok=True)
    for d in ["papers", "datasheets", "standards", "repos", "webpages", "other"]:
        (base / "library" / d).mkdir(parents=True, exist_ok=True)
    for filename, data in TEMPLATES.items():
        path = state / filename
        if not path.exists():
            dump_yaml(path, data)
    sources = state / "sources.csv"
    if not sources.exists():
        with sources.open("w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerow(["SourceID", "Type", "Title", "Publisher", "Year", "URL", "LocalPath", "Tier", "WhyUseful", "ReadingPriority", "Status"])
    evidence = state / "evidence.jsonl"
    evidence.touch(exist_ok=True)
    return base


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("project_root", type=Path)
    args = p.parse_args()
    print(init(args.project_root))


if __name__ == "__main__":
    main()
