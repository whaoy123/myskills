#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def section(path: Path, fallback: str) -> str:
    if not path.exists():
        return fallback
    text = path.read_text(encoding="utf-8").strip()
    return text if text else fallback


def build(project_root: Path) -> Path:
    base = project_root / ".prestudy"
    state = base / "research_state"
    reports = base / "reports"
    reports.mkdir(parents=True, exist_ok=True)

    project = load_yaml(state / "project.yaml")
    pitfalls = load_yaml(state / "pitfalls.yaml").get("items", [])
    open_questions = load_yaml(state / "open_questions.yaml").get("questions", [])
    plan = load_yaml(state / "project_plan.yaml").get("stages", [])
    handoff = load_yaml(state / "dida_handoff.yaml")

    important_pitfalls = [
        p for p in pitfalls
        if p.get("impact") in {"HIGH", "CRITICAL"} or p.get("action") == "BLOCKER"
    ]
    blocking_questions = [
        q for q in open_questions if q.get("impact") == "BLOCKING" and q.get("status") != "RESOLVED"
    ]

    lines = [
        f"# {project.get('title') or 'Engineering Prestudy'} — FINAL",
        "",
        "## 1. 当前目标",
        project.get("current_goal") or project.get("initial_goal") or "待补充。",
        "",
        "## 2. 当前理解",
        section(reports / "current_understanding.md", "尚未生成理解报告。"),
        "",
        "## 3. 现状、前辈实现与可借鉴内容",
        section(reports / "research_landscape.md", "尚未生成现状调研报告。"),
        "",
        "## 4. 必须注意的坑 / 风险",
    ]

    if important_pitfalls:
        for p in important_pitfalls:
            lines.append(
                f"- **{p.get('id')} {p.get('title')}**："
                f"{p.get('impact')} / {p.get('action')}；"
                f"建议：{p.get('mitigation') or '待补充'}"
            )
    else:
        lines.append("- 当前没有登记 HIGH/CRITICAL/BLOCKER 级注意事项。")

    lines += ["", "## 5. 推荐实施路线", section(reports / "implementation_plan.md", "尚未生成实施计划。")]

    lines += ["", "## 6. 剩余阻塞问题"]
    if blocking_questions:
        for q in blocking_questions:
            lines.append(f"- {q.get('id')}: {q.get('question')}")
    else:
        lines.append("- 无未解决的 BLOCKING 问题。")

    lines += ["", "## 7. 阶段与产出"]
    if plan:
        for stage in plan:
            outputs = "；".join(stage.get("outputs", [])) or "待补充"
            lines.append(f"- **{stage.get('id')} {stage.get('title')}**：{outputs}")
    else:
        lines.append("- 尚未形成 project_plan。")

    lines += ["", "## 8. Dida 交接状态", f"- status: `{handoff.get('status', 'DRAFT')}`"]
    lines.append(f"- work_packages: {len(handoff.get('work_packages', []))}")

    out = reports / "FINAL.md"
    out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("project_root", type=Path)
    args = p.parse_args()
    print(build(args.project_root))


if __name__ == "__main__":
    main()
