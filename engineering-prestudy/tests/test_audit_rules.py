from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_retained_artifact_budget_enforced(tmp_path: Path):
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "init_project.py"), str(tmp_path)],
        check=True,
    )
    state = tmp_path / ".prestudy" / "research_state"
    with (state / "sources.csv").open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        for i in range(3):
            writer.writerow([
                f"S{i+1:03d}", "paper", f"Source {i+1}", "Publisher", "2026",
                "https://example.invalid", f"library/other/s{i}.txt", "L1",
                "HIGH", "HIGH", "useful", "HIGH", "RETAINED",
                "EXCEPTION" if i == 2 else "REFERENCE",
                "third source needed" if i == 2 else "",
            ])
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_state.py"), str(state)],
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert "exceeds budget" in result.stdout


def test_approved_handoff_blocked_by_unresolved_blocker(tmp_path: Path):
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "init_project.py"), str(tmp_path)],
        check=True,
    )
    state = tmp_path / ".prestudy" / "research_state"

    project = yaml.safe_load((state / "project.yaml").read_text(encoding="utf-8"))
    project["current_stage"] = "DESIGN_PLAN"
    (state / "project.yaml").write_text(
        yaml.safe_dump(project, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    pitfalls = {
        "schema_version": 1,
        "items": [{
            "id": "PIT-001",
            "title": "Unknown maximum voltage",
            "category": "electrical_safety",
            "impact": "CRITICAL",
            "action": "BLOCKER",
            "status": "OPEN",
            "mitigation": "Confirm maximum voltage from primary documentation",
            "verification": "Documented limit available",
            "evidence": ["F001"],
        }],
    }
    (state / "pitfalls.yaml").write_text(
        yaml.safe_dump(pitfalls, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    plan = {
        "schema_version": 1,
        "revision": 1,
        "stages": [{
            "id": "STAGE-01",
            "title": "Design",
            "objective": "Design",
            "outputs": [],
            "acceptance": [],
            "dependencies": [],
            "pitfalls": ["PIT-001"],
        }],
    }
    (state / "project_plan.yaml").write_text(
        yaml.safe_dump(plan, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    handoff = {
        "schema_version": 1,
        "source_plan_revision": 1,
        "status": "APPROVED",
        "approval_required": True,
        "work_packages": [],
    }
    (state / "dida_handoff.yaml").write_text(
        yaml.safe_dump(handoff, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    (state / "evidence.jsonl").write_text(
        '{"id":"F001","type":"FACT","statement":"unknown","source_id":"S001","locator":"x"}\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "prestudy_audit.py"),
            str(state),
            "--project-root",
            str(tmp_path),
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode != 0
    assert "blocker pitfall" in result.stdout
