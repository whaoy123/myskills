#!/usr/bin/env python3
"""将 系统设计方案模板.md 转换为 Word 文档，基于开题报告.dotx 模板。"""

import re
import shutil
import zipfile
import os
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ============================================================
# 常量
# ============================================================
TEMPLATE_SRC = "/mnt/c/Users/why/Desktop/开题报告.dotx"
MD_PATH = "/home/why/FPGA/1553B/系统设计方案模板.md"
OUT_PATH = "/home/why/FPGA/1553B/系统设计方案模板.docx"
MERMAID_SYS = "/tmp/mermaid_sys.png"
MERMAID_FPGA = "/tmp/mermaid_fpga.png"

# 页面可用宽度 14.66cm（A4, 左3.17+右3.17）
PAGE_W = 14.66


# ============================================================
# 工具函数
# ============================================================

def load_template_as_docx(src_path):
    """将 .dotx 复制并转换 content type 后作为 .docx 打开。"""
    tmp = "/tmp/_template_as_docx.docx"
    shutil.copy(src_path, tmp)
    with zipfile.ZipFile(tmp, "r") as z:
        files = {}
        for item in z.infolist():
            data = z.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.decode().replace(
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
                ).encode()
            files[item.filename] = data
    os.remove(tmp)
    with zipfile.ZipFile(tmp, "w") as z2:
        for name, data in files.items():
            z2.writestr(name, data)
    return Document(tmp)


def set_run_font(run, cn_font="宋体", en_font="Times New Roman", size=Pt(12)):
    """设置 run 的中西文字体，默认小四（12pt）。"""
    run.font.name = en_font
    run.font.size = size
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:eastAsia"), cn_font)


def add_run_with_font(paragraph, text, cn_font="宋体", en_font="Times New Roman", size=Pt(12)):
    """向段落添加一个 run 并设置字体。"""
    run = paragraph.add_run(text)
    set_run_font(run, cn_font, en_font, size)
    return run


def set_cell_paragraph(cell, text, style_name="表格文"):
    """设置单元格内容，使用指定样式。"""
    cell.text = ""
    p = cell.paragraphs[0]
    try:
        p.style = cell.part.document.styles[style_name]
    except KeyError:
        pass
    # 清除多余间距
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    # 表格文样式自带字号，不覆盖
    set_run_font(run, size=Pt(10.5))
    return p


def cm_to_twips(cm):
    """厘米转 twips（1 cm = 567 twips）。"""
    return int(round(cm * 567))


def set_table_col_widths(table, widths_cm):
    """直接设置表格网格列宽和单元格宽度，确保 Word 使用固定列宽。"""
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    tbl = table._tbl
    tblPr = tbl.find(f"{{{ns}}}tblPr")
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)

    # 设置表格总宽 = 固定值（dxa = twips）
    tblW = tblPr.find(f"{{{ns}}}tblW")
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    total_twips = cm_to_twips(sum(widths_cm))
    tblW.set(qn("w:w"), str(total_twips))
    tblW.set(qn("w:type"), "dxa")

    # 设置 tblLayout 为 fixed
    tblLayout = tblPr.find(f"{{{ns}}}tblLayout")
    if tblLayout is None:
        tblLayout = OxmlElement("w:tblLayout")
        tblPr.append(tblLayout)
    tblLayout.set(qn("w:type"), "fixed")

    # 更新 tblGrid 的 gridCol 宽度（dxa = twips）
    tblGrid = tbl.find(f"{{{ns}}}tblGrid")
    if tblGrid is not None:
        gridCols = tblGrid.findall(f"{{{ns}}}gridCol")
        for i, col in enumerate(gridCols):
            if i < len(widths_cm):
                col.set(qn("w:w"), str(cm_to_twips(widths_cm[i])))

    # 同时设置每行单元格宽度
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if i < len(widths_cm):
                cell.width = Cm(widths_cm[i])


def insert_seq_field(paragraph, seq_name):
    """插入 Word SEQ 域实现自动编号。"""
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    run1 = paragraph.add_run()
    run1._element.append(fld_begin)

    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" SEQ {seq_name} \\* ARABIC "
    run2 = paragraph.add_run()
    run2._element.append(instr)

    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    run3 = paragraph.add_run()
    run3._element.append(fld_sep)

    run4 = paragraph.add_run("1")
    set_run_font(run4)

    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run5 = paragraph.add_run()
    run5._element.append(fld_end)


def add_page_break(doc):
    """插入分页符。"""
    p = doc.add_paragraph()
    run = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._element.append(br)


def repeat_table_header(row):
    """设置表格行在跨页时重复显示为表头。"""
    trPr = row._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)


# ============================================================
# 列宽计算
# ============================================================

def text_display_width_cm(text):
    """估算文字单行显示宽度（cm），基于表格文 10.5pt 字号。
    已含 Word 单元格左右边距（各 0.19cm）和边框（约 0.04cm）。"""
    PAD = 0.46  # Word 单元格左右边距+边框合计
    w = PAD
    for ch in text:
        if ord(ch) > 127:
            w += 0.38
        else:
            w += 0.22
    return w


def calc_col_widths(header, data_rows):
    """按内容单行显示宽度计算列宽，总和 = PAGE_W。
    原则：每列刚好够放最长内容的一行；放不下时才允许折行。"""
    cols = len(header)

    # 1. 计算每列最长内容的单行宽度
    need = []
    for c in range(cols):
        texts = [header[c]]
        for row in data_rows:
            if c < len(row):
                texts.append(row[c])
        max_cm = max(text_display_width_cm(t) for t in texts)
        need.append(max(0.3, max_cm))

    total_need = sum(need)

    # 短列（最长内容 <= 6 个字符）必须保持一行宽度
    short_cols = set()
    for c in range(cols):
        texts = [header[c]]
        for row in data_rows:
            if c < len(row):
                texts.append(row[c])
        max_len = max(len(t) for t in texts)
        if max_len <= 6:
            short_cols.add(c)

    if total_need <= PAGE_W:
        # 所有列都能一行放下，剩余空间按比例分配
        widths = list(need)
        spare = PAGE_W - total_need
        if spare > 0:
            for c in range(cols):
                widths[c] += spare * (need[c] / total_need)
    else:
        # 超出页面：先保证短列不折行，剩余空间分给长列
        short_total = sum(need[c] for c in short_cols)
        long_cols = [c for c in range(cols) if c not in short_cols]
        long_total_need = sum(need[c] for c in long_cols)
        available_for_long = PAGE_W - short_total

        widths = [0.0] * cols
        for c in short_cols:
            widths[c] = need[c]

        if available_for_long <= 0:
            # 连短列都放不下，按比例压缩所有列
            ratio = PAGE_W / total_need
            widths = [n * ratio for n in need]
        elif available_for_long >= long_total_need:
            # 长列也能全放下
            for c in long_cols:
                widths[c] = need[c]
        else:
            # 长列需要压缩，从最宽的开始压缩
            long_sorted = sorted(long_cols, key=lambda i: need[i], reverse=True)
            remaining = available_for_long
            for idx in long_sorted:
                min_w = text_display_width_cm(header[idx])
                ideal = need[idx] / long_total_need * available_for_long
                widths[idx] = max(min_w, ideal)
                remaining -= widths[idx]
            # 修正舍入
            if abs(remaining) > 0.01:
                max_long = long_sorted[0]
                widths[max_long] += remaining

    widths = [round(w, 2) for w in widths]
    diff = round(PAGE_W - sum(widths), 2)
    max_idx = widths.index(max(widths))
    widths[max_idx] = round(widths[max_idx] + diff, 2)
    return widths


def get_caption_before(lines, idx, prefix):
    """从 idx 位置向前查找形如 '表 N-N 名称' 或 '图 N-N 名称' 的题注行。
    返回题注名称部分（去掉 '表/图 N-N' 前缀），未找到返回空字符串。"""
    j = idx - 1
    while j >= 0:
        s = lines[j].strip()
        if not s:
            j -= 1
            continue
        m = re.match(r"^" + prefix + r"\s*\d+[\-\.]\d+\s*(.*)", s)
        if m:
            return m.group(1).strip()
        break
    return ""


# ============================================================
# 解析与写入
# ============================================================

def parse_and_write(md_path, doc):
    """解析 Markdown 并写入 Word 文档。"""
    text = Path(md_path).read_text(encoding="utf-8")
    lines = text.split("\n")

    mermaid_counter = [0]
    mermaid_files = [MERMAID_SYS, MERMAID_FPGA]
    mermaid_captions = ["系统总体框图", "FPGA 整体设计导图"]

    i = 0
    is_first_heading = True
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "---":
            i += 1
            continue

        # 跳过表/图题注行（已由表格/图块处理器消费）
        if re.match(r"^(表|图)\s*\d+[\-\.]\d+\s*\S", stripped):
            i += 1
            continue

        # 标题
        heading_match = re.match(r"^(#{1,3})\s+(.*)", stripped)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            heading_text = re.sub(r"^\d+(\.\d+)*\.?\s*", "", heading_text)

            if level == 1 and not is_first_heading:
                add_page_break(doc)
            is_first_heading = False

            h = doc.add_heading(heading_text, level=level)
            for run in h.runs:
                run.font.name = "Times New Roman"
                rPr = run._element.get_or_add_rPr()
                rFonts = rPr.get_or_add_rFonts()
                rFonts.set(qn("w:eastAsia"), "宋体")
            i += 1
            continue

        # 代码块
        if stripped.startswith("```"):
            code_block_start = i
            lang = stripped[3:].strip().lower()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # i 现在指向代码块之后的第一行

            if lang == "mermaid" and mermaid_counter[0] < len(mermaid_files):
                idx = mermaid_counter[0]
                png_path = mermaid_files[idx]
                mermaid_counter[0] += 1

                # 从代码块之后的位置向后查找 '图 X-X 名称' 行
                fig_cap_name = ""
                fig_cap_line = -1
                for j in range(i, min(i + 5, len(lines))):
                    m = re.match(r"^图\s*\d+[\-\.]\d+\s*(.*)", lines[j].strip())
                    if m:
                        fig_cap_name = m.group(1).strip()
                        fig_cap_line = j
                        break
                if not fig_cap_name and idx < len(mermaid_captions):
                    fig_cap_name = mermaid_captions[idx]

                if os.path.exists(png_path) and os.path.getsize(png_path) > 100:
                    p_img = doc.add_paragraph()
                    p_img.style = doc.styles["图片"]
                    run = p_img.add_run()
                    run.add_picture(png_path, width=Cm(14))
                else:
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    add_run_with_font(p_img, "[占位图示：待替换为正式插图]", size=Pt(9))

                # 图题注（下方）：图 + SEQ + 题注名称
                p_cap = doc.add_paragraph()
                p_cap.style = doc.styles["Caption"]
                add_run_with_font(p_cap, "图", size=Pt(10.5))
                insert_seq_field(p_cap, "Figure")
                if fig_cap_name:
                    add_run_with_font(p_cap, f"-{fig_cap_name}", size=Pt(10.5))

                # 跳过已被消费的 '图 X-X 名称' 行
                if fig_cap_line >= 0:
                    i = fig_cap_line + 1
            else:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = add_run_with_font(p, "[此处为占位内容]", size=Pt(9))
                run.font.color.rgb = RGBColor(128, 128, 128)
            continue

        # 表格
        if stripped.startswith("|") and "|" in stripped[1:]:
            table_start_i = i
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            if len(table_lines) >= 3:
                header = [c.strip() for c in table_lines[0].split("|")[1:-1]]
                data_rows = []
                for tl in table_lines[2:]:
                    row = [c.strip() for c in tl.split("|")[1:-1]]
                    data_rows.append(row)

                # 如果表头全为空，把第一行数据提升为表头
                if all(not h for h in header) and data_rows:
                    header = data_rows[0]
                    data_rows = data_rows[1:]
                    if not data_rows:
                        continue

                # 表题注（在表上方）：表 + SEQ + 题注名称
                cap_name = get_caption_before(lines, table_start_i, "表")
                p_cap = doc.add_paragraph()
                p_cap.style = doc.styles["Caption"]
                add_run_with_font(p_cap, "表", size=Pt(10.5))
                insert_seq_field(p_cap, "Table")
                if cap_name:
                    add_run_with_font(p_cap, f"-{cap_name}", size=Pt(10.5))

                # 计算列宽
                col_widths = calc_col_widths(header, data_rows)

                # 创建表格
                cols = len(header)
                table = doc.add_table(rows=1 + len(data_rows), cols=cols, style="Table Grid")
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                table.autofit = False

                # 设置列宽
                set_table_col_widths(table, col_widths)

                # 表头行
                for c_idx, text in enumerate(header):
                    set_cell_paragraph(table.rows[0].cells[c_idx], text)
                repeat_table_header(table.rows[0])

                # 数据行
                for r_idx, row_data in enumerate(data_rows):
                    for c_idx, text in enumerate(row_data):
                        if c_idx < cols:
                            set_cell_paragraph(table.rows[r_idx + 1].cells[c_idx], text)

                doc.add_paragraph()  # 表后空行
            continue

        # 无序列表
        list_match = re.match(r"^[-*]\s+(.*)", stripped)
        if list_match:
            while i < len(lines):
                lm = re.match(r"^[-*]\s+(.*)", lines[i].strip())
                if lm:
                    p = doc.add_paragraph(style="List Paragraph")
                    add_run_with_font(p, lm.group(1))
                    i += 1
                else:
                    break
            continue

        # 有序列表
        ordered_match = re.match(r"^(\d+)\.\s+(.*)", stripped)
        if ordered_match:
            while i < len(lines):
                om = re.match(r"^(\d+)\.\s+(.*)", lines[i].strip())
                if om:
                    p = doc.add_paragraph(style="List Paragraph")
                    add_run_with_font(p, f"（{om.group(1)}）{om.group(2)}")
                    i += 1
                else:
                    break
            continue

        # ASCII 流程图
        if stripped.startswith("+") and stripped.endswith("+"):
            block_lines = []
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith("+"):
                    block_lines.append(lines[i])
                    i += 1
                elif s.startswith("|") and block_lines:
                    block_lines.append(lines[i])
                    i += 1
                else:
                    break
            if len(block_lines) > 2:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = add_run_with_font(p, "[占位图示：待替换为正式插图]", size=Pt(9))
                run.font.color.rgb = RGBColor(128, 128, 128)

                # 查找 ASCII 块之后的 '图 X-X 名称' 行并生成题注
                fig_cap_name = ""
                fig_cap_line = -1
                for j in range(i, min(i + 5, len(lines))):
                    m = re.match(r"^图\s*\d+[\-\.]\d+\s*(.*)", lines[j].strip())
                    if m:
                        fig_cap_name = m.group(1).strip()
                        fig_cap_line = j
                        break
                if fig_cap_name:
                    p_cap = doc.add_paragraph()
                    p_cap.style = doc.styles["Caption"]
                    add_run_with_font(p_cap, "图", size=Pt(10.5))
                    insert_seq_field(p_cap, "Figure")
                    add_run_with_font(p_cap, f"-{fig_cap_name}", size=Pt(10.5))
                    i = fig_cap_line + 1
            continue

        # 普通段落
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(1.56)
        add_run_with_font(p, stripped)
        i += 1

    return doc


# ============================================================
# 主流程
# ============================================================

if __name__ == "__main__":
    print("加载模板...")
    doc = load_template_as_docx(TEMPLATE_SRC)

    print("解析 Markdown 并写入 Word...")
    parse_and_write(MD_PATH, doc)

    print(f"保存到 {OUT_PATH}...")
    doc.save(OUT_PATH)
    print(f"完成: {OUT_PATH}")
