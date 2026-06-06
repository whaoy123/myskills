# md-to-docx

Convert Markdown documents into Word `.docx` files with template-aware formatting.

This skill is intended for Chinese academic, course, and technical reports where the output must follow a Word template and needs reliable handling of headings, tables, images, captions, page breaks, and mixed Chinese/English typography.

## Files

- `SKILL.md`: Codex skill instructions and activation metadata.
- `md2docx.py`: Conversion script based on `python-docx`.

## Dependencies

```bash
pip install python-docx
```

## Usage

The current script is configured through constants near the top of `md2docx.py`:

```python
TEMPLATE_SRC = "path/to/template.dotx"
MD_PATH = "path/to/source.md"
OUT_PATH = "path/to/output.docx"
MERMAID_SYS = "path/to/diagram1.png"
MERMAID_FPGA = "path/to/diagram2.png"
```

Update those paths for the target project, then run:

```bash
python md2docx.py
```

After generating the Word file, open or render it to verify headings, tables, captions, images, fonts, and page breaks.
