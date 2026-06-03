# md-to-docx

将中文技术方案 Markdown 文档转换为基于指定 Word 模板的 `.docx` 文件。

## 功能

- 自动加载 `.dotx` 模板并继承样式
- 表格列宽按内容自适应（含 Word 单元格边距计算）
- 题注使用 Word SEQ 域，表和图独立编号，F9 一键更新
- Mermaid 图渲染为 PNG 插入
- 标题三级以内，每章自动分页
- 中西文混排（宋体 + Times New Roman）

## 依赖

```bash
pip3 install python-docx
```

## 使用

```bash
python3 md2docx.py
```

修改脚本顶部的常量即可适配不同项目。
