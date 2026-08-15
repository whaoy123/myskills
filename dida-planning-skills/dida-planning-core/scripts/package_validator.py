from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

SKILLS = [
    "dida-cli", "dida-task-capture", "dida-task-breakdown", "dida-task-estimator",
    "dida-daily-planner", "dida-task-progress", "dida-weekly-review", "dida-planning-profile",
    "dida-planning-memory"
]


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"): return {}
    end = text.find("\n---\n", 4)
    if end < 0: return {}
    out = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1); out[k.strip()] = v.strip()
    return out


def _manifest_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        parts = path.relative_to(root).parts
        if rel == "MANIFEST.sha256" or ".git" in parts or "__pycache__" in parts or path.suffix == ".pyc":
            continue
        if rel.startswith("dida-planning-core/state/") and rel != "dida-planning-core/state/.gitkeep":
            continue
        files[rel] = path
    return files


def validate_manifest(root: Path) -> list[str]:
    manifest = root / "MANIFEST.sha256"
    if not manifest.exists():
        return ["missing MANIFEST.sha256"]
    errors: list[str] = []
    entries: dict[str, str] = {}
    for line_no, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-fA-F]{64})\s+\./(.+)", line)
        if not match:
            errors.append(f"MANIFEST.sha256:{line_no}: malformed entry")
            continue
        digest, rel = match.group(1).lower(), match.group(2).replace("\\", "/")
        if rel in entries:
            errors.append(f"MANIFEST.sha256:{line_no}: duplicate {rel}")
            continue
        entries[rel] = digest

    files = _manifest_files(root)
    for rel in sorted(set(files) - set(entries)):
        errors.append(f"MANIFEST.sha256: missing entry {rel}")
    for rel in sorted(set(entries) - set(files)):
        errors.append(f"MANIFEST.sha256: missing file {rel}")
    for rel in sorted(set(entries) & set(files)):
        actual = hashlib.sha256(files[rel].read_bytes()).hexdigest()
        if actual != entries[rel]:
            errors.append(f"MANIFEST.sha256: hash mismatch {rel}")
    return errors


def validate(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []; warnings: list[str] = []; names = set()
    for skill in SKILLS:
        p = root / skill / "SKILL.md"
        if not p.exists(): errors.append(f"missing {p}"); continue
        text = p.read_text(encoding="utf-8"); fm = frontmatter(text)
        if fm.get("name") != skill: errors.append(f"{p}: name mismatch")
        if not fm.get("description"): errors.append(f"{p}: missing description")
        if fm.get("name") in names: errors.append(f"duplicate skill name {fm.get('name')}")
        names.add(fm.get("name"))
        lines = len(text.splitlines())
        if lines > 140: warnings.append(f"{p}: {lines} lines; consider reducing")
        for ref in re.findall(r'`(references/[^`]+\.md)`', text):
            if not (root / skill / ref).exists(): errors.append(f"{p}: missing reference {ref}")
        if not (root / skill / "agents" / "openai.yaml").exists(): warnings.append(f"{skill}: missing agents/openai.yaml")
    memory_assets = root / "dida-planning-memory" / "assets" / "memory-categories"
    expected_memory_assets = {
        "长期记忆｜项目规则.md", "长期记忆｜工具与环境.md",
        "长期记忆｜工作方式.md", "长期记忆｜通用约定.md"
    }
    if not memory_assets.exists():
        errors.append("missing memory category assets")
    else:
        missing = expected_memory_assets - {p.name for p in memory_assets.glob("*.md")}
        for name in sorted(missing): errors.append(f"missing memory category asset {name}")
    for doc in ["README.md", "REVIEW_REPORT.md", "SUBAGENT_REVIEW_PROMPT.md"]:
        if not (root / doc).exists(): errors.append(f"missing root document {doc}")
    errors.extend(validate_manifest(root))

    scripts = root / "dida-planning-core" / "scripts"
    for py in scripts.rglob("*.py"):
        try: compile(py.read_text(encoding="utf-8"), str(py), "exec")
        except Exception as exc: errors.append(f"compile {py}: {exc}")
    # Single source of truth guard
    forbidden = ["sqlite", "markdown stays the only source", "markdown-only"]
    for p in [root/s/"SKILL.md" for s in SKILLS]:
        if not p.exists(): continue
        low = p.read_text(encoding="utf-8").lower()
        for token in forbidden:
            if token in low: errors.append(f"{p}: forbidden legacy source-of-truth phrase {token}")
    return errors, warnings


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--root", required=True); args = ap.parse_args()
    errors, warnings = validate(Path(args.root).resolve())
    for w in warnings: print("WARNING:", w)
    for e in errors: print("ERROR:", e)
    print(f"Validated: {len(SKILLS)} skills; {len(errors)} errors; {len(warnings)} warnings")
    raise SystemExit(1 if errors else 0)

if __name__ == "__main__": main()
