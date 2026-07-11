---
name: synthesizable-human-rtl
description: Use for writing, refactoring, reviewing, debugging, or explaining synthesizable Verilog/SystemVerilog RTL in .v, .vh, .sv, or .svh files, including FSMs, datapaths, memories, clock/reset, CDC/RDC-sensitive logic, and FPGA/ASIC cleanup. Default to SystemVerilog for new RTL; combine synthesis-safe design rules with readable handwritten structure, semantic names, and Chinese intent comments.
---

# Synthesizable Human RTL

Write RTL that is synthesis-safe, tool-aware, and easy for a hardware engineer to understand.

## Priority and language choice

Apply rules in this order:

1. Project conventions and proven toolchain limits.
2. Synthesis correctness: clocks, resets, CDC/RDC, drivers, assignment semantics, widths, and memory inference.
3. Readability: meaningful decomposition, naming, and comments.

For new design RTL, create `.sv` / `.svh` files and use supported SystemVerilog constructs (`logic`, `always_ff`, `always_comb`, sized enums, `typedef`, and packages) when they improve clarity.

For existing `.v` / `.vh` files, preserve Verilog-2001 syntax unless the user requests migration or the repository and target flow already support SystemVerilog. Do not introduce SystemVerilog syntax into a `.v` file merely by default.

Before changes, inspect nearby RTL and identify the synthesis/simulation toolchain, project reset and clocking policy, FPGA/ASIC target, and local style. State unknown tool-sensitive assumptions.

## Synthesis rules

- Use one clock domain per `always_ff`; use nonblocking assignments for sequential state and blocking assignments in `always_comb`.
- Do not gate fabric clocks. Follow the project reset policy; treat asynchronous reset release and CDC/RDC as explicit architecture concerns.
- Provide defaults or complete assignments for combinational outputs. Treat latches, multiple procedural drivers, and read-before-write ambiguity as blockers.
- Use explicit literal widths, casts, signedness, counter bounds, and guarded `$clog2` calculations. Declare enum base widths when encoding matters.
- Do not use `casex`. Use wildcard cases, `unique`, `priority`, assertions, interfaces, and advanced SV features only when their semantic promise and tool support are established.
- Keep design RTL free from verification-only or timing constructs such as classes, randomization, dynamic arrays, queues, delays, events, file I/O, DPI, and `force`/`release`.
- Use bounded loops and named generate blocks. Follow proven vendor/project templates for RAM, ROM, DSP, and initialization behavior.
- Use reviewed synchronizers, async FIFOs, or handshakes for crossings; never conceal a crossing in ordinary combinational logic.

## Human-readable RTL structure

- Start from the dataflow story: what is stored, what advances it, key decisions, and which outputs are decoded versus registered.
- Give each block one responsibility. Usually separate decode/qualification, next-state logic, state update, datapath updates, and output generation.
- Prefer explicit state names tied to behavior and separate next-state and state-register blocks for nontrivial FSMs. Add a short state-flow comment when useful.
- Prefer clocked logic for hold behavior and protocol progress. Use combinational blocks for pure decode, qualification, next-state decisions, and clear muxes.
- Keep straightforward expressions local. Extract a helper only when it captures a real protocol concept, is reused, or materially improves a branch.
- Use semantic names rather than mechanical placeholders. Keep `_i` / `_o` on ports by default; use `_d` / `_q` only when it genuinely clarifies a next/current pair.
- Add Chinese comments for module purpose, tricky control flow, state-hold behavior, protocol constraints, and corner-case intent. Explain why, not syntax. Preserve an English-only repository convention unless the user approves a change.
- Give every newly declared RTL variable its own nearby Chinese intent comment. In this user's preferred declaration layout, put that comment at the end of the declaration line; group variables of the same function contiguously without blank lines, and use a blank line plus a short block comment only between different functional groups.
- For three-process FSMs, use concise responsibility headings in the user's preferred form, such as `// 状态机转移判定` and `// 状态机更新`; do not label blocks "第一段/第二段/第三段". Give detailed comments to timing-sensitive counters such as `// SYNC 对齐计数器独立更新`, and keep routine state-register comments brief.
- In a clocked block whose behavior depends on FSM state, use `case (state_reg)` so each state's sequential work is visible together; do not hide state-specific actions in long `else if` chains. Organize the module's logic in protocol-time order: sampling and sync-header detection first, then alignment and data reception, and finally end-of-word checks such as parity. Do not force IDLE-only initialization ahead of earlier protocol stages merely because it belongs to IDLE.
- For timing-sensitive protocol logic, explain comments as a readable sequence of elapsed beats, the resulting sample-window location, and the purpose (for example, "进入 SYNC 一拍 + 保持 14 拍 + 进入 DATA 一拍"). Avoid relying solely on abstract labels such as `P1/P16` when a reader cannot reconstruct the data position from them.
- Treat `valid` plus its data, type, and error fields as one held result bundle: once produced, keep every field stable until a successful ready/valid handshake or until the documented contract allows a newly completed result to overwrite it. If handshake and new completion happen on the same edge, make the new result the explicit higher-priority update so it is not lost.
- Keep error semantics non-overlapping: each protocol stage sets its own named error register at the point the condition is detected (for example Manchester, parity, or word-length). The final result stage may OR those stored flags for an aggregate error output, but do not introduce a composite error qualification that repeats or obscures earlier checks.
- Prefer named port connections. Keep clocks, resets, and CDC-sensitive controls visible.

## Workflow

1. Inspect the local RTL idioms and tool constraints.
2. Identify correctness risks first: synthesis boundary, clock/reset/CDC, drivers, latches, widths/signedness, and memory behavior.
3. Implement the smallest clear structure that meets the function.
4. Review simulation-versus-synthesis risks: incomplete decisions, X behavior, wildcard cases, and false `unique`/`priority` promises.
5. Run available compile, lint, simulation, or synthesis checks. Report any unverified tool assumptions, then remove tool-generated libraries and logs (for example `xsim.dir`, `xvlog.log`, `xvlog.pb`) unless the user explicitly asks to keep them.

## Oversampled serial receiver pattern

For a protocol receiver that samples a serial line at a fixed oversampling ratio, keep the sample shift window running continuously and let the IDLE state gate *detection*, not the physical history collection. State the oldest/newest bit convention in the declaration comment.

- When a sequential block must decide from the sample being captured on that same clock edge, form a combinational `next_shift_window = {shift_reg[W-2:0], rx_i}` and decode that window. Do not accidentally decode the pre-shift register and introduce an undocumented extra cycle.
- For a multi-stage word, give each protocol phase an explicit role: sync recognition/alignment, data-symbol collection, then parity/end-of-word validation. Keep their counters separate when they describe different timing concepts.
- If a later CHECK phase needs a following symbol or gap to move into a central decode window, explain the exact elapsed samples and window indices in Chinese comments; do not compress this into an unexplained magic counter value.
- Set each concrete error flag in the state where its condition is observed. Preserve those flags until the result stage; the result stage only aggregates them into the externally visible error field.
- If an enable is allowed to change only between words, latch it in IDLE and hold it for the entire active word. Do not drive an external receive-enable directly from a live control input during reception.
- In sequential `case` branches, an omitted assignment already expresses register hold. Avoid redundant self-assignments such as `q <= q;` unless a target flow specifically requires them.
- When deriving verification scenarios from a sampled window, calculate the exact protocol samples occupying that window before classifying a normal sequence as an error. Test plans must cover normal protocol traffic—including back-to-back words—according to the specification; do not weaken or exclude valid behavior merely because an incomplete RTL version might reject it. Use fault injection only for behavior that is actually outside the protocol contract.

## Review output order

Report: (1) synthesis correctness risks, (2) simulation/synthesis mismatch risks, (3) readability and maintainability improvements, then (4) toolchain caveats.
