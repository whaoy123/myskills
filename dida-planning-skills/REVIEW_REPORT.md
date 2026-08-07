# DIDA 智能日程管理 Skills 最终审查报告

## 1. 审查范围

本次审查覆盖：

- 9 个用户 Skill 的触发条件、职责边界和渐进加载；
- `dida-planning-core` 的解析、依赖、排期、估时、进度、冲突合并、同步队列和迁移脚本；
- 6 个规划配置 NOTE 模板和 4 个长期记忆分类模板；
- Windows/Linux 安装脚本；
- 旧 Markdown 系统的任务、估时和记忆迁移预览；
- README、审查子代理配置和测试。

版本：`1.1.0`，日期：`2026-08-06`。

## 2. 最终结论

当前包已经满足以下核心约束：

1. 滴答清单是任务、规划偏好和长期工作记忆的唯一业务权威。
2. 本地只保留可重建估时缓存、待同步操作和迁移预览，不形成第二个可编辑数据库。
3. 规划偏好、长期记忆、任务当前事实和估时样本有明确且互斥的负责人。
4. 长期记忆采用独立原子任务，不恢复单体 Markdown 记忆文件。
5. 记忆条目不会被误当成普通任务参与排期、估时、进度或周统计。
6. 自动保存策略与 ChatGPT 记忆机制一致：显式保存/遗忘优先；稳定直接陈述的低敏信息可自动保存并告知；推断、冲突和敏感信息默认先确认。
7. 所有 Skill 保持短小，详细协议按需从 references 和共享脚本读取。

未发现阻止交付的已知高危问题。

## 3. 自动验证结果

- 包结构校验：**9 个 Skill，0 errors，0 warnings**。
- Python 单元测试：**21 项全部通过**。
- 全部 Python 文件编译检查：通过。
- 临时目录完整安装：通过，识别到 9 个 Skill 和共享核心。
- Skill 主文件总行数：553 行；单个 `SKILL.md` 为 46～78 行。
- 旧系统扫描：识别 21 个任务、6 个重复规则、1 个偏好、1 个估时校准和 1 个旧记忆文件。
- 旧记忆预览：9 个条目中，6 个自动判定不迁移，3 个进入人工复核，0 个直接写入滴答。
- 所有迁移脚本默认 `writes_performed: false`。

验证命令：

```bash
python dida-planning-core/scripts/package_validator.py --root .
python -m unittest discover -s dida-planning-core/tests -v
bash install.sh /tmp/dida-skills-install-test
```

## 4. 按严重程度的发现与修复

### 高：缺少通用长期记忆负责人 — 已修复

原 1.0.0 版只有 `dida-planning-profile`，项目规则、工具环境和跨项目工作方式没有明确落点，容易被错误塞进偏好或某个普通任务。

修复：新增 `dida-planning-memory`，并明确四类所有权：

- 排期偏好 → `dida-planning-profile`；
- 任务当前事实 → 对应任务；
- 估时证据 → estimator/progress；
- 跨任务长期规则 → `dida-planning-memory`。

涉及：

- `dida-planning-memory/SKILL.md`
- `dida-planning-core/references/system-spec.md`
- `README.md`

### 高：记忆子任务可能被当成工作任务 — 已修复

项目专属记忆挂在项目父任务下，如果只依赖 `required_for_parent: false`，仍可能被日计划、估时或周复盘读取为普通任务。

修复：增加 `config`、`memory_category`、`memory` 三类非工作角色的统一排除逻辑。

- 排程器返回 `non_work_record`，不安排记忆；
- 估时器拒绝给记忆估时；
- 父任务进度和完成门禁忽略记忆；
- 各上层 Skill 明确从任务指标中排除记忆和配置记录。

涉及：

- `dida-planning-core/scripts/common.py`
- `dida-planning-core/scripts/scheduling_engine.py`
- `dida-planning-core/scripts/estimation_engine.py`
- `dida-planning-core/scripts/progress_engine.py`
- `dida-daily-planner/SKILL.md`
- `dida-task-estimator/SKILL.md`
- `dida-task-progress/SKILL.md`
- `dida-weekly-review/SKILL.md`

### 高：自动记忆可能因调用方漏传字段而过度保存 — 已修复

初版 `memory_policy.py` 将缺失的 `directly_stated` 默认为真，调用方漏传时可能把推断信息当作直接陈述。

修复：改为失败安全，缺失时默认不自动保存。只有同时满足：

- `stable: true`
- `future_useful: true`
- `directly_stated: true`
- 非敏感、非推断、非冲突

才允许自动保存。

涉及：

- `dida-planning-core/scripts/memory_policy.py`
- `dida-planning-core/tests/test_core.py`

### 中：偏好和记忆可能双写 — 已修复

“以后周三晚上不排科研”属于排期偏好；“项目原始 Word 不得覆盖”属于项目规则。若不先判断所有权，可能同时写进 profile 和 memory。

修复：所有保存动作先进行 owner routing，并禁止为方便而复制同一事实。

涉及：

- `dida-planning-memory/SKILL.md`
- `dida-planning-profile/SKILL.md`
- `dida-planning-profile/references/config-notes.md`

### 中：大 NOTE 会重新产生 token 和并发问题 — 已修复

将所有长期记忆放入一个 NOTE 会造成全量读取、字段覆盖和冲突合并困难。

修复：使用 4 个分类父 NOTE，每条记忆是独立子任务：

- `长期记忆｜项目规则`
- `长期记忆｜工具与环境`
- `长期记忆｜工作方式`
- `长期记忆｜通用约定`

项目专属记忆直接挂在对应项目父任务下，并设置 `required_for_parent: false`。

涉及：

- `dida-planning-memory/assets/memory-categories/`
- `dida-planning-memory/references/memory-format.md`

### 中：显式遗忘可能只追加相反信息 — 已修复

长期记忆必须有单一当前事实。仅追加“新规则”会留下两个冲突记录。

修复：显式“忘掉”优先删除或修正权威记录；完整删除请求不会把原内容复制到评论。存在多个候选时停止并要求选择。

涉及：

- `dida-planning-memory/SKILL.md`
- `dida-planning-memory/references/memory-policy.md`

### 中：旧 Markdown 记忆可能把过时基础设施重新迁回 — 已修复

旧记忆包含“Markdown 是唯一数据源”等已失效规则以及会话维护元数据，不能整体搬入滴答。

修复：`scan_legacy.py` 识别旧 memory，`classify_legacy_memory.py` 逐条生成只读分类预览。试扫时旧存储规则和维护元数据被自动过滤，真正可能长期有用的内容仅进入人工复核。

涉及：

- `dida-planning-core/scripts/migration/scan_legacy.py`
- `dida-planning-core/scripts/migration/classify_legacy_memory.py`

### 低：系统状态缺少记忆分类 ID — 已修复

在 `系统状态｜Schema与迁移版本` 中增加 4 个记忆分类父任务 ID 和 `memory_schema: 1`，避免以后广泛搜索。

涉及：

- `dida-planning-profile/assets/config-notes/系统状态｜Schema与迁移版本.md`

## 5. 各 Skill 审核意见

| Skill | 结论 | 审核意见 |
|---|---|---|
| `dida-cli` | 通过 | 保持纯执行层；读前解析、写后回读、失败去重和删除影响提示完整；不做规划或记忆决策。 |
| `dida-task-capture` | 通过 | 只负责记录任务；长期规则转交 memory；不会在记忆分类下创建普通工作任务。 |
| `dida-task-breakdown` | 通过 | 四级工作层级明确；只读取当前项目相关记忆；记忆子任务不参与工作拆分和完成门禁。 |
| `dida-task-estimator` | 通过 | 使用特征、相似样本和收缩；拒绝配置/记忆记录；AI 并行时间不重复占用个人日历。 |
| `dida-daily-planner` | 通过 | 固定/保护/可移动边界清晰；不改硬截止；非工作记录不会进入容量和排程。 |
| `dida-task-progress` | 通过 | 原生完成成功后才写完成评论；记忆不参与进度；完成时发现长期规则会转交 memory。 |
| `dida-weekly-review` | 通过 | 不创建 Markdown 周计划；配置和记忆不进入任务数量、逾期、容量和完成率指标。 |
| `dida-planning-profile` | 通过 | 只管理稳定排期偏好；临时例外不长期保存；一般项目/工具记忆不会被吸收到 profile。 |
| `dida-planning-memory` | 通过 | 显式保存/遗忘、自动保存、敏感信息、去重、冲突、检索和原子存储规则完整。 |
| `dida-planning-core` | 通过 | 确定性逻辑集中，21 项测试覆盖关键不变量；不形成第二业务数据库。 |

## 6. 记忆自动添加的最终规则

### 直接保存

- 用户明确说“记住、保存到记忆、以后都按这个规则”；
- 信息即使较琐碎，也以用户明确持久化要求为准；
- 敏感信息只有在用户明确要求时保存，并尽量概括。

### 可以自动保存并告知

- 用户直接陈述；
- 预计长期稳定；
- 未来会明显改变相似任务的处理；
- 低敏感；
- 不属于任务、profile 或估时系统的已有字段。

### 必须先问

- AI 从多次行为推断出的习惯；
- 稳定性不确定；
- 与已有记忆冲突但替换意图不清楚；
- 未明确要求保存的敏感内容。

### 不保存

- 单日例外、临时位置和短期状态；
- 随口或无未来价值的细节；
- 用户仅要求翻译、改写或校对的素材；
- 当前任务进度、日期、估时等已有权威字段；
- 可以从当前任务直接读取、无需跨任务记忆的内容。

## 7. 仍需真实滴答账户验证的事项

当前环境没有安装并登录 `dida`，以下内容无法进行真实账号联调：

1. 当前安装版本的准确命令参数；
2. NOTE 类型与父子 NOTE 的实际显示方式；
3. 多行评论和 Planner 区在真实接口中的保真情况；
4. 单独修改重复天气任务当日实例；
5. 专注统计响应字段；
6. 大量子任务下的检索和性能；
7. 删除带子任务/评论/专注记录任务时的具体客户端提示。

所有写 Skill 都要求以本机 `--help` 为准，并在写后回读。上述限制不会改变架构，但首次上线应使用测试清单做一轮联调。

## 8. 子代理审查状态

交付包包含：

- `.codex/agents/skill-reviewer.toml`
- `SUBAGENT_REVIEW_PROMPT.md`

当前运行环境中没有 `codex` 命令，也没有可调用的子代理执行工具，因此未声称已经真实启动 Codex 子代理。本报告来自隔离的第二轮逻辑审查、静态检查、单元测试、旧系统试扫和干净安装测试。

在本地 Codex 中可使用包内提示词启动只读 `skill_reviewer`，对 9 个 Skill 做第三方复核。真实子代理若提出确认的问题，应修复后重新运行 validator 和全部测试。
