# myskills

Reusable Codex skills for hardware design and technical documentation workflows.

## Skills

### RTL Design & Verification

| Skill | Description |
|-------|-------------|
| [rtl-stepwise-coding](rtl-stepwise-coding/SKILL.md) | Stepwise RTL collaboration workflow: one key question per round, confirmed design rules, small synthesizable increments, project-rule awareness, and verification handoff. Uses `synthesizable-human-rtl` for RTL coding standards. |
| [synthesizable-human-rtl](synthesizable-human-rtl/SKILL.md) | Current preferred RTL writing standard for synthesizable Verilog/SystemVerilog: synthesis-safe design, readable handwritten structure, semantic names, Chinese intent comments, and minimal incremental implementation. |
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

### Citation & Bibliography (GB/T 7714—2025)

| Skill | Description |
|-------|-------------|
| [gbt7714-2025-citation-generator](gbt7714-2025-citation-generator/SKILL.md) | 从 DOI、URL、正式出版页面、题名信息或论文 PDF 中提取并核实元数据，按 GB/T 7714—2025 生成期刊论文、会议论文、图书、学位论文、报告、标准、专利、网站和网页等参考文献。 |
| [gbt7714-2025-citation-auditor](gbt7714-2025-citation-auditor/SKILL.md) | 检查和修订现有参考文献是否符合 GB/T 7714—2025，并可通过正式网页或论文 PDF 核验作者、题名、期刊或会议名称、年份、卷期、页码、文章编号、出版项、报告编号和 DOI。 |

### 日程管理 / Dida Planning (滴答清单)

| Skill | Description |
|-------|-------------|
| [dida-cli](dida-planning-skills/dida-cli/SKILL.md) | 通过本地 DIDA CLI 安全读写滴答清单/Dida365：任务、清单、标签、专注记录、习惯与倒计时的查询和更新，不做规划决策。 |
| [dida-daily-planner](dida-planning-skills/dida-daily-planner/SKILL.md) | 构建/修订滴答清单每日时间块日程：非重叠时段、固定/受保护/可移动块、依赖检查、当前时区、天气任务更新、容量、休息与重排。 |
| [dida-planning-core](dida-planning-skills/dida-planning-core/README.md) | dida 系列共享核心：任务字段契约、系统规范、调度/依赖/进度/估算/记忆策略引擎、迁移脚本与测试。 |
| [dida-planning-memory](dida-planning-skills/dida-planning-memory/SKILL.md) | 保存/检索/更新/遗忘 Dida 规划记忆，不复制任务状态或配置文件。 |
| [dida-planning-profile](dida-planning-skills/dida-planning-profile/SKILL.md) | 初始化/检查/更新“系统配置”NOTE 任务：工作时长、精力、移动权限、估时覆盖、任务体/标签协议、时区、天气与健身。 |
| [dida-task-breakdown](dida-planning-skills/dida-task-breakdown/SKILL.md) | 将父任务拆解为阶段、可执行子任务、完成标准与可执行依赖。 |
| [dida-task-capture](dida-planning-skills/dida-task-capture/SKILL.md) | 捕获任务/想法/提醒/项目到滴答清单：收集箱、简洁标题、正文、父任务、清单选择与隐私处理。 |
| [dida-task-estimator](dida-planning-skills/dida-task-estimator/SKILL.md) | 估算/重估任务日历占用：任务特征、自底向上范围、相似完成任务、置信度收缩与风险覆盖。 |
| [dida-task-progress](dida-planning-skills/dida-task-progress/SKILL.md) | 开始/暂停/等待/恢复/更新进度/完成/删除任务，记录专注与实际时间证据，更新父任务进度并追加校准批注。 |
| [dida-weekly-review](dida-planning-skills/dida-weekly-review/SKILL.md) | 周复盘：逾期与截止风险、停滞父任务、等待依赖、估时绩效、容量与下周任务池。 |

### Hardware Design / Altium & Analog

| Skill | Description |
|-------|-------------|
| [altium-schematic-autowire](altium-schematic-autowire/SKILL.md) | 根据已确定的元件/引脚/网络连接关系，生成可审计的 Altium Designer 原理图批量放置与自动连线方案（DelphiScript/.PrjScr、CSV、校验报告）；不替代电路拓扑决策。 |
| [analog-acquisition-error-budget](analog-acquisition-error-budget/SKILL.md) | 计算/合并/审计模拟采集与 ADC 链路误差：分压器、分流、隔离放大器、运放、滤波器、多路复用器、ADC、基准、时钟、PCB、RMS 算法与校准；统一折算到报告端并分开最坏值与 RSS。 |

### Interactive Questioning

| Skill | Description |
|-------|-------------|
| [grilling](grilling/SKILL.md) | 对计划、决定或想法进行持续压力测试，逐题追问并给出建议答案，直到达成共识。 |
| [grill-me](grill-me/SKILL.md) | 以连续追问（/grilling 会话）打磨计划或设计。 |

### Workflow Orchestration

| Skill | Description |
|-------|-------------|
| [tiered-model-orchestrator](tiered-model-orchestrator/SKILL.md) | 由主控模型负责方案、任务派发、审核和最终验收，由一个或多个执行模型在独立 Codex 任务中并行实现与测试；每次触发先确认模型和并发数。 |

## Usage

Each skill lives in its own directory with a `SKILL.md` that serves as the skill definition. Some skills include supplementary files:

- `agents/` — Agent configuration for OpenCode/Codex environments
- `references/` — Reference documents for coding standards and style guides
- `templates/` — Template spreadsheets for output formatting
- `examples/` — Example outputs for format reference
