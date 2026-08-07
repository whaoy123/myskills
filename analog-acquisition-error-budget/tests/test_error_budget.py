import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "error_budget.py"
spec = importlib.util.spec_from_file_location("error_budget", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)


class ErrorBudgetTests(unittest.TestCase):
    def base_measurement(self):
        return {
            "name": "test",
            "value": 115.0,
            "unit": "V",
            "full_scale_input": 200.0,
            "temperature_reference_c": 25.0,
            "temperature_operating_c": 75.0,
            "frequency_hz": 400.0,
            "random_sigma_multiplier": 3.0,
            "calibration_mode": "none",
            "nodes": {"system_input": 1.0, "divider_output": 0.0035307, "adc_input": 0.0070614},
            "adc": {"bits": 16, "input_span_v": 4.096},
        }

    def test_percent_reading(self):
        row = mod.normalize_source(self.base_measurement(), {
            "name": "gain", "spec_type": "percent_reading", "value": 0.2,
            "combination": "systematic", "calibration_class": "gain"
        })
        self.assertAlmostEqual(row.input_error, 0.23, places=12)

    def test_local_offset_referral(self):
        row = mod.normalize_source(self.base_measurement(), {
            "name": "offset", "spec_type": "local_offset_v", "value": 0.0003,
            "node": "divider_output", "combination": "systematic", "calibration_class": "offset"
        })
        self.assertAlmostEqual(row.raw_input_error, 0.0003 / 0.0035307, places=12)
        self.assertAlmostEqual(row.input_error, 0.0003 / 0.0035307, places=12)

    def test_offset_removed_by_mean_before_rms(self):
        m = self.base_measurement()
        m["result_algorithm"] = "rms_mean_removed"
        row = mod.normalize_source(m, {
            "name": "offset", "spec_type": "local_offset_v", "value": 0.0003,
            "node": "divider_output", "combination": "systematic", "calibration_class": "offset"
        })
        self.assertGreater(row.raw_input_error, 0.08)
        self.assertEqual(row.input_error, 0.0)

    def test_offset_raw_rms_uses_square_sum(self):
        m = self.base_measurement()
        m["result_algorithm"] = "rms_raw_zero_mean_signal"
        row = mod.normalize_source(m, {
            "name": "offset", "spec_type": "input_referred_v", "value": 1.0,
            "error_role": "offset", "combination": "systematic", "calibration_class": "none"
        })
        self.assertAlmostEqual(row.input_error, math.sqrt(115**2 + 1) - 115, places=12)

    def test_lsb_referral(self):
        row = mod.normalize_source(self.base_measurement(), {
            "name": "inl", "spec_type": "lsb", "value": 2,
            "node": "adc_input", "combination": "systematic", "calibration_class": "none"
        })
        expected = 2 * (4.096 / 65536) / 0.0070614
        self.assertAlmostEqual(row.input_error, expected, places=12)

    def test_calibration_removes_gain_and_offset(self):
        m = self.base_measurement()
        m["calibration_mode"] = "two_point"
        result = mod.analyze({"measurement": m, "sources": [
            {"name":"gain","spec_type":"percent_reading","value":0.2,"combination":"systematic","calibration_class":"gain"},
            {"name":"offset","spec_type":"input_referred_v","value":0.1,"combination":"systematic","calibration_class":"offset"},
            {"name":"drift","spec_type":"input_referred_v","value":0.05,"combination":"systematic","calibration_class":"none"}
        ]})
        self.assertAlmostEqual(result["pre_calibration"]["systematic_worst_case"], 0.38)
        self.assertAlmostEqual(result["post_calibration"]["systematic_worst_case"], 0.05)

    def test_random_rss(self):
        m = self.base_measurement()
        result = mod.analyze({"measurement": m, "sources": [
            {"name":"n1","spec_type":"input_referred_v","value":0.03,"combination":"random","calibration_class":"none"},
            {"name":"n2","spec_type":"input_referred_v","value":0.04,"combination":"random","calibration_class":"none"}
        ]})
        self.assertAlmostEqual(result["pre_calibration"]["random_rms"], 0.05)
        self.assertAlmostEqual(result["pre_calibration"]["conservative_systematic_plus_k_sigma"], 0.15)

    def test_rc_attenuation(self):
        row = mod.normalize_source(self.base_measurement(), {
            "name":"rc","spec_type":"first_order_lowpass_attenuation","value":0,
            "frequency_hz":400,"cutoff_hz":6800,"combination":"systematic","calibration_class":"none"
        })
        h = 1 / math.sqrt(1 + (400/6800)**2)
        self.assertAlmostEqual(row.input_error, 115 * (1-h), places=12)


if __name__ == "__main__":
    unittest.main()
