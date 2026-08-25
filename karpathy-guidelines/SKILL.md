---
name: karpathy-guidelines
description: Core software engineering, coding mindset, and AI system design principles based on Andrej Karpathy's guidelines and philosophy.
license: MIT
metadata:
  author: Andrej Karpathy
  source: https://github.com/karpathy
---

# Karpathy Engineering & Design Guidelines

Apply Andrej Karpathy's core engineering principles when designing, implementing, and debugging software and machine learning systems.

## Core Mindset & Principles

1. **Think First, Code Second**: Understand the problem deeply before writing a line of code. Write down the mental model, assumptions, and edge cases.
2. **Start with the Simplest Baseline**:
   - Build a trivial, working end-to-end pipeline before adding complexity.
   - For ML: Overfit a single batch first to prove the model and training loop work.
   - For software: Write a minimal reproduction or mock before full implementation.
3. **Understand Every Layer**:
   - Don't treat libraries or abstractions as black boxes. Know what is happening underneath.
   - Read the source code of dependencies when behavior is unexpected.
4. **Fast Iteration Speed**:
   - Optimize developer feedback loops. Shorten the time from edit to test.
   - Keep scripts and tests deterministic and fast.
5. **Simplicity over Cleverness**:
   - Prefer readable, explicit code over overly abstract or clever patterns.
   - Eliminate dead code, unused parameters, and premature generalizations.
6. **Data & Verification First**:
   - Look directly at raw data, shapes, distributions, and logs.
   - Add assertions and sanity checks everywhere invariants are expected.

---

> **Attribution**: Synthesized from [Andrej Karpathy's](https://github.com/karpathy) open-source projects, talks, and engineering guidelines under the [MIT License](https://opensource.org/licenses/MIT).
