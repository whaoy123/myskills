---
name: markitdown
description: |
  Convert common documents, media, archives, and web-oriented inputs to Markdown with Microsoft's MarkItDown package when an AI/agent workflow needs LLM-friendly text extraction or normalization. Use for PDF, Word, PowerPoint, Excel, images, audio, HTML, CSV/JSON/XML, ZIP, EPUB, and other formats supported by the installed MarkItDown version. Do not use when the task requires pixel-faithful layout preservation or round-trip editing of the original document.
---

# MarkItDown File-to-Markdown Conversion

Use Microsoft's `markitdown` package as a preprocessing layer:

`source file / supported input → MarkItDown → Markdown → downstream search, summarization, indexing, review, or agent workflow`

Upstream project: <https://github.com/microsoft/markitdown>

## When to use

Use this skill when the primary goal is to turn supported source material into compact Markdown that preserves useful document structure for machine consumption.

Typical cases:

- Convert PDF, DOCX, PPTX, XLS/XLSX, HTML, CSV, JSON, XML, EPUB, ZIP, image, or audio inputs to Markdown.
- Normalize mixed document formats before search, indexing, summarization, extraction, comparison, or LLM analysis.
- Create an inspectable `.md` intermediate file before a larger document-processing workflow.

Do not treat MarkItDown as a high-fidelity document renderer. If exact pagination, visual layout, fonts, annotations, drawing geometry, or round-trip Office editing matters, use a format-specific workflow instead.

## Dependency check

Check whether the package is already installed:

```bash
python -m pip show markitdown
```

Install all optional format handlers when broad format coverage is required:

```bash
python -m pip install 'markitdown[all]'
```

For a smaller environment, install only the required extras, for example:

```bash
python -m pip install 'markitdown[pdf,docx,pptx,xlsx]'
```

Do not silently change an existing Python environment if dependency installation is outside the user's requested scope. State the required command instead.

## CLI workflow

Prefer the CLI for one-off deterministic conversion:

```bash
markitdown input.pdf -o output.md
```

If `-o` is unavailable in the installed version, use shell redirection:

```bash
markitdown input.pdf > output.md
```

For a batch job, keep the source files unchanged and write Markdown outputs to a separate directory. Preserve a stable source-to-output filename mapping so later analysis can be traced back to the original file.

## Python API workflow

Use the Python API when conversion is part of a larger script:

```python
from pathlib import Path
from markitdown import MarkItDown

source = Path("report.pdf")
output = Path("report.md")

converter = MarkItDown()
result = converter.convert(str(source))
output.write_text(result.text_content, encoding="utf-8")
```

Keep conversion separate from downstream summarization or transformation. First create or inspect the Markdown representation; then run the next stage.

## Verification

After conversion, check at least these items before treating the Markdown as authoritative input:

1. The output is non-empty and corresponds to the intended source file.
2. Major headings, tables, lists, links, and text blocks are present where expected.
3. Pages or objects dominated by scans, drawings, equations, charts, or unusual embedded content have not silently lost critical information.

If the source is primarily visual, inspect the original alongside the Markdown rather than assuming text extraction captured everything.

## Security boundary

MarkItDown performs file and network I/O with the privileges of the current process. Treat untrusted files and URLs as untrusted inputs, use the narrowest practical access scope, and avoid running conversion with credentials or filesystem permissions that the task does not need.

Do not expose private directories, credentials, tokens, or unrelated local files to a conversion workflow merely for convenience.

## Output contract

When this skill is used, report:

- source input path or identifier;
- Markdown output path, when a file was created;
- conversion command or API path used;
- any material extraction limitation detected during verification.

Do not claim visual or semantic fidelity that was not checked.

## Upstream and license

This skill is an integration wrapper around Microsoft's open-source MarkItDown project; it does not vendor the upstream implementation. MarkItDown is licensed under the MIT License. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
