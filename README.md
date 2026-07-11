# myskills

Reusable Codex skills for hardware design and technical documentation workflows.

## Skills

### RTL Design & Verification

| Skill | Description |
|-------|-------------|
| [synthesizable-human-rtl](synthesizable-human-rtl/SKILL.md) | 合并后的可综合 RTL 规范：覆盖 SystemVerilog、时钟复位、FSM、采样窗口、错误处理，并强调人类可读的结构、语义命名和中文意图注释。 |
| [grill-driven-rtl-design](grill-driven-rtl-design/SKILL.md) | 以设计文档质询、逐拍时序确认和增量实现驱动 RTL 设计；适合需求仍在讨论、需要边问边写的协议模块。 |
| [rtl-adversarial-tb](rtl-adversarial-tb/SKILL.md) | Adversarial three-phase workflow for generating SV testbenches: (1) verification plan, (2) adversarial review until approved, (3) TB authoring and simulation. |

### PCB & Wiring Documentation

| Skill | Description |
|-------|-------------|
| [connector-wiring-table-generator](connector_wiring_table_skill/SKILL.md) | Generate polished xlsx wiring tables for adapter cables and harnesses from schematics, connector pin definitions, and example workbooks. Connector-agnostic — works with circular, D-sub, aviation, terminal block, and board-to-wire connectors. |
| [pcb-soldering-table-from-schematic](pcb_soldering_table_skill/SKILL.md) | Generate PCB soldering/assembly checklists from schematics, BOMs, and assembly drawings. Outputs a formatted xlsx with designators, part numbers, packages, quantities, solder joint counts, and notes for the soldering technician. |

### Document Production

| Skill | Description |
|-------|-------------|
| [md-to-docx](md-to-docx/SKILL.md) | Convert Markdown documents to Word `.docx` with template-aware formatting. Designed for Chinese academic, course, and technical reports with mixed Chinese/English typography, SEQ caption numbering, and citation formatting. |

## Usage

Each skill lives in its own directory with a `SKILL.md` that serves as the skill definition. Some skills include supplementary files:

- `agents/` — Agent configuration for OpenCode/Codex environments
- `references/` — Reference documents for coding standards and style guides
- `templates/` — Template spreadsheets for output formatting
- `examples/` — Example outputs for format reference
