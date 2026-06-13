---
name: rtl-adversarial-tb
description: 为 RTL 模块生成 SV Testbench 的对抗式三阶段工作流。第一阶段提出验证方案，第二阶段对抗审核直到通过，第三阶段编写 TB 并跑仿真。适用于任何可综合 Verilog/SV 模块。
---

# RTL Adversarial TB

用三个子代理对抗式协作，为 RTL 模块生成高质量的 SystemVerilog Testbench。

## 工作流总览

```
用户给出 RTL 文件
        │
        ▼
  ┌─────────────┐
  │ 子代理 1    │  提出验证方案
  │ 方案设计    │  → verification_plan.md
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐     ┌─────────────┐
  │ 子代理 2    │◄───►│ 子代理 1    │  对抗审核
  │ 方案审核    │     │ 修改方案    │  → review_feedback.md
  └──────┬──────┘     └─────────────┘
         │ 审核通过
         ▼
  ┌─────────────┐
  │ 子代理 3    │  编写 TB + 跑仿真
  │ TB 编写     │  → <module>_tb.sv
  └─────────────┘
```

## 使用方式

用户说"帮我写 TB"、"验证这个模块"、"生成 testbench"时触发此技能。

输入：
- 用户指定的 RTL 文件路径（Verilog 或 SystemVerilog）
- 可选：位宽、数据格式、特殊约束等补充说明

输出（放在 `<rtl文件名>_tb/` 目录下）：
- `verification_plan.md` — 验证方案文档
- `review_feedback.md` — 审核记录
- `<module>_tb.sv` — SV Testbench

## 阶段一：方案设计（子代理 1）

### 输入
- DUT 源码（读取用户指定的 RTL 文件）

### 输出要求
将方案写入 `<rtl文件名>_tb/verification_plan.md`，内容必须包含：

1. **DUT 功能概述**
   - 模块接口（端口列表、位宽、方向）
   - 功能描述（一句话）
   - 时序特性（纯组合 / 单周期 / 流线 / 状态机）

2. **功能覆盖点（Functional Coverage Items）**
   - 以表格列出，每行包含编号、覆盖点、说明
   - 必须覆盖：
     - 正常功能路径
     - 特殊输入值（零、最大、最小、1、-1 等）
     - 边界条件
     - 控制信号的所有有效组合（如有）

3. **定向测试场景（Directed Test Cases）**
   - 以表格列出，每行包含编号、场景名、输入、预期输出
   - 预期输出应具体到数值（如果可能），或标注"参考模型计算"

4. **随机测试策略**
   - 值域约束
   - 随机数量建议
   - 覆盖率收集策略（如适用）

5. **自检策略（Self-Checking）**
   - 参考模型实现方式（bit-accurate 级别）
   - 比较策略（精确匹配 / 容差匹配，容差值）
   - 报告格式

6. **TB 结构**
   - 用树形图列出组件划分
   - 说明每个组件的职责

7. **仿真终止条件**

### 质量要求
- 用中文写
- 功能点必须可验证（每个点都能映射到一个 PASS/FAIL 判定）
- 边界条件必须给出具体预期（不能只写"检查行为"）

## 阶段二：对抗审核（子代理 2 ↔ 子代理 1）

### 审核标准（子代理 2）

审核员从以下维度逐项检查：

| 维度 | 检查项 |
|------|--------|
| 完整性 | 功能点是否覆盖 DUT 所有路径 |
| 正确性 | 定向测试的预期输出是否正确 |
| 边界 | 最大值、最小值、零、溢出边界是否覆盖 |
| 自检 | 参考模型是否 bit-accurate，容差是否合理 |
| 随机 | 随机约束是否合理，覆盖率是否可收敛 |
| 特殊值 | 乘以 0、1、-1、j、-j 等特殊值是否测试 |
| 结构 | TB 结构是否模块化，是否便于维护 |
| 可执行 | 仿真终止条件是否明确，是否可自动判定 |

### 对抗流程

```
round = 0
while not approved and round < 5:
    round += 1
    审核员读取 verification_plan.md，输出：
      - "APPROVED: 方案通过审核"  → 退出循环
      - "REJECTED: [具体修改要求]" → 方案设计者根据反馈修改方案
```

### 审核反馈格式

写入 `<rtl文件名>_tb/review_feedback.md`：

```markdown
# 审核反馈

## 审核结果：通过 / 需修正

### 问题 1：[标题]
- **现状**：[当前方案的问题]
- **影响**：[会导致什么验证漏洞]
- **修正**：[具体修改建议]

### 问题 2：...
```

### 修改方案格式

方案设计者读取 `review_feedback.md` 后更新 `verification_plan.md`，在修改处加注释标明修正来源。

### 终止条件
- 审核通过，或
- 达到 5 轮仍未通过（使用当前方案继续，但在报告中标注）

## 阶段三：TB 编写与测试（子代理 3）

### 输入
- DUT 源码
- 通过审核的 `verification_plan.md`

### 输出
- `<rtl文件名>_tb/<module>_tb.sv` — SV Testbench

### 编写规范

1. **参考模型**
   - 用 `task automatic` 或 `function` 实现
   - 必须与 DUT 位级一致（bit-accurate）
   - 中间变量位宽与 DUT 一致

2. **测试组织**
   - 定向测试用命名 task（如 `run_T01_identity()`）
   - 随机测试用循环 + `$urandom_range`
   - 每组测试调用统一的 `check_result` 任务

3. **自检逻辑**
   - 比较 DUT 输出与参考模型输出
   - 精确匹配或容差匹配（按方案要求）
   - PASS 时静默，FAIL 时打印详细信息（输入、DUT 输出、参考输出、差值）

4. **统计报告**
   - 仿真结束打印：总测试数 / PASS / FAIL
   - 全部 PASS 打印 "ALL PASS"

5. **超时保护**
   - 加 `initial begin #100ms; $finish; end` 防止死锁

6. **注释**
   - 用中文
   - 解释测试意图，不解释 SV 语法

### 仿真运行

写完 TB 后：
1. 检测可用仿真器（优先 xsim > iverilog > QuestaSim）
2. 编译、链接、运行
3. 报告仿真结果

如果仿真器不可用，只报告 TB 文件已写好。

## Workflow 实现

当此技能被触发时，使用 Workflow 工具执行以下脚本结构：

```javascript
export const meta = {
  name: 'rtl-adversarial-tb',
  description: '对抗式三阶段 RTL Testbench 生成',
  phases: [
    { title: '方案设计', detail: '子代理1提出验证方案' },
    { title: '对抗审核', detail: '子代理2审核方案，迭代直到通过' },
    { title: 'TB编写与测试', detail: '子代理3按方案编写SV testbench并跑仿真' },
  ],
};

// Phase 1: 方案设计
phase('方案设计');
const plan = await agent(
  `你是一个资深验证工程师。请读取 <DUT_PATH>，为该模块提出完整的 SV testbench 验证方案。
   要求：...（见阶段一规范）
   将方案写入 <TB_DIR>/verification_plan.md`,
  { label: '方案设计', phase: '方案设计' }
);

// Phase 2: 对抗审核（最多5轮）
phase('对抗审核');
let approved = false;
let round = 0;
while (!approved && round < 5) {
  round++;
  const review = await agent(
    `你是一个严格的验证方案审核员。请读取 <DUT_PATH> 和 <TB_DIR>/verification_plan.md。
     审核标准：...（见阶段二审核标准）
     如果通过输出 "APPROVED"，否则输出 "REJECTED" 和修改意见。
     将审核结果写入 <TB_DIR>/review_feedback.md`,
    { label: `审核第${round}轮`, phase: '对抗审核' }
  );
  if (review includes 'APPROVED') {
    approved = true;
  } else {
    await agent(
      `根据 <TB_DIR>/review_feedback.md 修改 <TB_DIR>/verification_plan.md`,
      { label: `修改方案第${round}轮`, phase: '对抗审核' }
    );
  }
}

// Phase 3: TB编写
phase('TB编写与测试');
await agent(
  `你是一个SV验证工程师。读取 <DUT_PATH> 和 <TB_DIR>/verification_plan.md，
   编写 SV testbench 到 <TB_DIR>/<module>_tb.sv，并尝试仿真。
   要求：...（见阶段三规范）`,
  { label: 'TB编写', phase: 'TB编写与测试' }
);
```

### 参数替换

脚本中的占位符在运行时替换：
- `<DUT_PATH>` — 用户指定的 RTL 文件路径
- `<TB_DIR>` — 输出目录（`<RTL目录>/<模块名>_tb/`）
- `<module>` — 模块名

### Agent 调用说明

每个 agent 调用必须：
- 使用 `{label, phase}` 参数标记阶段
- 将输出文件写入磁盘（通过 Write 工具）
- 下一个 agent 通过读取磁盘文件获取上一步结果

### 错误处理

- 如果 Workflow agent 调用失败（API 错误），回退为串行执行：直接在主会话中分步完成三个阶段
- 如果仿真器不可用，只输出 TB 文件，不报错

## 与 rtl-human-style 技能的配合

如果用户同时启用了 `rtl-human-style` 技能：
- DUT 代码遵循 rtl-human-style 的编码规范
- TB 代码也遵循 rtl-human-style 的 TB 规范（模块化 task、命名规范、注释风格）
- 验证方案中的 TB 结构应与 rtl-human-style 的 TB guidance 一致

## 示例对话

**用户**：帮我为 `adder.v` 写个 testbench

**Claude**：
1. 读取 `adder.v`
2. 触发 rtl-adversarial-tb 技能
3. 创建 `adder_tb/` 目录
4. 子代理 1 提出验证方案 → `adder_tb/verification_plan.md`
5. 子代理 2 审核（可能 1-3 轮对抗）→ `adder_tb/review_feedback.md`
6. 子代理 3 编写 TB → `adder_tb/adder_tb.sv`，并跑仿真
7. 汇报结果
