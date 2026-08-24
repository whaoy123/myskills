# md-to-docx

把 Markdown 转成模板感知、可回读校验的 Word `.docx`。

适合中文技术报告、课程报告、论文草稿和工程文档。支持标题、正文、列表、表格、图片、Mermaid 渲染图、题注、数字参考文献交叉引用和中英文字体处理。

## 安装

```bash
pip install python-docx
```

## 基本使用

```bash
python md2docx.py \
  --input report.md \
  --output report.docx
```

使用 `.docx/.dotx` 模板：

```bash
python md2docx.py \
  --input report.md \
  --template report.dotx \
  --output report.docx \
  --report report_validation.json
```

## 图片

标准 Markdown 图片：

```markdown
![系统结构](images/system.png)
```

相对路径默认从 Markdown 所在目录解析，也可指定：

```bash
--asset-dir /path/to/assets
```

Mermaid 代码块先由外部工具渲染为图片，再按文档出现顺序重复传入：

```bash
--mermaid-image system.png \
--mermaid-image fpga.png
```

缺失图片默认写入占位并记录到 validation report；需要严格模式时使用：

```bash
--strict-assets
```

## 常用参数

```text
-i, --input <file.md>
-o, --output <file.docx>
-t, --template <file.docx|file.dotx>
--asset-dir <dir>
--mermaid-image <image>      # 可重复
--page-width-cm <number>
--keep-heading-numbering
--no-chapter-page-breaks
--strict-assets
--report <report.json>
```

## 校验

脚本保存后会重新用 `python-docx` 打开输出文件，并核对表格和嵌入图片数量。推荐始终保存 `--report`。

结构校验只能证明 DOCX 可打开、主要对象没有在写入过程中丢失；正式交付仍应再看一次标题、分页、表格宽度、图片和题注的视觉效果。

## 测试

```bash
python -m unittest discover -s tests -v
```
