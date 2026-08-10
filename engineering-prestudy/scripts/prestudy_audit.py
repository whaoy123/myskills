#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml

from validate_state import validate as validate_state


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def collect_evidence(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if item.get("id"):
            out[item["id"]] = item
    return out


def audit(state: Path, project_root: Path | None = None) -> tuple[list[str], list[str]]:
    errors = validate_state(state)
    warnings: list[str] = []
    if errors:
        return errors, warnings

    project = load_yaml(state / "project.yaml")
    rq = load_yaml(state / "research_questions.yaml").get("questions", [])
    pitfalls = load_yaml(state / "pitfalls.yaml").get("items", [])
    plan = load_yaml(state / "project_plan.yaml")
    handoff = load_yaml(state / "dida_handoff.yaml")
    sources = read_csv(state / "sources.csv")
    search_log = read_csv(state / "search_log.csv")
    evidence = collect_evidence(state / "evidence.jsonl")

    for item in evidence.values():
        if item.get("type") == "FACT" and item.get("confidence") == "HIGH":
            if not item.get("locator"):
                warnings.append(f"high-confidence FACT {item['id']} has no locator")

    saturated_ids = {q.get("id") for q in rq if q.get("status") == "SATURATED"}
    for qid in saturated_ids:
        rows = [r for r in search_log if r.get("QuestionID") == qid]
        if not rows:
            errors.append(f"SATURATED research question {qid} has no search_log entries")
            continue
        if not any(r.get("MateriallyNew", "").strip().lower() in {"false", "no", "0"} for r in rows):
            warnings.append(
                f"SATURATED research question {qid} has no logged low-marginal-value search pass"
            )

    retained = [r for r in sources if r.get("Status", "").strip().upper() == "RETAINED"]
    if project_root is not None:
        prestudy = project_root / ".prestudy"
        for row in retained:
            sid = row.get("SourceID", "")
            note = prestudy / "notes" / f"{sid}.md"
            if sid and not note.exists():
                errors.append(f"retained source {sid} missing notes/{sid}.md")
            local = row.get("LocalPath", "").strip()
            if local:
                local_path = Path(local)
                resolved = (
                    project_root / local_path
                    if local_path.parts and local_path.parts[0] == ".prestudy"
                    else prestudy / local_path
                )
                if not resolved.exists():
                    errors.append(f"retained source {sid or '?'} LocalPath does not exist: {local}")

    stages = plan.get("stages", [])
    serialized_plan = json.dumps(stages, ensure_ascii=False)
    for pit in pitfalls:
        pid = pit.get("id", "?")
        impact = pit.get("impact")
        action = pit.get("action")
        status = pit.get("status")
        if status == "RESOLVED":
            continue
        if action in {"DESIGN_CONSTRAINT", "VERIFY", "BLOCKER"}:
            if pid not in serialized_plan and project.get("current_stage") == "DESIGN_PLAN":
                errors.append(
                    f"pitfall {pid} action={action} is not referenced by project_plan during DESIGN_PLAN"
                )
        if action == "BLOCKER" and status not in {"RESOLVED", "MITIGATED"}:
            if handoff.get("status") in {"APPROVED", "HANDED_OFF"}:
                errors.append(
                    f"handoff cannot be {handoff.get('status')} while blocker pitfall {pid} remains {status}"
                )
        if impact == "CRITICAL" and not pit.get("verification"):
            warnings.append(f"CRITICAL pitfall {pid} has no explicit verification field")

    for dec in load_yaml(state / "decisions.yaml").get("decisions", []):
        if dec.get("status") == "CONFIRMED" and not dec.get("evidence") and not dec.get("user_judgment"):
            warnings.append(
                f"CONFIRMED decision {dec.get('id', '?')} has neither evidence nor user_judgment"
            )

    if project_root is not None:
        reports = project_root / ".prestudy" / "reports"
        expected = [
            "research_brief.md",
            "current_understanding.md",
            "research_landscape.md",
            "implementation_plan.md",
            "FINAL.md",
        ]
        for name in expected:
            if not (reports / name).exists():
                warnings.append(f"missing report scaffold: reports/{name}")

    return errors, warnings


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("state_root", type=Path)
    p.add_argument("--project-root", type=Path)
    args = p.parse_args()

    errors, warnings = audit(args.state_root, args.project_root)
    if errors:
        print("FAIL")
        for item in errors:
            print(f"- ERROR: {item}")
        for item in warnings:
            print(f"- WARN: {item}")
        raise SystemExit(1)

    print("PASS")
    for item in warnings:
        print(f"- WARN: {item}")


if __name__ == "__main__":
    main()
