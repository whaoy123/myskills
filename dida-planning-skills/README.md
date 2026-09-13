# DIDA 智能日程管理 Skills

这是一组面向 Codex / ChatGPT Skills 的滴答清单任务规划技能。

**滴答清单是任务事实的唯一业务权威；Skill 负责“怎么规划”，MCP/连接器负责“怎么读写”。** 模型记忆、聊天上下文和本地缓存只能补充背景，不能用于证明任务清单完整。

## 运行架构

```text
                    dida-planning-profile
                             ↓
                     dida-task-breakdown
                             ↓
                     dida-task-estimator
                             ↓
                     dida-daily-planner
                             ↓
                 TickTick / 滴答清单 MCP
                             ↑
            dida-task-progress / weekly-review
```

- **首选执行层：TickTick / 滴答清单 MCP 或等价一等连接器工具。**
- **兼容回退：`dida-cli`。** 仅在运行环境没有可用 MCP/连接器时使用；不再作为 ChatGPT 场景的默认读写路径。
- `dida-planning-core` 保留为估时、依赖、容量、迁移等确定性逻辑库，不承担任务事实存储。

## 目录

- `dida-manager`：唯一顶层入口与意图路由。
- `dida-task-capture`：任务分类、去重、归档和录入规则。
- `dida-task-breakdown`：拆分父子任务并建立依赖。
- `dida-task-estimator`：估算任务日历占用时长。
- `dida-daily-planner`：全局风险扫描、日/周容量规划；只有用户明确要求时才生成具体时钟块。
- `dida-task-progress`：更新进度、状态、完成记录和实际耗时。
- `dida-weekly-review`：周复盘、截止风险、最晚启动风险和下周任务池。
- `dida-planning-profile`：维护作息、容量、移动权限等稳定规划偏好。
- `dida-planning-memory`：保存长期项目规则、工具环境及工作约定；不承担当前任务事实。
- `dida-planning-core`：共享 Python 核心，不是独立对话 Skill。
- `dida-cli`：**legacy/local fallback**，仅在没有 MCP/连接器时提供本地 CLI 读写。

## 数据归属

| 信息 | 权威来源 |
|---|---|
| 当前任务、状态、正文、日期、父子关系、完成状态 | 滴答清单 |
| 稳定排期偏好 | `dida-planning-profile` 对应运行态配置 |
| 跨项目长期规则、工具环境、工作约定 | `dida-planning-memory` / 明确的运行态规则 |
| 项目专属长期规则 | 项目父任务下的规则记录或明确项目配置 |
| 估时和实际用时样本 | 任务评论 / focus 记录 + 可重建缓存 |
| 临时日程例外 | 当次计划/相关任务，不写长期记忆 |
| 模型记忆、聊天上下文 | 仅作背景提示，**不得作为任务完整性来源** |

## 全局规划安全契约

当用户要求的是**全局规划**，例如：

- “帮我安排今天/这周”；
- “我现在应该干什么”；
- “看看我所有任务怎么排”；
- “把近期任务整体整理一下”；

在给出计划前必须先通过 MCP/连接器完成一次**全量未完成任务扫描**：

1. 枚举所有当前可访问项目/清单；
2. 读取所有未完成任务，处理分页，不得只看“今天/未来 7 天”；
3. 同时保留无日期任务、远期任务、waiting 任务和父任务的必要元数据；
4. 检查硬截止、剩余估时、依赖、外部等待、必要提前量和未来真实容量；
5. 为有截止/交付约束的任务判断 **latest safe start（最晚安全启动时间）**；
6. 只在完成上述风险扫描后，选择今天/本周真正应该进入执行池的任务。

### 最晚安全启动时间

`latest_safe_start` 不是简单的截止日前一天。应综合：

- 任务自身 remaining work；
- 必须串行的前置任务时长；
- 审核、采购、打样、物流、预约、等待反馈等外部 lead time；
- 估时不确定性和必要 buffer；
- 截止前用户真实可用容量。

如果信息不足，标记“启动风险未知”，不能因为 due date 很远就默认安全。

**局部 CRUD 不要求全量扫描。** 例如“把拿伞改到周二”“这个任务完成了”“加一个 BOM 核对任务”，只需精确解析相关任务并修改，避免无意义的全库读取。

## 规划与执行边界

- Skill 决定：分类、拆解、估时、依赖、优先级、容量和风险。
- MCP/连接器执行：搜索、读取、创建、更新、移动、完成、评论、focus 等真实操作。
- 对写操作执行 read-before-write / write / read-back；遇到超时先读取确认，避免重复写入。
- 只有用户明确要求具体时间块时才生成具体时钟；“安排这周”默认按天/优先级规划，不擅自制造执行块。

## 安装

### MCP / 连接器环境（推荐）

只需安装这些规划 Skill；不要求本地 `dida-cli` 登录。运行时直接使用可用的 TickTick/滴答清单 MCP 或连接器工具。

### 本地 CLI 回退环境

仅当没有可用 MCP/连接器、需要在本地 Codex 中直接访问滴答时，才需要：

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

## 推荐使用顺序

1. `dida-manager` 判断是局部操作还是全局规划。
2. 全局规划先执行全量未完成任务扫描。
3. 范围不清先用 `dida-task-breakdown`。
4. 时间不可信先用 `dida-task-estimator`。
5. 用 `dida-daily-planner` 做风险/容量规划。
6. 通过 MCP/连接器应用变更并 read-back。
7. 实际执行后由 `dida-task-progress` 写入进度/实际耗时。
8. 周期性由 `dida-weekly-review` 检查积压、截止和最晚启动风险。

## 验证

```bash
python dida-planning-core/scripts/package_validator.py --root .
python -m unittest discover -s dida-planning-core/tests -v
```

## 迁移原则

迁移工具默认只生成预览，不直接写入滴答。应先去重、重建父子关系并人工检查歧义，再分批执行。旧系统的快照、会话、写锁、日/周计划投影和验证日志不迁移。旧记忆迁移时必须先按“任务事实 / 规划偏好 / 长期记忆 / 不迁移”重新分类，禁止把旧 Markdown 记忆库整体复制进一个 NOTE。
