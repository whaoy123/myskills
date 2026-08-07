from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from planner_event import render_event


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("seed_json"); ap.add_argument("--output",required=True); args=ap.parse_args()
    rows=json.loads(Path(args.seed_json).read_text(encoding="utf-8")); out=[]
    for row in rows:
        event={"event":"completed","operation_id":str(uuid.uuid4()),"prior_estimate_minutes":row.get("estimated_minutes"),"calendar_minutes":row.get("calendar_minutes"),"included_in_estimation":bool(row.get("included")),"category":row.get("category"),"mode":row.get("mode"),"reason":"legacy estimation sample migration"}
        out.append({"legacy_task_id":row.get("task_id"),"comment":render_event(event),"preview_only":True})
    Path(args.output).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"comments={len(out)} preview_only=true")

if __name__ == "__main__": main()
