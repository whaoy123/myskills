---
name: grill-driven-rtl-design
description: RTL architecture & module design driven by relentless interactive grilling and design-tree pruning before writing Verilog/SystemVerilog.
---

# Grill-Driven RTL Design

Execute an adversarial, requirement-clarification interview (Grill) specifically for FPGA/ASIC digital circuit design before synthesizing any RTL module.

## Workflow

1. **Clock & Reset Domains**: Clarify clock frequencies, reset polarity (async/sync active-low), CDC requirements, and domain crossings.
2. **Interface Protocol**: Define exact ready/valid handshakes, backpressure behavior, latency, burst length, and bus widths.
3. **Data Path & Throughput**: Establish throughput targets (1 item/cycle vs multi-cycle latency), pipelining stages, and DSP/BRAM/LUT resource trade-offs.
4. **Corner Cases & Error Handling**: Pinpoint overflow, underflow, timeout, out-of-order responses, and corrupted frames before writing RTL.
5. **Synthesizability & Coding Style**: Adhere to `synthesizable-human-rtl` standards for clean, readable, synthesis-safe SystemVerilog.

---

> **Attribution**: Combines the relentless questioning workflow from [Matt Pocock's grill-me](https://github.com/mattpocock/skills) with hardware RTL engineering best practices.
