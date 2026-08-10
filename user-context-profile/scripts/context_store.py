#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import yaml

FILES = {
    "profile": "profile.yaml",
    "knowledge": "knowledge.yaml",
    "preferences": "preferences.yaml",
    "meta": "context_meta.yaml",
}

DEFAULTS = {
    "profile": {"schema_version": 1, "identity": {}, "roles": [], "long_term_goals": [], "resources": {}, "constraints": []},
    "knowledge": {"schema_version": 1, "domains": {}},
    "preferences": {"schema_version": 1, "explanation": {"preferred": [], "avoid": []}, "response": {}, "research": {}},
    "meta": {"schema_version": 1, "initialized": True, "state": "PARTIAL", "sources": {}, "pending_promotions": []},
}


def default_root() -> Path:
    return Path.home() / ".prestudy" / "user-context"


def load_yaml(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return copy.deepcopy(default)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else copy.deepcopy(default)


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def init(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for key, filename in FILES.items():
        path = root / filename
        if not path.exists():
            save_yaml(path, DEFAULTS[key])


def load_unified(root: Path) -> dict[str, Any]:
    init(root)
    profile = load_yaml(root / FILES["profile"], DEFAULTS["profile"])
    knowledge = load_yaml(root / FILES["knowledge"], DEFAULTS["knowledge"])
    preferences = load_yaml(root / FILES["preferences"], DEFAULTS["preferences"])
    meta = load_yaml(root / FILES["meta"], DEFAULTS["meta"])
    return {"profile": profile, "knowledge": knowledge, "preferences": preferences, "meta": meta}


def set_domain(root: Path, domain: str, level: str, self_report: str, confidence: str) -> None:
    allowed = {"unknown", "beginner", "foundational", "intermediate", "advanced"}
    if level not in allowed:
        raise SystemExit(f"invalid level: {level}")
    data = load_yaml(root / FILES["knowledge"], DEFAULTS["knowledge"])
    domains = data.setdefault("domains", {})
    entry = domains.setdefault(domain, {})
    entry.update({"level": level, "self_report": self_report, "confidence": confidence})
    entry.setdefault("known", [])
    entry.setdefault("gaps", [])
    entry.setdefault("evidence", [])
    save_yaml(root / FILES["knowledge"], data)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=default_root())
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("load")
    sd = sub.add_parser("set-domain")
    sd.add_argument("domain")
    sd.add_argument("level")
    sd.add_argument("self_report")
    sd.add_argument("--confidence", default="high", choices=["high", "medium"])
    args = p.parse_args()
    if args.cmd == "init":
        init(args.root)
    elif args.cmd == "load":
        print(json.dumps(load_unified(args.root), ensure_ascii=False, indent=2))
    elif args.cmd == "set-domain":
        init(args.root)
        set_domain(args.root, args.domain, args.level, args.self_report, args.confidence)


if __name__ == "__main__":
    main()
