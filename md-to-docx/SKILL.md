# md-to-docx: Markdown 转 Word 技能

## 功能

将中文技术方案 Markdown 文档转换为基于指定 Word 模板的 `.docx` 文件，自动处理标题、表格、图片、列表、题注和分页。

## 使用方式

用户提供：
1. Markdown 源文件路径
2. Word 模板路径（`.dotx`）
3. 可选：Mermaid 图片路径、自定义列宽规则

## 核心流程

### 1. 加载模板

`.dotx` 文件不能直接用 python-docx 打开，需要先转换 content type：

```python
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
```

### 2. 字号与字体

| 场景 | 字号 | 中文字体 | 英文字体 |
|---|---|---|---|
| 正文（Normal） | 12pt（小四） | 宋体 | Times New Roman |
| 表格（表格文） | 10.5pt（五号） | 宋体 | Times New Roman |
| 标题（Heading） | 继承模板 | 宋体 | Times New Roman |
| 题注（Caption） | 10.5pt | 宋体 | Times New Roman |

设置 run 字体时必须同时设置 `w:eastAsia`：

```python
run.font.name = "Times New Roman"
run.font.size = Pt(12)
run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
```

### 3. 标题处理

- 使用模板的 Heading 1/2/3 样式，不使用四级及以下
- 去掉 Markdown 中的章节编号：`re.sub(r"^\d+(\.\d+)*\.?\s*", "", heading_text)`
- 一级标题前插入分页符（第一个除外）

### 4. 表格处理

#### 4.1 列宽计算

关键参数（基于 10.5pt 宋体 + Word 默认单元格边距）：

```python
PAD = 0.46    # Word 单元格左右边距(各0.19cm)+边框(0.04cm)+余量
CN_CHAR = 0.38  # 中文字符宽度 cm
EN_CHAR = 0.22  # 英文字符宽度 cm
```

公式：`列宽 = PAD + 字符数 × 字符宽度`

列宽分配策略：
- 计算每列最长内容的单行宽度
- 短列（最长内容 ≤ 6 字符）保持一行宽度
- 剩余空间分配给长列
- 超出页面时只压缩长列，短列不压缩

#### 4.2 表格宽度单位

Word `tblW` 的 `dxa` 单位是 **twips**（1/20点），不是 EMU！

```python
def cm_to_twips(cm):
    return int(round(cm * 567))  # 1cm = 567 twips
```

必须同时设置：
- `tblW` 的 `w:w` 和 `w:type="dxa"`
- `tblLayout` 的 `w:type="fixed"`
- `tblGrid` 的每个 `gridCol` 的 `w:w`
- 每行每个 cell 的 `width`

#### 4.3 空表头处理

如果表头行全部为空（如 `|   |   |`），将第一行数据提升为表头。

#### 4.4 表格样式

- 使用模板的「表格文」样式
- 不加粗表头
- 设置重复表头行（跨页时自动重复）

### 5. 题注

- 表题注在表上方，图题注在图下方
- 使用 Word SEQ 域实现自动编号，表和图独立编号
- 格式：「表 SEQ Table \* ARABIC」「图 SEQ Figure \* ARABIC」
- 打开 Word 后 Ctrl+A → F9 更新编号

### 6. 图片

- Mermaid 图通过 mermaid.ink API 渲染为 PNG（注意中文标签需替换为英文）
- ASCII 框图用占位文字替代
- 使用模板的「图片」样式（居中）

### 7. 列表

- 使用模板的 List Paragraph 样式
- 每项独立段落

### 8. 分页

- 每个一级标题前插入分页符
- 长表格自动跨页，重复表头行

## 依赖

```bash
pip3 install python-docx --break-system-packages
```

## 脚本位置

`/home/why/FPGA/1553B/md2docx.py` — 当前项目的转换脚本，可作为模板参考。
