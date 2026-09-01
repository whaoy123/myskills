# My Codex Skills

Reusable Codex and AI Agent skills for hardware design, RTL development, technical research, engineering documentation, document automation, and productivity workflows.

## Skill Catalog

### Technical Research, Context & Planning

| Skill | Description |
|-------|-------------|
| [engineering-prestudy](engineering-prestudy/SKILL.md) | Orchestrates technical prestudy from initial understanding through evidence-backed research, design tradeoffs, staged implementation planning, and optional Dida handoff. |
| [research-understanding](research-understanding/SKILL.md) | Builds and refines the project mental model, identifies conceptual gaps, and maintains project-specific knowledge state. |
| [research-landscape](research-landscape/SKILL.md) | Researches authoritative sources, standards, papers, products, open-source projects, predecessor implementations, pitfalls, contradictions, and reusable evidence. |
| [research-design-planning](research-design-planning/SKILL.md) | Converts research evidence into trade studies, confirmed decisions, project stages, acceptance criteria, dependencies, and Dida-compatible work packages. |
| [user-context-profile](user-context-profile/SKILL.md) | Provides reusable user background, knowledge level, preferences, goals, and constraints to other skills while keeping private runtime context outside the distributable package. |

### RTL Design & Verification

| Skill | Description |
|-------|-------------|
| [rtl-design-flow](rtl-design-flow/SKILL.md) | Orchestrates the RTL module flow across Contract, Design, Coding, Pre-TB Review, Verification, Debug/Regression, and stage gates without duplicating child-skill rules. |
| [rtl-module-contract](rtl-module-contract/SKILL.md) | Produces a compact `module_contract.md` that freezes interface, module purpose, responsibilities, and externally observable capabilities before detailed RTL design. |
| [rtl-design-doc](rtl-design-doc/SKILL.md) | Produces a stable `rtl_design.md` describing the module's main flow, responsibility split, key storage, timing semantics, and design intent. |
| [synthesizable-human-rtl](synthesizable-human-rtl/SKILL.md) | RTL coding standard for synthesis-safe Verilog/SystemVerilog expression, project-compatible language usage, semantic naming, formatting, structure, and intent-focused comments. |
| [rtl-pre-tb-review](rtl-pre-tb-review/SKILL.md) | Runs a lightweight pre-TB static review for interface, width, reset, drivers, FSM control, handshake, counters, and consistency with the approved design. |
| [rtl-verification](rtl-verification/SKILL.md) | Builds the verification plan, SystemVerilog TB, simulation scripts, Questa wave setup, debug record, and regression loop from the approved Contract and Design. |
| [rtl-adversarial-tb](rtl-adversarial-tb/SKILL.md) | Uses an adversarial three-stage workflow for verification-plan review, SystemVerilog TB authoring, and simulation. |
| [questa-wave-layout](questa-wave-layout/SKILL.md) | Generates readable Questa/ModelSim waveform layouts and `.do` scripts from transaction semantics and verification goals. |

### Hardware Design & Analog

| Skill | Description |
|-------|-------------|
| [analog-acquisition-error-budget](analog-acquisition-error-budget/SKILL.md) | 计算、合并和审计模拟采集与 ADC 链路误差，统一折算到报告端，并分开最坏值与 RSS；复杂场景由确定性脚本计算。 |
| [hardware-power-budget](hardware-power-budget/SKILL.md) | 从原理图、Netlist、BOM 与官方数据手册建立整板/整机电源预算，按 rail 汇总典型/最坏电流与功耗并检查器件容量。 |
| [pcb-schematic-bom-review](pcb-schematic-bom-review/SKILL.md) | 交叉审查设计背景、原理图 PDF、BOM、网表与官方手册，检查真实连线、阻容感与电源参数、隔离/保护、MPN 与 Footprint、重复物料，并给出分级投板结论。 |
| [national-instruments-clean-uninstall](national-instruments-clean-uninstall/SKILL.md) | Cleanly remove all NI software, MAX/DAQmx configuration, residual files, and registry entries on Windows. |
| [national-instruments-cdaq-setup](national-instruments-cdaq-setup/SKILL.md) | Installs a clean cDAQ stack with NI Package Manager, NI-DAQmx/MAX, and FlexLogger Lite while avoiding unnecessary NI drivers. |

### PCB & Wiring Documentation

| Skill | Description |
|-------|-------------|
| [connector-wiring-table-generator](connector_wiring_table_skill/SKILL.md) | Generates deterministic `.xlsx` wiring tables from AD pin/net exports, external connector pinouts, and signal metadata, with script validation and round-trip auditing. |
| [pcb-soldering-table-from-schematic](pcb_soldering_table_skill/SKILL.md) | Generates PCB soldering/assembly checklists from schematics, BOM, procurement, and invoice data with deterministic quantity and reconciliation checks. |

### Document Production, Citation & Reimbursement

| Skill | Description |
|-------|-------------|
| [thesis-opening-report-auditor](thesis-opening-report-auditor/SKILL.md) | 审阅中文Word开题报告的结构、题注、交叉引用、参考文献原生编号、中文与英文/字母数字边界空格、修订和提交风险；支持按用户授权修改副本。 |
| [md-to-docx](md-to-docx/SKILL.md) | Converts Markdown to template-aware Word `.docx` for Chinese academic, course, and technical reports with mixed typography, captions, and citation formatting. |
| [material-reimbursement-table-generator](material_reimbursement_table_skill/SKILL.md) | 从采购发票 PDF 提取明细并生成或更新科研与办公材料验收单 Excel，支持税额、折扣、运费、动态公式和模板格式继承。 |
| [invoice-soldering-components-extractor](invoice_components_extractor_skill/SKILL.md) | 从采购发票 PDF 提取焊接元器件，整理类别、型号、封装和数量并导出 Excel/Markdown。 |
| [gbt7714-2015-citation-generator](gbt7714-2015-citation-generator/SKILL.md) | 从 DOI、URL、正式出版页面、题名信息或论文 PDF 核实元数据并生成 GB/T 7714—2015 参考文献。 |
| [gbt7714-2015-citation-auditor](gbt7714-2015-citation-auditor/SKILL.md) | 审核和修订 GB/T 7714—2015 参考文献，并通过正式网页或论文 PDF 核验关键元数据。 |
| [gbt7714-2025-citation-generator](gbt7714-2025-citation-generator/SKILL.md) | 从 DOI、URL、正式出版页面、题名信息或论文 PDF 核实元数据并生成 GB/T 7714—2025 参考文献。 |
| [gbt7714-2025-citation-auditor](gbt7714-2025-citation-auditor/SKILL.md) | 审核和修订 GB/T 7714—2025 参考文献，并通过正式网页或论文 PDF 核验关键元数据。 |

### Human-Facing Documentation & Finalization

| Skill | Description |
|-------|-------------|
| [engineering-doc-style](engineering-doc-style/SKILL.md) | Engineering-document style layer for direct, natural, information-dense design notes, interface descriptions, technical records, and reports. |
| [humanizer](humanizer/SKILL.md) | Final writing layer for concise, direct, natural prose that removes common AI-writing patterns and unnecessary defensive wording while preserving required precision. |
| [no-negative-echo](no-negative-echo/SKILL.md) | Finalizes human-facing artifacts from the accepted, verified state and checks titles, filenames, comments, metadata, commits, PR text, release notes, and handoffs for session-history residue. |

### Interactive Questioning & Thinking Stress-Test

| Skill | Description |
|-------|-------------|
| [grill-me](grill-me/SKILL.md) | 对计划、决定或想法进行持续深度压力测试，逐题追问并给出建议答案，直到形成可执行结论。 |

### Fitness & Training

| Skill | Description |
|-------|-------------|
| [tan-chengyi-perspective](tan-chengyi-perspective/SKILL.md) | 原样收录 `harpercoddog/Tanchengyi-Coach`：基于谭成义公开训练内容安排训练计划、分析动作、处理平台期，并将训练、营养、睡眠和恢复组织成可复盘闭环。 |

### Software Engineering & Workflow Orchestration

| Skill | Description |
|-------|-------------|
| [karpathy-guidelines](karpathy-guidelines/SKILL.md) | Core software-engineering, coding, and AI-system design principles based on Andrej Karpathy's public guidance. |
| [tiered-model-orchestrator](tiered-model-orchestrator/SKILL.md) | Uses the current conversation as the orchestrator for Explorer, Worker, Tester, and Reviewer agents, with task-topology planning, parallel execution, repair loops, independent review, and final acceptance. |

### 日程管理 / Dida Planning (滴答清单)

| Skill | Description |
|-------|-------------|
| [dida-cli](dida-planning-skills/dida-cli/SKILL.md) | 通过本地 DIDA CLI 读写滴答清单/Dida365 的任务、清单、标签、专注记录、习惯与倒计时。 |
| [dida-daily-planner](dida-planning-skills/dida-daily-planner/SKILL.md) | 构建和修订每日时间块日程，处理固定块、受保护块、依赖、容量、休息和重排。 |
| [dida-planning-core](dida-planning-skills/dida-planning-core/README.md) | Dida 系列共享核心，提供任务字段契约、调度、依赖、进度、估算、记忆策略、容量分析、迁移脚本与测试。 |
| [dida-planning-memory](dida-planning-skills/dida-planning-memory/SKILL.md) | 保存、检索、更新和遗忘 Dida 规划记忆。 |
| [dida-planning-profile](dida-planning-skills/dida-planning-profile/SKILL.md) | 初始化、检查和更新规划 profile，包括工作时长、精力、移动权限、估时覆盖、任务体/标签协议和时区。 |
| [dida-task-breakdown](dida-planning-skills/dida-task-breakdown/SKILL.md) | 将父任务拆解为阶段、可执行子任务、完成标准和依赖。 |
| [dida-task-capture](dida-planning-skills/dida-task-capture/SKILL.md) | 将任务、想法、提醒和项目捕获到滴答清单。 |
| [dida-task-estimator](dida-planning-skills/dida-task-estimator/SKILL.md) | 估算和重估任务的日历占用与风险缓冲。 |
| [dida-task-progress](dida-planning-skills/dida-task-progress/SKILL.md) | 管理任务开始、暂停、等待、恢复、进度更新、完成和删除，并记录实际时间证据。 |
| [dida-weekly-review](dida-planning-skills/dida-weekly-review/SKILL.md) | 执行周复盘，检查逾期、截止风险、停滞父任务、等待依赖、估时表现、容量和下周任务池。 |

---

## Attribution & Open-Source Licenses / 鸣谢与开源许可证

本仓库包含基于开源社区项目整理、引用、改写或直接收录的 Skill。对应来源与署名/许可证要求如下：

| 技能名称 | 使用方式 | 原作者 / 维护者 | 原始开源仓库 / 链接 | 许可证 / 使用要求 |
|---|---|---|---|---|
| **grill-me** | 社区引用 | **Matt Pocock** | [mattpocock/skills](https://github.com/mattpocock/skills) | **MIT License** |
| **karpathy-guidelines** | 思想总结 / 整理 | **Andrej Karpathy** | [karpathy](https://github.com/karpathy) | **MIT License** |
| **humanizer** | 社区引用 | **Siqi Chen (blader)** | [blader/humanizer](https://github.com/blader/humanizer) | **MIT License** |
| **anti-defensive-writing → humanizer** | 融合 / 改写 | **Kiterlin** | [Kiterlin/anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing) | **MIT License** |
| **no-negative-echo** | 社区引用 / 本仓库内再分发 | **LB623** | [LB623/no-negative-echo](https://github.com/LB623/no-negative-echo) | **MIT License** |
| **tan-chengyi-perspective** | 社区引用 / 原样收录 | **harpercoddog** | [harpercoddog/Tanchengyi-Coach](https://github.com/harpercoddog/Tanchengyi-Coach) | **使用或再分发时保留原作者署名、原始仓库链接及上游文件中的来源/鸣谢信息** |

### Third-Party Usage & Redistribution / 第三方使用与再分发

- `humanizer` 中包含来自 `anti-defensive-writing` 的改写内容。调用 `humanizer` 生成、润色或压缩普通文本时，生成结果可以直接使用，无需添加 Kiterlin 署名。再分发对应源码、文档或 substantial portions 时，应保留原作者版权声明和 MIT 许可声明。第三方许可文本见 [`humanizer/THIRD_PARTY_NOTICES.md`](humanizer/THIRD_PARTY_NOTICES.md)。
- `no-negative-echo` 作为独立 Skill 收录。调用该 Skill 生成或清理普通输出时，生成结果可以直接使用，无需添加 LB623 署名。再分发该 Skill、脚本、文档或 substantial portions 时，应保留 `Copyright (c) 2026 LB623` 和 MIT 许可声明。完整许可和来源说明见 [`no-negative-echo/LICENSE`](no-negative-echo/LICENSE) 与 [`no-negative-echo/THIRD_PARTY_NOTICES.md`](no-negative-echo/THIRD_PARTY_NOTICES.md)。
- `tan-chengyi-perspective` 原样收录自 [harpercoddog/Tanchengyi-Coach](https://github.com/harpercoddog/Tanchengyi-Coach)。使用、修改或再分发时，请保留原作者/维护者署名、原始仓库链接，以及上游 README、SKILL、references 和 scripts 中已有的来源与鸣谢信息。

---

## Runtime-State Rule

Distributable skills stay stateless. The repository contains reusable skill definitions, scripts, references, schemas, templates, examples, tests, and agent configuration.

Real user data and project runtime state live outside the distributable package, for example in `~/.prestudy/user-context/` and `<project>/.prestudy/`. Runtime directories, downloaded research libraries, task data, credentials, and personal local paths remain outside this repository.

## Usage

Each skill lives in its own directory with a `SKILL.md` as its primary definition. A skill may also contain:

- `scripts/` — deterministic calculation, validation, initialization, or auditing tools
- `references/` — stable domain or method references
- `schemas/` — input/output contracts
- `templates/` — reusable templates and empty runtime-state shapes
- `examples/` — synthetic or sanitized examples
- `tests/` — deterministic regression checks
- `agents/` — optional agent configuration
