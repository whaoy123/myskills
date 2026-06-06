---
name: md-to-docx
description: Convert Markdown files to Word .docx documents, especially Chinese academic, course, and technical reports that need Word templates, headings, tables, images, captions, page breaks, and consistent Chinese/English typography.
metadata:
  short-description: Convert Markdown to Word DOCX with template-aware formatting
---

# md-to-docx

Use this skill when the user asks to convert a Markdown document (`.md`) into a Word document (`.docx`), especially for Chinese academic reports, course reports, technical proposals, or documents that must follow a Word template.

## What This Skill Does

This skill uses `md2docx.py` and `python-docx` to generate a `.docx` file from Markdown. It is designed for template-aware document production rather than plain Markdown export.

Supported behavior includes:

- Loading a `.dotx` Word template by converting its content type so `python-docx` can open it.
- Preserving template styles for headings and body text where possible.
- Handling headings, paragraphs, lists, tables, images, captions, and chapter page breaks.
- Setting mixed Chinese/English fonts, typically SimSun for Chinese and Times New Roman for English.
- Using Word `SEQ` fields for figure/table caption numbering when applicable.
- Rendering numeric citation markers such as `性能[22]` as smaller superscript Word cross-references instead of plain text.
- Calculating table column widths from content instead of blindly stretching every table.
- Inserting pre-rendered Mermaid PNGs when the source document references diagrams.

## Important Local Detail

The bundled script is not currently a parameterized command-line tool. Before running it, inspect and update the constants near the top of `md2docx.py`:

```python
TEMPLATE_SRC = "path/to/template.dotx"
MD_PATH = "path/to/source.md"
OUT_PATH = "path/to/output.docx"
MERMAID_SYS = "path/to/diagram1.png"
MERMAID_FPGA = "path/to/diagram2.png"
```

For a new document, copy or adapt `md2docx.py` into the working project, update these paths, then run the script from that project context.

## Workflow

1. Read the Markdown source and identify required assets such as images or Mermaid output PNGs.
2. Locate the Word template (`.dotx` or `.docx`) the output should follow.
3. Copy/adapt `md2docx.py` if needed, then update `TEMPLATE_SRC`, `MD_PATH`, `OUT_PATH`, and image constants.
4. Ensure dependencies are installed:

```bash
pip install python-docx
```

5. Run the conversion script:

```bash
python md2docx.py
```

6. Open or render the generated `.docx` to verify headings, tables, captions, images, page breaks, and fonts.

## Formatting Rules To Preserve

- Use Word template heading styles for Heading 1/2/3.
- Strip Markdown-style manual chapter numbering from headings when the template handles numbering.
- Insert a page break before each top-level chapter except the first one when producing report-style documents.
- Convert numeric citations in body text, list items, and table cells, such as `[22]` or `[1, 2]`, into small superscript Word `REF` fields using `\* CHARFORMAT`, so Word field updates keep the referenced number superscript. Create matching bookmarks on bibliography entries such as `[22] ...` or, inside a references section, `22. ...`; do not leave citation markers as ordinary baseline text.
- Keep body text around 12 pt unless the template says otherwise.
- Use smaller table text, commonly 10.5 pt, for dense academic or technical tables.
- Set `w:eastAsia` explicitly for Chinese fonts when formatting runs.
- Keep short table columns compact and assign remaining width to description/notes columns.

## When To Use Other Tools

Use the general `doc` or `documents` skill when the task is primarily editing an existing `.docx`, reviewing layout, redlining, or visually verifying a Word document. Use this skill when the main task is Markdown-to-DOCX generation.
