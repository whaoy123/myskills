from __future__ import annotations

import importlib.util
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[1]
INIT = load_module("init_project", ROOT / "scripts" / "init_project.py")
VALIDATE = load_module("validate_state", ROOT / "scripts" / "validate_state.py")


def test_init_and_validate(tmp_path: Path):
    prestudy = INIT.init(tmp_path, ROOT / "templates" / "reports")
    state = prestudy / "research_state"

    assert (state / "search_log.csv").exists()
    assert (state / "pitfalls.yaml").exists()
    assert (prestudy / "reports" / "FINAL.md").exists()
    assert VALIDATE.validate(state) == []
