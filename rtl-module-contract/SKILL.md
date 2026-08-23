---
name: rtl-module-contract
description: 在 RTL 设计开始前，把模块边界整理成简短、稳定、可审核的 module_contract.md。只定义接口、模块职责和对外能力，不提前绑定 FSM、寄存器、伪代码或具体实现。
---

# RTL Module Contract

## 目标

在进入 RTL 详细设计前，先回答一件事：

> 这个模块对外到底应该表现成什么样。

`module_contract.md` 是模块边界和外部行为的约定，不是 RTL 的文字版，也不是详细设计文档。

它只保留三部分：

1. Interface
2. Purpose
3. Capabilities

如果后续内部 FSM、寄存器、流水线或组合逻辑重写，但模块对外职责没有变化，Contract 应尽量不需要修改。

---

## 与其他 Skill 的配合

### `grill-me`

当接口、职责或对外功能存在关键歧义时，使用 `grill-me` 逐项确认。

要求：

- 先读项目已有文档、RTL、接口和上下游模块，能从环境得到的事实不要问用户；
- 每次只问一个会影响模块边界或外部行为的问题；
- 给出推荐答案；
- 不在 Contract 阶段追问 FSM 怎么拆、寄存器怎么写、内部条件怎么组合。

### `engineering-doc-style`

如果该 Skill 可用，最终文档必须应用它的工程文档风格：简洁、直接、少解释、少防御性语言，不把简单内容扩成报告。

---

# 1. Interface

直接列出完整端口声明。

每个端口至少明确：

- `input/output`；
- 位宽；
- 外部语义。

推荐形式：

```verilog
input         clk_i,        // 16MHz 接收时钟
input         rst_n_i,      // 低有效复位
input         enable_i,     // 接收使能
input         ready_i,      // 上层允许接收当前结果
output        valid_o,      // 当前输出结果有效
output [15:0] data_o,       // 接收到的 16bit 数据
output        sync_type_o,  // 1: 命令/状态字，0: 数据字
```

## Interface 写作规则

接口注释只描述信号对外代表什么，不描述内部怎么产生。

推荐：

```verilog
output word_error_o, // 当前输出字存在字级错误
```

避免：

```verilog
output word_error_o, // parity 或 Manchester 检测失败后由 CHECK 状态置位
```

如果端口还没有最终确定，可以保留少量明确的 `TODO`，但不能假装已经决定。

---

# 2. Purpose

Purpose 只允许 1～2 句话。

它只回答三个问题：

1. 这个模块处理什么；
2. 完成什么转换、控制或处理；
3. 最终向谁提供什么结果。

判断标准：

> 如果内部 RTL 全部重写，但模块用途不变，这段 Purpose 就不应该改。

示例：

> 接收单通道 MIL-STD-1553B 差分总线信号，将总线上的字解析为上层可使用的 16-bit 数据、字类型及字级状态信息。

Purpose 中不要写：

- FSM 状态；
- 计数器；
- 具体算法步骤；
- `valid` 由什么条件产生；
- 寄存器和内部信号名。

---

# 3. Capabilities

Capabilities 描述模块具备哪些外部可观察、可独立验证的能力。

一般控制在 3～10 条。

每一条都应满足：

> 可以直接判断“做到了 / 没做到”，并能自然映射到后续验证点。

示例：

- 能识别并接收一个完整的 1553B 字；
- 能区分命令/状态字与数据字；
- 能输出 16-bit 数据；
- 能输出字级错误状态；
- 能输出相邻字之间的时间间隔；
- 支持 `valid/ready` 结果交付。

不要把实现方式写成 Capability，例如：

- 使用 16MHz 过采样；
- 使用移位寄存器检测同步头；
- 在 CHECK 状态完成奇偶校验；
- 使用 6 状态 FSM。

这些属于后续 RTL Design 或 RTL Coding。

---

# 不属于 Module Contract 的内容

以下内容默认不要放进 `module_contract.md`：

- FSM 结构和状态名；
- 寄存器列表；
- 伪代码；
- 内部布尔表达式；
- 计数器具体位宽和加减方式；
- pipeline 具体拆法；
- 内部错误处理流程；
- 逐拍实现细节。

如果某个细节会改变模块对外功能、接口或 Capability，则提升为 Contract 内容；否则留到 `rtl_design.md` 或 RTL 中。

---

# 工作流程

## Step 1：读取已有上下文

优先读取：

- 需求文档；
- 顶层结构；
- 已有接口；
- 上下游模块；
- 已有 RTL；
- 协议资料；
- 项目规则。

先判断哪些内容已经确定，不重复问用户。

## Step 2：整理第一版 Contract

先生成：

```markdown
# <Module> Module Contract

## Interface
...

## Purpose
...

## Capabilities
...
```

## Step 3：只追问关键缺口

如果仍存在会改变以下内容的问题，使用 `grill-me` 一次问一个：

- 端口；
- 方向；
- 位宽；
- 模块职责；
- 外部可观察功能；
- 与上下游的职责边界。

不要在本阶段追问内部实现细节。

## Step 4：用户确认后冻结

Contract 通过后，作为后续 `rtl_design.md` 和验证计划的输入。

---

# 通过条件

只有同时满足以下三条，`module_contract.md` 才算通过：

1. **接口确定**
   - 端口、方向、位宽和外部语义不存在关键歧义。

2. **职责确定**
   - 能用 1～2 句话说清模块存在的意义。

3. **功能确定**
   - 每条 Capability 都可以明确判断是否实现，并且不依赖具体内部实现方式。

Contract 通过只代表模块边界已经确定，不代表所有内部时序、FSM 和实现细节已经冻结。

---

# 修改规则

后续开发中只有以下情况需要回写 Contract：

- 新增、删除或改变接口；
- 模块职责发生变化；
- Capability 新增、删除或语义变化；
- 原来属于其他模块的外部职责正式转移到本模块。

下面这些情况通常不修改 Contract：

- FSM 状态数变化；
- 中间寄存器变化；
- `valid` 内部实现条件从 `a` 改成 `g`，但对外语义未变；
- 修复纯实现 Bug；
- 重构组合逻辑或流水线结构但外部行为不变。

文档更新可以在 RTL 和验证稳定后统一同步，不要求每次试验性代码修改都立即改文档。

---

# 示例

下面的例子只示范 Contract 的粒度，不要求所有模块长得一样。

## 示例 1：1553B RX

### Interface

```verilog
input         clk_i,         // 接收时钟
input         rst_n_i,       // 低有效复位
input         enable_i,      // 接收使能
input         ready_i,       // 上层允许接收当前结果
output        valid_o,       // 当前字结果有效
output [15:0] data_o,        // 16bit 字数据
output        sync_type_o,   // 1: 命令/状态字，0: 数据字
output        busy_o,        // 当前通道正在接收字
output        word_error_o,  // 当前输出字存在字级错误
output [8:0]  gap_time_o,    // 前一字结束到本字开始的间隔
input         rx_p_i,        // 差分正端
input         rx_n_i,        // 差分负端
output        rxen_o         // 通道接收使能
```

### Purpose

接收单通道 MIL-STD-1553B 差分总线信号，将完整总线字解析为上层可使用的数据、字类型、字间隔和字级状态信息。

### Capabilities

- 接收并输出一个完整的 1553B 字；
- 区分命令/状态字与数据字；
- 输出 16bit 字数据；
- 输出字级错误状态；
- 输出相邻字之间的时间间隔；
- 支持 `valid/ready` 结果交付。

这里不写 16MHz 过采样、同步头检测窗口、状态机状态和计数器实现。

---

## 示例 2：AXI4-Lite Slave Bridge

### Interface

接口应完整列出 AXI4-Lite 的 AW/W/B/AR/R 五个通道，以及内部寄存器读写接口。端口注释只解释协议角色和内部接口含义。

### Purpose

作为 AXI4-Lite Slave 接收上游控制访问，并转换为内部简单寄存器读写请求，再把访问结果转换为 AXI4-Lite 响应。

### Capabilities

- 接收 AXI4-Lite 写地址和写数据；
- 发起一次对应的内部寄存器写访问；
- 返回 AXI4-Lite 写响应；
- 接收 AXI4-Lite 读地址；
- 发起一次对应的内部寄存器读访问；
- 返回 AXI4-Lite 读数据和读响应；
- 支持 AXI4-Lite 通道背压。

这里不写 AW/W 内部如何缓存、FSM 分几段、READY 具体由哪个状态产生。

---

## 示例 3：1553B BM

### Interface

接口应完整列出 RX 字结果输入、过滤配置、时间戳接口、BRAM 写接口以及必要的控制/状态端口。

### Purpose

接收一路 1553B RX 字结果，对总线消息进行监听、筛选和消息级解析，并把符合条件的消息整理成记录写入后级存储。

### Capabilities

- 监听一路 1553B 接收字流；
- 根据配置筛选需要记录的消息；
- 识别主要 1553B 消息类型；
- 对消息级错误进行记录；
- 为记录关联时间戳；
- 将完整消息转换为固定记录格式写入后级存储；
- 在一条消息完成后形成可供后级读取的有效记录。

这里不写具体消息状态机、BRAM offset 写入顺序、超时计数器实现和错误位内部组合逻辑；这些进入 `rtl_design.md`。
