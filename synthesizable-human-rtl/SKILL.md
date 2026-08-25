---
name: synthesizable-human-rtl
description: RTL coding-standard Skill for synthesizable Verilog/SystemVerilog. Use after module behavior and key design semantics are defined to express RTL with synthesis-safe constructs, project-compatible language usage, semantic naming, consistent formatting, and intent-focused comments. It does not define requirements, architecture, implementation staging, verification strategy, or debug workflow.
---

# Synthesizable Human RTL

把已经确定的 RTL 行为写成**可综合、工具兼容、结构清楚、像工程师手写的 Verilog/SystemVerilog**。

这个 Skill 只负责“代码怎么写”，不负责“模块应该做什么”。

## 职责边界

本 Skill 负责：

- Verilog / SystemVerilog 语言和工具链兼容；
- 时序逻辑、组合逻辑、FSM、存储器等 RTL 的综合安全写法；
- 命名、格式、代码组织和注释；
- 避免常见 simulation / synthesis mismatch；
- 保持代码容易人工阅读和 Review。

本 Skill 不负责：

- 定义模块需求、接口或 Capability；
- 决定尚未确认的功能语义、关键时序或错误处理；
- 决定开发阶段、一次实现多少功能或如何拆迭代；
- 制定 Verification Plan、TB、Debug 或 Regression 流程；
- 把某个具体项目、协议或模块的实现经验推广成所有 RTL 的默认规则。

这些内容由 `rtl-design-flow`、`rtl-module-contract`、`rtl-design-doc`、`rtl-verification` 等对应 Skill 负责。

## 优先级与语言选择

按以下优先级执行：

1. 当前项目已经确认的代码规范和工具链限制；
2. 综合正确性与时序/复位/CDC 等硬件安全要求；
3. 本 Skill 的默认可读性和格式规则。

新建 RTL 时，如果项目工具链支持，默认使用 `.sv` / `.svh`，优先采用 `logic`、`always_ff`、`always_comb`、显式宽度 enum、`typedef`、package 等能提高可读性的 SystemVerilog 构造。

已有 `.v` / `.vh` 文件默认保持 Verilog-2001 兼容，除非用户要求迁移，或项目已经明确允许 SystemVerilog。不要因为本 Skill 默认偏好 SystemVerilog 就把 SV 语法直接写进 `.v` 文件。

## 综合安全规则

- 时序寄存器使用非阻塞赋值；组合过程使用阻塞赋值。
- 一个寄存器只允许一个明确的过程驱动；multiple driver、意外 latch、read-before-write 歧义视为阻塞问题。
- 不使用逻辑门去门控 fabric clock；时钟、复位和 CDC/RDC 敏感控制必须清楚可见。
- CDC 使用经过 Review 的同步器、异步 FIFO 或握手机制，不把跨时钟域问题隐藏在普通组合逻辑中。
- 所有信号、参数、类型和网络必须显式声明，不依赖 implicit net。
- SystemVerilog 默认使用四态 `logic`；只有确实需要 net 语义时使用 `wire`，例如 `inout`、受支持的三态端口或有意的 continuous net。
- 组合输出必须有完整赋值或明确默认值。
- 常量、counter bound、cast、signedness、enum base width 和 `$clog2` 边界必须显式处理。
- 多位量作为布尔条件时，优先显式写 `!= '0` / `== '0`，不要依赖隐式 reduction 语义。
- 不把 `X` 当综合 don't-care 使用；不使用 `casex`；片内普通 mux 不使用内部 `Z`。
- 每个 `case` 必须有 `default:`。
- `unique` / `priority` 只有在设计语义确实保证对应关系且工具链支持时才使用。
- 同一个 clocked process 内，不用多个彼此独立的非阻塞赋值依赖源码顺序给同一寄存器位制造隐含优先级；用 `if / else if` 或显式 `case` 表达。
- 综合函数保持无副作用、所有路径完整赋值，不在设计 RTL 中使用 verification-only / timing-only 构造，如 class、randomization、dynamic array、queue、delay、event、file I/O、DPI、`force/release`。
- loop 必须有可综合的有界范围；generate block 使用有意义的名字。
- RAM、ROM、DSP、初始化和厂商专用 primitive 优先遵循当前项目已经验证过的模板。

## 端口、参数与实例化

- 端口方向、类型和位宽必须显式。
- 默认使用语义化端口名，并遵循项目既有 `_i` / `_o` / `_io` 或其他命名约定。
- 实例化全部使用 named port connection 和 named parameter override。
- 不使用 positional port / parameter、`.*` 或 `defparam`。
- 未使用输出明确写 `.port()`；固定输入使用显式、位宽正确的常量。
- SystemVerilog 的 `.clk_i` 只在 formal port 与本地 signal 名字完全相同时使用；名字不同时写完整 `.port(signal)`。
- 每个 instance 使用有语义的实例名并遵循项目习惯，例如 `u_fifo`、`i_fifo` 或 `fifo_i`。

## 控制语句与格式

- `if (cond)`、`case (state)` 等控制关键字与 `(` 之间留空格；函数、task、macro 名与 `(` 之间不额外加空格。
- 二元运算符两侧留空格；逗号后留空格；当运算优先级需要读者额外推理时加括号。
- 单行且完整的控制语句可以省略 `begin/end`；一旦语句换行，就使用 `begin/end`。
- `begin` 与对应控制关键字放同一行；`end` 单独成行；`end else begin` 保持在同一行。
- `case` item 的冒号前不留空格，冒号后至少一个空格。
- 不写没有意义的完整位宽切片，例如本来就是整个 `bus` 时再写 `bus[WIDTH-1:0]`。

## RTL 结构与命名

- 一个代码块只承担一个清楚职责，例如 decode、next-state、state update、datapath update 或 output generation。
- 非平凡 FSM 优先使用明确的状态名，并把 next-state 与 state-register 职责分清。
- 简单表达式保持局部；只有真正表示协议/硬件概念、需要复用、跨时序边界或明显提升可读性时才抽成中间信号。
- 使用语义化名字，不使用 `tmp1`、`flag2` 这类机械占位名。
- `_d` / `_q` 只表示真正的寄存器 next/current 语义：`name_q` 是当前寄存值，`name_d` 是下一拍将装载的组合值。
- 当存在显式 `name_d` / `name_q` 对时，两者使用相同 base name、类型和宽度；`name_d` 在组合逻辑中完整生成，`name_q` 只由对应时序过程驱动。
- 不需要显式 next-value 时可以只保留 `_q`；纯延迟流水可使用 `_q`、`_q2`、`_q3` 表达拍数。
- 代码组织按当前模块真实的数据流、控制流或协议时间顺序排列，不按历史修改顺序或声明出现顺序机械堆放。
- 时钟、复位、状态、关键计数器和 CDC 相关信号应容易在代码中定位。

## 注释规则

- 默认使用中文意图注释；如果项目已经统一为英文，则保持项目约定。
- 注释解释“为什么这样做、这个寄存器表示什么、这个时序约束是什么”，不要翻译语法。
- 新增 RTL 变量默认在声明附近写简短意图注释；同一功能组连续排列，不同功能组之间再用空行和小标题分隔。
- FSM 注释写职责，例如 `// 状态机转移判定`、`// 状态机更新`，不要写“第一段/第二段/第三段”。
- timing-sensitive counter 的注释应说明实际拍数、窗口位置和目的，让读者能重新推导时序。
- 注释描述当前有效实现、当前约束和必须保留的兼容/安全事实，不把已经废弃的讨论方案当作当前代码说明。

## 与设计流程的接口

调用本 Skill 时，功能行为应来自已经确认的 Contract / Design 或用户当前明确要求。

```text
Contract / Design  → 决定做什么
本 Skill           → 决定怎么写成 RTL
```

如果写代码时发现必须新增或改变以下任一内容，而现有 Contract / Design 没有答案，应把问题交回 `rtl-design-flow`，不要由本 Skill 静默决定：

- 模块职责或接口；
- 功能语义或数据语义；
- 关键时序；
- 错误处理；
- 缓存满、超时、覆盖、丢弃等策略；
- 会改变外部可观察行为的重要优先级。

## 提交前代码检查

- 语言版本与文件扩展名、工具链一致；
- 没有 implicit net、multiple driver、意外 latch 或位宽/符号歧义；
- 时序逻辑与组合逻辑赋值语义正确；
- `case` 有 `default:`，没有不安全的 `casex` / don't-care `X`；
- 端口、参数和实例化均为显式 named mapping；
- 命名能直接表达硬件语义；
- `_d/_q` 使用符合寄存器语义；
- 注释解释当前设计意图，而不是代码语法或无关历史；
- 没有把项目特例写成通用 RTL 规则。
