# myskills

Reusable Codex skills for hardware design and technical documentation workflows.

## Skills

### RTL Design & Verification

| Skill | Description |
|-------|-------------|
| [rtl-stepwise-coding](rtl-stepwise-coding/SKILL.md) | Stepwise RTL collaboration workflow: one key question per round, confirmed design rules, small synthesizable increments, project-rule awareness, and verification handoff. Uses `synthesizable-human-rtl` for RTL coding standards. |
| [synthesizable-human-rtl](synthesizable-human-rtl/SKILL.md) | Current preferred RTL writing standard for synthesizable Verilog/SystemVerilog: synthesis-safe design, readable handwritten structure, semantic names, Chinese intent comments, and minimal incremental implementation. |
| [synthesizable-systemverilog](synthesizable-systemverilog/SKILL.md) | Synthesizable SystemVerilog coding rules with Must/Should/Tool-gated levels. Covers clocking, reset, CDC, types, assignments, FSM style, and synthesis boundaries. Paired with `rtl-human-style`. |
| [rtl-human-style](rtl-human-style/SKILL.md) | Human-readable RTL and testbench style. Emphasizes readable decomposition, business-meaningful names, Chinese explanatory comments, and hand-written feel. |
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
