# DIDA CLI command baseline

This reference is based on `@suibiji/dida-cli` 0.1.11. The package is actively changing, so always prefer the installed command's `--help` output when syntax differs.

## Installation and authentication

```bash
npm install -g @suibiji/dida-cli
dida --version
dida --help

dida auth login
dida auth status
dida auth logout
```

A headless token command exists, but credentials must be entered only in the user's local terminal and must never be pasted into chat:

```bash
dida auth token <token>
```

## Projects / lists

```bash
dida project list --json
dida project get <projectId> --json
dida project data <projectId> --json

dida project create --name "工作" --color "#F18181" --view-mode list --kind TASK --json
dida project update <projectId> --name "新名字" --color "#4AB8A9" --json
dida project delete <projectId>
```

### Project groups / folders

```bash
dida project group list --json
dida project group create --name "工作" --json
dida project group update <groupId> --name "个人" --json
dida project group delete <groupId>
```

### Kanban columns

```bash
dida project column list <projectId> --json
dida project column create <projectId> --name "进行中" --json
dida project column update <projectId> <columnId> --name "已完成" --json
```

Inspect `dida project column --help` before deleting a column or using options not shown above.

## Tasks

### Read

```bash
dida task get <projectId> <taskId> --json
dida task filter --projects <projectId> --status 0 --json
dida task completed \
  --projects <projectId> \
  --start-date "2026-08-01T00:00:00+0800" \
  --end-date "2026-08-06T23:59:59+0800" \
  --json
```

`task filter` can accept additional fields such as date range and priorities in current releases. Inspect its help before constructing a complex query:

```bash
dida task filter --help
```

### Create

```bash
dida task create \
  --title "完成测试方案" \
  --project <projectId> \
  --due-date "2026-08-06T18:00:00+0800" \
  --json
```

Common fields shown by current package documentation include:

```text
--title
--project
--content
--due-date
--priority
--tags
--parent-id
--estimated-duration
--estimated-pomo
```

Do not use a field until the installed `dida task create --help` confirms it.

### Update

```bash
dida task update <taskId> \
  --id <taskId> \
  --project <projectId> \
  --title "新标题" \
  --json
```

Examples of optional updates in current package documentation:

```bash
dida task update <taskId> --id <taskId> --project <projectId> --tags 工作,紧急 --json
dida task update <taskId> --id <taskId> --project <projectId> --parent-id <parentTaskId> --json
dida task update <taskId> --id <taskId> --project <projectId> --parent-id null --json
dida task update <taskId> --id <taskId> --project <projectId> --estimated-duration 1500 --estimated-pomo 5 --json
```

### Complete, move, delete

```bash
dida task complete <projectId> <taskId>

dida task move \
  --from <sourceProjectId> \
  --to <destinationProjectId> \
  --task <taskId>

dida task delete <projectId> <taskId>
```

### Comments

```bash
dida task comment list <projectId> <taskId> --json
dida task comment add <projectId> <taskId> --title "已处理" --json
dida task comment delete <projectId> <taskId> <commentId>
```

## Tags

```bash
dida tag list --json
dida tag create --name urgent --label urgent --json
```

Inspect help before updating or deleting tags.

## Habits

```bash
dida habit list --json
dida habit get <habitId> --json

dida habit create \
  --name "每天喝水" \
  --repeat "RRULE:FREQ=DAILY;INTERVAL=1" \
  --goal 8 \
  --unit 杯 \
  --json

dida habit update <habitId> --name "每天喝水 2L" --goal 2000 --unit ml --json
dida habit checkin <habitId> --stamp 20260806 --value 1 --goal 1 --json
dida habit checkins --habits <habitId> --from 20260801 --to 20260831 --json
```

## Focus records

```bash
dida focus get <focusId> --type pomodoro --json
dida focus list \
  --from "2026-08-01T00:00:00+0800" \
  --to "2026-08-06T23:59:59+0800" \
  --type pomodoro \
  --json

dida focus create \
  --type pomodoro \
  --task-id <taskId> \
  --start-time "2026-08-06T09:00:00+0800" \
  --end-time "2026-08-06T09:25:00+0800" \
  --duration 1500 \
  --json

dida focus delete <focusId> --type pomodoro
```

The documented focus query window is limited to 30 days. Split longer ranges into multiple requests.

## Countdowns

```bash
dida countdown list --json
```
