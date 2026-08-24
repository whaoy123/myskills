---
name: questa-wave-layout
description: 为 RTL/TB 工程生成便于人工查看的 Questa/ModelSim 波形布局和可直接运行的 .do 脚本。先理解一次完整事务，再动态选择信号、分组、排序、radix 和初始运行窗口；每次运行使用独立 work 目录。只辅助人工读波形，不修改 RTL/TB 或验证预期。
---

# Questa Wave Layout

这个 Skill 的职责是：

> 让 AI 在 RTL 仿真时，先理解 DUT、TB 和验证目标，再生成适合人工阅读的 Questa/ModelSim 波形布局和辅助 `.do` 脚本。

它不是验证规范，也不负责定义 DUT 应该怎么工作。正常正确性判断仍以 `module_contract`、`rtl_design`、`verification_plan`、TB specification 和自动 checker 为依据。

---

## 输入

优先读取：

1. DUT RTL；
2. TB；
3. `verification_plan.md`；
4. 已有仿真脚本；
5. 用户已经认可或实际跑通过的 Questa `.do` / 波形布局示例。

如果已有脚本已经验证过编译、仿真参数或工程路径，优先继承这些已知条件，不要无理由重新发明一套流程。

---

## 输出

生成或更新可直接执行的 Questa `.do`，例如：

```text
run_xxx_wave.do
```

目标是执行：

```tcl
do run_xxx_wave.do
```

后直接得到一个适合人工检查的波形环境，而不是再手工逐个添加大量信号。

典型流程：

```text
建立独立 work 目录
↓
vlib / vmap
↓
vlog
↓
vsim +acc
↓
打开 Wave
↓
按功能分组 add wave
↓
设置合理 radix
↓
运行到有意义的观察窗口
↓
zoom
```

---

# 核心原则

## 1. 先理解一次完整事务，再设计波形

不要先看信号名然后机械分类。

先从 RTL、TB 和验证计划中确定：

```text
一次完整事务从哪里开始
经过哪些阶段
在哪里结束
成功如何体现
错误如何体现
```

然后按这个事务的数据流 / 控制流设计波形窗口。

波形从上到下应该尽量让人自然地沿着一次事务往下读，不需要频繁上下跳转寻找相关信号。

例如接收模块可能是：

```text
输入
↓
接口使能
↓
同步检测
↓
接收过程
↓
最终数据
↓
错误状态
↓
必要内部 debug
```

不要按 RTL 文件中的声明顺序机械排列。

---

## 2. 分组数量和组名必须根据模块动态决定

**不存在固定 8 组规则。**

一个模块可能需要：

```text
4 组
6 组
8 组
10 组
```

都可以。

目标不是凑组数，而是让一次完整事务容易读。

不同模块应体现自己的真实结构。例如：

### AXI Bridge 示例

```text
Clock / Reset
AXI Write
AXI Read
Internal Request
Response
State / Buffer
Error
```

### Cache 示例

```text
Clock / Reset
CPU Request
Tag / Hit
Miss Handling
Memory Interface
Data Path
State
```

`Sync Detection`、`Receive Progress` 这类概念属于特定接收模块，不能硬套到其他 RTL。

---

## 3. 不默认使用 `add wave -r /*`

不要默认：

```tcl
add wave -r /*
```

这种做法会把大量无关内部信号全部塞进波形窗口，降低可读性。

AI 应先理解模块，再主动选择真正有观察价值的信号。

通常优先：

```text
clock / reset
顶层输入输出
valid / ready / enable / busy
主要状态机
关键 counter / pointer
关键握手事件
最终 data / result
error / status
必要的内部 debug 信号
```

不要因为信号“能看到”就全部加入。

---

## 4. 内部 Debug 信号要克制

以下信号只有确实帮助理解当前行为时才加入：

```text
shift register
大位宽历史窗口
中间组合信号
内部临时 decode
```

必要时单独放入：

```text
Internal Debug
```

这类组中。

内部信号应服务于解释当前状态、时序或 Bug 根因，不服务于“看起来完整”。

---

## 5. radix 根据语义设置

不要给所有信号统一 radix。

常见选择：

```tcl
# 状态机
add wave -radix symbolic ...

# counter / pointer
add wave -radix unsigned ...

# data / address / result
add wave -radix hexadecimal ...

# 位模式 / Manchester / shift window
add wave -radix binary ...
```

单 bit 控制信号通常保持默认显示即可。

radix 的目标是让人最快理解信号语义，而不是统一格式。

---

# Questa 执行规则

## 6. 每次 `.do` 执行必须创建独立 work 目录

这是强制规则。

不要让多个 Questa GUI、重复运行或并行仿真共用同一个：

```text
work/
modelsim.ini
vsim.wlf
```

固定共享临时目录可能导致：

```text
permission denied
work library 冲突
modelsim.ini / vsim.wlf 互相抢占
```

每次运行应生成唯一目录，例如：

```tcl
set run_tag "[pid]_[clock clicks]"
set sim_dir [file normalize \
    [file join $env(TEMP) "questa_wave_$run_tag"]]

file mkdir $sim_dir
cd $sim_dir

vlib work
vmap work work
```

如果脚本需要从工程目录读取 RTL / TB，应在 `cd` 前先把工程路径和源文件路径转换为绝对路径，避免切换到临时目录后相对路径失效。

原则：

> 一次 `.do` 执行对应一个独立 Questa 仿真工作目录。

不要为了复用编译结果而默认共享可写 `work` library，除非项目已经有明确、经过验证的并发隔离机制。

---

## 7. 编译和仿真优先沿用项目已验证命令

对 SystemVerilog 项目，常见已验证形式：

```tcl
vlog -sv $rtl_file $tb_file
vsim -voptargs=+acc -t 1ps work.tb_top
```

如果需要观察 DUT 内部信号，优先通过合适的 `+acc` 保留可见性，而不是为了看波形去修改 RTL。

具体 `vlog` / `vsim` 参数必须结合当前项目、Questa 版本和已有脚本确定，不要把某一个项目的命令行无条件硬套到所有工程。

---

## 8. 初始 run 时间按完整关键事务选择

不要固定：

```tcl
run 22 us
```

某个 RX 测试里 `22 us` 合适，只是因为它足够覆盖一次：

```text
sync
→ 16 bit data
→ parity/check
→ valid/ready
```

Skill 的规则是：

> 根据 TB 和目标事务选择一个能覆盖一次完整关键事务的初始运行窗口。

优先依据：

1. TB 中第一项完整测试的持续时间；
2. `verification_plan.md` 给出的关键观察窗口；
3. 第一个有意义的 checker / checkpoint；
4. 已有脚本中经过验证的运行时间。

如果无法合理判断，可以运行到 TB 的第一个关键检查点，或者使用已有验证计划中的时间窗口。

---

# 默认工作步骤

## 1. Inspect

读取：

```text
RTL
TB
verification plan
已有仿真脚本
已有人工认可的波形示例
```

确认：

- DUT 层级；
- TB top；
- 编译依赖；
- 目标仿真器和版本；
- 已有 `vlog` / `vsim` 用法。

## 2. Understand transaction

确定：

```text
事务起点
主要阶段
阶段之间的关键事件
事务终点
成功结果
错误结果
```

## 3. Select signals

只选择：

```text
接口
主要控制
主要状态
关键计数 / 指针
关键数据
错误 / 状态
必要 debug
```

先保证能解释一次完整事务，再考虑补充内部细节。

## 4. Design groups

根据模块真实结构动态决定：

- 组数；
- 组名；
- 组顺序；
- 组内信号顺序。

历史布局可以作为参考，但不能把某个模块的专有概念变成全局模板。

## 5. Generate DO

生成可以直接执行的 `.do`，至少处理：

```text
独立临时 work 目录
vlib / vmap
compile
elaborate / vsim
Wave 窗口
功能分组
radix
初始 run
zoom
```

## 6. Run / validate

如果 Questa/ModelSim 可用，应实际执行至少一次：

```text
compile
elaborate
run
```

至少确认：

```text
源文件路径正确
TB top 正确
信号层级正确
add wave 没有大量 signal not found
仿真能够运行到目标窗口
```

波形脚本本身的可运行性属于这个 Skill 的验收范围。

## 7. Refine

结合人工阅读体验调整：

```text
信号多少
组名
组顺序
组内顺序
radix
运行窗口
```

优先删掉没有帮助的信号，再考虑增加更多内部信号。

---

# RX 实测参考示例

下面是一个 `MIL1553B_RX` 实际使用过的布局思路，只作为 **RX 模块参考起点**，不是通用固定模板。

```text
1. Clock / Reset
2. RX Physical Input
3. RX Interface / Handshake
4. Sync Detection
5. Receive Progress
6. Data / Result
7. Error
8. Internal Debug
```

参考信号：

### Clock / Reset

```text
rx_clk
rst_n
sample_en
sample_cnt
```

### RX Physical Input

```text
enable
inject_enable
txa_p
txa_n
rx_p
rx_n
rx_bit
rx_diff_valid
```

### RX Interface / Handshake

```text
busy
rxen
valid
ready
fire
```

### Sync Detection

```text
sync_half_level
sync_cmd_status
sync_data
rx_pre_valid
rx_now_valid
rx_next_valid
sync_type_reg
```

### Receive Progress

```text
state_reg
next_state
sync_align_count_reg
data_sample_count_reg
data_bit_count_reg
check_sample_count_reg
data_first_half_level
data_second_half_level
manchester_valid
data_bit
```

### Data / Result

```text
data_reg
odd_parity_valid
state_end_pulse
data
sync_type
```

### Error

```text
differential_error_reg
manchester_error_reg
parity_error_reg
word_error
```

### Internal Debug

```text
shift_d
diff_valid_shift_d
```

同一个信号通常只放在最合适的一组里。例如 `word_error` 应保留在 `Error`，不要同时重复出现在 `Data / Result`。

---

# 与 RTL Verification 的边界

`questa-wave-layout` 负责：

```text
帮助人工读波形
选择有价值的观察信号
设计 waveform layout
生成/整理 Questa .do
验证 .do 能正常运行
```

它不能擅自：

```text
修改 RTL 功能
改变 TB 检查逻辑
修改 expected result
修改 assertion
为了波形好看改变激励或设计行为
```

预期行为必须来自：

```text
module_contract
rtl_design
verification_plan
TB specification
```

不能根据当前 RTL 的实际输出倒推出“正确行为应该就是这样”。

Questa/ModelSim 的平台级环境故障可以单独排查，但不要把一次项目中的 IPv6、RPC 或其他系统 workaround 写成这个 Skill 的核心规则。只有已经确认与波形脚本稳定性直接相关的通用规则才沉淀进来，例如：

> 不共享可写仿真 work 目录。
