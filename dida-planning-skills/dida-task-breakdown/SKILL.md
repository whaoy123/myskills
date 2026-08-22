---
name: dida-task-breakdown
description: Decompose a Dida parent task into clean sub-tasks, deliverables, completion criteria (DoD), and half-hour estimate tags (#0.5h, #1.0h...). Use when the user asks to 拆任务, 细化项目, 建立子任务, 任务划分, 整理任务池, or identify prerequisites. Do not generate daily clock execution blocks.
---

# Dida Task Breakdown

Turn complex projects and milestones into structured, atomic sub-tasks with clear completion criteria (DoD) and estimated duration tags.

## Core Architectural Mapping (四大主干体系)

All research and technical tasks belong to one of the following branches:

1. **🚀 1553B 课题** (清单: `研究生`)
   - `开题报告`（去重精炼、格式校对、PPT对齐、导师/师兄沟通）
   - `上位机与通信`（代码研读、功能改造、以太网控制实验、RPC实验）
   - `1553B IP核与收发`（BM/RT/BC 模块、协议收发工程）
2. **⚡ AVRplus 复刻** (清单: `研究生`)
   - `调理隔离板`（原理图接口设计、PCB布局布线、爬电间隙核查、电阻选型、DIAG测试点）
   - `Field 采样与励磁`（自研内部 FIELD_GND 差分采样）
3. **📚 Verilog 写法学习** (清单: `研究生`)
   - `common_cells`（仓库结构、基础数据通路、仲裁/流路由、CDC/复位、验证对应）
   - `pulp_axi`（模块化总线设计）
   - `taxi`（数据流与 Cocotb 验证）
4. **💼 数字IC 找工作** (清单: `工作`)
   - `UART/低速总线 IP核`（参数化、RTL与验证）
   - `PCIe`（分层与数据流、DLP RTL与测试、规范标注）
   - `集创赛与 CPU 体系`（Ibex 分层与验证、TileLink/CHI、RVWMO、Cache 重写）
   - `前端交付流程`（Lint、CDC、综合、STA、PPA）
5. **📦 485 相关工程与TB**
   - 独立归档于【研究生，任务归档】清单，不与主线混杂。

## Breakdown Guidelines

1. **Atomic & Executable**: Each leaf task should have a clear deliverable and concise `## 完成标准 (DoD)`.
2. **Tagging with Estimation**: Apply `#0.5h`, `#1.0h`, `#1.5h`, `#2.0h`, `#2.5h`, `#3.0h` tags based on task complexity (rounded up to 0.5h).
3. **No Clock Blocks**: Do not generate rigid time-of-day execution blocks (e.g. `10:30-11:15`); let the user freely select tasks each day.
4. **Checklists**: Use checklist items for fine-grained steps under a task.
