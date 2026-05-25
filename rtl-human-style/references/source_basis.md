# Source Basis

Primary external references used while shaping this skill:

1. lowRISC Verilog Coding Style Guide
   - https://github.com/lowRISC/style-guides/blob/master/VerilogCodingStyle.md
2. lowRISC DV Coding Style Guide
   - https://github.com/lowRISC/style-guides/blob/master/DVCodingStyle.md
3. Verible linter docs
   - https://chipsalliance.github.io/verible/verilog_lint.html
4. Verible formatter docs
   - https://chipsalliance.github.io/verible/verilog_format.html
5. systemverilog.io style guide
   - https://www.systemverilog.io/verification/styleguide/
6. OpenTitan DV methodology
   - https://opentitan.org/earlgrey_1.0.0/book/doc/contributing/dv/methodology/index.html

How this skill uses them:

- `lowRISC`: structure and naming discipline
- `Verible`: enforceable subset ideas
- `systemverilog.io`: presentation and readability conventions
- `OpenTitan DV`: testbench decomposition and protocol-check placement

This skill intentionally does not copy any one guide verbatim. It synthesizes them into a more human-handwritten RTL style.
