from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_dida_bridge_requires_approval_and_omits_schedule(tmp_path: Path):
    handoff = tmp_path / "dida_handoff.yaml"
    data = {
        "schema_version": 1,
        "source_plan_revision": 1,
        "status": "DRAFT",
        "approval_required": True,
        "work_packages": [{
            "id": "WP001",
            "stage": "STAGE-01",
            "title": "Check creepage",
            "expected_outputs": ["review record"],
            "acceptance": ["minimum spacing verified"],
            "dependencies": [],
            "pitfall_ids": ["PIT-001"],
        }],
    }
    handoff.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    output = tmp_path / "bridge.jsonl"

    blocked = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_dida_bridge.py"), str(handoff), str(output)],
        text=True,
        capture_output=True,
    )
    assert blocked.returncode != 0

    data["status"] = "APPROVED"
    handoff.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    allowed = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_dida_bridge.py"), str(handoff), str(output)],
        text=True,
        capture_output=True,
    )
    assert allowed.returncode == 0, allowed.stdout + allowed.stderr

    row = json.loads(output.read_text(encoding="utf-8").strip())
    assert row["estimated_duration"] is None
    assert row["date"] is None
    assert row["priority"] is None
    assert row["requires_dida_breakdown"] is True
    assert row["requires_dida_estimation"] is True
