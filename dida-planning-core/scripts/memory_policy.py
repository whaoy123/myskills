from __future__ import annotations

import argparse
import json
from typing import Any

MEMORY_OWNERS = {"memory", "profile", "task", "estimation"}


def decide(candidate: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic policy decision after semantic owner classification.

    Input booleans are supplied by the calling skill after interpreting the user statement.
    This function intentionally does not infer sensitive categories from raw text.
    """
    owner = candidate.get("owner", "memory")
    if owner not in MEMORY_OWNERS:
        raise ValueError(f"invalid owner: {owner}")

    if candidate.get("explicit_forget"):
        return {"decision": "forget", "owner": owner, "reason": "explicit_forget"}

    if owner != "memory":
        return {"decision": "route", "owner": owner, "reason": "owned_elsewhere"}

    if candidate.get("explicit_save"):
        return {
            "decision": "save",
            "owner": owner,
            "reason": "explicit_save",
            "minimize": bool(candidate.get("sensitive")),
        }

    if candidate.get("from_transform") or candidate.get("temporary") or candidate.get("trivial"):
        return {"decision": "skip", "owner": owner, "reason": "not_durable_memory"}

    if candidate.get("sensitive"):
        return {"decision": "ask", "owner": owner, "reason": "sensitive_without_explicit_request"}

    if candidate.get("inferred") or candidate.get("conflict") or not candidate.get("stable", False):
        return {"decision": "ask", "owner": owner, "reason": "needs_confirmation"}

    if candidate.get("future_useful", False) and candidate.get("directly_stated", False):
        return {"decision": "save", "owner": owner, "reason": "durable_future_useful", "minimize": False}

    return {"decision": "skip", "owner": owner, "reason": "insufficient_future_value"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="JSON object or @path")
    args = ap.parse_args()
    raw = args.json
    if raw.startswith("@"):
        data = json.load(open(raw[1:], encoding="utf-8"))
    else:
        data = json.loads(raw)
    print(json.dumps(decide(data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
