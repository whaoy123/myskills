from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def dump_yaml(path: Path, data: dict):
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def setup_scenario(tmp_path: Path, kind: str, pitfall_id: str, pitfall_title: str):
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "init_project.py"), str(tmp_path)],
        check=True,
    )
    base = tmp_path / ".prestudy"
    state = base / "research_state"

    project = yaml.safe_load((state / "project.yaml").read_text(encoding="utf-8"))
    project.update({
        "project_id": f"TEST-{kind.upper()}",
        "title": f"{kind} prestudy",
        "initial_goal": f"research {kind}",
        "current_goal": f"choose a practical {kind} route",
        "current_stage": "DESIGN_PLAN",
    })
    dump_yaml(state / "project.yaml", project)

    saturation = {
        "mechanism_understood": True,
        "landscape_known": True,
        "predecessor_known_or_not_applicable": True,
        "evidence_adequate": True,
        "tradeoffs_visible": True,
        "blocking_unknowns_handled": True,
        "low_marginal_value": True,
    }
    dump_yaml(state / "research_questions.yaml", {
        "schema_version": 1,
        "questions": [{
            "id": "RQ001",
            "question": f"How should {kind} be implemented?",
            "status": "SATURATED",
            "saturation": saturation,
        }],
    })

    with (state / "search_log.csv").open("a", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerow([
            "SEARCH001", "RQ001", "2026-08-10T12:00:00+08:00", "snowball",
            f"{kind} implementation pitfalls", "web/github/papers",
            "No materially new route found", "false", "false", "stop",
        ])

    with (state / "sources.csv").open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "S001", "official", "Reference source", "Authority", "2026",
            "https://example.invalid/ref", "library/other/reference.txt", "L1",
            "HIGH", "HIGH", "authoritative reference", "HIGH", "RETAINED",
            "REFERENCE", "",
        ])
        writer.writerow([
            "S002", "implementation", "Implementation source", "Predecessor", "2026",
            "https://example.invalid/impl", "library/other/implementation.txt", "L1",
            "HIGH", "MEDIUM", "representative predecessor", "HIGH", "RETAINED",
            "IMPLEMENTATION", "",
        ])

    for sid, filename in [("S001", "reference.txt"), ("S002", "implementation.txt")]:
        (base / "library" / "other" / filename).write_text("fixture", encoding="utf-8")
        (base / "notes" / f"{sid}.md").write_text(
            "# Reading guide\n\nWhy selected.\nWhat to read first.\n", encoding="utf-8"
        )

    (state / "evidence.jsonl").write_text(
        json.dumps({
            "id": "F001",
            "type": "FACT",
            "statement": "Representative fact",
            "source_id": "S001",
            "locator": "section 1",
            "confidence": "HIGH",
        }, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    dump_yaml(state / "pitfalls.yaml", {
        "schema_version": 1,
        "items": [{
            "id": pitfall_id,
            "title": pitfall_title,
            "category": kind,
            "impact": "HIGH",
            "action": "DESIGN_CONSTRAINT",
            "status": "MITIGATED",
            "why_it_happens": "Common predecessor failure mode",
            "consequence": "Rework or failure",
            "mitigation": "Apply explicit constraint and verify it",
            "verification": "Review/test before stage completion",
            "evidence": ["F001"],
        }],
    })

    dump_yaml(state / "decisions.yaml", {
        "schema_version": 1,
        "decisions": [{
            "id": "D001",
            "decision": f"Use representative {kind} route",
            "status": "CONFIRMED",
            "evidence": ["F001"],
        }],
    })

    dump_yaml(state / "project_plan.yaml", {
        "schema_version": 1,
        "revision": 1,
        "stages": [{
            "id": "STAGE-01",
            "title": "Implement prototype",
            "objective": "Build a safe representative prototype",
            "outputs": ["prototype", "verification record"],
            "acceptance": ["pitfall mitigation verified"],
            "dependencies": [],
            "pitfalls": [pitfall_id],
            "design_constraints": [{"pitfall_id": pitfall_id, "constraint": "apply mitigation"}],
        }],
    })

    dump_yaml(state / "dida_handoff.yaml", {
        "schema_version": 1,
        "source_plan_revision": 1,
        "status": "DRAFT",
        "approval_required": True,
        "work_packages": [{
            "id": "WP001",
            "stage": "STAGE-01",
            "title": "Build prototype",
            "expected_outputs": ["prototype", "verification record"],
            "acceptance": ["pitfall mitigation verified"],
            "dependencies": [],
            "pitfall_ids": [pitfall_id],
        }],
    })
    return state


def run_audit(tmp_path: Path):
    state = tmp_path / ".prestudy" / "research_state"
    return subprocess.run(
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


def test_high_voltage_hardware_scenario(tmp_path: Path):
    setup_scenario(tmp_path, "hardware", "PIT-HV-001", "Creepage/clearance may be insufficient")
    result = run_audit(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    final_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_final.py"), str(tmp_path)],
        text=True,
        capture_output=True,
    )
    assert final_result.returncode == 0, final_result.stdout + final_result.stderr
    final_text = (tmp_path / ".prestudy" / "reports" / "FINAL.md").read_text(encoding="utf-8")
    assert "Creepage/clearance may be insufficient" in final_text


def test_rtl_scenario(tmp_path: Path):
    setup_scenario(tmp_path, "rtl", "PIT-RTL-001", "CDC assumption may fail in hardware")
    result = run_audit(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_algorithm_scenario(tmp_path: Path):
    setup_scenario(tmp_path, "algorithm", "PIT-ALG-001", "Paper result may depend on hidden preprocessing")
    result = run_audit(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
