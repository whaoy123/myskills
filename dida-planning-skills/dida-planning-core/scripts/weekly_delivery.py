"""Pure weekly-delivery validation. Inputs are transient connector snapshots.

No network, local task database, calendar scheduling, or remote writes are used.
Budget values are explicitly supplied human-effort limits, never calendar slots.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

CORE_LEVELS = {"must", "should"}
WORK_OWNERS = {"task", "phase"}
STATUSES = {"planned", "delivered", "not_delivered", "blocked", "cancelled", "unverified"}
EVIDENCE_KINDS = {"user_report", "artifact", "test_log", "tool_result", "demonstration"}
WEEK_FIELDS = ("week_start", "weekly_commitment", "weekly_delivery")


def iso_date(value: Any, *, monday: bool = False) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("expected ISO date YYYY-MM-DD")
    result = date.fromisoformat(value)
    if monday and result.weekday() != 0:
        raise ValueError("week_start must be a Monday")
    return result


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _minutes(value: Any) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def _string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (isinstance(value, list) and (bool(value) or not nonempty)
            and all(_text(item) for item in value))


def _evidence_valid(value: Any) -> bool:
    return (isinstance(value, list) and all(
        isinstance(item, dict) and isinstance(item.get("kind"), str)
        and item["kind"] in EVIDENCE_KINDS and _text(item.get("detail"))
        for item in value))


def validate_contract(contract: Any, week_start: Any) -> list[str]:
    """Validate the extension's shape; this cannot verify external artifacts."""
    errors: list[str] = []
    if not isinstance(contract, dict):
        return ["weekly_delivery must be a JSON object"]
    if type(contract.get("schema")) is not int or contract["schema"] != 1:
        errors.append("weekly_delivery.schema must be integer 1")
    if not isinstance(contract.get("slot"), str) or contract["slot"] not in {"work", "growth"}:
        errors.append("weekly_delivery.slot must be work or growth")
    for key in ("outcome", "artifact", "scope", "verification"):
        if not _text(contract.get(key)):
            errors.append(f"weekly_delivery.{key} must be nonempty text")
    if not _string_list(contract.get("criteria"), nonempty=True):
        errors.append("weekly_delivery.criteria must contain acceptance criteria")
    for key in ("support_task_ids", "exclusions"):
        if not _string_list(contract.get(key)):
            errors.append(f"weekly_delivery.{key} must be a string array")
    refs = contract.get("support_task_ids")
    if _string_list(refs) and len(set(refs)) != len(refs):
        errors.append("weekly_delivery.support_task_ids contains duplicate IDs")
    status = contract.get("status")
    if not isinstance(status, str) or status not in STATUSES:
        errors.append("weekly_delivery.status is invalid")
    if not _evidence_valid(contract.get("evidence")):
        errors.append("weekly_delivery.evidence must contain valid kind/detail objects")
    elif status == "delivered" and not contract["evidence"]:
        errors.append("delivered requires evidence; progress alone is insufficient")
    try:
        start = iso_date(week_start, monday=True)
        target = iso_date(contract.get("target_date"))
        if not start <= target <= start + timedelta(days=6):
            errors.append("weekly_delivery.target_date must be inside the selected week")
    except ValueError as exc:
        errors.append(f"weekly_delivery date: {exc}")
    return errors


def assess_acceptance(contract: dict[str, Any], *, week_start: str,
                      criterion_results: list[bool | None] | None = None,
                      evidence: list[dict[str, Any]] | None = None,
                      user_attested: bool = False,
                      blocked_reason: str | None = None) -> dict[str, Any]:
    """Return an acceptance recommendation, never native completion operations.

    user_attested means the user explicitly confirmed the contracted scope and
    criteria, not just hours worked or one subordinate step.
    """
    errors = validate_contract(contract, week_start)
    if errors:
        raise ValueError("; ".join(errors))
    if type(user_attested) is not bool:
        raise ValueError("user_attested must be boolean")
    records = deepcopy(contract["evidence"] if evidence is None else evidence)
    if not _evidence_valid(records):
        raise ValueError("invalid evidence")
    if blocked_reason is not None and not _text(blocked_reason):
        raise ValueError("blocked_reason must be nonempty text")
    if criterion_results is not None:
        if (not isinstance(criterion_results, list)
                or len(criterion_results) != len(contract["criteria"])
                or any(item is not None and type(item) is not bool for item in criterion_results)):
            raise ValueError("criterion_results must match every criterion with bool or null")
    # Contrary evidence is not erased by a generic claim of completion.
    if blocked_reason is not None:
        status, reason = "blocked", blocked_reason
    elif criterion_results is not None and any(item is False for item in criterion_results):
        status, reason = "not_delivered", "at least one criterion is not satisfied"
    elif user_attested and any(item["kind"] == "user_report" for item in records):
        status, reason = "delivered", "user explicitly confirmed the contracted result"
    elif (criterion_results is not None and all(item is True for item in criterion_results)
          and any(item["kind"] != "user_report" for item in records)):
        status, reason = "delivered", "all criteria checked with observed evidence"
    else:
        status, reason = "unverified", "complete acceptance evidence is missing"
    return {"status": status, "reason": reason, "evidence": records,
            "native_owner_completion": False}


def evaluate_plan(data: dict[str, Any]) -> dict[str, Any]:
    """Validate normalized task data and report workload/unknown feasibility.

    Expected task keys are documented in weekly-contract.md. Normalization is
    a connector-layer responsibility, not an excuse to invent API parameters.
    """
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    start = iso_date(data.get("week_start"), monday=True)
    end = start + timedelta(days=6)
    try:
        as_of = iso_date(data["as_of"]) if data.get("as_of") is not None else None
    except ValueError as exc:
        raise ValueError(f"as_of: {exc}") from exc
    cap = data.get("core_limit", 2)
    if type(cap) is not int or cap < 1:
        raise ValueError("core_limit must be a positive integer")
    errors: list[str] = []
    warnings: list[str] = []
    unknowns: list[str] = []
    blockers: list[str] = []
    if cap > 2 and not _text(data.get("override_reason")):
        errors.append("a core_limit above 2 requires an explicit user-approved override_reason")
    complete = data.get("inventory_complete") is True
    if not complete:
        unknowns.append("inventory_incomplete: global coverage has not been established")
    budget = data.get("effort_budget_minutes")
    if budget is not None and not _minutes(budget):
        raise ValueError("effort_budget_minutes must be finite nonnegative minutes or null")
    raw_tasks = data.get("tasks")
    if not isinstance(raw_tasks, list):
        raise ValueError("tasks must be an array")
    tasks: dict[str, dict[str, Any]] = {}
    for task in raw_tasks:
        if not isinstance(task, dict) or not _text(task.get("id")):
            errors.append("every task requires a nonempty string id")
            continue
        if task["id"] in tasks:
            errors.append(f"duplicate task id: {task['id']}")
            continue
        role = task.get("role", "task")
        if not isinstance(role, str) or role not in {"project", "phase", "task", "block", "config", "memory", "memory_category"}:
            errors.append(f"{task['id']}: invalid role")
            continue
        tasks[task["id"]] = task
        if type(task.get("completed")) is not bool:
            errors.append(f"{task['id']}: completed must be explicitly boolean")
    obligations = data.get("obligation_task_ids", [])
    if not _string_list(obligations):
        raise ValueError("obligation_task_ids must be a string array")
    if len(obligations) != len(set(obligations)):
        warnings.append("duplicate obligation references were counted once")
    core: list[dict[str, Any]] = []
    candidates: list[str] = []
    stale: list[str] = []
    selected: dict[str, set[str]] = {}
    children: dict[str, list[str]] = {}
    for task in tasks.values():
        parent = task.get("parent_id")
        if parent and task.get("completed") is False:
            children.setdefault(str(parent), []).append(task["id"])

    def add_leaf(task_id: str, source: str) -> None:
        task = tasks.get(task_id)
        if task is None:
            errors.append(f"{source}: unresolved task reference {task_id}")
            return
        if task.get("role", "task") != "task":
            errors.append(f"{source}: {task_id} is not an executable leaf task")
            return
        if children.get(task_id):
            errors.append(f"{source}: {task_id} has unfinished children; use leaf estimates")
            return
        selected.setdefault(task_id, set()).add(source)

    for task in tasks.values():
        tid = task["id"]
        present = [key in task for key in WEEK_FIELDS[:2]]
        contract = task.get("weekly_delivery")
        if any(present) and not all(present):
            errors.append(f"{tid}: week_start and weekly_commitment must occur together")
            continue
        if contract is not None and not all(present):
            errors.append(f"{tid}: weekly_delivery requires the legacy week/commitment pair")
            continue
        if not any(present):
            continue
        try:
            task_week = iso_date(task["week_start"], monday=True)
        except ValueError as exc:
            errors.append(f"{tid}: {exc}")
            continue
        level = task["weekly_commitment"]
        if not isinstance(level, str) or level not in CORE_LEVELS | {"candidate"}:
            errors.append(f"{tid}: invalid weekly_commitment")
            continue
        if task_week < start:
            stale.append(tid)
            continue
        if task_week > start:
            continue
        if task.get("role", "task") not in WORK_OWNERS:
            errors.append(f"{tid}: weekly owner must be task or phase")
            continue
        if contract is None:
            if level in CORE_LEVELS:
                unknowns.append(f"{tid}: legacy commitment needs a delivery contract")
                core.append(task)
                add_leaf(tid, tid)
            else:
                candidates.append(tid)
            continue
        contract_errors = validate_contract(contract, task["week_start"])
        errors.extend(f"{tid}: {message}" for message in contract_errors)
        if contract_errors:
            continue
        if level == "candidate":
            candidates.append(tid)
            continue
        if contract["status"] == "cancelled":
            continue
        core.append(task)
        if contract["status"] == "blocked":
            blockers.append(f"{tid}: delivery contract is blocked")
        refs = contract["support_task_ids"]
        if task.get("role", "task") == "phase" and not refs:
            errors.append(f"{tid}: phase owner requires explicit supporting leaf tasks")
        if tid in refs:
            errors.append(f"{tid}: support_task_ids must not self-reference")
            continue
        # Delivered slices no longer consume remaining effort, but their
        # references must still resolve. Their accepted scope is not reopened.
        for ref in refs or ([tid] if task.get("role", "task") == "task" else []):
            if contract["status"] == "delivered":
                if ref not in tasks:
                    errors.append(f"{tid}: unresolved task reference {ref}")
            else:
                add_leaf(ref, tid)
    for tid in set(obligations):
        add_leaf(tid, "obligation")
    if len(core) > cap:
        errors.append(f"core_commitment_limit: {len(core)} exceeds {cap}")
    has_growth = any(t.get("weekly_delivery", {}).get("slot") == "growth" for t in core)
    growth_deferral_reason = data.get("growth_deferral_reason")
    growth_resume_condition = data.get("growth_resume_condition")
    if core and not has_growth:
        if not _text(growth_deferral_reason):
            warnings.append("no growth deliverable: record growth_deferral_reason instead of silently deferring it")
        if not _text(growth_resume_condition):
            warnings.append("no growth deliverable: record growth_resume_condition for re-evaluation")
    if stale:
        warnings.append("stale week markers need review/archive; no automatic rollover performed")
    shared = sorted(tid for tid, sources in selected.items() if len(sources) > 1)
    if shared:
        warnings.append("shared leaf work counted once; each deliverable still needs its own acceptance")
    effort = 0.0
    for tid, sources in selected.items():
        task = tasks[tid]
        if task.get("completed") is True:
            continue
        remaining = task.get("remaining_minutes")
        if remaining is None:
            unknowns.append(f"{tid}: remaining effort is unknown")
        elif not _minutes(remaining):
            errors.append(f"{tid}: remaining_minutes must be finite nonnegative minutes")
        else:
            effort += remaining
            if remaining == 0 and task.get("effort_not_required") is not True:
                unknowns.append(f"{tid}: unfinished work has a zero estimate; confirm its meaning")
        if task.get("estimate_confidence") == "low":
            warnings.append(f"{tid}: low-confidence estimate; scope/buffer requires review")
        if task.get("blocked") is True:
            blockers.append(f"{tid}: hard dependency or external wait is unresolved")
        elif task.get("blocked") is not False:
            unknowns.append(f"{tid}: dependency/wait readiness has not been verified")
    if budget is None and selected:
        unknowns.append("weekly effort budget not supplied; feasibility cannot be assured")
    if budget is not None and effort > budget:
        blockers.append(f"effort_budget_exceeded: {effort:g} > {budget:g} minutes")
    risks: list[dict[str, Any]] = []
    for task in tasks.values():
        if task.get("completed") is True or task.get("role", "task") not in {"project", "phase", "task"}:
            continue
        tid, semantics = task["id"], task.get("date_semantics", "none")
        deadline = task.get("due_date")
        if semantics != "hard_deadline":
            continue
        try:
            due = iso_date(deadline)
        except ValueError:
            errors.append(f"{tid}: hard deadline needs a valid due_date")
            continue
        if as_of is not None and due < as_of:
            risks.append({"id": tid, "risk": "hard_deadline_overdue", "date": deadline})
        elif as_of is None and due < start:
            risks.append({"id": tid, "risk": "deadline_before_plan_week", "date": deadline})
        elif due <= end:
            risks.append({"id": tid, "risk": "hard_deadline_this_week", "date": deadline})
        latest = task.get("latest_safe_start")
        if latest is None or not _text(task.get("latest_start_basis")):
            risks.append({"id": tid, "risk": "latest_safe_start_unknown"})
        else:
            try:
                launch = iso_date(latest)
                if launch > due:
                    errors.append(f"{tid}: latest_safe_start occurs after hard deadline")
                elif launch <= end:
                    risks.append({"id": tid, "risk": "must_start_by_week_end", "date": latest,
                                  "basis": task["latest_start_basis"]})
            except ValueError:
                errors.append(f"{tid}: invalid latest_safe_start")
    covered = set(selected) | {t["id"] for t in core}
    for risk in risks:
        if risk["risk"] == "latest_safe_start_unknown":
            unknowns.append(f"{risk['id']}: deadline/start risk lacks adequate elapsed-time evidence")
        elif risk["id"] not in covered:
            unknowns.append(f"{risk['id']}: urgent risk outside the selected work needs a decision")
    feasibility = "invalid" if errors else "blocked" if blockers else "unknown" if unknowns else "feasible"
    return {"week_start": start.isoformat(), "inventory_complete": complete,
            "validation_passed": not errors, "feasibility": feasibility,
            "core_owner_ids": [t["id"] for t in core], "core_count": len(core),
            "candidate_ids": candidates, "obligation_task_ids": sorted(set(obligations)),
            "counted_task_ids": sorted(selected), "shared_task_ids": shared,
            "known_remaining_minutes": effort, "effort_budget_minutes": budget,
            "stale_owner_ids": stale, "risks": risks, "errors": errors,
            "blockers": blockers, "unknowns": unknowns, "warnings": warnings,
            "growth_tradeoff": {"has_growth": has_growth,
                                "deferral_reason": growth_deferral_reason,
                                "resume_condition": growth_resume_condition},
            "remote_mutations": []}


def prepare_week_rollover(task: dict[str, Any], next_week: str) -> dict[str, Any] | None:
    """Draft an archive and conditional clear; caller MUST archive/read back first."""
    boundary = iso_date(next_week, monday=True)
    if not any(key in task for key in WEEK_FIELDS):
        return None
    if not all(key in task for key in WEEK_FIELDS[:2]):
        raise ValueError("malformed week pair: resolve before clearing")
    old_week = iso_date(task["week_start"], monday=True)
    if old_week >= boundary:
        return None
    if not _text(task.get("id")) or task.get("role", "task") not in WORK_OWNERS:
        raise ValueError("valid owner id/role required")
    if (not isinstance(task["weekly_commitment"], str)
            or task["weekly_commitment"] not in CORE_LEVELS | {"candidate"}):
        raise ValueError("invalid weekly commitment")
    if "weekly_delivery" in task:
        errors = validate_contract(task["weekly_delivery"], task["week_start"])
        if errors:
            raise ValueError("malformed contract: " + "; ".join(errors))
    snapshot = {key: deepcopy(task[key]) for key in WEEK_FIELDS if key in task}
    canonical = json.dumps({"id": task["id"], **snapshot}, sort_keys=True, ensure_ascii=False, allow_nan=False)
    operation_id = "weekly-review-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]
    return {"owner_id": task["id"], "requires_archive_readback": True,
            "archive_event": {"event": "weekly_review", "operation_id": operation_id,
                              "owner_id": task["id"], "snapshot": snapshot},
            "conditional_clear_patch": {key: "__DELETE__" for key in snapshot},
            "native_field_updates": {}, "remote_mutations": []}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"),
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid JSON {value}")))
        result = evaluate_plan(data)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Input error: {exc}\n")
    rendered = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    raise SystemExit(0 if result["validation_passed"] else 1)


if __name__ == "__main__":
    main()
