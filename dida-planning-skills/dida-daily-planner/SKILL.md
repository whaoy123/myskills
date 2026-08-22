---
name: dida-daily-planner
description: Build or revise daily time-block recommendations with capacity and breaks ONLY when the user explicitly asks for schedule planning. Use ONLY for explicit user prompts like “帮我安排今天的具体日程”, “排一下今天的时间”, or “给今天的任务排个时段”. Do NOT trigger automatically for general task breakdowns or backlog queries.
---

# Dida Daily Planner (On-Demand Mode)

Provide actionable daily schedule recommendations **only upon explicit user request**.

## Operation Boundary

1. **Default Rule**: Under normal circumstances, the user independently picks tasks from the backlog to execute. Do NOT generate clock execution blocks automatically.
2. **Explicit Trigger Only**: Only when the user explicitly says "帮我安排今天/明天的具体日程", "排一下时间块", or similar scheduling commands, activate this planner.
3. **Capacity & Breaks**: Account for realistic rest, focus blocks (typically 30-90 min), and buffer.
4. **No Direct Overwrite of Hard Deadlines**: Propose execution slots without shifting external milestones.
