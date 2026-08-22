# Altium Schematic Autowire Skill

这是一个面向“连接关系已知、只想减少重复连线工作”的 Codex/Agent Skill。

## 推荐工作流

1. 将元件列表填入 `components.csv`。
2. 将每个网络的所有端点填入 `connections.csv`。
3. 运行 Skill 进行规范化和静态校验。
4. 查看 `03_validation_report.md`。
5. 仅在 PASS 或接受警告后，在 Altium 工程副本中运行 `.PrjScr/.pas`。
6. 编译工程并执行 ERC，再人工抽查关键网络。

## 为什么采用“一行一个网络端点”

相比 `FromRef/FromPin/ToRef/ToPin`，端点表可以直接描述一个网络连接三个或更多引脚，避免把星形网络拆成大量重复边，也便于检查同一引脚是否误入多个网络。

## 最快的绘图策略

默认让每个器件引脚拉一小段短线，再放置 Net Label。它比自动规划整页导线路径稳定得多，也更适合连接器、ADC 和多通道调理电路。

## 目录

- `SKILL.md`：完整 Skill 指令。
- `schemas/`：输入字段规范。
- `examples/`：示例任务。
- `templates/`：输出报告模板和脚本骨架。
- `references/OPEN_SOURCE_NOTES.md`：参考项目与取舍。

## 适合你的典型任务

- AVRplus 44 路连接器扇出。
- POR/PMG/CT 三相通道复制。
- 分压电阻、隔离放大器和 ADC 的批量连接。
- 多个相同连接器到测试点或端子的直通连接。

## 注意

此 Skill 的第一目标是“高速度、低重复劳动和连接可审查”，不是代替工程师决定电路拓扑。
