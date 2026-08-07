from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def read_json(path: str | None) -> Any:
    if path and path != "-":
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def write_json(value: Any, path: str | None = None) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False)
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def round_minutes(minutes: float) -> int:
    if minutes <= 0:
        return 0
    step = 5 if minutes < 90 else 15
    return max(step, int(round(minutes / step) * step))


NON_WORK_ROLES = {"config", "memory_category", "memory"}


def is_work_item(item: dict[str, Any]) -> bool:
    """Return false for configuration and durable-memory records."""
    return item.get("role") not in NON_WORK_ROLES
