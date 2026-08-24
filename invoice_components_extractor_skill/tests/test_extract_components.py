#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

import openpyxl

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from extract_soldering_components import (
    aggregate_included,
    classify_component,
    classify_decision,
    export_outputs,
    extract_csv,
    extract_xlsx,
    is_soldering_component,
    parse_pdf_line,
)


class TestExtractComponents(unittest.TestCase):
    def test_three_state_decision(self):
        self.assertEqual(classify_decision("*电子元件*贴片电容", "CL21B104KBCNNNC")[0], "include")
        self.assertEqual(classify_decision("*电子元件*配送费", "")[0], "exclude")
        self.assertEqual(classify_decision("*日用杂品*绝缘手套", "1000V")[0], "exclude")
        self.assertEqual(classify_decision("*其他*组件", "ABC-123")[0], "review")

    def test_compatibility_helpers(self):
        self.assertTrue(is_soldering_component("*电子元件*电流传感器", "CC6937S8-5FB010"))
        self.assertFalse(is_soldering_component("*印制电路板*线路板", "Project Outputs"))
        cat, model, package, _ = classify_component("*电子元件*贴片电容", "CL21B104KBCNNNC 0805")
        self.assertEqual(cat, "电容")
        self.assertIn("0805", package)
        self.assertIn("CL21B104KBCNNNC", model)

    def test_pdf_line_parsing_keeps_review_instead_of_silent_drop(self):
        record = parse_pdf_line("*电子元件*未知组件 无法解析", "invoice.pdf", 1, 8)
        self.assertIsNotNone(record)
        self.assertEqual(record["decision"], "review")
        self.assertEqual(record["reason"], "pdf_line_parse_failed")

    def test_pdf_line_parsing_include(self):
        line = "*电子元件*贴片电容 CL21B104KBCNNNC 0805 个 10 0.10 1.00 13% 0.13"
        record = parse_pdf_line(line, "invoice.pdf", 1, 10)
        self.assertEqual(record["decision"], "include")
        self.assertEqual(record["qty"], 10.0)
        self.assertEqual(record["category"], "电容")

    def test_safe_aggregation(self):
        records = [
            {
                "decision": "include", "category": "电阻", "normalized_model": "R0805-10K", "package": "0805 (SMD)",
                "unit": "个", "qty": 10, "name": "贴片电阻", "source_file": "a.csv", "source_row": 2, "reason": "component_keyword:电阻",
            },
            {
                "decision": "include", "category": "电阻", "normalized_model": "R0805-10K", "package": "0805 (SMD)",
                "unit": "个", "qty": 5, "name": "贴片电阻", "source_file": "b.csv", "source_row": 3, "reason": "component_keyword:电阻",
            },
        ]
        merged = aggregate_included(records)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["qty"], 15)
        self.assertIn("a.csv", merged[0]["source"])
        self.assertIn("b.csv", merged[0]["source"])

    def test_csv_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invoice.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["项目名称", "规格型号", "数量", "单位"])
                writer.writerow(["贴片电容", "CL21B104KBCNNNC 0805", "20", "个"])
                writer.writerow(["配送费", "", "1", "次"])
            records, warnings = extract_csv(path)
            self.assertFalse(warnings)
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["decision"], "include")
            self.assertEqual(records[1]["decision"], "exclude")

    def test_xlsx_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invoice.xlsx"
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(["商品名称", "规格型号", "数量", "单位"])
            ws.append(["螺钉式接线端子", "DB910-9.52-4P-GN-S", 4, "个"])
            wb.save(path)

            records, warnings = extract_xlsx(path)
            self.assertFalse(warnings)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["decision"], "include")
            self.assertEqual(records[0]["category"], "接线端子")

    def test_export_and_xlsx_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "input"
            output_dir = root / "output"
            input_dir.mkdir()
            csv_path = input_dir / "invoice.csv"
            with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["项目名称", "规格型号", "数量", "单位"])
                writer.writerow(["贴片电阻", "R0805-10K 0805", "10", "个"])
                writer.writerow(["未知组件", "ABC", "2", "个"])

            report = export_outputs(input_dir, output_dir)
            self.assertTrue(report["xlsx_validation"]["pass"])
            self.assertEqual(report["counts"]["review_records"], 1)
            self.assertTrue((output_dir / "components.xlsx").exists())
            self.assertTrue((output_dir / "review.csv").exists())
            self.assertTrue((output_dir / "normalized_records.csv").exists())


if __name__ == "__main__":
    unittest.main()
