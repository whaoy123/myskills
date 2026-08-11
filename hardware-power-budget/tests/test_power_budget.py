import importlib.util
import math
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "power_budget.py"
spec = importlib.util.spec_from_file_location("power_budget", MODULE_PATH)
pb = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pb
spec.loader.exec_module(pb)


def test_current_board_style_budget():
    data = {
        "design_margin_percent": 30,
        "rails": [
            {"name": "+5_SEC", "voltage_v": 5},
            {"name": "+15_SEC", "voltage_v": 15},
            {"name": "-15_SEC", "voltage_v": -15},
            {"name": "+12_PRI_POR", "voltage_v": 12},
            {"name": "+12_PRI_Field", "voltage_v": 12},
        ],
        "loads": [
            {"reference": "U1-U15", "component": "AMC3330", "quantity": 15, "rail": "+5_SEC", "current_typ_a": 0.0285, "current_max_a": 0.041, "source": "TI"},
            {"reference": "U16", "component": "AMC3302", "quantity": 1, "rail": "+5_SEC", "current_typ_a": 0.0275, "current_max_a": 0.04, "source": "TI"},
            {"reference": "U17-U20", "component": "ISO224 low side", "quantity": 4, "rail": "+5_SEC", "current_typ_a": 0.0078, "current_max_a": 0.0099, "source": "TI"},
            {"reference": "U21-U40", "component": "OPA197", "quantity": 20, "rail": "+15_SEC", "current_typ_a": 0.001, "current_max_a": 0.0015, "source": "TI"},
            {"reference": "U21-U40", "component": "OPA197", "quantity": 20, "rail": "-15_SEC", "current_typ_a": 0.001, "current_max_a": 0.0015, "source": "TI"},
            {"reference": "U17-U19", "component": "ISO224 high side", "quantity": 3, "rail": "+12_PRI_POR", "current_typ_a": 0.0061, "current_max_a": 0.0078, "source": "TI"},
            {"reference": "U20", "component": "ISO224 high side", "quantity": 1, "rail": "+12_PRI_Field", "current_typ_a": 0.0061, "current_max_a": 0.0078, "source": "TI"},
        ],
    }
    result = pb.compute(data)
    rails = {r["name"]: r for r in result["rails"]}
    assert math.isclose(rails["+5_SEC"]["budget_current_a"], 0.6946, rel_tol=1e-12)
    assert math.isclose(rails["+5_SEC"]["budget_power_w"], 3.473, rel_tol=1e-12)
    assert math.isclose(rails["+5_SEC"]["minimum_design_current_a"], 0.90298, rel_tol=1e-12)
    assert math.isclose(rails["+15_SEC"]["budget_current_a"], 0.03, rel_tol=1e-12)
    assert math.isclose(rails["-15_SEC"]["budget_power_w"], 0.45, rel_tol=1e-12)
    assert math.isclose(rails["+12_PRI_POR"]["budget_current_a"], 0.0234, rel_tol=1e-12)
    assert math.isclose(rails["+12_PRI_Field"]["budget_current_a"], 0.0078, rel_tol=1e-12)
    assert math.isclose(result["summary"]["root_budget_power_w"], 4.7474, rel_tol=1e-12)


def test_missing_max_makes_budget_incomplete():
    data = {
        "rails": [{"name": "+5V", "voltage_v": 5}],
        "loads": [{"reference": "U1", "component": "X", "quantity": 1, "rail": "+5V", "current_typ_a": 0.1, "source": "datasheet"}],
    }
    result = pb.compute(data)
    assert result["rails"][0]["budget_current_a"] is None
    assert result["summary"]["guarantee_complete"] is False


def test_dc_dc_backpropagation():
    data = {
        "rails": [
            {"name": "VIN", "voltage_v": 28},
            {"name": "+5V", "voltage_v": 5},
        ],
        "loads": [{"reference": "U1", "component": "load", "quantity": 1, "rail": "+5V", "current_typ_a": 0.5, "current_max_a": 1.0, "source": "datasheet"}],
        "converters": [{"name": "D1", "kind": "dc_dc", "input_rail": "VIN", "output_rails": ["+5V"], "efficiency_typ": 0.9, "efficiency_min": 0.8}],
    }
    result = pb.compute(data)
    rails = {r["name"]: r for r in result["rails"]}
    assert math.isclose(rails["VIN"]["budget_current_a"], 5 / 0.8 / 28, rel_tol=1e-12)
    assert math.isclose(result["converters"][0]["dissipation_w"], 1.25, rel_tol=1e-12)
