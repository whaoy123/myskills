---
name: md-to-docx
description: Convert finalized Markdown into a template-aware Word .docx with headings, tables, images, captions, citations, page breaks, and mixed Chinese/English typography. Use when the task is Markdown-to-DOCX production, especially for Chinese academic and engineering documents. Drive the bundled CLI instead of editing script constants, preserve source meaning, and verify the generated DOCX by reopening it before delivery.
metadata:
  short-description: Convert finalized Markdown to validated template-aware DOCX
---

# MD to DOCX

把已经基本定稿的 Markdown 转成可交付的 Word 文档。

这个 Skill 负责**文档转换和版式落地**，不负责替用户重新设计技术内容。

## 职责边界

负责：

- `.md/.markdown` → `.docx`；
- 使用 `.docx/.dotx` 模板；
- 标题、正文、列表、表格、图片、代码块、题注和分页；
- 中西文字体；
- 数字参考文献 `[n]` 的 Word REF 交叉引用；
- Mermaid 已渲染图片的插入；
- 生成后重新打开 DOCX 做结构校验。

不负责：

- 修改论文/报告的事实、结论或技术方案；
- 自动补不存在的参考文献、图片或数据；
- 把现有 Word 文档做复杂修订、批注、红线或版面重构；
- 用“转换成功”代替人工最终排版检查。

如果正文还需要明显润色，先完成内容层修改；工程文档可先经过 `engineering-doc-style` / `humanizer`，再执行本 Skill。不要在 DOCX 生成后再大规模重写正文，否则会破坏已经校验的排版结果。

## 输入

至少需要：

1. Markdown 源文件；
2. 输出 `.docx` 路径。

可选：

- `.docx` / `.dotx` 模板；
- 图片资源目录；
- 已经渲染好的 Mermaid PNG/JPG；
- 页面可用宽度；
- 是否保留 Markdown 手工章节编号；
- 是否关闭一级标题自动分页。

### 输入优先级

模板存在时，以模板已有样式和页面设置为优先；Skill 只补当前转换需要的内容。

图片路径优先按 Markdown 文件所在目录解析；如果用户给 `--asset-dir`，则以该目录为相对图片根目录。

页面可用宽度默认从当前 Word 文档的纸张和左右页边距计算；只有用户或模板要求特殊宽度时才显式传 `--page-width-cm`。

## 固定 CLI

脚本位于：

```text
md-to-docx/md2docx.py
```

基本调用：

```bash
python md2docx.py \
  --input report.md \
  --output report.docx
```

使用模板：

```bash
python md2docx.py \
  --input report.md \
  --template report.dotx \
  --output report.docx \
  --report report_validation.json
```

Mermaid 代码块本身不在本脚本里渲染。先把 Mermaid 渲染成图片，再按文档出现顺序传入：

```bash
python md2docx.py \
  -i report.md \
  -t report.dotx \
  -o report.docx \
  --mermaid-image system.png \
  --mermaid-image fpga.png
```

可选参数：

```text
--asset-dir <dir>
--mermaid-image <path>      # 可重复
--page-width-cm <number>
--keep-heading-numbering
--no-chapter-page-breaks
--strict-assets
--report <json>
```

禁止再通过修改 `md2docx.py` 顶部常量来切换项目。

## 支持的 Markdown 子集

当前正式支持：

- `#` ~ `######` 标题；Word 中映射到最多三级 Heading；
- 普通段落；
- `-` / `*` 无序列表；
- `1.` 有序列表；
- pipe table；
- fenced code block；
- Mermaid fenced block + 外部渲染图片；
- 标准图片：`![caption](path)`；
- `[1]`、`[1, 2]` 等数字引用；
- `表 1-1 名称` / `图 1-1 名称` 形式的题注提示。

没有明确支持的复杂 Markdown 语法不要假设一定正确转换。遇到 HTML、复杂嵌套列表、脚注、数学公式或特殊扩展时，先检查实际输出。

## 模板策略

### `.docx`

直接作为基础文档打开。

### `.dotx`

脚本在临时文件中转换 content type 后加载，不修改原模板。

### 无模板

使用 `python-docx` 的基础空白文档继续生成，不因缺少模板阻塞基本转换。

### 自定义样式缺失

`图片`、`表格文`、`Caption`、`No Spacing` 等样式存在则使用；不存在时降级到 Word 基础样式或直接格式，不因为缺少某个项目专用样式直接失败。

## 图片与 Mermaid

### 普通 Markdown 图片

```markdown
![系统结构](images/system.png)
```

相对路径从 `--asset-dir` 或 Markdown 所在目录解析。

### Mermaid

Markdown 中可以写：

````markdown
```mermaid
graph TD
    A --> B
```
图 1-1 系统结构
````

Mermaid 图片通过重复的 `--mermaid-image` 按出现顺序匹配。

如果图片缺失：

- 默认插入明确的缺失占位并记录到 validation report；
- `--strict-assets` 下直接失败。

不得用无关图片静默替代缺失资源。

## 表格规则

- 表格使用 `Table Grid`；
- 表头跨页重复；
- 默认按内容估算列宽；
- 短列优先保持紧凑；
- 总宽不超过当前页面可用宽度；
- 表格中的数字引用同样转成 REF 字段。

列宽算法只是排版辅助。复杂表格仍需最终视觉检查，不能把算法输出当成版面正确性的证明。

## 引用处理

正文中的数字引用：

```text
性能见文献[22]
```

会生成上标 Word `REF` 字段。

参考文献条目支持：

```text
[22] ...
```

或进入“参考文献 / References”章节后的：

```text
22. ...
```

脚本为编号建立 bookmark，再由正文引用跳转。

只建立交叉引用关系，不负责核实题录真实性或 GB/T 7714 格式；题录生成/核验交给对应 citation Skill。

## 固定工作流程

### Step 1 — Inspect source

检查：

- Markdown 是否存在；
- 图片和 Mermaid 数量；
- 是否依赖模板专有样式；
- 是否包含当前脚本不明确支持的复杂语法。

### Step 2 — Finalize prose before conversion

如果用户同时要求润色或修改内容，先修改 Markdown，再转换。

转换阶段原则上不改技术语义。

### Step 3 — Resolve template and assets

确认：

- 模板路径；
- 图片相对路径根目录；
- Mermaid 渲染图与代码块顺序；
- 输出路径。

### Step 4 — Run CLI

优先带 `--report`：

```bash
python md2docx.py ... --report validation.json
```

### Step 5 — Structural validation

脚本保存后重新使用 `python-docx` 打开生成文件，至少检查：

- DOCX 可以重新打开；
- 新增表格数量在保存后没有丢失；
- 新增嵌入图片数量在保存后没有丢失；
- 模板原有表格/图片计入 baseline，不会被误判成新内容；
- 缺失资源被明确记录。

结构校验 FAIL 时不得直接交付。

### Step 6 — Visual verification

如果当前环境支持渲染或打开 Word，最终再检查：

- 一级/二级/三级标题；
- 分页；
- 表格是否过宽或异常折行；
- 图片大小和题注；
- 中英文字体；
- 引用字段；
- 页面首尾是否出现明显孤行或空页。

结构 PASS 不等于视觉排版一定 PASS。

## 输出

正式交付：

```text
<name>.docx
```

建议保留内部校验：

```text
<name>_validation.json
```

默认向用户报告：

- DOCX 路径；
- 是否使用模板；
- 表格/图片数量；
- 是否有 missing assets；
- 结构校验 PASS/FAIL；
- 仍需人工看的视觉问题（如果有）。

## 验收条件

只有以下条件同时满足才算转换完成：

1. 输出 `.docx` 已生成；
2. 文件可以被 `python-docx` 重新打开；
3. 表格/图片结构校验通过；
4. missing assets 已处理或明确报告；
5. 没有为了适配模板改变 Markdown 的技术事实；
6. 若任务要求正式交付版，已完成可用范围内的视觉检查。

## Tests

运行：

```bash
python -m unittest discover -s tests -v
```

测试用于保护基础转换、表格、引用、图片缺失记录和 DOCX 回读，不替代具体模板的视觉验收。
