from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


def load(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--queue", required=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add"); add.add_argument("--operation", required=True); add.add_argument("--task-id"); add.add_argument("--type", required=True); add.add_argument("--base-hash"); add.add_argument("--failure", required=True)
    sub.add_parser("list")
    done = sub.add_parser("done"); done.add_argument("operation_id")
    fail = sub.add_parser("fail"); fail.add_argument("operation_id"); fail.add_argument("--reason", required=True)
    args = ap.parse_args(); path = Path(args.queue); rows = load(path)
    if args.cmd == "add":
        op = json.loads(Path(args.operation).read_text(encoding="utf-8"))
        row = {"operation_id": str(uuid.uuid4()), "task_id": args.task_id, "operation_type": args.type, "base_hash": args.base_hash, "changed_fields": sorted(op.keys()), "operation": op, "created_at": datetime.now().astimezone().isoformat(timespec="seconds"), "failure_reason": args.failure, "retry_count": 0, "status": "pending"}
        rows.append(row); save(path, rows); print(json.dumps(row, ensure_ascii=False, indent=2))
    elif args.cmd == "list":
        print(json.dumps([r for r in rows if r.get("status") == "pending"], ensure_ascii=False, indent=2))
    else:
        found = False
        for row in rows:
            if row["operation_id"] == args.operation_id:
                found = True
                if args.cmd == "done": row["status"] = "done"; row["resolved_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
                else: row["retry_count"] = int(row.get("retry_count", 0)) + 1; row["failure_reason"] = args.reason
        if not found: raise SystemExit("operation_id not found")
        save(path, rows)

if __name__ == "__main__": main()
