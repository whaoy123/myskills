from __future__ import annotations

import argparse
from typing import Any

from common import read_json, write_json
from planner_event import parse_event


def rebuild(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    samples=[]; audits=[]; malformed=[]
    for task in tasks:
        for comment in task.get("comments", []):
            text = comment.get("title") or comment.get("content") or comment.get("text") or ""
            if not text.startswith("[planner-event:v1]"): continue
            try: event=parse_event(text)
            except Exception as exc:
                malformed.append({"task_id":task.get("id"),"comment_id":comment.get("id"),"error":str(exc)}); continue
            if event.get("event") != "completed": continue
            record={
                "task_id": task.get("id"),
                "category": event.get("category") or task.get("category"),
                "mode": event.get("mode") or task.get("mode"),
                "familiarity": event.get("familiarity") or task.get("familiarity"),
                "clarity": event.get("clarity") or task.get("clarity"),
                "validation": event.get("validation") or task.get("validation"),
                "ai_mode": event.get("ai_mode") or task.get("ai_mode"),
                "output_scale": event.get("output_scale") or task.get("output_scale"),
                "estimated_minutes": event.get("prior_estimate_minutes"),
                "calendar_minutes": event.get("calendar_minutes"),
                "focus_minutes": event.get("focus_minutes"),
                "other_active_minutes": event.get("other_active_minutes"),
                "ai_parallel_minutes": event.get("ai_parallel_minutes"),
                "end_to_end_minutes": event.get("end_to_end_minutes"),
                "included": bool(event.get("included_in_estimation")),
                "operation_id": event.get("operation_id"),
            }
            if record["included"] and record["estimated_minutes"] and record["calendar_minutes"]:
                samples.append(record)
            else:
                audits.append(record)
    # Deduplicate retried comments by operation_id, keeping last occurrence.
    by_key={}
    for row in samples:
        key=row.get("operation_id") or f"{row.get('task_id')}:{len(by_key)}"; by_key[key]=row
    return {"samples":list(by_key.values()),"audits":audits,"malformed":malformed,"source":"dida-comments","business_authority":False}


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--output"); args=ap.parse_args(); data=read_json(args.input); tasks=data.get("tasks",data) if isinstance(data,dict) else data; write_json(rebuild(tasks),args.output)

if __name__ == "__main__": main()
