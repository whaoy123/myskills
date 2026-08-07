from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import re
from typing import Any


def _redact(text: str) -> str:
    text = re.sub(r"(?i)(authorization|token|cookie)(\s*[:=]\s*)[^\s]+", r"\1\2<redacted>", text)
    text = re.sub(r"(?i)bearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer <redacted>", text)
    return text


def run(args: list[str], expect_json: bool, timeout: int) -> dict[str, Any]:
    if not shutil.which("dida"):
        return {"ok": False, "error": "dida command not found", "install": "npm install -g @suibiji/dida-cli"}
    proc = subprocess.run(["dida", *args], capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    result: dict[str, Any] = {"ok": proc.returncode == 0, "returncode": proc.returncode, "stderr": _redact(proc.stderr.strip())}
    stdout = proc.stdout.strip()
    if expect_json and stdout:
        try: result["data"] = json.loads(stdout)
        except json.JSONDecodeError: result.update({"ok": False, "error": "malformed JSON", "stdout": stdout})
    else: result["stdout"] = stdout
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Generic safe wrapper; pass Dida args after --")
    ap.add_argument("--json", action="store_true", dest="expect_json")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("args", nargs=argparse.REMAINDER)
    ns = ap.parse_args()
    args = ns.args[1:] if ns.args[:1] == ["--"] else ns.args
    if not args: ap.error("provide Dida arguments after --")
    print(json.dumps(run(args, ns.expect_json, ns.timeout), ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
