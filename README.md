# myskills

Reusable Codex skills for hardware design, technical documentation, research, and planning workflows.

## Skills

### Research & Prestudy

| Skill | Description |
|-------|-------------|
| [user-context-profile](user-context-profile/SKILL.md) | Shared private user-context layer for background, knowledge level, learning preferences, goals, and reusable constraints. Reuses Dida-owned planning/tool facts when available and keeps user/project data outside distributable skill packages. |
| [engineering-prestudy](engineering-prestudy/SKILL.md) | Orchestrates technical prestudy from initial understanding through evidence-backed landscape research, design tradeoffs, staged implementation planning, and optional Dida handoff. |
| [research-understanding](research-understanding/SKILL.md) | Runs the understanding loop: bridge from existing knowledge, identify conceptual gaps, refine mental models, and maintain project-specific knowledge state. |
| [research-landscape](research-landscape/SKILL.md) | Researches current state, authoritative sources, papers, standards, products, open-source projects, reusable artifacts, contradictions, and evidence with traceable source records. |
| [research-design-planning](research-design-planning/SKILL.md) | Converts evidence into trade studies, confirmed decisions, project stages, outputs, acceptance criteria, dependencies, and a Dida-compatible handoff. |

### RTL Design & Verification

| Skill | Description |
|-------|-------------|
| [rtl-stepwise-coding](rtl-stepwise-coding/SKILL.md) | Stepwise RTL collaboration workflow: one key question per round, confirmed design rules, small synthesizable increments, project-rule awareness, and verification handoff. Uses `synthesizable-human-rtl` for RTL coding standards. |
| [synthesizable-human-rtl](synthesizable-human-rtl/SKILL.md) | Current preferred RTL writing standard for synthesizable Verilog/SystemVerilog: synthesis-safe design, readable handwritten structure, semantic names, Chinese intent comments, and minimal incremental implementation. |
| [rtl-adversarial-tb](rtl-adversarial-tb/SKILL.md) | Adversarial three-phase workflow for generating SV testbenches: (1) verification plan, (2) adversarial review until approved, (3) TB authoring and simulation. |

### PCB & Wiring Documentation

| Skill | Description |
|-------|-------------|
| [connector-wiring-table-generator](connector_wiring_table_skill/SKILL.md) | Generate deterministic xlsx wiring tables from fixed AD pin/net exports, external connector pinouts, and signal metadata, with script validation and round-trip auditing. |
| [pcb-soldering-table-from-schematic](pcb_soldering_table_skill/SKILL.md) | Generate PCB soldering/assembly checklists from schematics/BOM data with deterministic script calculation and validation of quantities and solder-joint counts. |

### Document Production & Reimbursement

| Skill | Description |
|-------|-------------|
| [md-to-docx](md-to-docx/SKILL.md) | Convert Markdown documents to Word `.docx` with template-aware formatting. Designed for Chinese academic, course, and technical reports with mixed Chinese/English typography, SEQ caption numbering, and citation formatting. |
| [material-reimbursement-table-generator](material_reimbursement_table_skill/SKILL.md) | 从各类采购发票 PDF 自动化解析明细并生成/更新科研与办公材料验收单 Excel（支持含税/不含税模式、负数折扣、运费、动态 `=SUM(...)` 公式与模板格式无损继承）。 |
| [invoice-soldering-components-extractor](invoice_components_extractor_skill/SKILL.md) | 从采购发票 PDF 自动化过滤非焊接物料（手套、PCB、外壳、运费、折扣），提取纯焊接元器件清单（类别 + 型号 + 封装 + 数量）并导出 Excel/Markdown。 |

### Citation & Bibliography (GB/T 7714—2025)

| Skill | Description |
|-------|-------------|
| [gbt7714-2025-citation-generator](gbt7714-2025-citation-generator/SKILL.md) | 从 DOI、URL、正式出版页面、题名信息或论文 PDF 中提取并核实元数据，按 GB/T 7714—2025 生成参考文献。 |
| [gbt7714-2025-citation-auditor](gbt7714-2025-citation-auditor/SKILL.md) | 检查和修订现有参考文献是否符合 GB/T 7714—2025，并通过正式网页或论文 PDF 核验关键元数据。 |

### 日程管理 / Dida Planning (滴答清单)

| Skill | Description |
|-------|-------------|
| [dida-cli](dida-planning-skills/dida-cli/SKILL.md) | 通过本地 DIDA CLI 安全读写滴答清单/Dida365：任务、清单、标签、专注记录、习惯与倒计时的查询和更新，不做规划决策。 |
| [dida-daily-planner](dida-planning-skills/dida-daily-planner/SKILL.md) | 构建/修订滴答清单每日时间块日程：非重叠时段、固定/受保护/可移动块、依赖检查、容量、休息与重排。 |
| [dida-planning-core](dida-planning-skills/dida-planning-core/README.md) | dida 系列共享核心：任务字段契约、系统规范、调度/依赖/进度/估算/记忆策略引擎、迁移脚本与测试。 |
| [dida-planning-memory](dida-planning-skills/dida-planning-memory/SKILL.md) | 保存/检索/更新/遗忘 Dida 规划记忆，不复制任务状态或 profile 配置。 |
| [dida-planning-profile](dida-planning-skills/dida-planning-profile/SKILL.md) | 初始化/检查/更新规划 profile：工作时长、精力、移动权限、估时覆盖、任务体/标签协议、时区等。 |
| [dida-task-breakdown](dida-planning-skills/dida-task-breakdown/SKILL.md) | 将父任务拆解为阶段、可执行子任务、完成标准与可执行依赖。 |
| [dida-task-capture](dida-planning-skills/dida-task-capture/SKILL.md) | 捕获任务/想法/提醒/项目到滴答清单。 |
| [dida-task-estimator](dida-planning-skills/dida-task-estimator/SKILL.md) | 估算/重估任务日历占用与风险缓冲。 |
| [dida-task-progress](dida-planning-skills/dida-task-progress/SKILL.md) | 开始/暂停/等待/恢复/更新进度/完成/删除任务并记录实际时间证据。 |
| [dida-weekly-review](dida-planning-skills/dida-weekly-review/SKILL.md) | 周复盘：逾期与截止风险、停滞父任务、等待依赖、估时绩效、容量与下周任务池。 |

### Hardware Design & Analog

| Skill | Description |
|-------|-------------|
| [analog-acquisition-error-budget](analog-acquisition-error-budget/SKILL.md) | 计算/合并/审计模拟采集与 ADC 链路误差：统一折算到报告端并分开最坏值与 RSS，复杂场景由确定性脚本计算。 |
| [hardware-power-budget](hardware-power-budget/SKILL.md) | 从原理图/Netlist/BOM 与官方数据手册建立整板/整机电源预算：按 rail 汇总典型/最坏电流与功耗、加一次设计余量、回推 DCDC/LDO 输入侧并检查最终选型容量。 |

### Interactive Questioning

| Skill | Description |
|-------|-------------|
| [grilling](grilling/SKILL.md) | 对计划、决定或想法进行持续压力测试，逐题追问并给出建议答案，直到达成共识。 |
| [grill-me](grill-me/SKILL.md) | 以连续追问（/grilling 会话）打磨计划或设计。 |

### Workflow Orchestration

| Skill | Description |
|-------|-------------|
| [tiered-model-orchestrator](tiered-model-orchestrator/SKILL.md) | 当前对话直接作为主控，按任务拓扑派发 Explorer、Worker、Tester、Reviewer 等子代理并行执行、返修和独立审核；默认子代理使用 Luna + max，并发数自动决定，不再额外创建二级主控聊天。 |

## Runtime-state rule

Distributable skills must stay stateless. Real user data and project runtime data live outside the skill package, for example in `~/.prestudy/user-context/` and `<project>/.prestudy/`. Do not commit these runtime directories, downloaded research libraries, task data, credentials, or personal local paths into this repository.

## Usage

Each skill lives in its own directory with a `SKILL.md` that serves as the skill definition. Some skills include supplementary files:

- `scripts/` — deterministic calculations, validation, initialization, or auditing
- `references/` — stable domain/method references
- `schemas/` — input/output contracts
- `templates/` — fixed templates and empty runtime-state shapes
- `examples/` — synthetic or sanitized examples
- `tests/` — deterministic regression checks
- `agents/` — optional agent configuration
