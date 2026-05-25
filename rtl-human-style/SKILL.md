---
name: rtl-human-style
description: Use when writing or refactoring RTL or testbench code and the goal is human-readable, hand-written-feeling Verilog/SystemVerilog rather than dense AI-shaped code. Best for modules with control logic, FSMs, handshake paths, cache/control pipelines, and reusable directed testbenches. Emphasize readable decomposition, business-meaningful state names, medium-to-high explanatory comments for tricky logic, and a small reusable TB structure.
---

# RTL Human Style

Write RTL and testbench code so a hardware engineer can skim it and recover the design intent quickly.

## Default stance

- Prefer readability over compression.
- Prefer stable handwritten structure over clever abstraction.
- Prefer business-meaningful names over mechanically uniform names.
- Keep the code close to synthesizable Verilog style unless SystemVerilog materially improves clarity.

## Source basis

Use these as background, not as laws:

- `lowRISC` for naming discipline and block structure.
- `Verible` for lintable subsets.
- `systemverilog.io` for spacing and readability conventions.
- `OpenTitan DV` for reusable TB layering and assertion placement.

If needed, read:

- [source_basis.md](references/source_basis.md)
- [writing_style_variants.md](references/writing_style_variants.md)

## Style target

The target style is:

- closer to experienced handwritten RTL than to template-generated RTL
- explicit about control flow
- willing to spend a few more lines to make the logic obvious
- comfortable with comments when they explain protocol intent, state meaning, or hazards

## Fixed preferences for this style

- 注释默认使用中文。
- 模块端口默认保留 `_i` / `_o` 命名。
- 内部信号不强制统一后缀，语义清楚优先。
- 仅在确实提升可读性时使用少量 SystemVerilog。
- 默认仍应贴近传统、可综合的 Verilog 写法。

## Core RTL rules

1. Start with the dataflow story.
   - Before writing code, identify:
     - what the module stores
     - what advances state
     - what the key decisions are
     - what outputs are pure decode vs registered behavior

2. One block, one responsibility.
   - Separate these when possible:
     - field decode
     - hit/miss or qualify logic
     - next-state logic
     - state register update
     - datapath register update
     - output generation
   - For control/state-hold behavior, prefer clocked blocks by default.
   - Treat large combinational output blocks as the exception, not the default.

3. Keep the top of the file readable.
   - Put the module purpose in comments first.
   - For control-heavy modules, include a short flow comment before the code.
   - Group declarations by function, not by random chronology.

4. Use names that explain design meaning.
   - Good:
     - `request_load_hit`
     - `tail_has_pending`
     - `store_wait_mem`
     - `branch_taken`
   - Avoid:
     - `tmp1`
     - `flag2`
     - `data_a1`
     - `logic_ok`

4.5 Keep simple logic simple.
   - If one assignment already expresses the intent clearly, keep it in one place.
   - Do not split a straightforward expression into several helper wires just to look structured.
   - Only extract an intermediate signal when it gives one of these benefits:
     - real reuse
     - a meaningful protocol/domain concept
     - a noticeable readability win in a branch or case item
   - For decode-style outputs such as branch targets, flush targets, or simple mux choices, prefer direct expression when a reader can understand it in one pass.

5. Do not force `_d/_q` everywhere.
   - Use `_d/_q` when a register pair is truly a next/current pair and that naming improves local clarity.
   - Do not rename naturally meaningful state just to satisfy a pattern.
   - For many handwritten modules, names like `state` / `next_state` are clearer than `state_q` / `state_d`.

6. Use comments where humans actually need help.
   - Explain:
     - why a state exists
     - why a handshake is held
     - why a corner case is blocked
     - what ordering or contract must be preserved
   - Do not explain syntax.

7. Split before a block becomes visually hostile.
   - If a combinational block mixes protocol arbitration, cache hit classification, refill bookkeeping, and response generation, split it.

8. Do not carpet the file with long boolean helper wires.
   - Avoid stacking many top-level declarations of the form:
     - `wire foo = a && b && c && d && e;`
   - A long helper expression is allowed only when:
     - it captures a real protocol concept
     - the name is stronger than the raw expression
     - it is reused or meaningfully simplifies a branch
   - If several such helpers start to accumulate, stop and rewrite the surrounding logic structure instead.
   - This rule does not mean every expression must be named; often the better fix is to keep the logic local and direct.

## Preferred naming guidance

- Ports may use `_i/_o` when the file already follows that convention or when it clearly improves scanning.
- For this style, module ports should keep `_i/_o` by default.
- Internals do not need rigid suffixing if the semantic name is already clear.
- Registers may use:
  - `state` / `next_state`
  - `pending_req_valid`
  - `resp_hold_valid`
  - `refill_word_ready_mask`
- Use `_d/_q` selectively, not religiously.

## Comment guidance

- 注释默认用中文写。
- 注释重点解释：
  - 设计意图
  - 控制流
  - 协议约束
  - 边界条件为什么要这样处理
- 注释里涉及信号名、关键字、状态名时，保持代码原名即可。

## Verilog / SystemVerilog boundary

- 默认先按 Verilog 风格组织代码。
- 只在能明显提升可读性时引入少量 SystemVerilog。
- 适合有限使用的 SV 内容包括：
  - 在 SV 原生文件里使用更清晰的声明方式
  - 少量能提升表达清晰度的类型写法
  - 环境已经稳定接受的小范围语法增强
- 不要为了“更现代”把模块整体改写成 SV 味很重的风格。

## FSM guidance

- Prefer explicit state names tied to behavior.
- Prefer a clear next-state block and a separate state update block.
- For large control modules, add a short state flow comment near the state declarations.
- Avoid burying state transitions inside a huge output block.
- If an output is really part of stored behavior or hold behavior, prefer updating it in a clocked block.
- Use combinational blocks mainly for:
  - pure decode
  - next-state decisions
  - simple mux/qualification logic
  - cases where combinational form is materially clearer
- When using a nontrivial combinational block for outputs/control, call out that it is a deliberate choice.

## Handshake guidance

- Define local helpers such as:
  - `req_fire`
  - `resp_fire`
  - `accepting_req_now`
- Use those helpers consistently instead of repeating full boolean expressions.
- Keep acceptance conditions close to the protocol story.
- Prefer a few high-value handshake helpers over many long compare helpers.
- If handshake progress needs "remembering" or holding behavior, prefer clocked logic instead of reconstructing everything through one big combinational block.

## Cache / pipeline control guidance

For modules like caches, arbiters, or pipeline controllers:

1. Separate the layers:
   - address decode
   - hit classification
   - FSM transitions
   - storage array control
   - response hold logic

2. Keep "current transaction" and "background work" visually distinct.
   - Example:
     - front-side request / response
     - refill / tail refill
     - eviction / writeback

3. If a section needs many helper wires, group and comment them by topic.
4. Do not import decode-style over-abstraction into local datapath choices.
   - If a target address or a select result is obvious at point of use, leave it direct.

## Testbench guidance

Use a small reusable structure, not a giant monolithic procedural block.

Preferred parts:

1. clock/reset generation
2. bus tasks or driver tasks
3. response monitor or protocol monitor
4. reusable check tasks
5. directed scenarios
6. assertions for timing/protocol contracts when helpful

For handshake-heavy DUTs:

- define `req_fire` / `resp_fire`
- write small tasks for one transaction
- keep protocol assertions near the interface semantics
- keep data checks in named tasks or mini-scoreboards

## Anti-patterns

Avoid code that feels generated:

- giant always blocks with several unrelated responsibilities
- deeply nested ternaries for control
- macros that hide most of the real assignments
- too many similarly named helper signals without grouping
- too many long equality/qualification wires at the top of the file
- comments that merely restate the code
- forcing every module into one universal template

## Repo preference extraction

When the user gives example files they like, infer style from them.

Current known preferences from this conversation:

- Likes `decoder`-style directness:
  - decode written in a straightforward semantic order
  - signal names remain close to architecture meaning
  - simple one-step outputs should stay simple instead of being expanded into helper chains
- Prefers clocked expression for control/hold behavior:
  - large `always @(*)` output blocks are not the default style
  - combinational control/output logic should be treated as a deliberate special case
- Likes `MIL1553_RT_r`-style explainability:
  - top-of-file flow comments
  - state names tied to behavior
  - higher comment density for tricky receive logic
- Dislikes hard-to-scan cache control:
  - too many derived signals at one level
  - protocol state and refill bookkeeping visually mixed together
- Prefers Chinese comments.
- Prefers keeping `_i/_o` on ports.
- Prefers only small, readability-driven use of SystemVerilog.

## When refactoring existing code

Refactor in this order:

1. add or improve the top-level intent comment
2. regroup declarations by function
3. split mixed combinational logic into smaller themed blocks
4. replace opaque helper names with semantic names
5. only then consider deeper structural cleanup

Do not rewrite large verified logic just to satisfy aesthetics unless readability gain is meaningful.
