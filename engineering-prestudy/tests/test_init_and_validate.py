from pathlib import Path

from scripts.init_project import init
from scripts.validate_state import validate


def test_init_creates_valid_state(tmp_path: Path):
    base = init(tmp_path / "project")
    state = base / "research_state"
    assert validate(state) == []
    assert (base / "library" / "repos").is_dir()
    assert (base / "reports").is_dir()


def test_invalid_stage_is_rejected(tmp_path: Path):
    base = init(tmp_path / "project")
    project = base / "research_state" / "project.yaml"
    text = project.read_text(encoding="utf-8")
    project.write_text(text.replace("current_stage: UNDERSTAND", "current_stage: INVALID"), encoding="utf-8")
    errors = validate(base / "research_state")
    assert any("invalid project current_stage" in e for e in errors)
