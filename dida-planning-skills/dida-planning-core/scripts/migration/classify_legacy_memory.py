from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def bullets_by_heading(body: str) -> list[dict[str, str]]:
    heading = ""
    out: list[dict[str, str]] = []
    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            heading = line[3:].strip()
        elif line.startswith("- "):
            out.append({"section": heading, "text": line[2:].strip()})
    return out


def classify_item(item: dict[str, str]) -> dict[str, Any]:
    text = item["text"]
    section = item.get("section", "")
    if section in {"维护", "归档规则", "已归档"}:
        return {**item, "decision": "skip", "reason": "maintenance_metadata"}
    if any(token in text for token in ["当前对话", "本窗口", "当前会话", "新窗口"]):
        return {**item, "decision": "skip", "reason": "temporary_session_context"}
    if "Markdown" in text and any(token in text for token in ["唯一规划数据源", "SQLite", "PWA"]):
        return {**item, "decision": "skip", "reason": "obsolete_storage_rule"}
    if any(token in text for token in ["作息", "健身", "日程", "工作时间", "精力"]):
        return {**item, "decision": "route", "owner": "profile", "reason": "planning_preference"}
    if any(token in text for token in ["任务状态", "剩余分钟", "截止", "当前进度"]):
        return {**item, "decision": "skip", "reason": "task_state_not_memory"}
    kind = "workflow" if any(token in text for token in ["需从", "默认", "不得", "必须", "不依赖", "解释"] ) else "convention"
    return {**item, "decision": "review", "owner": "memory", "memory_kind": kind, "reason": "durable_candidate_requires_human_review"}


def build(scan: dict[str, Any]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for rec in scan.get("records", []):
        if rec.get("type") != "memory":
            continue
        for item in bullets_by_heading(rec.get("body", "")):
            classified = classify_item(item)
            classified["source"] = rec.get("decoded_path")
            candidates.append(classified)
    counts: dict[str, int] = {}
    for c in candidates:
        counts[c["decision"]] = counts.get(c["decision"], 0) + 1
    return {"candidates": candidates, "counts": counts, "writes_performed": False}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("scan_json")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    scan = json.loads(Path(args.scan_json).read_text(encoding="utf-8"))
    result = build(scan)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
