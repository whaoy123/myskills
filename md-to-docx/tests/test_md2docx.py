#!/usr/bin/env python3

import importlib.util
import tempfile
import unittest
from pathlib import Path

from docx import Document


MODULE_PATH = Path(__file__).resolve().parents[1] / "md2docx.py"
spec = importlib.util.spec_from_file_location("md2docx", MODULE_PATH)
md2docx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(md2docx)


class TestMdToDocx(unittest.TestCase):
    def test_basic_conversion_without_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            md_path = root / "report.md"
            out_path = root / "report.docx"
            md_path.write_text(
                "# 1 第一章\n\n"
                "正文引用[1]。\n\n"
                "表 1-1 示例表\n"
                "| 项目 | 数值 |\n"
                "|---|---|\n"
                "| A | 1 |\n\n"
                "# 参考文献\n\n"
                "[1] Example reference.\n",
                encoding="utf-8",
            )

            doc = md2docx.load_document(None)
            stats = md2docx.parse_and_write(
                md_path,
                doc,
                asset_dir=root,
                mermaid_images=[],
            )
            doc.save(out_path)
            validation = md2docx.validate_output(out_path, stats)

            self.assertEqual(stats["tables"], 1)
            self.assertEqual(stats["reference_entries"], 1)
            self.assertTrue(validation["pass"])
            reopened = Document(out_path)
            self.assertEqual(len(reopened.tables), 1)

    def test_missing_markdown_image_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            md_path = root / "report.md"
            md_path.write_text("![缺失图](missing.png)\n", encoding="utf-8")

            doc = md2docx.load_document(None)
            stats = md2docx.parse_and_write(
                md_path,
                doc,
                asset_dir=root,
                mermaid_images=[],
            )

            self.assertEqual(stats["images"], 0)
            self.assertEqual(len(stats["missing_assets"]), 1)
            self.assertTrue(stats["missing_assets"][0].endswith("missing.png"))

    def test_table_width_never_exceeds_page_width(self):
        old_width = md2docx.PAGE_W
        try:
            md2docx.PAGE_W = 10.0
            widths = md2docx.calc_col_widths(
                ["编号", "很长很长的说明字段"],
                [["1", "这是一段非常长的中文内容，需要被压缩到页面宽度以内"]],
            )
            self.assertLessEqual(sum(widths), 10.02)
        finally:
            md2docx.PAGE_W = old_width


if __name__ == "__main__":
    unittest.main()
