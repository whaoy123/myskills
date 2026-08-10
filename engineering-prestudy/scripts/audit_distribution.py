#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

FORBIDDEN_PARTS = {".prestudy", "user-context", "research_state", "library", "reports"}
TEXT_EXTS = {".md", ".yaml", ".yml", ".json", ".jsonl", ".csv", ".py", ".txt"}
SUSPICIOUS = [
    re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\s]+", re.I),
    re.compile(r"/home/[^/\s]+/"),
    re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*['\"]?[^\s'\"]+"),
]


def audit(root: Path) -> list[str]:
    errors: list[str] = []
    for p in root.rglob("*"):
        rel = p.relative_to(root)
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            errors.append(f"forbidden runtime path: {rel}")
            continue
        if p.is_file() and p.suffix.lower() in TEXT_EXTS:
            text = p.read_text(encoding="utf-8", errors="ignore")
            for rx in SUSPICIOUS:
                if rx.search(text):
                    errors.append(f"suspicious private/runtime content: {rel}")
                    break
    return errors


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("skill_root", type=Path)
    args = p.parse_args()
    errors = audit(args.skill_root)
    if errors:
        print("FAIL")
        for e in errors:
            print(f"- {e}")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
