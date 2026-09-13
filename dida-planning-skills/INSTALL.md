# 安装与升级

## 推荐运行方式：MCP / 连接器

如果运行环境已经提供 TickTick / 滴答清单 MCP 或一等连接器工具，只需要安装规划 Skills；**不要求安装或登录 `dida-cli`**。

运行时职责：

```text
规划 / 拆解 / 估时 / 复盘 → dida-planning-skills
真实任务读写               → TickTick / 滴答清单 MCP
```

## 本地 CLI 回退（可选）

只有在 Codex/本地 Agent 环境没有可用 MCP/连接器、仍需要直接访问滴答时，才安装 DIDA CLI：

```powershell
node --version
npm install -g @suibiji/dida-cli
dida --version
dida auth login
dida auth status
```

CLI 版本可能改变参数。遇到未知字段时，以本机 `dida <group> <command> --help` 为准。

`dida-cli` 是 legacy/local fallback，不应在已有 MCP 的 ChatGPT 场景中成为默认执行路径。

## 安装 Skills

PowerShell：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\install.ps1
```

安装到其他位置：

```powershell
.\install.ps1 -Destination "D:\your-repo\.agents\skills"
```

Linux / macOS / WSL：

```bash
bash install.sh
```

安装脚本会覆盖同名技能目录，但不会删除其他技能。

## 升级

升级前如需保留本地估时缓存和待同步队列，可备份：

```text
~/.agents/skills/dida-planning-core/state/
```

这些文件不是业务权威；当前任务事实始终以 TickTick/滴答清单为准。缓存丢失后应能从远端任务、评论和 focus 记录重建。

## 首次初始化配置

已有运行态配置时不要重复初始化或覆盖。

确实是首次使用时，可按需执行：

```text
$dida-planning-profile 初始化系统配置
$dida-planning-memory 初始化长期记忆分类
```

初始化写入同样优先通过 MCP/连接器完成；只有没有连接器时才使用 CLI fallback。

## 全局规划验收

安装后做一次全局规划测试，确认：

1. 能枚举全部项目/清单；
2. 能读取全部未完成任务并处理分页；
3. 无日期和远期任务也进入风险检查；
4. planner 会检查 deadline、dependency、external lead time 和 `latest_safe_start`；
5. 写回操作能够 read-back 验证；
6. 用户未要求时不会自动生成具体时钟执行块。
