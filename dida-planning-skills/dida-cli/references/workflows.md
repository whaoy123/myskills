# Reliable agent workflows

## Resolve a project by name

1. Run:

   ```bash
   dida project list --json
   ```

2. Parse the JSON.
3. Prefer an exact `name` match.
4. If one match exists, retain both its name and ID.
5. If zero matches exist, report the available near matches.
6. If several matches exist, show the candidates rather than guessing.

## Resolve a task by title

1. Resolve the project first when the user named one.
2. Run:

   ```bash
   dida project data <projectId> --json
   ```

3. Match exact title first.
4. Use due date, status, parent, or tags to disambiguate.
5. Keep the selected `projectId` and `taskId` together.

When no project was named, search relevant projects with `task filter` if supported. Avoid issuing a separate broad API request for every project unless necessary.

## Create and verify

```bash
# 1. Resolve project ID
PROJECTS_JSON="$(dida project list --json)"

# 2. Create using the resolved ID
CREATED_JSON="$(dida task create \
  --title "完成测试记录" \
  --project "$PROJECT_ID" \
  --due-date "2026-08-06T18:00:00+0800" \
  --json)"

# 3. Extract returned task ID, then verify
# dida task get "$PROJECT_ID" "$TASK_ID" --json
```

The agent may use a temporary local parser such as Python, Node.js, or `jq` to read JSON, but must not persist private task data unless the user requested an export.

## Update without destroying unspecified fields

Before updating, fetch the current task. Pass only fields the user asked to change, plus IDs required by the CLI.

Example:

```bash
dida task update "$TASK_ID" \
  --id "$TASK_ID" \
  --project "$PROJECT_ID" \
  --due-date "2026-08-07T16:00:00+0800" \
  --json
```

Do not reconstruct the whole task from memory.

## Prevent duplicate writes after a timeout

When a create/update/move command times out or returns an unclear network error:

1. Do not immediately retry.
2. Refresh the destination project or task.
3. Check whether the requested state already exists.
4. Retry only when the read proves the write did not occur.

## Example user requests that should trigger this skill

- “把测试方案定稿加到滴答的南航项目，明天下午 4 点截止。”
- “列出滴答里今天还没完成的任务。”
- “把‘检查 PMG 测试数据’移到本周任务清单。”
- “完成滴答里的‘直通板 DRC 检查’。”
- “查一下过去一周完成了哪些任务。”
- “给‘论文修改’添加一条评论：已完成第三轮检查。”

## Requests that should not trigger this skill by themselves

- “帮我想一下明天做什么。”
- “把这个研究方向拆解一下。”
- “评价我的时间安排是否合理。”

Those are planning or analysis tasks. Invoke DIDA CLI only when the user also wants current Dida data read or changed.
