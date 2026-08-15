from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from common import is_work_item, read_json, write_json

@dataclass(order=True)
class Interval:
    start: datetime
    end: datetime


def dt(date: str, hm: str, offset: str) -> datetime:
    return datetime.fromisoformat(f"{date}T{hm}:00{offset}")


def subtract(intervals: list[Interval], busy: Interval) -> list[Interval]:
    out: list[Interval] = []
    for free in intervals:
        if busy.end <= free.start or busy.start >= free.end:
            out.append(free); continue
        if busy.start > free.start: out.append(Interval(free.start, busy.start))
        if busy.end < free.end: out.append(Interval(busy.end, free.end))
    return sorted(out)


def score(task: dict[str, Any]) -> tuple:
    priority = {5: 3, 3: 2, 1: 1, 0: 0, "high": 3, "medium": 2, "low": 1}.get(task.get("priority", 0), 0)
    deadline = task.get("deadline") or "9999-12-31"
    mobility = {"protected": 2, "movable": 1}.get(task.get("mobility"), 0)
    return (-priority, deadline, -mobility, task.get("title", ""))


def schedule(data: dict[str, Any]) -> dict[str, Any]:
    date = data["date"]; offset = data.get("utc_offset", "+08:00")
    free = [Interval(dt(date, w["start"], offset), dt(date, w["end"], offset)) for w in data["availability"]]
    fixed = []
    for item in data.get("fixed", []):
        iv = Interval(datetime.fromisoformat(item["start"]), datetime.fromisoformat(item["end"]))
        fixed.append({**item, "scheduled": True})
        free = subtract(free, iv)
    buffer_minutes = int(data.get("buffer_minutes", 10))
    scheduled = []
    unscheduled = []
    for task in sorted(data.get("tasks", []), key=score):
        if not is_work_item(task):
            unscheduled.append({**task, "reason": "non_work_record"}); continue
        if not task.get("dependencies_ready", True):
            unscheduled.append({**task, "reason": "dependency_not_ready"}); continue
        duration = int(task.get("duration_minutes") or 0)
        if duration <= 0:
            unscheduled.append({**task, "reason": "missing_estimate"}); continue
        if task.get("mobility") == "fixed" and task.get("start") and task.get("end"):
            continue
        placed = False
        for idx, slot in enumerate(list(free)):
            desired = slot.start
            energy = task.get("energy")
            if energy == "high" and data.get("high_energy_start"):
                desired = max(desired, dt(date, data["high_energy_start"], offset))
            end = desired + timedelta(minutes=duration)
            if end <= slot.end:
                item = {**task, "start": desired.isoformat(), "end": end.isoformat(), "scheduled": True}
                scheduled.append(item)
                busy_end = end + timedelta(minutes=buffer_minutes)
                free = subtract(free, Interval(desired, min(busy_end, slot.end)))
                placed = True; break
        if not placed:
            unscheduled.append({**task, "reason": "insufficient_capacity"})
    # invariant check
    all_intervals = [Interval(datetime.fromisoformat(x["start"]), datetime.fromisoformat(x["end"])) for x in fixed + scheduled]
    overlaps = []
    for i, a in enumerate(sorted(all_intervals)):
        for b in sorted(all_intervals)[i+1:]:
            if b.start >= a.end: break
            if b.start < a.end: overlaps.append((a.start.isoformat(), b.start.isoformat()))
    return {"date": date, "fixed": fixed, "scheduled": scheduled, "unscheduled": unscheduled, "remaining_free": [{"start": x.start.isoformat(), "end": x.end.isoformat()} for x in free], "overlaps": overlaps}


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--input", required=True); ap.add_argument("--output")
    args = ap.parse_args(); write_json(schedule(read_json(args.input)), args.output)

if __name__ == "__main__": main()
