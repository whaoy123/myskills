from __future__ import annotations

import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

START = "【Planner】"
END = "【/Planner】"
ALLOWED = {
    "role": {"project", "phase", "task", "block", "config", "memory_category", "memory"},
    "required_for_parent": {True, False},
    "progress": {0, 25, 50, 75, 90, 100},
    "date_semantics": {"hard_deadline", "execution_window", "target_date", "none"},
    "mobility": {"fixed", "protected", "movable"},
    "privacy": {"normal", "summary_only"},
    "estimate_confidence": {"low", "medium", "high"},
    "dependency_mode": {"all", "any"},
    "memory_scope": {"global", "project"},
    "memory_kind": {"project_rule", "tool_environment", "workflow", "convention"},
    "memory_source": {"explicit", "durable_fact", "confirmed_inference"},
    "memory_confidence": {"high", "medium"},
}
ORDER = [
    "schema", "role", "required_for_parent", "progress", "date_semantics", "mobility", "privacy",
    "estimate_confidence", "dependency_mode", "dependencies", "memory_scope", "memory_kind",
    "memory_source", "memory_confidence", "applies_to", "review_after", "supersedes"
]


def split_body(text: str) -> tuple[str, str | None]:
    start = text.find(START)
    if start < 0:
        return text.rstrip(), None
    end = text.find(END, start)
    if end < 0:
        raise ValueError("Planner block start exists without end marker")
    if text.find(START, start + len(START)) >= 0:
        raise ValueError("multiple Planner blocks are not allowed")
    natural = (text[:start] + text[end + len(END):]).strip()
    block = text[start + len(START):end].strip("\n")
    return natural, block


def _scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw in {"null", "None", "~"}: return None
    if raw in {"true", "false"}: return raw == "true"
    if re.fullmatch(r"-?\d+", raw): return int(raw)
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    return raw


def parse_block(block: str | None) -> OrderedDict[str, Any]:
    data: OrderedDict[str, Any] = OrderedDict()
    if not block:
        return data
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1; continue
        if not line.startswith(" ") and ":" in line:
            key, raw = line.split(":", 1)
            key = key.strip(); raw = raw.strip()
            if key == "dependencies":
                deps: list[dict[str, Any]] = []
                i += 1
                current: dict[str, Any] | None = None
                while i < len(lines):
                    dep_line = lines[i]
                    if dep_line and not dep_line.startswith(" "):
                        break
                    stripped = dep_line.strip()
                    if not stripped:
                        i += 1; continue
                    if stripped.startswith("-"):
                        if current: deps.append(current)
                        current = {}
                        rest = stripped[1:].strip()
                        if rest and ":" in rest:
                            k, v = rest.split(":", 1); current[k.strip()] = _scalar(v)
                    elif current is not None and ":" in stripped:
                        k, v = stripped.split(":", 1); current[k.strip()] = _scalar(v)
                    i += 1
                if current: deps.append(current)
                data[key] = deps
                continue
            data[key] = _scalar(raw)
        else:
            raise ValueError(f"unsupported Planner block line: {line!r}")
        i += 1
    return data


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema", 1) != 1:
        errors.append("schema must be 1")
    for key, allowed in ALLOWED.items():
        if key in data and data[key] not in allowed:
            errors.append(f"{key} has invalid value: {data[key]!r}")
    for idx, dep in enumerate(data.get("dependencies") or []):
        typ = dep.get("type")
        if typ not in {"finish_to_start", "start_to_start", "not_before", "external_wait"}:
            errors.append(f"dependencies[{idx}].type invalid")
        if dep.get("strength", "hard") not in {"hard", "soft"}:
            errors.append(f"dependencies[{idx}].strength invalid")
        if typ in {"finish_to_start", "start_to_start"} and not dep.get("task_id"):
            errors.append(f"dependencies[{idx}] requires task_id")
        if typ == "external_wait" and not (dep.get("task_id") or dep.get("external_ref")):
            errors.append(f"dependencies[{idx}] requires task_id or external_ref")
        if typ == "not_before" and not dep.get("not_before"):
            errors.append(f"dependencies[{idx}] requires not_before")
    return errors


def render_block(data: dict[str, Any]) -> str:
    ordered = list(ORDER) + [k for k in data if k not in ORDER]
    lines = [START]
    for key in ordered:
        if key not in data: continue
        value = data[key]
        if key == "dependencies":
            lines.append("dependencies:")
            for dep in value or []:
                first = True
                for dk, dv in dep.items():
                    prefix = "  - " if first else "    "
                    lines.append(f"{prefix}{dk}: {_format_scalar(dv)}")
                    first = False
            continue
        lines.append(f"{key}: {_format_scalar(value)}")
    lines.append(END)
    return "\n".join(lines)


def _format_scalar(value: Any) -> str:
    if value is None: return "null"
    if value is True: return "true"
    if value is False: return "false"
    return str(value)


def patch_body(text: str, patch: dict[str, Any]) -> str:
    natural, block = split_body(text)
    data = parse_block(block)
    if not data:
        data.update({
            "schema": 1, "role": "task", "progress": 0, "date_semantics": "none",
            "mobility": "movable", "privacy": "normal", "estimate_confidence": "low",
            "dependency_mode": "all", "dependencies": []
        })
    for key, value in patch.items():
        if value == "__DELETE__": data.pop(key, None)
        else: data[key] = value
    errors = validate(data)
    if errors: raise ValueError("; ".join(errors))
    return (natural.rstrip() + "\n\n" if natural else "") + render_block(data) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--patch-json")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--output")
    args = ap.parse_args()
    text = Path(args.input).read_text(encoding="utf-8")
    natural, block = split_body(text)
    data = parse_block(block)
    if args.validate:
        result = {"valid": not validate(data), "errors": validate(data), "natural_chars": len(natural), "planner": data}
        out = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        patch = json.loads(args.patch_json or "{}")
        out = patch_body(text, patch)
    if args.output: Path(args.output).write_text(out, encoding="utf-8")
    else: print(out, end="" if not args.validate else "\n")

if __name__ == "__main__":
    main()
