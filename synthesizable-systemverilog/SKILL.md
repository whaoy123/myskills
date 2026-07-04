---
name: synthesizable-systemverilog
description: Use for any task that writes, refactors, reviews, debugs, or creates coding standards for synthesizable Verilog/SystemVerilog RTL in .v, .vh, .sv, or .svh files. Trigger for modules, interfaces, packages, typedefs, FSMs/state machines, datapaths, memories, clock/reset logic, CDC/RDC-sensitive logic, lint or synthesis warnings, FPGA/ASIC RTL cleanup, Verilog-to-SystemVerilog migration, or questions about synthesizable RTL style. Applies to ASIC and FPGA design code, not verification-only testbench code. Use alongside rtl-human-style when producing Verilog/SystemVerilog code so the result is both synthesis-safe and human-readable.
---

# Synthesizable SystemVerilog

## Operating Stance

Treat SystemVerilog as a hardware design language with a synthesizable subset, not as a verification-only language. Use constructs that expose hardware intent to simulators, linters, formal tools, CDC/RDC tools, and synthesis.

Before changing code, identify the target toolchain, project style guide, lint rules, reset policy, clocking policy, FPGA/ASIC target, and existing local idioms. If the target synthesis flow is unknown, mark tool-sensitive recommendations as assumptions rather than hard requirements.

Read `references/paper-notes.md` when the task asks for paper-derived rationale, a design standard, a broad audit checklist, or a Verilog-to-SystemVerilog migration plan. For ordinary implementation, keep the reference unloaded unless a rule needs deeper rationale.

## Implementation Workflow

1. Inspect nearby RTL before editing: naming, reset style, assignment style, package/import style, memory templates, and tool pragmas.
2. Preserve intentional project conventions unless they conflict with correctness or the user asks for a new standard.
3. Apply the rules below with explicit `Must`, `Should`, and `Tool-gated` judgment in comments, reviews, or docs.
4. Keep generated RTL structurally obvious: one clear hardware meaning per block, bounded loops, explicit widths, and reviewable connectivity.
5. When feasible, run the repo's formatter, lint, simulation, synthesis check, or compile target. If unavailable, state the unverified assumptions.

## Must Rules

Clocking, reset, and crossings:

- Use `always_ff` for flops with one primary clock event plus optional reset event. Do not mix unrelated clocks in one sequential block.
- Use clock enables instead of fabric-gated clocks unless the project uses approved clock-gating cells, primitives, or constraints.
- Follow the project reset strategy. If async resets are used, prefer asynchronous assertion with synchronous release unless the design standard says otherwise.
- Treat CDC/RDC paths as architecture-level concerns. Use reviewed synchronizers, async FIFOs, handshakes, reset synchronizers, or project-approved primitives; do not hide crossings inside ordinary combinational logic.
- Do not rely on FPGA `initial` values, declaration initialization, or memory initialization for ASIC-portable reset behavior unless the target policy explicitly allows it.

Assignments and procedural RTL:

- Use nonblocking assignments (`<=`) for sequential state updates in `always_ff`.
- Use blocking assignments (`=`) for combinational calculations in `always_comb`.
- Give combinational outputs safe defaults before conditional overrides, or assign every output on every path.
- Avoid read-before-write surprises and mixed blocking/nonblocking behavior in the same intent region.
- Treat unintended latch inference, multiple procedural drivers, and incomplete assignment as review blockers.

Types, widths, and signedness:

- Use 4-state `logic` for most control, state, and storage RTL so X issues remain visible in simulation.
- Use `bit` in RTL only when 2-state X-masking is intentional, reviewed, and harmless for reset, CDC, power, and invalid-state analysis.
- Use explicit sizes for literals, casts, shifts, concatenations, masks, counters, and address calculations when width is not self-evident.
- Guard `$clog2` edge cases such as depths of 0 or 1 with localparams or helper functions.
- Declare enum base widths when encodings or interface widths matter.

Decisions:

- Do not use `casex` in synthesizable RTL.
- Treat `casez`, wildcard matching, and `case inside` as reviewed exceptions; document why X/wildcard behavior is safe.
- Use `unique`, `unique0`, or `priority` only when the semantic promise is true. False promises can create simulation warnings and unsafe synthesis optimization.
- Provide explicit defaults or illegal-state handling where completeness is not mechanically guaranteed.
- Prefer language-level intent over `full_case` and `parallel_case` pragmas.

Synthesis boundary:

- Keep design RTL free of verification-only constructs: classes, randomization, dynamic arrays, queues, mailboxes, semaphores, delays in design behavior, and event-driven testbench idioms.
- Treat `initial`/`final` blocks, `fork`/`join`, `wait`, named events, `force`/`release`, DPI, hierarchical references, `real`/`shortreal`, strings, and file I/O as non-synthesizable or target-gated. FPGA or ROM/RAM initialization exceptions must be tied to a known template or vendor flow.
- Keep synthesizable helper code zero-time and structurally clear. Prefer pure `automatic` functions returning values; they should not write globals, depend on static state, use timing, or hide hardware through output/ref side effects.
- Use tasks or `void function` only when side effects are explicit, reviewed, and supported by the flow.
- Use bounded procedural loops for replicated combinational/sequential behavior. Use `genvar` and named generate blocks for elaboration-time replication.

## Should Rules

Reusable design structure:

- Use `enum` for finite sets such as FSM states, opcodes, modes, and protocol phases.
- Use `typedef` for shared vector widths, packed structs, enums, and interface-visible types.
- Put shared types, constants, parameters, and pure helper functions in named packages. Avoid `$unit` declarations for reusable design definitions.
- Prefer explicit package imports or narrow local wildcard imports. Avoid broad wildcard imports in shared headers and modules where collisions are likely.
- Use packed structs to group fields that move together as a bit-accurate value. Use unpacked arrays for collections of elements.
- Use `$bits` and `$clog2` for derived widths when supported, wrapped in readable localparams where useful.

Processes and style:

- Use `always_comb` for combinational logic and `always_latch` only for intentional latches.
- Split large combinational blocks when defaults, priority, and dataflow are no longer easy to audit.
- Use casts to document intentional size, signedness, enum, or packed-struct conversions.
- Use named endings for long modules, interfaces, packages, generate blocks, and nested procedural blocks when readability improves.

Connectivity:

- Use named port connections. Use `.*` only when names are deliberately aligned, local, and reviewable.
- Keep clocks, resets, scan/DFT, power intent hooks, and CDC-sensitive controls visible enough for downstream tools and reviewers.

Memories and inference:

- Follow project/vendor templates for RAM, ROM, shift-register, and DSP inference.
- Document read-during-write behavior, byte enables, reset behavior, and initialization expectations.
- Avoid resetting large inferred memories unless the target template and area/timing tradeoff are intentional.
- Treat FPGA memory init files, vendor attributes, and ASIC memory macros as target-specific code paths.

## Tool-Gated Rules

- Use synthesizable interfaces only after confirming synthesis, lint, CDC/RDC, formal, DFT, UPF/power, IP packaging, and netlist naming support. Interfaces should bundle coherent protocol signals, not unrelated controls.
- Use modports or type-specific interface ports only when the project flow preserves role, direction, and tool visibility.
- Use assertions in RTL as verification aids, not as synthesis constraints. Confirm whether the flow accepts, strips, binds, or requires `translate_off` handling for assertions, especially inside interfaces.
- Use `uwire`, `case inside`, `foreach`, package chaining, extern modules, configurations, user-defined net types, and advanced task/function argument features only after project tool support is proven.
- Use language-version directives such as ``begin_keywords`` only if the flow supports them. Prefer local `timeunit` and `timeprecision` over global ``timescale`` where the project permits.

## Review Workflow

When reviewing RTL, report findings in this order:

1. Synthesis correctness risks: non-synthesizable constructs, inferred latches, multiple drivers, reset/clock misuse, CDC/RDC hazards, memory inference mismatches, width/sign bugs.
2. Simulation-synthesis mismatch risks: blocking/nonblocking misuse, wildcard cases, X optimism/pessimism, incomplete decisions, unsafe pragmas, false `unique`/`priority` promises.
3. Maintainability risks: duplicated type declarations, untyped magic vectors, package/import sprawl, over-broad interfaces, unclear generated hierarchy.
4. Toolchain caveats: constructs that are good SystemVerilog but require confirmation in the project's synthesis, lint, CDC/RDC, formal, DFT, or FPGA vendor flow.

When creating a coding standard, separate rules into:

- Must: required for correctness, synthesis portability, or project consistency.
- Should: preferred style with rare exceptions.
- Tool-gated: use only after synthesis, lint, simulator, and downstream-flow support are confirmed.

## Compatibility Guidance

The source paper predates many current tool releases. Do not blindly preserve its 2013 support matrix. Use its design principles as a base, then verify modern support for constructs such as `uwire`, `case inside`, `foreach`, package imports, interface synthesis, assertions in RTL, and advanced task/function arguments.
