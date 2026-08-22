---
name: dida-task-estimator
description: Estimate duration for Dida tasks using half-hour rounded up tags (#0.5h, #1.0h, #1.5h, #2.0h, #2.5h, #3.0h). Use for “大概多久”, “估时”, “重新估计剩余时间”, or task size assessment.
---

# Dida Task Estimator

Estimate realistic effort for tasks based on developer skill context, domain complexity, and risk buffer, outputting standardized half-hour tags.

## Estimation Tag Rules (半小时向上取整)

All task estimates are represented as tags on the task:

| Estimated Time | Tag to Apply | Typical Scenario |
| :--- | :---: | :--- |
| 1 ~ 30 mins | `#0.5h` | 周报、简单沟通/对齐、电阻改封装、爬电间隙核对、开票、收据处理 |
| 31 ~ 60 mins | `#1.0h` | 独立子模块TB改进、段落去重精炼、仓库结构与入口梳理 |
| 61 ~ 90 mins | `#1.5h` | 原理图接口设计、格式总校对、PCIe数据流图、基础数据通路研读 |
| 91 ~ 120 mins | `#2.0h` | CDC/复位RTL研读、上位机功能改造、以太网控制实验、Ibex RTL学习 |
| 121 ~ 180 mins | `#3.0h` | RPC最小可行性实验、PCB整体布局布线、Cache重写设计 |

## Guidelines

1. **Tag Format**: Add `#0.5h`, `#1.0h`, `#1.5h`, `#2.0h`, `#2.5h`, `#3.0h` to task tags.
2. **Context-Aware**: Read `记忆｜用户背景与技能栈` and `估时配置｜特征与风险缓冲` to accurately evaluate effort.
3. **Rationale in Body**: Keep a 1-line rationale inside the task description (e.g. `## 估时依据：...`).
4. **No Clock Schedule**: Duration tags are for workload planning; do not create start/end clock times.
