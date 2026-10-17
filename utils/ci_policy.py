"""Select final-candidate CI without native Allplan access or third-party imports."""
from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path
import re
import subprocess
import tomllib


DOCUMENTATION = ("AGENTS.md", "README.md", "docs/*", "evaluation-packages/*")
COMPATIBILITY = ("windows/*", "utils/register_python_host.*",
                 "utils/build_windows_package.py", "utils/ci_policy.py",
                 ".github/workflows/*", ".python-version", "uv.toml")


def matches(path, patterns):
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def compatibility_change(paths, read_blob):
    """Only the project's own version is exempt from configuration checks."""
    if any(matches(path, COMPATIBILITY) for path in paths):
        return True
    for path in set(paths) & {"pyproject.toml", "uv.lock"}:
        try:
            before = tomllib.loads(read_blob("before", path))
            after = tomllib.loads(read_blob("after", path))
            if path == "pyproject.toml":
                for data in (before, after):
                    project = data["project"]
                    if not isinstance(project.get("version"), str):
                        return True
                    project.pop("version")
            else:
                names = [tomllib.loads(read_blob(side, "pyproject.toml"))["project"]["name"]
                         for side in ("before", "after")]
                if not names[0] or names[0] != names[1]:
                    return True
                for data in (before, after):
                    for package in data.get("package", []):
                        if (package.get("name") == names[0]
                                and package.get("source") in ({"editable": "."}, {"virtual": "."})):
                            package.pop("version", None)
            if before != after:
                return True
        except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError):
            return True  # Missing, malformed or unreadable evidence cannot downgrade CI.
    return False


def plan_ci(event_name, event, paths=(), read_blob=None, *, history_available=True):
    if event_name == "workflow_dispatch":
        flag = str(event.get("inputs", {}).get("full_matrix", "true")).lower()
        if flag not in {"true", "false"}:
            raise ValueError("full_matrix must be true or false")
        run, full, reason = True, flag == "true", "Explicit final-candidate run"
    elif event_name == "pull_request":
        pr = event["pull_request"]
        if pr.get("draft", False):
            run, full, reason = False, False, "Draft: use focused local tests during iteration"
        elif not history_available:
            run, full, reason = True, True, "Comparison unavailable: full compatibility matrix"
        elif all(matches(path, DOCUMENTATION) for path in paths):
            run, full, reason = False, False, "Documentation only: no product tests or builds"
        else:
            default_branch = event.get("repository", {}).get("default_branch", "main")
            integration = pr["base"]["ref"] == default_branch
            run, full = True, integration or compatibility_change(paths, read_blob)
            reason = "Main integration or compatibility change" if full else "Standard final candidate"
    else:
        raise ValueError(f"Unsupported CI event: {event_name}")
    versions = ["3.11", "3.12", "3.13"] if full else ["3.12"]
    return {"run_portable": run, "full_matrix": full, "reason": reason,
            "matrix": {"include": [{"os": system, "python": version}
                                   for system in ("ubuntu-latest", "windows-latest")
                                   for version in versions]}}


def comparison(event):
    pr = event["pull_request"]
    before = event.get("before") if event.get("action") == "synchronize" else pr["base"].get("sha")
    after = pr["head"].get("sha")
    for revision in (before, after):
        if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision) or set(revision) == {"0"}:
            raise ValueError("Missing comparison revision")
    return before, after


def main():
    event_name = os.environ["GITHUB_EVENT_NAME"]
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    paths, available = (), True
    read_blob = None
    if event_name == "pull_request" and not event["pull_request"].get("draft", False):
        try:
            before, after = comparison(event)
            raw = subprocess.check_output(["git", "diff", "--name-only", "--no-renames", "-z",
                                           before, after, "--"], text=True, stderr=subprocess.PIPE)
            paths = tuple(path for path in raw.split("\0") if path)
            def read_blob(side, path):
                revision = before if side == "before" else after
                return subprocess.check_output(["git", "show", f"{revision}:{path}"],
                                               text=True, encoding="utf-8", stderr=subprocess.PIPE)
        except (ValueError, OSError, subprocess.SubprocessError):
            available = False
    plan = plan_ci(event_name, event, paths, read_blob, history_available=available)
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
        output.write("matrix=" + json.dumps(plan["matrix"]) + "\n")
        output.write("run_portable=" + str(plan["run_portable"]).lower() + "\n")
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
