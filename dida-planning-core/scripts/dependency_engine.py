from __future__ import annotations

import argparse
from datetime import datetime
from typing import Any

from common import read_json, write_json


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def evaluate(task: dict[str, Any], tasks: dict[str, dict[str, Any]], now: datetime) -> dict[str, Any]:
    deps = task.get("dependencies") or []
    results = []
    for dep in deps:
        typ = dep.get("type")
        strength = dep.get("strength", "hard")
        ready = False
        reason = ""
        if typ == "not_before":
            threshold = _dt(dep["not_before"])
            ready = now >= threshold
            reason = f"not before {threshold.isoformat()}"
        else:
            target = tasks.get(str(dep.get("task_id"))) if dep.get("task_id") else None
            if typ in {"finish_to_start", "start_to_start"} and target is None:
                ready = False; reason = "dependency task not found"
            elif typ == "finish_to_start":
                ready = bool(target.get("completed")); reason = "dependency must be completed"
            elif typ == "start_to_start":
                ready = bool(target.get("started") or target.get("completed") or target.get("progress", 0) > 0); reason = "dependency must be started"
            elif typ == "external_wait":
                if dep.get("task_id"):
                    ready = bool(target and (target.get("completed") or dep.get("resolved")))
                else:
                    ready = bool(dep.get("resolved"))
                reason = f"external event unresolved: {dep.get('external_ref') or dep.get('task_id')}"
            else:
                reason = "unsupported dependency type"
        results.append({**dep, "ready": ready, "reason": None if ready else reason, "blocking": (not ready and strength == "hard")})
    mode = task.get("dependency_mode", "all")
    if not results: ready = True
    elif mode == "any": ready = any(r["ready"] for r in results)
    else: ready = all(r["ready"] or r.get("strength") == "soft" for r in results)
    return {"task_id": task.get("id"), "ready": ready, "mode": mode, "dependencies": results, "warnings": [r for r in results if not r["ready"] and r.get("strength") == "soft"]}


def cycle_check(edges: list[dict[str, str]]) -> dict[str, Any]:
    graph: dict[str, list[str]] = {}
    for e in edges:
        graph.setdefault(e["source"], []).append(e["target"])
    visiting: set[str] = set(); visited: set[str] = set(); cycle: list[str] = []
    def dfs(node: str, path: list[str]) -> bool:
        if node in visiting:
            cycle.extend(path[path.index(node):] + [node]); return True
        if node in visited: return False
        visiting.add(node)
        for nxt in graph.get(node, []):
            if dfs(nxt, path + [nxt]): return True
        visiting.remove(node); visited.add(node); return False
    for node in graph:
        if dfs(node, [node]): return {"acyclic": False, "cycle": cycle}
    return {"acyclic": True, "cycle": []}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--cycle-check", action="store_true")
    args = ap.parse_args()
    data = read_json(args.input)
    if args.cycle_check:
        write_json(cycle_check(data["edges"]))
    else:
        now = _dt(data.get("now") or datetime.now().astimezone().isoformat())
        task_map = {str(t["id"]): t for t in data.get("tasks", [])}
        write_json(evaluate(data["task"], task_map, now))

if __name__ == "__main__":
    main()
