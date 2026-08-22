import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_wiring_table.py"

class WiringTableTest(unittest.TestCase):
    def test_board_pin_is_resolved_from_ad(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            inp, out = root / "input", root / "output"
            inp.mkdir()
            (inp / "ad_pin_net.csv").write_text("BoardConnector,BoardPin,NetName\nU1,7,POR_A\nU1,8,POR_B\n", encoding="utf-8")
            (inp / "external_pinout.csv").write_text("SheetName,CableEnd,CablePin,NetName,TargetBoardConnector,BoardPinHint,CableConnectorModel,Gender,MatesTo\nAVRplus方向,L1,1,POR_A,U1,,MODEL-A,母头,AVRplus\nAVRplus方向,L1,2,POR_B,U1,,MODEL-A,母头,AVRplus\n", encoding="utf-8")
            (inp / "signal_catalog.csv").write_text("NetName,SignalDefinition,WireType,ElectricalAttribute,Include\nPOR_A,POR Phase A,0.5,115Vac,yes\nPOR_B,POR Phase B,0.5,115Vac,yes\n", encoding="utf-8")
            cp = subprocess.run([sys.executable, str(SCRIPT), str(inp), str(out)], capture_output=True, text=True)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            with (out / "normalized_connections.csv").open("r", encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]["CablePin"], "1")
            self.assertEqual(rows[0]["BoardPin"], "7")
            self.assertEqual(rows[1]["CablePin"], "2")
            self.assertEqual(rows[1]["BoardPin"], "8")
            self.assertIn("PASS", (out / "validation_report.md").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
