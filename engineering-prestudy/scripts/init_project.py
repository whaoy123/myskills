#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

import yaml

TEMPLATES = {
    "project.yaml": {
        "schema_version": 1,
        "project_id": "",
        "title": "",
        "initial_goal": "",
        "current_goal": "",
        "current_stage": "UNDERSTAND",
        "goal_history": [],
        "purpose": "",
        "constraints": [],
        "existing_assets": [],
        "research_policy": {
            "retained_artifact_budget": 2,
            "allow_extra_retained": False,
            "snowball_rounds_default": 1,
        },
    },
    "knowledge_model.yaml": {
        "schema_version": 1,
        "inherited": [],
        "known": [],
        "current_beliefs": [],
        "unclear": [],
        "confirmed_updates": [],
        "promotion_candidates": [],
    },
    "research_questions.yaml": {"schema_version": 1, "questions": []},
    "open_questions.yaml": {"schema_version": 1, "questions": []},
    "pitfalls.yaml": {"schema_version": 1, "items": []},
    "decisions.yaml": {"schema_version": 1, "decisions": []},
    "project_plan.yaml": {"schema_version": 1, "revision": 1, "stages": []},
    "dida_handoff.yaml": {
        "schema_version": 1,
        "source_plan_revision": 1,
        "status": "DRAFT",
        "approval_required": True,
        "work_packages": [],
    },
}

SOURCE_COLUMNS = [
    "SourceID", "Type", "Title", "Publisher", "Year", "URL", "LocalPath",
    "Tier", "Authority", "Independence", "WhyUseful", "ReadingPriority",
    "Status", "RetentionRole", "RetentionReason",
]
SEARCH_LOG_COLUMNS = [
    "SearchID", "QuestionID", "Timestamp", "Phase", "Query", "Scope",
    "ResultSummary", "NewRoute", "MateriallyNew", "NextAction",
]

REPORT_TEMPLATES = [
    "research_brief.md",
    "current_understanding.md",
    "research_landscape.md",
    "implementation_plan.md",
    "FINAL.md",
]


def dump_yaml(path: Path, data: dict) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def write_csv_header(path: Path, columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerow(columns)


def init(root: Path, template_root: Path | None = None) -> Path:
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
        write_csv_header(sources, SOURCE_COLUMNS)

    search_log = state / "search_log.csv"
    if not search_log.exists():
        write_csv_header(search_log, SEARCH_LOG_COLUMNS)

    (state / "evidence.jsonl").touch(exist_ok=True)

    if template_root is not None:
        for name in REPORT_TEMPLATES:
            src = template_root / name
            dst = base / "reports" / name
            if src.exists() and not dst.exists():
                shutil.copyfile(src, dst)

    return base


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("project_root", type=Path)
    p.add_argument(
        "--template-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "templates" / "reports",
    )
    args = p.parse_args()
    print(init(args.project_root, args.template_root))


if __name__ == "__main__":
    main()
