# DIDA 智能日程管理 Skills

这是一组面向 Codex / ChatGPT Skills 的滴答清单任务管理技能。滴答清单是任务、规划偏好和长期工作记忆的唯一业务权威；本地只保存可重建的估时缓存、待同步操作和迁移预览。

## 目录

- `dida-cli`：滴答 CLI 的安全执行层。
- `dida-task-capture`：记录任务和收集箱事项。
- `dida-task-breakdown`：拆分父子任务并建立依赖。
- `dida-task-estimator`：估算任务日历占用时长。
- `dida-daily-planner`：生成并写入每日时间块。
- `dida-task-progress`：更新进度、状态、完成记录和实际耗时。
- `dida-weekly-review`：周复盘、截止风险和下周任务池。
- `dida-planning-profile`：维护作息、容量、移动权限等稳定规划偏好。
- `dida-planning-memory`：保存、检索、更新和遗忘长期项目规则、工具环境及工作约定。
- `dida-planning-core`：共享 Python 核心，不是独立对话 Skill。

## 数据归属

| 信息 | 唯一负责人 |
|---|---|
| 任务当前状态、正文、日期、依赖 | 对应滴答任务 |
| 稳定排期偏好 | `dida-planning-profile` |
| 跨项目长期规则、工具环境、工作约定 | `dida-planning-memory` |
| 项目专属长期规则 | 项目父任务下的独立记忆子任务 |
| 估时和实际用时样本 | 任务评论 + 可重建本地缓存 |
| 临时日程例外 | 当次计划/相关任务，不写长期记忆 |

`dida-planning-memory` 参考了 ChatGPT 记忆机制的边界：明确要求保存或遗忘时必须执行；稳定、直接陈述、低敏感且长期有用的信息可以自动保存并告知；推断出的偏好或敏感信息不会静默保存；翻译/改写素材、临时和琐碎信息不进入长期记忆。

## 安装

要求：

- Node.js 20 或更高版本；
- `npm install -g @suibiji/dida-cli`；
- Python 3.10 或更高版本；
- 已执行 `dida auth login`。

Windows PowerShell：

```powershell
.\install.ps1
```

Linux / macOS / WSL：

```bash
bash install.sh
```

安装脚本把九个 Skill 和共享核心复制到 `~/.agents/skills`。Codex 通常会自动发现变更；若未出现，重启 Codex 后运行 `/skills`。

## 首次使用顺序

1. 运行 `$dida-planning-profile 初始化系统配置`，建立“系统配置”清单及六个配置 NOTE。
2. 运行 `$dida-planning-memory 初始化长期记忆分类`，建立四个记忆分类父 NOTE，并把 ID 写回系统状态。
3. 运行 `$dida-task-capture 记录一个测试任务`，验证读写与回读。
4. 使用 `$dida-task-estimator` 为测试任务写入预计时长。
5. 使用 `$dida-daily-planner` 生成一天的时间块。
6. 确认稳定后，再使用迁移工具扫描旧 Markdown 系统。

## 记忆使用示例

```text
$dida-planning-memory 记住：南航发电机项目不能覆盖原始设计方案，只修改修改稿
$dida-planning-memory 查一下南航发电机项目有哪些长期规则
$dida-planning-memory 忘掉“默认使用某工具”的那条记忆
```

稳定规划偏好仍交给 profile：

```text
$dida-planning-profile 以后周三晚上不要安排科研任务
```

## 验证

```bash
python dida-planning-core/scripts/package_validator.py --root .
python -m unittest discover -s dida-planning-core/tests -v
```

## 审核资料

- `REVIEW_REPORT.md`：全部技能和共享核心的审查结论、修复项和剩余风险。
- `SUBAGENT_REVIEW_PROMPT.md`：在本地 Codex 中调用只读审查子代理的提示词。
- `.codex/agents/skill-reviewer.toml`：只读审查代理配置。
- `MANIFEST.sha256`：交付文件哈希。

## 迁移原则

迁移工具默认只生成预览，不直接写入滴答。应先去重、重建父子关系并人工检查歧义，再分批执行。旧系统的快照、会话、写锁、日/周计划投影和验证日志不迁移。旧记忆迁移时必须先按“任务事实 / 规划偏好 / 长期记忆 / 不迁移”重新分类，禁止把旧 Markdown 记忆库整体复制进一个 NOTE。可先运行 `scan_legacy.py`，再用 `classify_legacy_memory.py` 生成只读候选清单。
