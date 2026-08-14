#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
invoice_components_extractor_skill / extract_soldering_components.py
从采购发票 PDF 自动化过滤并提取纯焊接元器件清单（类别 + 型号 + 封装/安装形式 + 参数说明 + 数量）
"""

import os
import sys
import argparse
import glob
import re
import pdfplumber
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

# 排除关键词列表（非焊接上板元器件）
EXCLUDE_KEYWORDS = [
    '手套', '劳保', '工具', '运费', '配送费', '包装费', '快递', '服务费',
    '线路板', 'pcb', '打板', '印制电路板', '塑壳', '外壳', '外罩', '外壳组件',
    '螺丝', '螺母', '铜柱', '扎带', '导热胶', '胶水', '焊锡', '吸锡带'
]

def is_soldering_component(name, model=""):
    """
    判断项目是否为需要焊接的实际电子元器件
    """
    full_text = f"{name} {model}".lower()
    
    # 1. 检查排除词
    for kw in EXCLUDE_KEYWORDS:
        if kw in full_text:
            return False
            
    # 2. 如果包含星号且没有负号，且属于典型电子元件/半导体/芯片/连接器分类
    if any(k in full_text for k in ['电阻', '电容', '电感', '芯片', '传感器', '二极管', '三极管', 
                                    'mos', '场效应管', '连接器', '端子', '晶振', '继电器', '开关', '插针', '排母', '针座', 'd-sub', 'dr44', 'db44']):
        return True
        
    return False

def classify_component(name, model=""):
    """
    对元器件进行分类、封装识别和参数提炼
    """
    text = f"{name} {model}"
    
    category = "其他元器件"
    package = "标准"
    desc = text
    clean_model = model if model else name

    # 识别分类
    if '传感器' in text or 'ic' in text.lower() or '芯片' in text:
        category = "芯片/传感器"
        if 'sop-8' in text.lower() or 's8' in text.lower() or 'soic' in text.lower():
            package = "SOP-8 (贴片)"
        elif 'qfp' in text.lower() or 'qfn' in text.lower():
            package = "QFP/QFN (贴片)"
        else:
            package = "贴片/集成电路"
    elif '电容' in text:
        category = "电容"
        if '0805' in text:
            package = "0805 (贴片)"
        elif '0603' in text:
            package = "0603 (贴片)"
        elif '1206' in text:
            package = "1206 (贴片)"
        elif '0402' in text:
            package = "0402 (贴片)"
        else:
            package = "贴片陶瓷"
    elif '电阻' in text:
        category = "电阻"
        if '2512' in text:
            package = "2512 (贴片)"
        elif '0805' in text:
            package = "0805 (贴片)"
        elif '0603' in text:
            package = "0603 (贴片)"
        elif '插件' in text or 'mor' in text.lower():
            package = "AXIAL (插件)"
        else:
            package = "贴片电阻"
    elif '端子' in text or '接线' in text:
        category = "接线端子"
        if '9.52' in text:
            package = "间距9.52mm (插件)"
        elif '7.62' in text:
            package = "间距7.62mm (插件)"
        elif '5.0' in text or '5.08' in text:
            package = "间距5.0mm (插件)"
        else:
            package = "直插插件"
    elif '连接器' in text or 'db' in text.lower() or 'dr' in text.lower():
        category = "连接器"
        if '弯针' in text or '弯插' in text:
            package = "D-SUB 44P (弯插)"
        elif '焊线' in text:
            package = "D-SUB 44P (焊线)"
        else:
            package = "插接件"

    # 清理型号
    clean_model = re.sub(r'^\*.*?\*', '', clean_model).strip()
    if not clean_model:
        clean_model = re.sub(r'^\*.*?\*', '', name).strip()
        
    return category, clean_model, package, desc

def extract_soldering_components(invoices_dir, output_xlsx=None):
    """
    从指定发票目录解析所有 PDF 并生成纯焊接元器件清单
    """
    pdf_files = sorted(glob.glob(os.path.join(invoices_dir, "*.pdf")))
    if not pdf_files:
        print(f"未在目录 {invoices_dir} 中找到 PDF 发票！")
        return []

    components = []
    
    for pf in pdf_files:
        with pdfplumber.open(pf) as pdf:
            page = pdf.pages[0]
            lines = (page.extract_text() or "").split('\n')
            
            for line in lines:
                line = line.strip()
                if not line.startswith('*'):
                    continue
                # 排除折扣行（负数）
                if ' -' in line or re.search(r'\s-\d+\.\d+', line):
                    continue
                    
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        tax_str = parts[-1]
                        rate_str = parts[-2]
                        amt_str = parts[-3]
                        price_str = parts[-4]
                        qty_str = parts[-5]
                        unit_str = parts[-6]
                        name_parts = parts[:-6]
                        
                        full_name = " ".join(name_parts)
                        qty = float(qty_str)
                        
                        # 拆分型号与名称
                        raw_name = parts[0]
                        raw_model = " ".join(parts[1:-6]) if len(parts) > 7 else ""
                        
                        if is_soldering_component(raw_name, raw_model):
                            cat, model, pkg, desc = classify_component(raw_name, raw_model)
                            components.append({
                                'category': cat,
                                'model': model if model else full_name,
                                'package': pkg,
                                'raw_name': full_name,
                                'qty': qty,
                                'unit': unit_str,
                                'source_file': os.path.basename(pf)
                            })
                    except (ValueError, IndexError):
                        pass

    if output_xlsx:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = '焊接元器件清单'
        
        headers = ['序号', '类别', '型号 / 规格', '封装 / 安装形式', '原始品名', '数量', '单位']
        ws.append(headers)
        
        header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        header_font = Font(name='微软雅黑', size=11, bold=True, color='FFFFFF')
        data_font = Font(name='微软雅黑', size=10)
        thin_side = Side(style='thin', color='D9D9D9')
        border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        
        for col in range(1, 8):
            c = ws.cell(row=1, column=col)
            c.fill = header_fill
            c.font = header_font
            c.alignment = Alignment(horizontal='center', vertical='center')
            
        for idx, comp in enumerate(components, 1):
            row_data = [idx, comp['category'], comp['model'], comp['package'], comp['raw_name'], comp['qty'], comp['unit']]
            ws.append(row_data)
            row_idx = idx + 1
            for col_idx in range(1, 8):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = data_font
                cell.border = border
                if col_idx in [1, 2, 4, 6, 7]:
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                    
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 16
        ws.column_dimensions['C'].width = 35
        ws.column_dimensions['D'].width = 22
        ws.column_dimensions['E'].width = 40
        ws.column_dimensions['F'].width = 10
        ws.column_dimensions['G'].width = 8
        
        wb.save(output_xlsx)
        print(f"成功导出焊接元器件清单：{output_xlsx}（共 {len(components)} 项）")

    return components

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="采购发票纯焊接元器件提取工具")
    parser.add_argument('--invoices-dir', required=True, help="发票 PDF 目录")
    parser.add_argument('--output-xlsx', default=None, help="导出的 Excel 路径 (.xlsx)")
    
    args = parser.parse_args()
    comps = extract_soldering_components(args.invoices_dir, args.output_xlsx)
    
    print("\n=== 提取结果 ===")
    for idx, c in enumerate(comps, 1):
        print(f"{idx:2d}. [{c['category']}] {c['model']} ({c['package']}) x {c['qty']} {c['unit']}")
