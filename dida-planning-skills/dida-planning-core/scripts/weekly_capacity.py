from __future__ import annotations

import argparse
from datetime import date, datetime
from typing import Any

from common import is_work_item, read_json, write_json


DEFAULT_RESERVE_RATIO = 0.35
RECOMMENDED_RESERVE_RANGE = (0.30, 0.40)
COMMITTED_TIERS = {"must", "should"}
ALL_TIERS = COMMITTED_TIERS | {"candidate"}


def _identifier(item: dict[str, Any], index: int) -> str:
    return str(item.get("id") or item.get("task_id") or item.get("title") or index)


def _week_start(value: Any) -> date:
    if not isinstance(value, str):
        raise ValueError("week_start is required and must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("week_start is required and must be YYYY-MM-DD") from exc
    if parsed.weekday() != 0:
        raise ValueError("week_start must be a Monday")
    return parsed


def _positive_number(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        return None
    return minutes if minutes > 0 else None


def _estimate(item: dict[str, Any]) -> int | None:
    # Remaining occupancy is preferred when an estimator/progress pass supplied it.
    for key in ("remaining_minutes", "estimated_minutes", "duration_minutes"):
        if key in item:
            return _positive_number(item[key])
    return None


def _tier(item: dict[str, Any]) -> str:
    value = item.get("weekly_commitment", item.get("commitment", item.get("tier")))
    if value not in ALL_TIERS:
        raise ValueError(f"mainline {_identifier(item, 0)} has invalid weekly commitment: {value!r}")
    return value


def _dependency_risk(item: dict[str, Any], identifier: str) -> dict[str, Any] | None:
    if item.get("dependencies_ready") is False or item.get("dependency_ready") is False:
        return {"id": identifier, "reason": "dependency_not_ready", "blocking": True}
    unresolved = []
    blocking = False
    for dependency in item.get("dependencies") or []:
        if dependency.get("blocking") is True or dependency.get("ready") is False or dependency.get("resolved") is False:
            strength = dependency.get("strength", "hard")
            dependency_blocking = dependency.get("blocking") is True or strength == "hard"
            blocking = blocking or dependency_blocking
            unresolved.append({
                key: dependency[key]
                for key in ("type", "task_id", "external_ref", "strength", "note")
                if key in dependency
            } | {"strength": strength, "blocking": dependency_blocking})
    if unresolved:
        return {"id": identifier, "reason": "dependency_not_ready", "blocking": blocking, "dependencies": unresolved}
    return None


def _parse_datetime_or_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None


def _deadline_risk(item: dict[str, Any], identifier: str, start: date, end: date, estimate: int | None) -> dict[str, Any] | None:
    hard = item.get("date_semantics") == "hard_deadline" or item.get("hard_deadline") is True
    deadline_value = item.get("deadline") or item.get("due_date")
    if not hard:
        return None
    if deadline_value is None:
        return {"id": identifier, "reason": "hard_deadline_missing_date", "blocking": True}
    deadline = _parse_datetime_or_date(deadline_value)
    if deadline is None:
        return {"id": identifier, "reason": "hard_deadline_invalid_date", "deadline": deadline_value, "blocking": True}
    if deadline < start:
        return {"id": identifier, "reason": "hard_deadline_before_week", "deadline": deadline.isoformat(), "blocking": True}
    if estimate is not None:
        available = item.get("deadline_available_minutes")
        if isinstance(available, bool) or available is None:
            return {"id": identifier, "reason": "deadline_capacity_unknown", "deadline": deadline.isoformat(), "blocking": True}
        try:
            available_minutes = int(available)
        except (TypeError, ValueError):
            return {"id": identifier, "reason": "deadline_capacity_unknown", "deadline": deadline.isoformat(), "blocking": True}
        if available_minutes < 0:
            return {"id": identifier, "reason": "deadline_capacity_unknown", "deadline": deadline.isoformat(), "blocking": True}
        if estimate > available_minutes:
            return {
                "id": identifier,
                "reason": "insufficient_capacity_before_deadline",
                "deadline": deadline.isoformat(),
                "capacity_gap_minutes": estimate - available_minutes,
                "blocking": True,
            }
    if deadline <= end:
        return {"id": identifier, "reason": "hard_deadline_this_week", "deadline": deadline.isoformat(), "blocking": False}
    last_viable = _parse_datetime_or_date(item.get("last_viable_start"))
    if last_viable is not None and last_viable < start:
        return {"id": identifier, "reason": "last_viable_start_before_week", "deadline": deadline.isoformat(), "blocking": True}
    return None


def stale_commitment_updates(tasks: list[dict[str, Any]], current_week_start: str) -> list[dict[str, Any]]:
    """Return read-only clear patches for task-local commitments from another week."""
    current = _week_start(current_week_start).isoformat()
    stale = []
    for index, task in enumerate(tasks):
        if not is_work_item(task):
            continue
        if "week_start" not in task and "weekly_commitment" not in task:
            continue
        identifier = _identifier(task, index)
        week_value = task.get("week_start")
        commitment = task.get("weekly_commitment")
        reason = None
        if "week_start" not in task or "weekly_commitment" not in task or commitment not in ALL_TIERS:
            reason = "malformed_weekly_commitment"
        else:
            try:
                parsed_week = _week_start(week_value).isoformat()
            except ValueError:
                reason = "malformed_weekly_commitment"
            else:
                if parsed_week != current:
                    reason = "stale_weekly_commitment"
        if reason:
            stale.append({
                "id": identifier,
                "title": task.get("title"),
                "week_start": week_value,
                "weekly_commitment": commitment,
                "reason": reason,
                "clear_patch": {"week_start": "__DELETE__", "weekly_commitment": "__DELETE__"},
            })
    return stale


def assess_capacity(data: dict[str, Any]) -> dict[str, Any]:
    """Assess selected weekly mainlines without making priority decisions."""
    start = _week_start(data.get("week_start"))
    capacity = data.get("weekly_capacity_minutes", data.get("available_minutes"))
    if isinstance(capacity, bool) or capacity is None:
        raise ValueError("weekly_capacity_minutes is required")
    try:
        capacity = int(capacity)
    except (TypeError, ValueError) as exc:
        raise ValueError("weekly_capacity_minutes must be a non-negative integer") from exc
    if capacity < 0:
        raise ValueError("weekly_capacity_minutes must be a non-negative integer")
    try:
        reserve_ratio = float(data.get("reserve_ratio", DEFAULT_RESERVE_RATIO))
    except (TypeError, ValueError) as exc:
        raise ValueError("reserve_ratio must be a number from 0 to less than 1") from exc
    if not 0 <= reserve_ratio < 1:
        raise ValueError("reserve_ratio must be a number from 0 to less than 1")

    mainlines = data.get("mainlines", data.get("candidate_mainlines", []))
    if not isinstance(mainlines, list):
        raise ValueError("mainlines must be a list")
    end = start.fromordinal(start.toordinal() + 6)
    details = []
    missing_estimates = []
    dependency_risks = []
    deadline_risks = []
    committed_minutes = 0
    candidate_minutes = 0
    committed_missing_estimate = False
    committed_dependency_blocked = False
    committed_deadline_blocked = False

    for index, item in enumerate(mainlines):
        if not isinstance(item, dict):
            raise ValueError("each mainline must be an object")
        if not is_work_item(item):
            raise ValueError(f"mainline {_identifier(item, index)} must be a work role")
        identifier = _identifier(item, index)
        tier = _tier(item)
        estimate = _estimate(item)
        committed = tier in COMMITTED_TIERS
        if estimate is None:
            missing_estimates.append({"id": identifier, "tier": tier})
            committed_missing_estimate = committed_missing_estimate or committed
        elif committed:
            committed_minutes += estimate
        else:
            candidate_minutes += estimate
        dependency_risk = _dependency_risk(item, identifier)
        if dependency_risk:
            dependency_risks.append(dependency_risk)
            committed_dependency_blocked = committed_dependency_blocked or (committed and dependency_risk.get("blocking") is True)
        deadline_risk = _deadline_risk(item, identifier, start, end, estimate)
        if deadline_risk:
            deadline_risks.append(deadline_risk)
            committed_deadline_blocked = committed_deadline_blocked or (committed and deadline_risk.get("blocking") is True)
        details.append({
            "id": identifier,
            "title": item.get("title"),
            "weekly_commitment": tier,
            "estimated_minutes": estimate,
            "counts_as_committed": committed,
        })

    reserved_minutes = int(capacity * reserve_ratio)
    usable_capacity = capacity - reserved_minutes
    selection_count = len(mainlines)
    selection_count_ok = 2 <= selection_count <= 4
    capacity_fits = committed_minutes <= usable_capacity
    fits = (
        selection_count_ok
        and capacity_fits
        and not committed_missing_estimate
        and not committed_dependency_blocked
        and not committed_deadline_blocked
    )
    result = {
        "week_start": start.isoformat(),
        "weekly_capacity_minutes": capacity,
        "reserve_ratio": reserve_ratio,
        "recommended_reserve_ratio": DEFAULT_RESERVE_RATIO,
        "recommended_reserve_range": [RECOMMENDED_RESERVE_RANGE[0], RECOMMENDED_RESERVE_RANGE[1]],
        "reserved_minutes": reserved_minutes,
        "usable_capacity_minutes": usable_capacity,
        "usable_capacity": usable_capacity,
        "committed_minutes": committed_minutes,
        "candidate_minutes": candidate_minutes,
        "remaining_committed_capacity_minutes": max(usable_capacity - committed_minutes, 0),
        "overflow_minutes": max(committed_minutes - usable_capacity, 0),
        "capacity_fits": capacity_fits,
        "fits": fits,
        "planning_valid": fits,
        "selection_count": selection_count,
        "selection_count_ok": selection_count_ok,
        "mainlines": details,
        "missing_estimates": missing_estimates,
        "dependency_risks": dependency_risks,
        "deadline_risks": deadline_risks,
        "stale_commitments": stale_commitment_updates(data.get("tasks", []), start.isoformat()),
    }
    if not RECOMMENDED_RESERVE_RANGE[0] <= reserve_ratio <= RECOMMENDED_RESERVE_RANGE[1]:
        result["warnings"] = ["reserve_ratio is outside the recommended 30%-40% range"]
    else:
        result["warnings"] = []
    return result


assess_week_capacity = assess_capacity


def main() -> None:
    ap = argparse.ArgumentParser(description="Assess weekly mainline capacity from JSON; no Dida state is stored locally.")
    ap.add_argument("--input", required=True, help="JSON input file, or - for stdin")
    ap.add_argument("--output", help="Write JSON output to this file instead of stdout")
    args = ap.parse_args()
    write_json(assess_capacity(read_json(args.input)), args.output)


if __name__ == "__main__":
    main()
