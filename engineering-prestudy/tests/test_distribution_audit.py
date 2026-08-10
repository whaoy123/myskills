from pathlib import Path

from scripts.audit_distribution import audit


def test_clean_skill_passes(tmp_path: Path):
    (tmp_path / "SKILL.md").write_text("safe skill", encoding="utf-8")
    assert audit(tmp_path) == []


def test_runtime_state_is_rejected(tmp_path: Path):
    runtime = tmp_path / ".prestudy"
    runtime.mkdir()
    (runtime / "project.yaml").write_text("schema_version: 1", encoding="utf-8")
    errors = audit(tmp_path)
    assert any("forbidden runtime path" in e for e in errors)
