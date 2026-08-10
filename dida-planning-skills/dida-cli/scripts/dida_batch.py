"""Safe, single-process batch helper for Dida365 planning work.

Commands:
  scheduled  Read scheduled tasks in a date window.
  search     Search task titles/bodies across selected projects.
  plan       Dry-run or apply create/update/comment operations with read-back.

The script intentionally does not support completion, deletion, or cross-project
move operations.  Those actions remain better handled by the normal Dida CLI
because their scope and consequences need individual review.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_BASE = "https://api.dida365.com/open/v1"
MAX_PARALLEL_READS = 4


def configure_console() -> None:
    """Keep JSON/text output usable on Windows consoles with a legacy code page."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


configure_console()


class DidaError(RuntimeError):
    pass


class DidaApi:
    def __init__(self, token: str):
        self.token = token

    def request(self, path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
        body = None
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(API_BASE + path, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=30) as response:
                raw = response.read()
        except (HTTPError, URLError) as exc:
            detail = exc.read().decode("utf-8", "replace") if isinstance(exc, HTTPError) else str(exc)
            raise DidaError(f"Dida API request failed: {path}: {detail}") from exc
        return json.loads(raw.decode("utf-8")) if raw else None

    def projects(self) -> list[dict[str, Any]]:
        return self.request("/project")

    def project_data(self, project_id: str) -> dict[str, Any]:
        return self.request(f"/project/{project_id}/data")

    def filter_tasks(self, start_date: str, end_date: str, statuses: list[int] | None) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {"startDate": start_date, "endDate": end_date}
        if statuses is not None:
            payload["status"] = statuses
        return self.request("/task/filter", "POST", payload)

    def get_task(self, project_id: str, task_id: str) -> dict[str, Any]:
        return self.request(f"/project/{project_id}/task/{task_id}")

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("/task", "POST", payload)

    def update_task(self, task_id: str, project_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        return self.request(f"/task/{task_id}", "POST", {"id": task_id, "projectId": project_id, **fields})

    def comments(self, project_id: str, task_id: str) -> list[dict[str, Any]]:
        return self.request(f"/project/{project_id}/task/{task_id}/comments")

    def add_comment(self, project_id: str, task_id: str, title: str) -> dict[str, Any]:
        return self.request(f"/project/{project_id}/task/{task_id}/comment", "POST", {"title": title})


def load_api() -> DidaApi:
    profile_root = Path(os.environ.get("USERPROFILE", str(Path.home())))
    config_path = profile_root / ".config" / "dida-cli" / "config.json"
    try:
        token = json.loads(config_path.read_text(encoding="utf-8")).get("access_token")
    except (OSError, json.JSONDecodeError) as exc:
        raise DidaError(f"cannot read Dida CLI config: {config_path}") from exc
    if not token:
        raise DidaError("Dida access token is missing; run `dida auth status` first")
    return DidaApi(token)


def validate_iso_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid date: {value}") from exc
    return value


def emit(data: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    if isinstance(data, list):
        for row in data:
            print(f"- [{row.get('project', row.get('project_id', '?'))}] {row.get('title', '?')} ({row.get('id', row.get('task_id', '?'))})")
        return
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_scheduled(args: argparse.Namespace) -> int:
    api = load_api()
    statuses = args.status if args.status is not None else [0]
    tasks = api.filter_tasks(args.start, args.end, statuses)
    project_names = {project["id"]: project.get("name", project["id"]) for project in api.projects()}
    rows = [
        {
            "project": project_names.get(task.get("projectId"), task.get("projectId")),
            "project_id": task.get("projectId"),
            "id": task.get("id"),
            "title": task.get("title"),
            "parent_id": task.get("parentId"),
            "start_date": task.get("startDate"),
            "due_date": task.get("dueDate"),
            "status": task.get("status"),
        }
        for task in tasks
    ]
    rows.sort(key=lambda row: (row["project"] or "", row["start_date"] or "", row["title"] or ""))
    payload = {"start": args.start, "end": args.end, "status": statuses, "tasks": rows}
    if args.json:
        emit(payload, True)
    else:
        print(f"已排期任务 {args.start} ~ {args.end}：{len(rows)} 条")
        emit(rows, False)
    return 0


def selected_projects(api: DidaApi, project_ids: list[str] | None, all_projects: bool) -> list[dict[str, Any]]:
    if not project_ids and not all_projects:
        raise DidaError("search requires at least one --project, or explicit --all-projects")
    projects = api.projects()
    by_id = {project["id"]: project for project in projects}
    if project_ids:
        missing = [project_id for project_id in project_ids if project_id not in by_id]
        if missing:
            raise DidaError(f"unknown project IDs: {', '.join(missing)}")
        return [by_id[project_id] for project_id in project_ids]
    return [project for project in projects if project.get("kind") in {"TASK", "NOTE"}]


def cmd_search(args: argparse.Namespace) -> int:
    api = load_api()
    projects = selected_projects(api, args.project, args.all_projects)
    query = args.query if args.case_sensitive else args.query.casefold()
    data_by_project: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=min(MAX_PARALLEL_READS, len(projects))) as pool:
        futures = {pool.submit(api.project_data, project["id"]): project for project in projects}
        for future in as_completed(futures):
            project = futures[future]
            data_by_project[project["id"]] = future.result()
    rows = []
    for project in projects:
        for task in data_by_project[project["id"]].get("tasks", []):
            haystack = f"{task.get('title') or ''}\n{task.get('content') or ''}"
            comparable = haystack if args.case_sensitive else haystack.casefold()
            if query not in comparable:
                continue
            row = {
                "project": project.get("name", project["id"]),
                "project_id": project["id"],
                "id": task.get("id"),
                "title": task.get("title"),
                "parent_id": task.get("parentId"),
                "start_date": task.get("startDate"),
                "due_date": task.get("dueDate"),
                "status": task.get("status"),
            }
            if args.show_content:
                row["content"] = task.get("content") or ""
            rows.append(row)
    rows.sort(key=lambda row: (row["project"] or "", row["title"] or ""))
    payload = {"query": args.query, "searched_projects": [project["id"] for project in projects], "tasks": rows}
    if args.json:
        emit(payload, True)
    else:
        print(f"搜索“{args.query}”：{len(rows)} 条")
        emit(rows, False)
    return 0


FIELD_ALIASES = {
    "title": "title",
    "content": "content",
    "parent_id": "parentId",
    "start_date": "startDate",
    "due_date": "dueDate",
    "all_day": "isAllDay",
    "time_zone": "timeZone",
    "priority": "priority",
    "tags": "tags",
    "estimated_duration": "estimatedDuration",
    "estimated_pomo": "estimatedPomo",
}


def load_plan(path: str) -> list[dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    operations = raw.get("operations") if isinstance(raw, dict) else raw
    if not isinstance(operations, list) or not operations:
        raise DidaError("plan input must be a non-empty JSON list or an object with operations")
    for index, operation in enumerate(operations):
        if not isinstance(operation, dict) or operation.get("op") not in {"create", "update", "comment"}:
            raise DidaError(f"invalid operation at index {index}; allowed ops: create, update, comment")
    return operations


def resolve_ref(value: Any, created: dict[str, str], field_name: str) -> Any:
    if not isinstance(value, str) or not value.startswith("@"):
        return value
    key = value[1:]
    if key not in created:
        raise DidaError(f"{field_name} references unknown or not-yet-created key: {value}")
    return created[key]


def normalized_fields(raw_fields: dict[str, Any], current_task: dict[str, Any] | None, created: dict[str, str]) -> dict[str, Any]:
    if not isinstance(raw_fields, dict):
        raise DidaError("fields must be an object")
    result: dict[str, Any] = {}
    duration_change = False
    for source, value in raw_fields.items():
        if source not in FIELD_ALIASES:
            raise DidaError(f"unsupported field: {source}")
        target = FIELD_ALIASES[source]
        value = resolve_ref(value, created, source)
        if target in {"estimatedDuration", "estimatedPomo"}:
            duration_change = True
            continue
        result[target] = value
    if duration_change:
        existing = ((current_task or {}).get("focusSummaries") or [{}])[0].copy()
        if "estimated_duration" in raw_fields:
            existing["estimatedDuration"] = raw_fields["estimated_duration"]
        if "estimated_pomo" in raw_fields:
            existing["estimatedPomo"] = raw_fields["estimated_pomo"]
        result["focusSummaries"] = [existing]
    return result


def expected_fields(raw_fields: dict[str, Any], created: dict[str, str]) -> dict[str, Any]:
    result = normalized_fields(raw_fields, None, created)
    if "focusSummaries" in result:
        focus = result.pop("focusSummaries")[0]
        if "estimatedDuration" in focus:
            result["estimatedDuration"] = focus["estimatedDuration"]
        if "estimatedPomo" in focus:
            result["estimatedPomo"] = focus["estimatedPomo"]
    return result


def utc_equivalent(value: Any) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def actual_value(task: dict[str, Any], field: str) -> Any:
    if field == "estimatedDuration":
        return ((task.get("focusSummaries") or [{}])[0]).get("estimatedDuration")
    if field == "estimatedPomo":
        return ((task.get("focusSummaries") or [{}])[0]).get("estimatedPomo")
    return task.get(field)


def verify_task(task: dict[str, Any], expected: dict[str, Any]) -> None:
    for field, wanted in expected.items():
        actual = actual_value(task, field)
        if field in {"startDate", "dueDate"}:
            if wanted is None and actual is None:
                continue
            if utc_equivalent(wanted) == utc_equivalent(actual) and utc_equivalent(wanted) is not None:
                continue
        elif actual == wanted:
            continue
        raise DidaError(f"read-back mismatch for task {task.get('id')} field {field}: wanted {wanted!r}, got {actual!r}")


def operation_project_id(operation: dict[str, Any], created: dict[str, str]) -> str:
    project_id = resolve_ref(operation.get("project_id"), created, "project_id")
    if not isinstance(project_id, str) or not project_id:
        raise DidaError("operation requires project_id")
    return project_id


def operation_task_id(operation: dict[str, Any], created: dict[str, str]) -> str:
    task_id = resolve_ref(operation.get("task_id"), created, "task_id")
    if not isinstance(task_id, str) or not task_id:
        raise DidaError("operation requires task_id")
    return task_id


def create_payload(operation: dict[str, Any], project_id: str, created: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(operation.get("title"), str) or not operation["title"].strip():
        raise DidaError("create operation requires a non-empty title")
    raw_fields = dict(operation.get("fields") or {})
    if "title" in raw_fields or "content" in raw_fields:
        raise DidaError("create title/content belong at the operation top level")
    fields = normalized_fields(raw_fields, None, created)
    payload = {"title": operation["title"], "projectId": project_id}
    if "content" in operation:
        payload["content"] = operation["content"]
    for source in ("isAllDay", "startDate", "dueDate", "timeZone", "priority", "tags"):
        if source in fields:
            payload[source] = fields.pop(source)
    expected = {"title": operation["title"], **expected_fields(raw_fields, created)}
    if "content" in operation:
        expected["content"] = operation["content"]
    return payload, fields | ({"parentId": resolve_ref(operation["parent_id"], created, "parent_id")} if "parent_id" in operation else {})


def dry_run(operations: list[dict[str, Any]]) -> int:
    summaries = []
    for index, operation in enumerate(operations):
        summary = {"index": index, "op": operation["op"], "key": operation.get("key"), "project_id": operation.get("project_id")}
        if operation["op"] == "create":
            summary |= {"title": operation.get("title"), "parent_id": operation.get("parent_id"), "fields": operation.get("fields", {})}
        elif operation["op"] == "update":
            summary |= {"task_id": operation.get("task_id"), "fields": operation.get("fields", {})}
        else:
            summary |= {"task_id": operation.get("task_id"), "operation_id": operation.get("operation_id")}
        summaries.append(summary)
    print(json.dumps({"dry_run": True, "operations": summaries}, ensure_ascii=False, indent=2))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    operations = load_plan(args.input)
    if not args.apply:
        return dry_run(operations)
    api = load_api()
    created: dict[str, str] = {}
    results = []
    for index, operation in enumerate(operations):
        op = operation["op"]
        project_id = operation_project_id(operation, created)
        if op == "create":
            payload, follow_up = create_payload(operation, project_id, created)
            task = api.create_task(payload)
            task_id = task.get("id")
            if not task_id:
                raise DidaError(f"create operation {index} did not return a task ID")
            if follow_up:
                current = api.get_task(project_id, task_id)
                follow_up = normalized_fields({
                    **{key: value for key, value in operation.get("fields", {}).items() if key in {"estimated_duration", "estimated_pomo"}},
                    **({"parent_id": operation["parent_id"]} if "parent_id" in operation else {}),
                }, current, created) | {key: value for key, value in follow_up.items() if key != "focusSummaries"}
                api.update_task(task_id, project_id, follow_up)
            verified = api.get_task(project_id, task_id)
            expected = {"title": operation["title"]}
            if "content" in operation:
                expected["content"] = operation["content"]
            expected |= expected_fields(operation.get("fields", {}), created)
            if "parent_id" in operation:
                expected["parentId"] = resolve_ref(operation["parent_id"], created, "parent_id")
            verify_task(verified, expected)
            if operation.get("key"):
                key = operation["key"]
                if key in created:
                    raise DidaError(f"duplicate create key: {key}")
                created[key] = task_id
            results.append({"index": index, "op": op, "task_id": task_id, "title": verified.get("title")})
            continue

        task_id = operation_task_id(operation, created)
        if op == "update":
            current = api.get_task(project_id, task_id)
            fields = normalized_fields(operation.get("fields", {}), current, created)
            if not fields:
                raise DidaError("update operation requires at least one field")
            api.update_task(task_id, project_id, fields)
            verified = api.get_task(project_id, task_id)
            verify_task(verified, expected_fields(operation["fields"], created))
            results.append({"index": index, "op": op, "task_id": task_id, "title": verified.get("title")})
            continue

        text = operation.get("text")
        if not isinstance(text, str) or not text.strip():
            raise DidaError("comment operation requires non-empty text")
        operation_id = operation.get("operation_id")
        comments = api.comments(project_id, task_id)
        if operation_id and any(operation_id in str(comment.get("title", "")) for comment in comments):
            results.append({"index": index, "op": op, "task_id": task_id, "skipped": "operation_id already present"})
            continue
        api.add_comment(project_id, task_id, text)
        verified_comments = api.comments(project_id, task_id)
        if not any(comment.get("title") == text for comment in verified_comments):
            raise DidaError(f"read-back mismatch: comment was not found on {task_id}")
        results.append({"index": index, "op": op, "task_id": task_id, "comment_added": True})
    print(json.dumps({"dry_run": False, "created": created, "results": results}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Single-process Dida365 batch helper")
    subcommands = parser.add_subparsers(dest="command", required=True)

    scheduled = subcommands.add_parser("scheduled", help="read scheduled tasks in a date window")
    scheduled.add_argument("--start", type=validate_iso_date, required=True)
    scheduled.add_argument("--end", type=validate_iso_date, required=True)
    scheduled.add_argument("--status", type=int, action="append", default=None, help="repeatable Dida status code; default 0")
    scheduled.add_argument("--json", action="store_true")
    scheduled.set_defaults(func=cmd_scheduled)

    search = subcommands.add_parser("search", help="search task titles and bodies in selected projects")
    search.add_argument("--query", required=True)
    search.add_argument("--project", action="append", default=None)
    search.add_argument("--all-projects", action="store_true")
    search.add_argument("--case-sensitive", action="store_true")
    search.add_argument("--show-content", action="store_true")
    search.add_argument("--json", action="store_true")
    search.set_defaults(func=cmd_search)

    plan = subcommands.add_parser("plan", help="dry-run or apply explicit create/update/comment operations")
    plan.add_argument("--input", required=True, help="JSON plan: a list or an object with operations")
    plan.add_argument("--apply", action="store_true", help="perform writes; omit for dry-run")
    plan.set_defaults(func=cmd_plan)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except DidaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
