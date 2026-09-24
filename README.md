# MySkills

用于 Codex 与各类 AI Agent 的可复用 Skill 集合，覆盖硬件设计审核、RTL 开发与验证、技术预研、工程文档、PCB/接线资料生成、参考文献处理、滴答清单任务管理等工作流。

## 技能目录

### 技术预研、设计上下文与事实管理

| Skill | 用途 |
|---|---|
| [engineering-prestudy](engineering-prestudy/SKILL.md) | 从问题理解、资料检索、方案权衡一直推进到分阶段实施计划，并可衔接任务管理。 |
| [research-understanding](research-understanding/SKILL.md) | 建立和修正项目认知模型，识别概念缺口，维护项目知识状态。 |
| [research-landscape](research-landscape/SKILL.md) | 检索标准、论文、官方资料、产品、开源项目、前代实现、常见问题与相互矛盾的证据。 |
| [research-design-planning](research-design-planning/SKILL.md) | 将研究证据转化为方案对比、已确认设计决定、阶段划分、验收标准和依赖关系。 |
| [engineering-design-fact-base](engineering-design-fact-base/SKILL.md) | 将硬件、RTL、嵌入式、接口和器件选型讨论持续沉淀为结构化、可追踪、可更新的工程事实库。 |
| [user-context-profile](user-context-profile/SKILL.md) | 向其他 Skill 提供可复用的用户背景、知识水平、偏好、目标和约束，同时将私有运行态信息留在分发包之外。 |
| [github-shared-memory](github-shared-memory/SKILL.md) | 维护基于 GitHub Markdown 仓库的跨 Agent 共享长期上下文，记录已确认事实、决策、当前状态和下一步。 |

### 硬件设计、原理图与模拟采集

| Skill | 用途 |
|---|---|
| [hardware-design-review](hardware-design-review/SKILL.md) | 硬件主审核入口。基于原理图 PDF、Netlist、BOM、Datasheet 规则模块、PCB 证据和项目条件建立可追踪设计模型，检查连线、参数、信号链、电源/隔离域、BOM/封装一致性、外部接口保护和 PCB 约束，输出 `PASS / FAIL / UNCLEAR / N/A` 以及明确的投板放行判断。 |
| [datasheet-to-design-guide](datasheet-to-design-guide/SKILL.md) | 将具体器件 Datasheet 转换为 `usage-guide.md`、`checklist.md`、`PROVENANCE.md` 和 `module.yaml`，供 `hardware-design-review` 直接加载。 |
| [hardware-power-budget](hardware-power-budget/SKILL.md) | 从原理图、Netlist、BOM 和官方 Datasheet 建立各电源轨负载清单，计算典型/最坏电流、功耗、上游输入需求和 DCDC/LDO 设计余量。 |
| [analog-acquisition-error-budget](analog-acquisition-error-budget/SKILL.md) | 对分压、隔离、运放、滤波、MUX、ADC、基准和算法组成的模拟采集链进行误差预算，并区分最坏值、RSS 与随机噪声。 |
| [national-instruments-cdaq-setup](national-instruments-cdaq-setup/SKILL.md) | 在 Windows 上建立较干净的 NI cDAQ 使用环境，安装 NI Package Manager、NI-DAQmx/MAX 与 FlexLogger Lite。 |
| [national-instruments-clean-uninstall](national-instruments-clean-uninstall/SKILL.md) | 清理 Windows 上的 NI 软件、MAX/DAQmx 配置、残留文件与注册表项。 |

### RTL 设计与验证

| Skill | 用途 |
|---|---|
| [rtl-design-flow](rtl-design-flow/SKILL.md) | RTL 模块开发总流程，组织 Contract、设计、编码、Pre-TB Review、验证、调试/回归和阶段门。 |
| [rtl-module-contract](rtl-module-contract/SKILL.md) | 在详细设计前生成紧凑的 `module_contract.md`，冻结接口、职责和外部可观察行为。 |
| [rtl-design-doc](rtl-design-doc/SKILL.md) | 生成稳定的 `rtl_design.md`，描述主数据流、职责拆分、关键存储、时序语义和设计意图。 |
| [synthesizable-human-rtl](synthesizable-human-rtl/SKILL.md) | 面向可综合 Verilog/SystemVerilog 的编码规范，约束语言用法、命名、结构、格式和注释。 |
| [rtl-pre-tb-review](rtl-pre-tb-review/SKILL.md) | 在写 Testbench 前做轻量静态审核，检查接口、位宽、复位、驱动、FSM、握手、计数器和设计一致性。 |
| [rtl-verification](rtl-verification/SKILL.md) | 从已确认 Contract/Design 构建验证计划、SystemVerilog TB、仿真脚本、Questa 波形、Debug 记录和回归闭环。 |
| [rtl-adversarial-tb](rtl-adversarial-tb/SKILL.md) | 采用对抗式三阶段流程进行验证计划复核、Testbench 编写和仿真。 |
| [questa-wave-layout](questa-wave-layout/SKILL.md) | 根据事务语义和验证目标生成可读的 Questa/ModelSim 波形布局与 `.do` 脚本。 |

### PCB、接线与装配资料

| Skill | 用途 |
|---|---|
| [connector-wiring-table-generator](connector_wiring_table_skill/SKILL.md) | 根据 Altium 引脚网络数据、接口定义和线束规划生成并校验接线表 Excel，支持一对一、多对一/一对多和双绞线。 |
| [pcb-soldering-table-from-schematic](pcb_soldering_table_skill/SKILL.md) | 根据网表、原理图、BOM 和采购证据生成 PCB 焊接/备料清单 Excel，并校验型号、封装、DNP、数量与到货状态。 |
| [invoice-components-extractor](invoice_components_extractor_skill/SKILL.md) | 从采购发票或采购明细中提取可焊接电子元器件采购证据，为后续装配清单提供输入。 |

### 工程文档、论文与参考文献

| Skill | 用途 |
|---|---|
| [thesis-opening-report-auditor](thesis-opening-report-auditor/SKILL.md) | 审阅中文 Word 开题报告的结构、题注、交叉引用、参考文献编号、排版和提交风险。 |
| [thesis-opening-report-reviser](thesis-opening-report-reviser/SKILL.md) | 根据审核问题和用户决策整体修订开题报告，并在修改后再次调用审核 Skill 复核。 |
| [docx-sequential-citation-rebuilder](docx-sequential-citation-rebuilder/SKILL.md) | 重建 Word 顺序编码制参考文献系统，按正文首次出现顺序重排文献，并修复书签、REF 和上角标。 |
| [md-to-docx](md-to-docx/SKILL.md) | 将 Markdown 转换为适合中文学术、课程和技术报告的模板化 Word 文档。 |
| [gbt7714-2015-citation-generator](gbt7714-2015-citation-generator/SKILL.md) | 根据 DOI、URL、正式出版页面、题名信息或论文 PDF 核实元数据并生成 GB/T 7714—2015 参考文献。 |
| [gbt7714-2015-citation-auditor](gbt7714-2015-citation-auditor/SKILL.md) | 审核和修订 GB/T 7714—2015 参考文献，并核验关键元数据。 |
| [gbt7714-2025-citation-generator](gbt7714-2025-citation-generator/SKILL.md) | 根据 DOI、URL、正式出版页面、题名信息或论文 PDF 核实元数据并生成 GB/T 7714—2025 参考文献。 |
| [gbt7714-2025-citation-auditor](gbt7714-2025-citation-auditor/SKILL.md) | 审核和修订 GB/T 7714—2025 参考文献，并核验关键元数据。 |
| [material-reimbursement-table](material_reimbursement_table_skill/SKILL.md) | 从增值税电子发票提取明细，并依据材料/办公验收单模板生成或更新报销 Excel。 |

### 面向人的写作与最终整理

| Skill | 用途 |
|---|---|
| [engineering-doc-style](engineering-doc-style/SKILL.md) | 面向工程设计说明、接口说明、技术记录和报告的写作风格层，强调直接、自然和信息密度。 |
| [humanizer](humanizer/SKILL.md) | 对普通文本做最终润色和压缩，减少常见 AI 写作痕迹与多余防御性表达。 |
| [no-negative-echo](no-negative-echo/SKILL.md) | 在交付前清理标题、文件名、注释、元数据、Commit/PR 文本、Release Note 和交接材料中的会话历史残留。 |

### 软件工程与工作流编排

| Skill | 用途 |
|---|---|
| [ponytail](ponytail/SKILL.md) | 编码时优先 YAGNI、复用现有实现、标准库和最小可行 diff，抑制不必要的抽象、依赖、脚手架和过度设计。 |
| [karpathy-guidelines](karpathy-guidelines/SKILL.md) | 基于 Andrej Karpathy 公开内容整理的软件工程、编码和 AI 系统设计原则。 |
| [markitdown](markitdown/SKILL.md) | 封装 Microsoft MarkItDown，将 PDF、Word、PowerPoint、Excel、图片、音频、HTML、压缩包和 EPUB 等转换为适合 LLM 处理的 Markdown。 |
| [tiered-model-orchestrator](tiered-model-orchestrator/SKILL.md) | 当前会话保留最终主控与验收权；Ruflo 可用时作为多 Agent 执行层，负责 swarm、workflow、状态、worktree 隔离和执行记忆，不可用时回退到原生子代理或独立 Codex 任务。 |

### 滴答清单任务管理

| Skill | 用途 |
|---|---|
| [dida-manager](dida-planning-skills/dida-manager/SKILL.md) | 滴答清单体系的顶层入口和路由中枢，判断局部任务操作或全局规划，并分发给对应子 Skill；优先使用 MCP/连接器。 |
| [dida-cli](dida-planning-skills/dida-cli/SKILL.md) | 在没有可用连接器时，通过本地 DIDA CLI 读写滴答清单任务及相关数据。 |
| [dida-daily-planner](dida-planning-skills/dida-daily-planner/SKILL.md) | 处理每日任务安排、容量、固定约束、依赖和重排。 |
| [dida-planning-core](dida-planning-skills/dida-planning-core/SKILL.md) | Dida 系列共享核心，提供字段契约、依赖、进度、估时、规划状态和相关确定性脚本。 |
| [dida-planning-memory](dida-planning-skills/dida-planning-memory/SKILL.md) | 保存、检索、更新和整理 Dida 规划使用的长期记忆。 |
| [dida-planning-profile](dida-planning-skills/dida-planning-profile/SKILL.md) | 初始化、检查和更新规划 Profile，包括估时覆盖、任务体/标签协议和其他规划约定。 |
| [dida-task-breakdown](dida-planning-skills/dida-task-breakdown/SKILL.md) | 将父任务拆为阶段、可执行子任务、完成标准和依赖。 |
| [dida-task-capture](dida-planning-skills/dida-task-capture/SKILL.md) | 将任务、想法、提醒和项目捕获到滴答清单。 |
| [dida-task-estimator](dida-planning-skills/dida-task-estimator/SKILL.md) | 根据任务特征和历史信息进行估时和重估。 |
| [dida-task-progress](dida-planning-skills/dida-task-progress/SKILL.md) | 管理任务开始、暂停、等待、恢复、进度更新、完成和删除，并记录实际进展证据。 |
| [dida-weekly-review](dida-planning-skills/dida-weekly-review/SKILL.md) | 执行周复盘，检查逾期、截止风险、停滞任务、等待依赖、估时表现和下周交付任务。 |

### 互动式思考与训练

| Skill | 用途 |
|---|---|
| [grill-me](grill-me/SKILL.md) | 对计划、决定或想法做持续压力测试，逐题追问并推动形成可执行结论。 |
| [tan-chengyi-perspective](tan-chengyi-perspective/SKILL.md) | 基于谭成义公开训练内容安排训练计划、分析动作、处理平台期，并组织训练、营养、睡眠和恢复闭环。 |

---

## 使用方式

每个 Skill 位于独立目录中，以 `SKILL.md` 作为主定义文件；根据需要还可以包含：

- `scripts/`：确定性计算、校验、初始化或审计脚本；
- `references/`：稳定的领域规则、方法和来源资料；
- `schemas/`：输入输出与状态结构定义；
- `templates/`：可复用模板和空白运行态结构；
- `examples/`：合成或脱敏示例；
- `tests/`：确定性回归测试；
- `agents/`：可选 Agent 配置。

可分发 Skill 应保持无状态。真实用户数据、项目运行态、下载资料、任务数据、凭据以及个人本地路径应保存在仓库之外，例如 `~/.prestudy/user-context/`、`<project>/.prestudy/` 或具体项目自己的运行态目录中。

## 鸣谢与开源许可证

本仓库包含基于开源社区项目整理、引用、改写或直接收录的 Skill。对应来源与许可要求如下。

| Skill | 使用方式 | 原作者 / 维护者 | 上游项目 | 许可证 / 要求 |
|---|---|---|---|---|
| **grill-me** | 社区引用 | **Matt Pocock** | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT License |
| **karpathy-guidelines** | 思想总结 / 整理 | **Andrej Karpathy** | [karpathy](https://github.com/karpathy) | MIT License |
| **ponytail** | 社区引用 / 原样收录 | **Dietrich Gebert** | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT License；再分发时保留版权与许可声明 |
| **markitdown** | 工具集成 / Skill 封装 | **Microsoft Corporation** | [microsoft/markitdown](https://github.com/microsoft/markitdown) | MIT License；运行时依赖遵循上游许可 |
| **tiered-model-orchestrator（Ruflo 集成）** | 执行层适配 / 流程思想参考 | **ruvnet** | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | MIT License；本 Skill 的主控与验收规则仍为本仓库自有 |
| **humanizer** | 社区引用 | **Siqi Chen (blader)** | [blader/humanizer](https://github.com/blader/humanizer) | MIT License |
| **anti-defensive-writing → humanizer** | 融合 / 改写 | **Kiterlin** | [Kiterlin/anti-defensive-writing](https://github.com/Kiterlin/anti-defensive-writing) | MIT License |
| **no-negative-echo** | 社区引用 / 仓库内再分发 | **LB623** | [LB623/no-negative-echo](https://github.com/LB623/no-negative-echo) | MIT License |
| **tan-chengyi-perspective** | 社区引用 / 原样收录 | **harpercoddog** | [harpercoddog/Tanchengyi-Coach](https://github.com/harpercoddog/Tanchengyi-Coach) | 再分发时保留原作者署名、原仓库链接及上游来源/鸣谢信息 |
| **datasheet-to-design-guide** | 基于流程思想改写 / 派生 | **Sergey Lebedev / Londeren** | [Londeren/claude-plugins](https://github.com/Londeren/claude-plugins)（`book-to-skill`） | MIT License；再分发时保留版权与许可声明 |

补充说明：

- `markitdown` 只封装 Microsoft MarkItDown 的使用方式，不在本仓库复制其实现源码；完整说明见 [`markitdown/THIRD_PARTY_NOTICES.md`](markitdown/THIRD_PARTY_NOTICES.md)。
- `ponytail` 原样收录上游核心 Skill，并保留 MIT License，见 [`ponytail/LICENSE`](ponytail/LICENSE) 与 [`ponytail/THIRD_PARTY_NOTICES.md`](ponytail/THIRD_PARTY_NOTICES.md)。
- `tiered-model-orchestrator` 参考 Ruflo 的公开执行模型，把 Ruflo 作为可选运行后端；来源说明见 [`tiered-model-orchestrator/THIRD_PARTY_NOTICES.md`](tiered-model-orchestrator/THIRD_PARTY_NOTICES.md)。
- `humanizer` 包含来自 `anti-defensive-writing` 的改写内容；再分发相关源码或 substantial portions 时应保留相应 MIT 声明，见 [`humanizer/THIRD_PARTY_NOTICES.md`](humanizer/THIRD_PARTY_NOTICES.md)。
- `no-negative-echo` 的完整许可和来源说明见 [`no-negative-echo/LICENSE`](no-negative-echo/LICENSE) 与 [`no-negative-echo/THIRD_PARTY_NOTICES.md`](no-negative-echo/THIRD_PARTY_NOTICES.md)。
- `tan-chengyi-perspective` 原样收录自上游项目，修改或再分发时应继续保留原有来源和鸣谢信息。
- `datasheet-to-design-guide` 基于 `Londeren/claude-plugins` 中 `book-to-skill` 的流程思想改写，使用它生成的普通工程文档无需额外署名；再分发 Skill 本体或 substantial portions 时应保留对应版权与许可声明。
