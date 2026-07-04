# Paper Notes: Synthesizing SystemVerilog

Source: Stuart Sutherland and Don Mills, "Synthesizing SystemVerilog: Busting the Myth that SystemVerilog is only for Verification", SNUG Silicon Valley 2013. These notes are an internal distilled summary from the locally provided PDF, not a replacement for the original paper.

Use this reference as a design-standard companion, not as a current synthesis support matrix. The paper was based on Synopsys Design Compiler 2012.06-SP4 and Synplify-Pro 2012.09-SP1. Confirm support in the active simulator, lint, formal, CDC/RDC, DFT, FPGA vendor, and synthesis tools.

## Core Thesis

SystemVerilog extends Verilog for both design and verification. Many additions are useful for synthesizable RTL because they reduce duplicated declarations, make intent checkable, and prevent simulation/synthesis mismatches.

The useful design stance is: write the clearest synthesizable SystemVerilog subset that the project toolchain and downstream flow support.

## Paper-Derived Rules

Declarations and types:

- Prefer `logic` for most design declarations, then use explicit net types only where net behavior is part of the design intent.
- Prefer 4-state `logic` for most control/storage RTL because 2-state `bit` can hide Xs from reset, CDC, power-intent, and invalid-state problems.
- Use `bit` only for deliberately 2-state datapath modeling or tool-verified cases where X masking is acceptable.
- Use `enum` for values with a finite legal set. This is especially important for FSM states and protocol modes.
- Use `typedef` liberally for shared vectors, enums, structs, and interface-visible types.
- Use packed structs to group related fields that must move as a bit vector; use unpacked arrays for element collections.
- Use packages for shared declarations. Avoid `$unit` because it creates fragile compile-order and namespace coupling.

Parameterized and reusable RTL:

- Prefer parameterized modules and package-defined types over repeated local declarations.
- Keep package imports close enough to be clear. Avoid wildcard imports when name collisions are likely.
- Use `$bits` and `$clog2` for derived widths, with guarded localparams when edge cases such as depth 0 or 1 are possible.

Procedural RTL:

- Use `always_comb`, `always_latch`, and `always_ff` to express intent and let tools check it.
- Use `always_ff` with a single primary clock and optional reset event; keep unrelated clocks in separate blocks.
- Use nonblocking assignments for flops and blocking assignments for combinational calculations.
- Treat `always_latch` as a declaration of intent, not a way to silence warnings.
- Avoid increment/decrement and compound assignment operators in RTL when they hide ordering or width effects; use explicit assignments when clarity is better.
- Use casts to resolve intentional size or type conversions and to silence only meaningful warnings.

Decision logic:

- Avoid `casex` in synthesizable RTL.
- Treat `casez`, `case inside`, and wildcard matching as reviewed exceptions because wildcard/X behavior must match the design intent.
- Use `unique`, `unique0`, and `priority` only when they accurately describe the decision tree.
- Prefer language-level intent over synthesis pragmas such as `full_case` and `parallel_case`.
- Add assertions around case expressions, enum validity, and impossible states when they document and check assumptions, but handle them according to the project's synthesis/formal flow.

Subroutines:

- Prefer pure `automatic` functions returning values for reusable RTL behavior.
- Preferred RTL functions should not write globals, depend on static state, use timing, or hide hardware through output/ref side effects.
- Allow zero-time tasks or `void function` only when side effects are clear and tool support is proven.
- Avoid timing controls and verification-style behavior in design subroutines.
- Treat defaulted task/function inputs, `ref` arguments, and other advanced features as tool-gated unless the project flow proves support.

Connectivity and hierarchy:

- Use named port connections for clarity.
- Use dot-name and dot-star shortcuts only where naming conventions make the connection obvious and reviewable.
- Use interfaces only when the full downstream flow supports them and the interface bundles a coherent protocol or bus.
- Avoid interfaces that collect unrelated clocks, resets, DFT, power, or miscellaneous controls simply to reduce port count.
- Use modports or type-specific interface ports when they help establish role and direction and are supported by the flow.

Loops, generate, and replication:

- Use bounded procedural loops for fixed hardware replication or reductions.
- Use `genvar` and named generate blocks for elaboration-time replication.
- Treat `foreach` as a readability improvement only after synthesis support and generated hardware clarity are confirmed.
- Avoid dynamic or data-dependent loop bounds that do not map to fixed hardware.

Memory and target inference:

- Use the project's known RAM/ROM inference templates rather than generic array code when inference quality matters.
- Document read-during-write behavior, byte enables, reset behavior, and initialization mechanism.
- Separate FPGA-specific initialization and vendor attributes from ASIC-portable RTL assumptions.

File and time semantics:

- Use explicit language-version controls only if the project flow supports them and benefits from them.
- Prefer local `timeunit` and `timeprecision` over global ``timescale`` behavior where project policy permits.
- Use named block/module endings when they improve readability in large nested RTL.

Tool-gated or cautionary constructs:

- `uwire` is valuable for single-driver intent, but practical use depends on synthesis, simulation, lint, and netlist flow support.
- Assertions in RTL are verification aids; synthesis may ignore, reject, strip, or require special pragmas or bind flows.
- Package chaining, extern modules, configurations, user-defined net types, and generic net types need project-specific support confirmation.
- Interfaces are synthesizable in many flows, but support quality varies with hierarchy, modports, arrays of interfaces, DFT, UPF, CDC tools, IP packaging, and generated netlists.

## Review Checklist

Use this checklist when asked to audit RTL against the paper:

- Are ports and internal signals typed consistently, with `logic`, `bit`, and explicit nets used intentionally?
- Are finite-value variables represented as enums with appropriate base widths?
- Are repeated widths and field groups represented as typedefs, structs, and packages?
- Are shared declarations in named packages rather than `$unit`?
- Are procedural blocks written with `always_comb`, `always_ff`, or intentional `always_latch`?
- Do sequential blocks use nonblocking assignments and combinational blocks use blocking assignments?
- Are resets, generated clocks, clock enables, CDC paths, and RDC paths handled by approved patterns?
- Are case statements free of unsafe `casex` usage?
- Are `casez`, `case inside`, and wildcard matches justified?
- Do `unique`, `unique0`, and `priority` match the actual design promise?
- Are full/parallel case pragmas absent or justified?
- Are functions/tasks zero-time, synthesizable, and free of unclear side effects?
- Are loops bounded and generate blocks named/reviewable?
- Are memory inference, initialization, and read-during-write semantics target-appropriate?
- Are interfaces used only for coherent signal groups and supported by downstream tools?
- Are assertions handled according to synthesis/formal/lint policy?
- Are time and language-version directives local and project-compatible?
- Are tool-sensitive constructs called out with a required synthesis/lint/downstream-flow check?
