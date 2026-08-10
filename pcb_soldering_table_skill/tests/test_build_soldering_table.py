import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_soldering_table.py"

class SolderingTableTest(unittest.TestCase):
    def test_counts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            inp, out = root / "input", root / "output"
            inp.mkdir()
            (inp / "bom.csv").write_text("Designator,Model,Footprint\nR1,100R,R0805\nR2,100R,R0805\nJ1,DB44,DB44\n", encoding="utf-8")
            (inp / "component_rules.csv").write_text("MatchField,MatchValue,DisplayPackage,MountType,PinsPerPart,FixedPinsPerPart,Include,Notes\nFootprint,R0805,0805,SMD,2,0,yes,\nModel,DB44,DB44公头,THT,44,2,yes,\n", encoding="utf-8")
            cp = subprocess.run([sys.executable, str(SCRIPT), str(inp), str(out)], capture_output=True, text=True)
            self.assertEqual(cp.returncode, 0, cp.stderr)
            report = (out / "validation_report.md").read_text(encoding="utf-8")
            self.assertIn("SMD solder joints: 4", report)
            self.assertIn("THT solder joints: 46", report)
            self.assertIn("Total solder joints: 50", report)

if __name__ == "__main__":
    unittest.main()
