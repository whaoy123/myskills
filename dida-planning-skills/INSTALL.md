# 安装与升级

## 安装 DIDA CLI

```powershell
node --version
npm install -g @suibiji/dida-cli
dida --version
dida auth login
dida auth status
```

CLI 版本可能改变参数。每次遇到未知字段时，以本机 `dida <group> <command> --help` 为准。

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

安装脚本会覆盖同名技能目录，但不会删除其他技能。

## 升级

升级前备份本地估时缓存和待同步队列：

```text
~/.agents/skills/dida-planning-core/state/
```

这些文件不是业务权威；即使丢失，也应能从滴答任务评论重建。

## 首次初始化长期记忆

安装后依次执行：

```text
$dida-planning-profile 初始化系统配置
$dida-planning-memory 初始化长期记忆分类
```

长期记忆本体仍在滴答中；本地不保存第二份可编辑记忆库。
