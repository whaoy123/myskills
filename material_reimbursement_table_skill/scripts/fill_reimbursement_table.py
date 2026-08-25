#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
material_reimbursement_table_skill / fill_reimbursement_table.py
自动化发票解析与材料报销验收单生成脚本
"""

import os
import sys
import argparse
import glob
import re
import pdfplumber
import xlrd
import xlwt
from xlutils.copy import copy

def parse_invoice_pdf(pdf_path, tax_inclusive=True):
    """
    解析单张增值税电子发票（PDF）
    返回字典包含发票基本信息及明细行列表
    """
    fname = os.path.basename(pdf_path)
    items = []
    invoice_info = {
        'file': fname,
        'path': pdf_path,
        'date': '',
        'invoice_no': '',
        'vendor': '',
        'buyer': '',
        'total_amount': 0.0,
        'tax_amount': 0.0,
        'total_with_tax': 0.0,
        'items': []
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += (page.extract_text() or "") + "\n"
        
        # 提取开票日期
        date_match = re.search(r'开票日期[：:]\s*(\d{4})年(\d{1,2})月(\d{1,2})日', full_text)
        if date_match:
            invoice_info['date'] = f"{date_match.group(1)}年{date_match.group(2)}月{date_match.group(3)}日"
            invoice_info['year'] = int(date_match.group(1))
            invoice_info['month'] = int(date_match.group(2))
            invoice_info['day'] = int(date_match.group(3))
        
        # 提取发票号码
        no_match = re.search(r'发票号码[：:]\s*(\d+)', full_text)
        if no_match:
            invoice_info['invoice_no'] = no_match.group(1)
            
        # 提取销方名称
        vendor_match = re.search(r'销\s*售\s*方\s*信\s*息.*?名称[：:]\s*([^\n\r]+)', full_text, re.DOTALL)
        if vendor_match:
            invoice_info['vendor'] = vendor_match.group(1).strip()
        else:
            v_alt = re.search(r'售\s*名\s*称\s*[:：]?\s*([^\n\r]+)', full_text)
            if v_alt:
                invoice_info['vendor'] = v_alt.group(1).strip()

        # 解析表格明细
        page = pdf.pages[0]
        text_lines = page.extract_text().split('\n')
        
        # 针对常见发票行进行正则提取
        # 常见行格式：
        # 1. 普通商品行: *分类*名称 规格型号 单位 数量 单价 金额 税率 税额
        # 2. 折扣行: *分类*名称 [规格型号] -金额 税率 -税额
        # 3. 配送费/服务费行: *分类*配送费 次 1 单价 金额 税率 税额
        
        for line in text_lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测价税合计
            if '价税合计' in line:
                amt_m = re.search(r'[¥￥]?\s*(\d+\.\d{2})', line.split('(')[-1] if '(' in line else line)
                if amt_m:
                    invoice_info['total_with_tax'] = float(amt_m.group(1))
                continue
                
            # 检测合计
            if line.startswith('合 计') or line.startswith('合计'):
                m_totals = re.findall(r'[¥￥]?\s*(\d+\.\d{2})', line)
                if len(m_totals) >= 1:
                    invoice_info['total_amount'] = float(m_totals[0])
                if len(m_totals) >= 2:
                    invoice_info['tax_amount'] = float(m_totals[1])
                continue

            # 匹配带星号的项目行
            if line.startswith('*'):
                # 匹配折扣行 (包含负数)
                disc_match = re.search(r'^(\*[^*]+\*[^\s]+)\s+(-\d+\.\d+)\s+(\d+%|免税)?\s*(-\d+\.\d+)?', line)
                if disc_match:
                    name = disc_match.group(1)
                    amt = float(disc_match.group(2))
                    tax = float(disc_match.group(4)) if disc_match.group(4) else 0.0
                    items.append({
                        'name': name,
                        'unit': '',
                        'qty': '',
                        'price': '',
                        'amount_excl': amt,
                        'tax': tax,
                        'amount_incl': round(amt + tax, 2)
                    })
                    continue

                # 匹配标准商品明细行
                # 例如: *电子元件*贴片电容 CL21B104KBCNNNC 个 50 0.133 6.65 13% 0.86
                # 或: *日用杂品*德力西电气绝缘手套 1000V防水绝缘手套 包 1 23.81 23.81 13% 3.09
                parts = line.split()
                if len(parts) >= 6:
                    # 尝试从末尾向前解析: 税额, 税率, 金额, 单价, 数量, 单位
                    try:
                        tax_str = parts[-1]
                        rate_str = parts[-2]
                        amt_str = parts[-3]
                        price_str = parts[-4]
                        qty_str = parts[-5]
                        unit_str = parts[-6]
                        name_parts = parts[:-6]
                        
                        amt_val = float(amt_str)
                        tax_val = float(tax_str) if not tax_str.endswith('%') else 0.0
                        qty_val = float(qty_str)
                        price_val = float(price_str)
                        
                        full_name = " ".join(name_parts)
                        
                        items.append({
                            'name': full_name,
                            'unit': unit_str,
                            'qty': qty_val,
                            'price_excl': price_val,
                            'amount_excl': amt_val,
                            'tax': tax_val,
                            'amount_incl': round(amt_val + tax_val, 2),
                            'price_incl': round((amt_val + tax_val) / qty_val, 4) if qty_val else 0.0
                        })
                        continue
                    except (ValueError, IndexError):
                        pass

    invoice_info['items'] = items
    return invoice_info

def fill_reimbursement_excel(invoices_dir, template_xls, output_xls, dept_name="智能测试与控制技术研究所", fill_date=None, tax_inclusive=True):
    """
    根据发票目录解析所有 PDF 并填入报销表格第一页
    """
    # 1. 扫描所有发票
    pdf_files = sorted(glob.glob(os.path.join(invoices_dir, "*.pdf")))
    if not pdf_files:
        print(f"未在目录 {invoices_dir} 中找到 PDF 发票文件！")
        return False
        
    all_items = []
    latest_year, latest_month, latest_day = 2026, 8, 11
    
    for pf in pdf_files:
        info = parse_invoice_pdf(pf, tax_inclusive=tax_inclusive)
        if 'year' in info and info['year']:
            latest_year = info['year']
            latest_month = info['month']
            latest_day = info['day']
            
        for it in info['items']:
            if tax_inclusive:
                amt = it.get('amount_incl', it.get('amount_excl', 0.0))
                p = it.get('price_incl', it.get('price_excl', ''))
            else:
                amt = it.get('amount_excl', 0.0)
                p = it.get('price_excl', '')
                
            all_items.append({
                'name': it['name'],
                'unit': it['unit'],
                'qty': it['qty'],
                'price': p,
                'amount': amt,
                'vendor': ''
            })

    if fill_date:
        # 支持自定义日期字符串 YYYY-MM-DD
        m = re.match(r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})', fill_date)
        if m:
            latest_year, latest_month, latest_day = int(m.group(1)), int(m.group(2)), int(m.group(3))

    # 2. 读取模板并复制结构
    rb = xlrd.open_workbook(template_xls, formatting_info=True)
    wb = copy(rb)
    ws0 = wb.get_sheet(0)

    # 3. 样式定义（完全符合原版宋体格式）
    borders_thin = xlwt.Borders()
    borders_thin.left = xlwt.Borders.THIN
    borders_thin.right = xlwt.Borders.THIN
    borders_thin.top = xlwt.Borders.THIN
    borders_thin.bottom = xlwt.Borders.THIN

    f_14 = xlwt.Font()
    f_14.name = 'SimSun'
    f_14.height = 14 * 20

    f_12 = xlwt.Font()
    f_12.name = 'SimSun'
    f_12.height = 12 * 20

    f_10 = xlwt.Font()
    f_10.name = 'SimSun'
    f_10.height = 10 * 20

    f_11 = xlwt.Font()
    f_11.name = 'SimSun'
    f_11.height = 11 * 20

    # 日期样式
    style_date_yr = xlwt.XFStyle()
    style_date_yr.font = f_14
    al_date_yr = xlwt.Alignment()
    al_date_yr.horz = xlwt.Alignment.HORZ_CENTER
    al_date_yr.vert = xlwt.Alignment.VERT_CENTER
    style_date_yr.alignment = al_date_yr

    style_date_md = xlwt.XFStyle()
    style_date_md.font = f_14
    al_date_md = xlwt.Alignment()
    al_date_md.horz = xlwt.Alignment.HORZ_LEFT
    al_date_md.vert = xlwt.Alignment.VERT_CENTER
    style_date_md.alignment = al_date_md

    # 数据居中与边框
    style_td_center = xlwt.XFStyle()
    style_td_center.font = f_14
    al_center = xlwt.Alignment()
    al_center.horz = xlwt.Alignment.HORZ_CENTER
    al_center.vert = xlwt.Alignment.VERT_CENTER
    style_td_center.alignment = al_center
    style_td_center.borders = borders_thin

    style_unit = xlwt.XFStyle()
    style_unit.font = f_12
    style_unit.alignment = al_center
    style_unit.borders = borders_thin

    style_empty_box = xlwt.XFStyle()
    style_empty_box.borders = borders_thin

    # 合计样式
    style_total_lbl = xlwt.XFStyle()
    style_total_lbl.font = f_11
    al_total_lbl = xlwt.Alignment()
    al_total_lbl.horz = xlwt.Alignment.HORZ_LEFT
    al_total_lbl.vert = xlwt.Alignment.VERT_BOTTOM
    style_total_lbl.alignment = al_total_lbl
    style_total_lbl.borders = borders_thin

    style_total_val = xlwt.XFStyle()
    style_total_val.font = f_10
    al_total_val = xlwt.Alignment()
    al_total_val.horz = xlwt.Alignment.HORZ_RIGHT
    al_total_val.vert = xlwt.Alignment.VERT_CENTER
    style_total_val.alignment = al_total_val
    style_total_val.borders = borders_thin

    # 签名栏样式
    style_sign_left = xlwt.XFStyle()
    style_sign_left.font = f_14
    al_sign = xlwt.Alignment()
    al_sign.horz = xlwt.Alignment.HORZ_LEFT
    al_sign.vert = xlwt.Alignment.VERT_CENTER
    style_sign_left.alignment = al_sign
    b_sign_left = xlwt.Borders()
    b_sign_left.top = xlwt.Borders.THIN
    b_sign_left.bottom = xlwt.Borders.THIN
    b_sign_left.left = xlwt.Borders.THIN
    style_sign_left.borders = b_sign_left

    style_sign_mid = xlwt.XFStyle()
    style_sign_mid.font = f_14
    style_sign_mid.alignment = al_sign
    b_sign_mid = xlwt.Borders()
    b_sign_mid.top = xlwt.Borders.THIN
    b_sign_mid.bottom = xlwt.Borders.THIN
    style_sign_mid.borders = b_sign_mid

    style_sign_right = xlwt.XFStyle()
    style_sign_right.font = f_14
    style_sign_right.alignment = al_sign
    b_sign_right = xlwt.Borders()
    b_sign_right.top = xlwt.Borders.THIN
    b_sign_right.bottom = xlwt.Borders.THIN
    b_sign_right.right = xlwt.Borders.THIN
    style_sign_right.borders = b_sign_right

    style_note = xlwt.XFStyle()
    style_note.font = f_14
    style_note.alignment = al_sign

    # 4. 写入表头信息
    ws0.write(1, 2, latest_year, style_date_yr)
    ws0.write(1, 3, f'年 {latest_month}月', style_date_md)
    ws0.write(1, 4, f'{latest_day}日', style_date_md)

    # 5. 写入明细行 (Row 4 开始)
    curr_row = 4
    for it in all_items:
        ws0.row(curr_row).height = 402
        ws0.write(curr_row, 0, it['name'], style_td_center)
        ws0.write(curr_row, 1, it['unit'], style_unit)
        ws0.write(curr_row, 2, it['qty'], style_td_center if it['qty'] != '' else style_empty_box)
        ws0.write(curr_row, 3, it['price'], style_td_center if it['price'] != '' else style_empty_box)
        ws0.write(curr_row, 4, it['amount'], style_td_center if it['amount'] != '' else style_empty_box)
        ws0.write(curr_row, 5, it['vendor'], style_empty_box)
        curr_row += 1

    # 6. 写入合计行与自动求和公式
    total_row = curr_row
    ws0.row(total_row).height = 402
    ws0.write(total_row, 0, '合计', style_total_lbl)
    ws0.write(total_row, 1, '', style_empty_box)
    ws0.write(total_row, 2, '', style_empty_box)
    ws0.write(total_row, 3, '', style_empty_box)
    # Excel 行号从 1 开始，数据从第 5 行到第 total_row 行
    formula_str = f"SUM(E5:E{total_row})"
    ws0.write(total_row, 4, xlwt.Formula(formula_str), style_total_val)
    ws0.write(total_row, 5, '', style_empty_box)
    curr_row += 1

    # 7. 写入经办人/验收人/负责人签名栏
    sign_row = curr_row
    ws0.row(sign_row).height = 669
    ws0.write(sign_row, 0, '经办人：', style_sign_left)
    ws0.write(sign_row, 1, '', style_sign_mid)
    ws0.write(sign_row, 2, '验收人：', style_sign_mid)
    ws0.write(sign_row, 3, '', style_sign_mid)
    ws0.write(sign_row, 4, '负责人：      ', style_sign_mid)
    ws0.write(sign_row, 5, '', style_sign_right)
    curr_row += 1

    # 8. 写入空行与注释
    ws0.row(curr_row).height = 348
    for c in range(6):
        ws0.write(curr_row, c, '')
    curr_row += 1

    ws0.row(curr_row).height = 348
    ws0.write(curr_row, 0, '注:1、本验收单由部门具体填报', style_note)
    for c in range(1, 6):
        ws0.write(curr_row, c, '')
    curr_row += 1

    ws0.row(curr_row).height = 348
    ws0.write(curr_row, 0, '   2、本验收单一式两联，一联交财务，一联部门留存备查', style_note)
    for c in range(1, 6):
        ws0.write(curr_row, c, '')

    # 9. 保存文件
    wb.save(output_xls)
    calc_sum = round(sum(i['amount'] for i in all_items), 2)
    print(f"成功更新验收单表格：{output_xls}")
    print(f"共填入明细项：{len(all_items)} 行，合计金额（含税={tax_inclusive}）：{calc_sum}，公式：=SUM(E5:E{total_row})")
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="材料报销验收单自动填报工具")
    parser.add_argument('--invoices-dir', required=True, help="发票 PDF 文件所在目录")
    parser.add_argument('--template-xls', required=True, help="报销表格原模板 .xls 路径")
    parser.add_argument('--output-xls', required=True, help="生成的目标 .xls 路径")
    parser.add_argument('--dept', default="智能测试与控制技术研究所", help="部门名称")
    parser.add_argument('--date', default=None, help="验收单日期，例如 2026-08-11")
    parser.add_argument('--tax-exclusive', action='store_true', help="按不含税金额填报（默认按含税价税合计填报）")

    args = parser.parse_args()
    fill_reimbursement_excel(
        invoices_dir=args.invoices_dir,
        template_xls=args.template_xls,
        output_xls=args.output_xls,
        dept_name=args.dept,
        fill_date=args.date,
        tax_inclusive=not args.tax_exclusive
    )
