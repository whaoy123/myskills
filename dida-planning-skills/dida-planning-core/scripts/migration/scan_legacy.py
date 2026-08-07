from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

U_RE = re.compile(r"#U([0-9A-Fa-f]{4})")


def decode_name(value: str) -> str:
    return U_RE.sub(lambda m: chr(int(m.group(1), 16)), value)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3: return {}, text
    data: dict[str, Any] = {}
    for line in parts[1].splitlines():
        if ":" not in line: continue
        k, v = line.split(":", 1); v = v.strip()
        if v in {"null", ""}: val: Any = None
        elif v in {"true", "false"}: val = v == "true"
        else:
            try: val = int(v)
            except ValueError: val = v.strip('"\'')
        data[k.strip()] = val
    return data, parts[2].lstrip()


def scan(root: Path) -> dict[str, Any]:
    records = []
    for path in root.rglob("*.md"):
        rel = "/".join(decode_name(p) for p in path.relative_to(root).parts)
        # Infrastructure intentionally excluded
        if any(x in rel for x in ["快照/", "会话/", "审计/", "日计划/", "周计划/", "skill/"]):
            continue
        try: text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        fm, body = parse_frontmatter(text)
        typ = fm.get("type")
        if typ not in {"task", "project", "recurring-rule", "preference", "estimation-calibration", "memory"}:
            continue
        records.append({"source_path": str(path), "decoded_path": rel, "type": typ, "frontmatter": fm, "body": body[:10000]})
    counts: dict[str, int] = {}
    for r in records: counts[r["type"]] = counts.get(r["type"], 0) + 1
    return {"source_root": str(root), "counts": counts, "records": records, "writes_performed": False}


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--output", required=True)
    args = ap.parse_args(); result = scan(Path(args.root)); Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"); print(json.dumps(result["counts"], ensure_ascii=False))

if __name__ == "__main__": main()
