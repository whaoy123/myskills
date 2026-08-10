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
    "search_log.csv",
    "evidence.jsonl",
    "open_questions.yaml",
    "pitfalls.yaml",
    "decisions.yaml",
    "project_plan.yaml",
    "dida_handoff.yaml",
]

STAGES = {"UNDERSTAND", "RESEARCH", "DESIGN_PLAN"}
RQ_STATUS = {"OPEN", "ACTIVE", "BLOCKED", "SATURATED", "CLOSED"}
OQ_TYPES = {
    "MISSING_INFORMATION",
    "SOURCE_CONFLICT",
    "NEEDS_EXPERIMENT",
    "NEEDS_ENGINEERING_ANALYSIS",
    "NEEDS_USER_DECISION",
}
OQ_IMPACT = {"LOW", "MEDIUM", "HIGH", "BLOCKING"}
DECISION_STATUS = {"PROPOSED", "CONFIRMED", "SUPERSEDED", "REJECTED"}
PITFALL_IMPACT = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
PITFALL_ACTION = {"WATCH", "DESIGN_CONSTRAINT", "VERIFY", "BLOCKER"}
PITFALL_STATUS = {"OPEN", "MITIGATED", "ACCEPTED", "RESOLVED"}
SOURCE_TIERS = {"L1", "L2", "L3", "L4"}
AUTHORITY = {"LOW", "MEDIUM", "HIGH"}
INDEPENDENCE = {"LOW", "MEDIUM", "HIGH", "N/A"}
RETENTION_ROLE = {"", "NONE", "REFERENCE", "IMPLEMENTATION", "EXCEPTION"}

SOURCE_COLUMNS = [
    "SourceID", "Type", "Title", "Publisher", "Year", "URL", "LocalPath",
    "Tier", "Authority", "Independence", "WhyUseful", "ReadingPriority",
    "Status", "RetentionRole", "RetentionReason",
]
SEARCH_LOG_COLUMNS = [
    "SearchID", "QuestionID", "Timestamp", "Phase", "Query", "Scope",
    "ResultSummary", "NewRoute", "MateriallyNew", "NextAction",
]


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return (reader.fieldnames or [], list(reader))


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
    if project.get("initial_goal") and not project.get("current_goal"):
        errors.append("project current_goal must not be empty when initial_goal is set")

    rq = load_yaml(state / "research_questions.yaml")
    for item in rq.get("questions", []):
        status = item.get("status", "OPEN")
        if status not in RQ_STATUS:
            errors.append(f"research question {item.get('id', '?')}: invalid status {status}")
        if status == "SATURATED":
            saturation = item.get("saturation", {})
            if not isinstance(saturation, dict):
                errors.append(f"research question {item.get('id', '?')}: saturation must be a mapping")
            else:
                required_flags = [
                    "mechanism_understood",
                    "landscape_known",
                    "predecessor_known_or_not_applicable",
                    "evidence_adequate",
                    "tradeoffs_visible",
                    "blocking_unknowns_handled",
                    "low_marginal_value",
                ]
                missing = [k for k in required_flags if saturation.get(k) is not True]
                if missing:
                    errors.append(
                        f"research question {item.get('id', '?')}: SATURATED without "
                        f"all stop-condition flags true: {', '.join(missing)}"
                    )

    oq = load_yaml(state / "open_questions.yaml")
    for item in oq.get("questions", []):
        if item.get("type") and item.get("type") not in OQ_TYPES:
            errors.append(f"open question {item.get('id', '?')}: invalid type {item.get('type')}")
        if item.get("impact") and item.get("impact") not in OQ_IMPACT:
            errors.append(f"open question {item.get('id', '?')}: invalid impact {item.get('impact')}")

    pitfalls = load_yaml(state / "pitfalls.yaml")
    pitfall_ids: set[str] = set()
    for item in pitfalls.get("items", []):
        pid = item.get("id")
        if not pid:
            errors.append("pitfall missing id")
            continue
        if pid in pitfall_ids:
            errors.append(f"duplicate pitfall id: {pid}")
        pitfall_ids.add(pid)
        for field in ["title", "category", "impact", "action", "status"]:
            if not item.get(field):
                errors.append(f"pitfall {pid}: missing {field}")
        if item.get("impact") and item.get("impact") not in PITFALL_IMPACT:
            errors.append(f"pitfall {pid}: invalid impact {item.get('impact')}")
        if item.get("action") and item.get("action") not in PITFALL_ACTION:
            errors.append(f"pitfall {pid}: invalid action {item.get('action')}")
        if item.get("status") and item.get("status") not in PITFALL_STATUS:
            errors.append(f"pitfall {pid}: invalid status {item.get('status')}")
        if item.get("impact") in {"HIGH", "CRITICAL"}:
            if not item.get("evidence"):
                errors.append(f"pitfall {pid}: HIGH/CRITICAL pitfall missing evidence")
            if not item.get("mitigation"):
                errors.append(f"pitfall {pid}: HIGH/CRITICAL pitfall missing mitigation")
        if item.get("impact") == "CRITICAL" and item.get("action") == "WATCH":
            errors.append(f"pitfall {pid}: CRITICAL pitfall cannot use WATCH action")

    decisions = load_yaml(state / "decisions.yaml")
    for item in decisions.get("decisions", []):
        if item.get("status") and item.get("status") not in DECISION_STATUS:
            errors.append(f"decision {item.get('id', '?')}: invalid status {item.get('status')}")

    handoff = load_yaml(state / "dida_handoff.yaml")
    if handoff.get("status") not in {"DRAFT", "APPROVED", "HANDED_OFF"}:
        errors.append(f"invalid dida handoff status: {handoff.get('status')}")
    if handoff.get("approval_required") is not True and handoff.get("status") == "DRAFT":
        errors.append("DRAFT dida handoff must require approval")
    for wp in handoff.get("work_packages", []):
        for field in ["id", "stage", "title", "expected_outputs", "acceptance", "dependencies"]:
            if field not in wp:
                errors.append(f"work package {wp.get('id', '?')}: missing {field}")

    source_fields, source_rows = read_csv(state / "sources.csv")
    if source_fields != SOURCE_COLUMNS:
        errors.append("sources.csv header does not match v1 contract")
    retained = []
    source_ids: set[str] = set()
    for row in source_rows:
        sid = row.get("SourceID", "").strip()
        if sid:
            if sid in source_ids:
                errors.append(f"duplicate source id: {sid}")
            source_ids.add(sid)
        tier = row.get("Tier", "").strip()
        if tier and tier not in SOURCE_TIERS:
            errors.append(f"source {sid or '?'}: invalid Tier {tier}")
        auth = row.get("Authority", "").strip()
        if auth and auth not in AUTHORITY:
            errors.append(f"source {sid or '?'}: invalid Authority {auth}")
        indep = row.get("Independence", "").strip()
        if indep and indep not in INDEPENDENCE:
            errors.append(f"source {sid or '?'}: invalid Independence {indep}")
        role = row.get("RetentionRole", "").strip()
        if role not in RETENTION_ROLE:
            errors.append(f"source {sid or '?'}: invalid RetentionRole {role}")
        if row.get("Status", "").strip().upper() == "RETAINED":
            retained.append(row)
            if not row.get("LocalPath", "").strip():
                errors.append(f"source {sid or '?'}: RETAINED source missing LocalPath")
            if role in {"", "NONE"}:
                errors.append(f"source {sid or '?'}: RETAINED source missing retention role")
            if role == "EXCEPTION" and not row.get("RetentionReason", "").strip():
                errors.append(f"source {sid or '?'}: EXCEPTION retention missing reason")

    policy = project.get("research_policy", {})
    budget = int(policy.get("retained_artifact_budget", 2))
    allow_extra = bool(policy.get("allow_extra_retained", False))
    if len(retained) > budget and not allow_extra:
        errors.append(
            f"retained artifact count {len(retained)} exceeds budget {budget}; "
            "set project.research_policy.allow_extra_retained=true with documented reasons"
        )

    search_fields, search_rows = read_csv(state / "search_log.csv")
    if search_fields != SEARCH_LOG_COLUMNS:
        errors.append("search_log.csv header does not match v1 contract")
    search_ids: set[str] = set()
    for row in search_rows:
        sid = row.get("SearchID", "").strip()
        if sid:
            if sid in search_ids:
                errors.append(f"duplicate search log id: {sid}")
            search_ids.add(sid)

    evidence_ids: set[str] = set()
    for lineno, line in enumerate(
        (state / "evidence.jsonl").read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"evidence.jsonl line {lineno}: invalid JSON: {e}")
            continue
        eid = item.get("id")
        if eid:
            if eid in evidence_ids:
                errors.append(f"duplicate evidence id: {eid}")
            evidence_ids.add(eid)
        etype = item.get("type")
        if etype == "FACT":
            if not item.get("source_id"):
                errors.append(f"evidence {eid or lineno}: FACT missing source_id")
        elif etype == "INFERENCE":
            if not item.get("basis"):
                errors.append(f"evidence {eid or lineno}: INFERENCE missing basis")
        else:
            errors.append(f"evidence {eid or lineno}: invalid type {etype}")

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
