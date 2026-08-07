from __future__ import annotations

import argparse
import copy
from typing import Any

from common import read_json, write_json
from planner_block import parse_block, render_block, split_body

STATE_PREFIX = "状态/"


def three_way(base: Any, latest: Any, proposed: Any) -> tuple[Any, bool]:
    if proposed == base: return latest, False
    if latest == base: return proposed, False
    if latest == proposed: return latest, False
    return latest, True


def merge_tags(base: list[str], latest: list[str], proposed: list[str]) -> tuple[list[str], list[str]]:
    conflicts: list[str] = []
    def state(tags): return [t for t in tags if t.startswith(STATE_PREFIX)]
    latest_state, proposed_state, base_state = state(latest), state(proposed), state(base)
    non_state = sorted((set(latest) | set(proposed)) - set(latest_state) - set(proposed_state))
    if latest_state != base_state and proposed_state != base_state and latest_state != proposed_state:
        conflicts.append("tags.state")
        chosen = latest_state
    elif proposed_state != base_state: chosen = proposed_state
    else: chosen = latest_state
    return non_state + chosen[:1], conflicts


def merge_content(base: str, latest: str, proposed: str) -> tuple[str, list[str]]:
    conflicts: list[str] = []
    bn, bb = split_body(base or ""); ln, lb = split_body(latest or ""); pn, pb = split_body(proposed or "")
    natural, conflict = three_way(bn, ln, pn)
    if conflict: conflicts.append("content.natural")
    bd, ld, pd = parse_block(bb), parse_block(lb), parse_block(pb)
    merged = copy.deepcopy(ld)
    for key in set(bd) | set(ld) | set(pd):
        value, c = three_way(bd.get(key), ld.get(key), pd.get(key))
        if c: conflicts.append(f"content.planner.{key}")
        else: merged[key] = value
    body = natural.rstrip()
    if merged: body = (body + "\n\n" if body else "") + render_block(merged)
    return body, conflicts


def merge_task(base: dict[str, Any], latest: dict[str, Any], proposed: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(latest); conflicts: list[str] = []
    fields = set(base) | set(latest) | set(proposed)
    for field in fields:
        if field in {"tags", "content"}: continue
        value, conflict = three_way(base.get(field), latest.get(field), proposed.get(field))
        if conflict: conflicts.append(field)
        else: merged[field] = value
    tags, tc = merge_tags(base.get("tags", []), latest.get("tags", []), proposed.get("tags", [])); merged["tags"] = tags; conflicts += tc
    content, cc = merge_content(base.get("content", ""), latest.get("content", ""), proposed.get("content", "")); merged["content"] = content; conflicts += cc
    if latest.get("completed") and not base.get("completed"):
        conflicts.append("completed_by_user_stop_planning")
    return {"merged": merged, "conflicts": sorted(set(conflicts)), "safe_to_write": not conflicts}


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--input", required=True); ap.add_argument("--output")
    args = ap.parse_args(); d = read_json(args.input); write_json(merge_task(d["base"], d["latest"], d["proposed"]), args.output)

if __name__ == "__main__": main()
