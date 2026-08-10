from pathlib import Path

from scripts.context_store import init, load_unified, set_domain


def test_init_and_domain(tmp_path: Path):
    root = tmp_path / "ctx"
    init(root)
    set_domain(root, "verilog", "intermediate", "能独立写项目", "high")
    data = load_unified(root)
    assert data["knowledge"]["domains"]["verilog"]["level"] == "intermediate"
    assert data["knowledge"]["domains"]["verilog"]["self_report"] == "能独立写项目"
