from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any

HEADER = "[planner-event:v1]"
ORDER = [
    "event", "operation_id", "timestamp", "prior_estimate_minutes", "calendar_minutes",
    "focus_minutes", "other_active_minutes", "ai_parallel_minutes", "end_to_end_minutes",
    "included_in_estimation", "reason", "note"
]


def render_event(data: dict[str, Any]) -> str:
    payload = dict(data)
    payload.setdefault("timestamp", datetime.now().astimezone().isoformat(timespec="seconds"))
    lines = [HEADER]
    for key in ORDER + [k for k in payload if k not in ORDER]:
        if key not in payload: continue
        value = payload[key]
        if value is None: text = "null"
        elif value is True: text = "true"
        elif value is False: text = "false"
        else: text = str(value).replace("\n", " ").strip()
        lines.append(f"{key}: {text}")
    return "\n".join(lines)


def parse_event(text: str) -> OrderedDict[str, Any]:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    if not lines or lines[0] != HEADER:
        raise ValueError("not a planner-event:v1 comment")
    data: OrderedDict[str, Any] = OrderedDict()
    for line in lines[1:]:
        if not line.strip(): continue
        if ":" not in line: raise ValueError(f"invalid event line: {line!r}")
        key, raw = line.split(":", 1); raw = raw.strip()
        if raw == "null": value: Any = None
        elif raw in {"true", "false"}: value = raw == "true"
        else:
            try: value = int(raw)
            except ValueError: value = raw
        data[key.strip()] = value
    return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-json")
    ap.add_argument("--parse")
    args = ap.parse_args()
    if args.from_json:
        data = json.loads(Path(args.from_json).read_text(encoding="utf-8")) if args.from_json != "-" else json.load(__import__('sys').stdin)
        print(render_event(data))
    elif args.parse:
        text = Path(args.parse).read_text(encoding="utf-8") if args.parse != "-" else __import__('sys').stdin.read()
        print(json.dumps(parse_event(text), ensure_ascii=False, indent=2))
    else:
        ap.error("use --from-json or --parse")

if __name__ == "__main__":
    main()
