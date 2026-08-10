from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "audit_distribution", ROOT / "scripts" / "audit_distribution.py"
)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
audit = module.audit


def test_clean_skill_passes(tmp_path: Path):
    (tmp_path / "SKILL.md").write_text("safe skill", encoding="utf-8")
    assert audit(tmp_path) == []


def test_templates_reports_are_allowed(tmp_path: Path):
    reports = tmp_path / "templates" / "reports"
    reports.mkdir(parents=True)
    (reports / "FINAL.md").write_text("# template", encoding="utf-8")
    assert audit(tmp_path) == []


def test_runtime_state_is_rejected(tmp_path: Path):
    runtime = tmp_path / ".prestudy"
    runtime.mkdir()
    (runtime / "project.yaml").write_text("schema_version: 1", encoding="utf-8")
    errors = audit(tmp_path)
    assert any("forbidden runtime path" in e for e in errors)


def test_top_level_runtime_reports_are_rejected(tmp_path: Path):
    runtime = tmp_path / "reports"
    runtime.mkdir()
    (runtime / "FINAL.md").write_text("real user report", encoding="utf-8")
    errors = audit(tmp_path)
    assert any("forbidden runtime path" in e for e in errors)
