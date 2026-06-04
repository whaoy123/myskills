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
PAD = 0.46    # Word 单元格左右边距(各0.19cm)+边框(0.04cm)
SAFETY = 0.08 # 列宽安全余量，避免渲染差异导致折行
```

公式：`列宽 = PAD + 字符数 × 字符宽度 + SAFETY`

#### 4.2 列宽分配规范

**表格总宽度按内容需求确定**
表格不强制铺满页面正文宽度。各列按最长内容设置最小宽度后，总宽度即为表格宽度。若总宽度未超过页面宽度，剩余空间分配给最宽列；若超过页面宽度，则压缩长列至页面宽度。

**短字段列按最小宽度设置**
"序号""编号""方向""单位""状态"等短列，保留满足内容显示的最小宽度，不人为拉宽。短列判定标准：该列所有内容（含表头）字符数不超过 6。

**固定内容列按最长内容设置**
"名称""类型""信号名""接口名""参数值"等列，按该列最长内容设置宽度，保证内容一行显示。

**说明类列作为弹性列**
"说明""备注""功能描述"等列，在其他列按最小宽度分配后，分配剩余空间。如果剩余空间不足以让说明内容一行显示，按分配到的宽度显示，允许折行。

**每列包含安全余量**
每列最小宽度 = 最长内容单行宽度 + 0.08cm 安全余量，避免 Word 渲染差异导致意外折行。

**避免无意义铺满**
不将短内容表格强行拉满整页。表格以"内容紧凑、阅读清晰"为优先。

**同类表格保持一致**
同一类表格采用统一列宽规则，保持相同字段的宽度规则一致。

#### 4.3 表格对齐与文字方向

- 表格整体居中对齐
- 单元格内非叙述性文字（如名称、编号、状态、方向等）居中对齐
- 说明叙述性文字如果一行放不下，左对齐

#### 4.4 表格宽度单位

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

#### 4.5 空表头处理

如果表头行全部为空（如 `|   |   |`），将第一行数据提升为表头。

#### 4.6 表格样式

- 使用模板的「表格文」样式
- 不加粗表头
- 设置重复表头行（跨页时自动重复）

### 5. 题注

- 表题注在表上方，图题注在图下方
- 使用 Word SEQ 域实现自动编号，表和图独立编号
- 自动从 Markdown 中提取题注名称，输出格式为「表 SEQ-名称」「图 SEQ-名称」
  - 表格：从表上方的 `表 N-N 名称` 行提取名称，原始题注行不再作为普通段落输出
  - 图（Mermaid）：从代码块下方的 `图 N-N 名称` 行提取名称，原始题注行被消费后跳过
  - 图（ASCII）：从 ASCII 块下方的 `图 N-N 名称` 行提取名称，原始题注行被消费后跳过
- 主循环中匹配 `^(表|图)\s*\d+[\-\.]\d+\s*\S` 的行自动跳过，避免题注重复输出
- 打开 Word 后 Ctrl+A → F9 更新编号

题注名称提取逻辑（`get_caption_before` 函数）：

```python
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
```

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
