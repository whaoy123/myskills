#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from extract_soldering_components import is_soldering_component, classify_component, extract_soldering_components

class TestExtractComponents(unittest.TestCase):
    def test_filter_rules(self):
        # 应该排除的
        self.assertFalse(is_soldering_component('*日用杂品*德力西电气绝缘手套', '1000V防水绝缘手套'))
        self.assertFalse(is_soldering_component('*印制电路板*线路板', 'Project Outputs for SPB'))
        self.assertFalse(is_soldering_component('*电子元件*电子元件', 'DB25/DB44/焊线式/塑壳'))
        self.assertFalse(is_soldering_component('*电子元件*配送费', ''))
        
        # 应该保留的
        self.assertTrue(is_soldering_component('*电子元件*电流传感器', 'CC6937S8-5FB010'))
        self.assertTrue(is_soldering_component('*电子元件*贴片电容', 'CL21B104KBCNNNC'))
        self.assertTrue(is_soldering_component('*电子元件*插件电阻', 'MOR02SJ033KA10'))
        self.assertTrue(is_soldering_component('*电子元件*螺钉式接线端子', 'DB910-9.52-4P-GN-S'))
        self.assertTrue(is_soldering_component('*电子元件*连接器', 'DR44实心车针/母头/弯针插板'))

    def test_classification(self):
        cat, model, pkg, _ = classify_component('*电子元件*贴片电容', 'CL21B104KBCNNNC 0805')
        self.assertEqual(cat, '电容')
        self.assertIn('0805', pkg)

if __name__ == '__main__':
    unittest.main()
