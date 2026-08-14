#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import xlrd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from fill_reimbursement_table import fill_reimbursement_excel, parse_invoice_pdf

class TestMaterialReimbursement(unittest.TestCase):
    def setUp(self):
        self.skill_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.template_xls = os.path.join(self.skill_dir, 'templates', '材料报销-原模板.xls')
        self.invoices_dir = r'd:\OneDrive\00_当前任务\aa_杂项\发票\至0804_发票'
        self.output_xls = os.path.join(self.skill_dir, 'examples', 'test_output.xls')

    def test_reimbursement_generation(self):
        if not os.path.exists(self.invoices_dir):
            self.skipTest("Invoices directory not accessible in this environment")

        success = fill_reimbursement_excel(
            invoices_dir=self.invoices_dir,
            template_xls=self.template_xls,
            output_xls=self.output_xls,
            tax_inclusive=True
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.output_xls))

        # Verify Excel properties
        wb = xlrd.open_workbook(self.output_xls, formatting_info=True)
        sh0 = wb.sheet_by_index(0)
        self.assertEqual(sh0.nrows, 36)
        self.assertEqual(sh0.ncols, 6)
        self.assertEqual(sh0.cell_value(0, 0), '哈工大郑州研究院材料验收单')
        self.assertEqual(sh0.cell_value(3, 0), '材料名称')
        self.assertEqual(sh0.cell_value(31, 0), '合计')

        if os.path.exists(self.output_xls):
            os.remove(self.output_xls)

if __name__ == '__main__':
    unittest.main()
