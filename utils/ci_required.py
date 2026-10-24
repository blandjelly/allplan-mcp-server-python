"""Fail-closed required check; inspect existing Actions results, never run builds."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ci_policy import DOCUMENTATION, comparison, matches


def require(condition, message):
    if not condition:
        raise ValueError(message)


def expected_jobs(outputs):
    require(outputs.get("full_matrix") in {"true", "false"}, "Missing matrix selection")
    versions = ("3.11", "3.12", "3.13") if outputs["full_matrix"] == "true" else ("3.12",)
    entries = [{"os": system, "python": version}
               for system in ("ubuntu-latest", "windows-latest") for version in versions]
    matrix = json.loads(outputs.get("matrix", "null"))
    require(isinstance(matrix, dict) and set(matrix) == {"include"}
            and isinstance(matrix["include"], list) and len(matrix["include"]) == len(entries)
            and all(entry in matrix["include"] for entry in entries),
            "Incomplete or unexpected required matrix")
    return {f"portable ({entry['os']}, {entry['python']})" for entry in entries}


def verify_jobs(jobs, portable_names, *, prior=False):
    names = portable_names | {"configuration", "package"}
    if prior:
        names |= {"ci-required"}
    actual_portable = [job["name"] for job in jobs if job["name"].startswith("portable (")]
    require(len(actual_portable) == len(portable_names) and set(actual_portable) == portable_names,
            "Missing, duplicate or unexpected portable configurations")
    for name in sorted(names):
        found = [job for job in jobs if job["name"] == name]
        require(len(found) == 1 and found[0].get("status") == "completed"
                and found[0].get("conclusion") == "success", f"Required job did not pass: {name}")


class Actions:
    def __init__(self):
        self.root = (os.environ["GITHUB_API_URL"].rstrip("/") + "/repos/"
                     + os.environ["GITHUB_REPOSITORY"] + "/actions/")

    def get(self, path, **query):
        url = self.root + path + ("?" + urlencode(query) if query else "")
        request = Request(url, headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                                       "Accept": "application/vnd.github+json",
                                       "X-GitHub-Api-Version": "2022-11-28"})
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    def jobs(self, run):
        jobs = []
        # Pin the attempt: an older successful attempt cannot hide a failed rerun.
        for page in range(1, 11):
            data = self.get(f"runs/{run['id']}/attempts/{run['run_attempt']}/jobs",
                            per_page=100, page=page)
            jobs.extend(data["jobs"])
            if len(jobs) == data["total_count"]:
                return jobs
            require(len(jobs) < data["total_count"] and data["jobs"], "Invalid job pagination")
        raise ValueError("Job evidence exceeds pagination limit")


def git(*args):
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.PIPE).rstrip("\n")


def reusable_revisions(event):
    if event.get("action") == "edited" and "base" not in event.get("changes", {}):
        _, after = comparison(event)
        before = after
    else:
        require(event.get("action") == "synchronize", "Reuse requires an unchanged-source update")
        before, after = comparison(event)
    require(git("merge-base", "--is-ancestor", before, after) == "", "Push is not an ancestor")
    for revision in git("rev-list", "--first-parent", "--max-count=20", before).splitlines():
        paths = git("diff", "--name-only", "--no-renames", "-z", revision, after, "--").split("\0")
        if any(path and not matches(path, DOCUMENTATION) for path in paths):
            break
        yield revision


def verify_reuse(event, current, api, portable_names, revisions):
    pr = event["pull_request"]
    for revision in revisions:
        data = api.get(f"workflows/{current['workflow_id']}/runs", head_sha=revision,
                       event="pull_request", per_page=100)
        require(data["total_count"] <= 100, "Incomplete prior run evidence")
        runs = [run for run in data["workflow_runs"]
                if run["id"] < current["id"] and run.get("head_sha") == revision
                and run.get("event") == "pull_request"
                and run.get("workflow_id") == current["workflow_id"]
                and run.get("head_repository", {}).get("full_name") == pr["head"]["repo"]["full_name"]
                and any(item.get("number") == event["number"]
                        and item.get("base", {}).get("sha") == pr["base"]["sha"]
                        and item.get("base", {}).get("ref") == pr["base"]["ref"]
                        for item in run.get("pull_requests", []))]
        for run in sorted(runs, key=lambda item: item["id"], reverse=True):
            require(run.get("status") == "completed" and run.get("conclusion") == "success",
                    "Latest matching prior run did not succeed")
            jobs = api.jobs(run)
            # A successful reuse gate is a link in the chain, not proof that tests ran.
            # Continue to an actual matrix/package run with the same product tree.
            if any(job["name"] == "package" and job.get("conclusion") == "skipped" for job in jobs):
                for name in ("configuration", "ci-required"):
                    found = [job for job in jobs if job["name"] == name]
                    require(len(found) == 1 and found[0].get("status") == "completed"
                            and found[0].get("conclusion") == "success", "Unverified prior skip")
                continue
            verify_jobs(jobs, portable_names, prior=True)
            return f"Reused complete validation from {revision}, run {run['id']}"
    raise ValueError("No accepted CI for unchanged product source and current PR base")


def evaluate(event_name, event, needs, api, run_id, run_attempt, revisions=reusable_revisions):
    require(needs.get("configuration", {}).get("result") == "success", "Configuration did not pass")
    if event_name == "pull_request":
        require(not event["pull_request"].get("draft", False),
                "Draft is not a validated candidate; mark Ready for review to run required CI")
    else:
        require(event_name == "workflow_dispatch", "Unsupported CI event")
    outputs = needs["configuration"]["outputs"]
    portable_names = expected_jobs(outputs)
    mode = outputs.get("validation_mode")
    results = {job: needs.get(job, {}).get("result") for job in ("portable", "package")}
    if mode == "documentation":
        require(event_name == "pull_request" and outputs.get("run_portable") == "false",
                "Invalid documentation exemption")
        require(all(value == "skipped" for value in results.values()), "Unexpected documentation job results")
        return "Documentation-only PR: product tests and package intentionally omitted"
    require(mode in {"candidate", "reuse"}, "Missing or invalid validation mode")
    if mode == "candidate":
        require(outputs.get("run_portable") == "true", "Candidate validation was not selected")
        require(all(value == "success" for value in results.values()), "Required tests/package did not succeed")
    else:
        reusable_event = (event.get("action") == "synchronize"
                          or (event.get("action") == "edited" and "base" not in event.get("changes", {})))
        require(event_name == "pull_request" and reusable_event
                and outputs.get("run_portable") == "false", "Invalid reuse exemption")
        require(all(value == "skipped" for value in results.values()), "Unexpected reuse job results")
    current = api.get(f"runs/{run_id}")
    require(str(current["id"]) == str(run_id) and str(current["run_attempt"]) == str(run_attempt),
            "Run attempt changed during validation")
    if mode == "candidate":
        verify_jobs(api.jobs(current), portable_names)
        return "All required matrix jobs and package passed for this candidate"
    return verify_reuse(event, current, api, portable_names, revisions(event))


def main():
    try:
        event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        message = evaluate(os.environ["GITHUB_EVENT_NAME"], event, json.loads(os.environ["CI_NEEDS"]),
                           Actions(), os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_RUN_ATTEMPT"])
        print(message)
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as summary:
            summary.write(message + "\n")
    except Exception as error:
        print(f"ci-required failed: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
