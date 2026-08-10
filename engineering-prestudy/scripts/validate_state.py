#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml

REQUIRED = [
    "project.yaml",
    "knowledge_model.yaml",
    "research_questions.yaml",
    "sources.csv",
    "evidence.jsonl",
    "open_questions.yaml",
    "pitfalls.yaml",
    "decisions.yaml",
    "project_plan.yaml",
    "dida_handoff.yaml",
]
STAGES = {"UNDERSTAND", "RESEARCH", "DESIGN_PLAN"}
RQ_STATUS = {"OPEN", "ACTIVE", "BLOCKED", "SATURATED", "CLOSED"}
OQ_TYPES = {"MISSING_INFORMATION", "SOURCE_CONFLICT", "NEEDS_EXPERIMENT", "NEEDS_ENGINEERING_ANALYSIS", "NEEDS_USER_DECISION"}
OQ_IMPACT = {"LOW", "MEDIUM", "HIGH", "BLOCKING"}
DECISION_STATUS = {"PROPOSED", "CONFIRMED", "SUPERSEDED", "REJECTED"}
PITFALL_IMPACT = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
PITFALL_ACTION = {"WATCH", "DESIGN_CONSTRAINT", "VERIFY", "BLOCKER"}
PITFALL_STATUS = {"OPEN", "MITIGATED", "ACCEPTED", "NOT_APPLICABLE"}


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def validate(state: Path) -> list[str]:
    errors: list[str] = []
    for name in REQUIRED:
        if not (state / name).exists():
            errors.append(f"missing required file: {name}")
    if errors:
        return errors

    project = load_yaml(state / "project.yaml")
    if project.get("current_stage") not in STAGES:
        errors.append(f"invalid project current_stage: {project.get('current_stage')}")

    rq = load_yaml(state / "research_questions.yaml")
    for item in rq.get("questions", []):
        status = item.get("status", "OPEN")
        if status not in RQ_STATUS:
            errors.append(f"research question {item.get('id', '?')}: invalid status {status}")

    oq = load_yaml(state / "open_questions.yaml")
    for item in oq.get("questions", []):
        if item.get("type") and item.get("type") not in OQ_TYPES:
            errors.append(f"open question {item.get('id', '?')}: invalid type {item.get('type')}")
        if item.get("impact") and item.get("impact") not in OQ_IMPACT:
            errors.append(f"open question {item.get('id', '?')}: invalid impact {item.get('impact')}")

    pitfalls = load_yaml(state / "pitfalls.yaml")
    for item in pitfalls.get("items", []):
        pid = item.get("id", "?")
        if item.get("impact") and item.get("impact") not in PITFALL_IMPACT:
            errors.append(f"pitfall {pid}: invalid impact {item.get('impact')}")
        if item.get("action") and item.get("action") not in PITFALL_ACTION:
            errors.append(f"pitfall {pid}: invalid action {item.get('action')}")
        if item.get("status") and item.get("status") not in PITFALL_STATUS:
            errors.append(f"pitfall {pid}: invalid status {item.get('status')}")
        if not item.get("failure_mode"):
            errors.append(f"pitfall {pid}: missing failure_mode")
        if not item.get("mitigation") and item.get("status") != "NOT_APPLICABLE":
            errors.append(f"pitfall {pid}: missing mitigation")
        if item.get("action") == "BLOCKER" and item.get("status") == "ACCEPTED":
            errors.append(f"pitfall {pid}: BLOCKER cannot be ACCEPTED without mitigation")

    decisions = load_yaml(state / "decisions.yaml")
    for item in decisions.get("decisions", []):
        if item.get("status") and item.get("status") not in DECISION_STATUS:
            errors.append(f"decision {item.get('id', '?')}: invalid status {item.get('status')}")

    handoff = load_yaml(state / "dida_handoff.yaml")
    if handoff.get("status") not in {"DRAFT", "APPROVED", "HANDED_OFF"}:
        errors.append(f"invalid dida handoff status: {handoff.get('status')}")
    if handoff.get("approval_required") is not True and handoff.get("status") == "DRAFT":
        errors.append("DRAFT dida handoff must require approval")

    with (state / "sources.csv").open("r", encoding="utf-8-sig", newline="") as f:
        fields = next(csv.reader(f), [])
    required_source_cols = ["SourceID", "Type", "Title", "Publisher", "Year", "URL", "LocalPath", "Tier", "WhyUseful", "ReadingPriority", "Status"]
    if fields != required_source_cols:
        errors.append("sources.csv header does not match v1 contract")

    for lineno, line in enumerate((state / "evidence.jsonl").read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"evidence.jsonl line {lineno}: invalid JSON: {e}")
            continue
        etype = item.get("type")
        if etype == "FACT":
            if not item.get("source_id"):
                errors.append(f"evidence {item.get('id', lineno)}: FACT missing source_id")
        elif etype == "INFERENCE":
            if not item.get("basis"):
                errors.append(f"evidence {item.get('id', lineno)}: INFERENCE missing basis")
        else:
            errors.append(f"evidence {item.get('id', lineno)}: invalid type {etype}")
    return errors


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("state_root", type=Path)
    args = p.parse_args()
    errors = validate(args.state_root)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
