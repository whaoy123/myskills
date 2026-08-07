# 开源方案借鉴说明

## Altium 官方脚本示例

Altium 提供 DelphiScript/JScript/VBScript 示例，并按 SCH、PCB、Workspace 等分类。适合作为 API 用法依据，但部分旧示例可能因 API 更新无法直接运行，因此本 Skill 要求先参考工作示例，再进行版本验证。

## altium-designer-addons/scripts-libraries

社区维护的大量 Altium 脚本集合，适合查找原理图对象创建、批处理和项目操作示例。项目本身也提示脚本年代和维护状态不一致，因此不能盲目复制。

## altium-scripts-skill

已有 Skill 强调优先检索大量可工作的示例脚本，再补 API 参考。本 Skill 借鉴其“先示例、后接口”的原则，但将范围收窄到原理图放置、连接和结构化输入输出。

## altium-mcp

通过 DelphiScript 在 Altium 和 MCP Server 之间建立接口，能够读取器件、引脚和原理图数据，并支持批量操作。适合交互式修改当前工程，但部署成本高于离线脚本。

## eda-agent

提供面向 Altium/KiCad 的大量 MCP 工具，可以在当前设计中读取和修改对象，但项目明确标注实验性，部分工具可能导致 DelphiScript 引擎崩溃。因此适合作为增强路径，不应替代备份和静态校验。

## SKiDL

用 Python 定义元件和网络，可输出 KiCad 网络表和可编辑原理图。核心启发是：连接关系应作为结构化、可测试的数据存在，而不是仅作为画布中的线。

## Circuit-Synth

用 Python 函数构建可复用电路，并强调版本控制、测试和参数化生成。其模板化重复通道思想适合本 Skill。

## atopile

声明式电子设计语言，强调模块、接口、约束和验证。其优点在于设计意图结构化，但主要面向 KiCad，因此本 Skill只借鉴输入模型与验证理念。

## 最终取舍

针对 Altium Designer 23 用户，默认选择：

结构化 CSV/YAML → 静态校验 → DelphiScript → Altium 工程副本执行 → ERC/人工审查。

不默认迁移到 KiCad，也不默认依赖实时 MCP。
