from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

SKILLS = [
    "dida-manager", "dida-cli", "dida-task-capture", "dida-task-breakdown", "dida-task-estimator",
    "dida-weekly-delivery", "dida-task-progress", "dida-weekly-review", "dida-planning-profile",
    "dida-planning-memory"
]


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
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


def _manifest_digest(path: Path) -> str:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        canonical = data
    else:
        # Canonicalize text to CRLF before hashing so the manifest is stable
        # across Git/Windows/Linux checkout line-ending policies.
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        canonical = text.replace("\n", "\r\n").encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


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
        actual = _manifest_digest(files[rel])
        if actual != entries[rel]:
            errors.append(f"MANIFEST.sha256: hash mismatch {rel}")
    return errors


def validate(root: Path, *, strict_manifest: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    names: set[str] = set()

    for skill in SKILLS:
        p = root / skill / "SKILL.md"
        if not p.exists():
            errors.append(f"missing {p}")
            continue
        text = p.read_text(encoding="utf-8")
        fm = frontmatter(text)
        if fm.get("name") != skill:
            errors.append(f"{p}: name mismatch")
        if not fm.get("description"):
            errors.append(f"{p}: missing description")
        if fm.get("name") in names:
            errors.append(f"duplicate skill name {fm.get('name')}")
        names.add(fm.get("name"))
        lines = len(text.splitlines())
        if lines > 140:
            warnings.append(f"{p}: {lines} lines; consider reducing")
        for ref in re.findall(r'`(references/[^`]+\.md)`', text):
            if not (root / skill / ref).exists():
                errors.append(f"{p}: missing reference {ref}")
        if not (root / skill / "agents" / "openai.yaml").exists():
            warnings.append(f"{skill}: missing agents/openai.yaml")

    memory_assets = root / "dida-planning-memory" / "assets" / "memory-categories"
    expected_memory_assets = {
        "长期记忆｜项目规则.md", "长期记忆｜工具与环境.md",
        "长期记忆｜工作方式.md", "长期记忆｜通用约定.md"
    }
    if not memory_assets.exists():
        errors.append("missing memory category assets")
    else:
        missing = expected_memory_assets - {p.name for p in memory_assets.glob("*.md")}
        for name in sorted(missing):
            errors.append(f"missing memory category asset {name}")

    for doc in ["README.md", "REVIEW_REPORT.md", "SUBAGENT_REVIEW_PROMPT.md"]:
        if not (root / doc).exists():
            errors.append(f"missing root document {doc}")

    # New templates must not reintroduce the retired scheduling metadata.
    scheduling_template_roots = [
        root / "dida-planning-profile" / "assets" / "config-notes",
        root / "dida-planning-memory" / "assets" / "memory-categories",
    ]
    for folder in scheduling_template_roots:
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for retired in ("mobility:", "date_semantics: execution_window"):
                if retired in text:
                    errors.append(f"{path}: retired scheduling metadata {retired!r}")

    manifest_issues = validate_manifest(root)
    if strict_manifest:
        errors.extend(manifest_issues)
    else:
        warnings.extend(f"release manifest drift: {issue}" for issue in manifest_issues)

    scripts = root / "dida-planning-core" / "scripts"
    for py in scripts.rglob("*.py"):
        try:
            compile(py.read_text(encoding="utf-8"), str(py), "exec")
        except Exception as exc:
            errors.append(f"compile {py}: {exc}")

    # Guard against the old architecture where a local shadow store was treated
    # as the business source of truth. Mentioning SQLite/Markdown as technology is
    # fine; claiming it is authoritative is not.
    forbidden_patterns = [
        r"sqlite.{0,40}(唯一|权威|source of truth)",
        r"(唯一|权威|source of truth).{0,40}sqlite",
        r"markdown stays the only source",
        r"markdown-only",
        r"从本地\s*sqlite\s*数据库.*(直接呈现|作为真值|读取当前任务)",
    ]
    for p in [root / s / "SKILL.md" for s in SKILLS]:
        if not p.exists():
            continue
        low = p.read_text(encoding="utf-8").lower()
        for pattern in forbidden_patterns:
            if re.search(pattern, low, flags=re.IGNORECASE):
                errors.append(f"{p}: forbidden legacy source-of-truth phrase matching {pattern!r}")

    return errors, warnings


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument(
        "--strict-manifest",
        action="store_true",
        help="Treat MANIFEST.sha256 drift as an error. Use for release/package integrity checks.",
    )
    args = ap.parse_args()

    errors, warnings = validate(Path(args.root).resolve(), strict_manifest=args.strict_manifest)
    for warning in warnings:
        print("WARNING:", warning)
    for error in errors:
        print("ERROR:", error)
    print(f"Validated: {len(SKILLS)} skills; {len(errors)} errors; {len(warnings)} warnings")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
