# 安装与升级 v1.5.0

## 先检查

在 `dida-planning-skills` 目录运行。需要 Python 3.10 或更新版本；本包新增逻辑只用标准库，不要求额外安装 YAML 库。

```powershell
python .\dida-planning-core\scripts\package_validator.py --root . --strict-manifest
python -m unittest discover -s .\dida-planning-core\tests -v
python .\install.py --dry-run
```

## 安装

默认安装到 `$HOME\.agents\skills`：

```powershell
python .\install.py
```

也可使用 `install.ps1` / `install.sh`，它们调用同一个 Python 安装器。

安装前验证包清单；已有同名技能和旧 `dida-daily-planner` 先移到技能目录之外的 `skill-backups/dida-时间戳-随机码`。安装失败会尝试恢复已移动目录。其他非滴答技能不变，旧缓存保留在备份中。

安装后的旧日程模块退出活跃技能目录。备份目录不应作为技能发现路径加载。

## 运行

优先使用可用的滴答 MCP/连接器；不要求在已有连接器时安装 CLI。

这次安装只改本地技能，不改滴答任务或 NOTE。旧运行态配置保留，只有用户授权时才合并新 `规划偏好｜周交付与任务投入` 规则。

## 升级后验证

用一个不写入的请求检查：“按当前任务拟定一到两个周交付物”。应先读取业务任务，给产物、范围、验收、支撑任务和未知项；不会创建周计划父任务、执行块或日程。

如果要应用到真实任务，再明确要求写回，并核对保存结果。
