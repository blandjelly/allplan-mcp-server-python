"""Candidate selection and actual GitHub-output behavior; no product/native calls."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "utils/ci_policy.py"
spec = importlib.util.spec_from_file_location("ci_policy", SCRIPT)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

PROJECT = '[project]\nname = "allplan-mcp-server"\nversion = "0.6.1"\nrequires-python = ">=3.11"\ndependencies = ["fastmcp==3.2.4"]\n'
LOCK = '''version = 1
requires-python = ">=3.11"
[[package]]
name = "allplan-mcp-server"
version = "0.6.1"
source = { editable = "." }
[[package]]
name = "fastmcp"
version = "3.2.4"
source = { registry = "https://pypi.org/simple" }
'''


def event(*, draft=False, base="feature/m4", action="opened"):
    return {"action": action, "repository": {"default_branch": "main"},
            "before": "c" * 40,
            "pull_request": {"draft": draft, "base": {"ref": base, "sha": "a" * 40},
                             "head": {"sha": "b" * 40}}}


class SelectionTests(unittest.TestCase):
    def plan(self, paths=("src/allplan_mcp/server.py",), *, payload=None,
             project=PROJECT, lock=LOCK, history=True):
        blobs = {("before", "pyproject.toml"): PROJECT, ("after", "pyproject.toml"): project,
                 ("before", "uv.lock"): LOCK, ("after", "uv.lock"): lock}
        return policy.plan_ci("pull_request", payload or event(), paths,
                              lambda side, path: blobs[side, path], history_available=history)

    def assert_matrix(self, plan, versions):
        self.assertTrue(plan["run_portable"])
        self.assertEqual({(j["os"], j["python"]) for j in plan["matrix"]["include"]},
                         {(system, version) for system in ("ubuntu-latest", "windows-latest") for version in versions})

    def test_ordinary_ready_candidate_uses_two_python312_platforms(self):
        self.assert_matrix(self.plan(), ["3.12"])

    def test_draft_skips_product_jobs_even_with_critical_changes_or_missing_history(self):
        for history in (True, False):
            plan = self.plan(["windows/setup.cmd"], payload=event(draft=True), history=history)
            self.assertFalse(plan["run_portable"])

    def test_documentation_and_owner_logs_skip_product_jobs_even_on_main(self):
        paths = ["AGENTS.md", "README.md", "docs/testing-policy.md", "docs/nested/guide.md",
                 "evaluation-packages/0.18.2/native-acceptance/owner/report.json"]
        self.assertFalse(self.plan(paths, payload=event(base="main"))["run_portable"])

    def test_new_code_alongside_documentation_still_runs_tests(self):
        self.assert_matrix(self.plan(["README.md", "src/allplan_mcp/server.py"]), ["3.12"])

    def test_project_version_only_in_both_files_does_not_expand_matrix(self):
        self.assert_matrix(self.plan(["pyproject.toml", "uv.lock", "src/allplan_mcp/__init__.py"],
                           project=PROJECT.replace("0.6.1", "0.6.2"), lock=LOCK.replace("0.6.1", "0.6.2")), ["3.12"])

    def test_version_only_pyproject_and_lock_are_each_exempt(self):
        self.assert_matrix(self.plan(["pyproject.toml"], project=PROJECT.replace("0.6.1", "0.6.2")), ["3.12"])
        self.assert_matrix(self.plan(["uv.lock"], lock=LOCK.replace("0.6.1", "0.6.2")), ["3.12"])

    def test_other_configuration_changes_require_full_compatibility(self):
        for old, new in ((">=3.11", ">=3.12"), ("3.2.4", "3.2.5"),
                         ("allplan-mcp-server", "another-project")):
            with self.subTest(change=new):
                self.assert_matrix(self.plan(["pyproject.toml"], project=PROJECT.replace(old, new)), ["3.11", "3.12", "3.13"])
        self.assert_matrix(self.plan(["pyproject.toml"], project=PROJECT+'\n[build-system]\nrequires = ["hatchling==1.28.0"]\n'), ["3.11", "3.12", "3.13"])

    def test_locked_dependency_or_python_change_requires_six_jobs(self):
        for old, new in (("3.2.4", "3.2.5"), (">=3.11", ">=3.12"), ("version = 1", "version = 2")):
            with self.subTest(change=new):
                self.assert_matrix(self.plan(["uv.lock"], lock=LOCK.replace(old, new)), ["3.11", "3.12", "3.13"])

    def test_registry_package_named_like_project_is_not_exempt(self):
        before = LOCK.replace('source = { editable = "." }', 'source = { registry = "https://pypi.org/simple" }')
        blobs = {("before", "uv.lock"): before, ("after", "uv.lock"): before.replace("0.6.1", "0.6.2")}
        read = lambda side, path: PROJECT if path == "pyproject.toml" else blobs[side, path]
        self.assert_matrix(policy.plan_ci("pull_request", event(), ["uv.lock"], read), ["3.11", "3.12", "3.13"])

    def test_virtual_self_package_version_is_exempt(self):
        before = LOCK.replace('editable = "."', 'virtual = "."')
        read = lambda side, path: PROJECT if path == "pyproject.toml" else (before if side == "before" else before.replace("0.6.1", "0.6.2"))
        self.assert_matrix(policy.plan_ci("pull_request", event(), ["uv.lock"], read), ["3.12"])

    def test_critical_install_and_ci_paths_require_full_matrix(self):
        for path in ("windows/setup.cmd", "utils/register_python_host.py", "utils/build_windows_package.py",
                     "utils/ci_policy.py", ".github/workflows/portable.yml", ".python-version", "uv.toml"):
            with self.subTest(path=path):
                self.assert_matrix(self.plan([path]), ["3.11", "3.12", "3.13"])

    def test_main_integration_requires_six_even_for_version_only_change(self):
        self.assert_matrix(self.plan(["pyproject.toml"], payload=event(base="main"),
                           project=PROJECT.replace("0.6.1", "0.6.2")), ["3.11", "3.12", "3.13"])

    def test_repository_default_branch_is_respected(self):
        payload = event(base="trunk")
        payload["repository"]["default_branch"] = "trunk"
        self.assert_matrix(self.plan(payload=payload), ["3.11", "3.12", "3.13"])

    def test_missing_history_or_invalid_metadata_cannot_downgrade_checks(self):
        self.assert_matrix(self.plan(history=False), ["3.11", "3.12", "3.13"])
        self.assert_matrix(self.plan(["pyproject.toml"], project="not TOML ["), ["3.11", "3.12", "3.13"])
        self.assert_matrix(self.plan(["pyproject.toml"], project=PROJECT.replace('version = "0.6.1"\n', '')), ["3.11", "3.12", "3.13"])
        self.assert_matrix(self.plan(["uv.lock"], lock="package = 5"), ["3.11", "3.12", "3.13"])

    def test_manual_standard_candidate_and_release_override(self):
        self.assert_matrix(policy.plan_ci("workflow_dispatch", {"inputs": {"full_matrix": "false"}}), ["3.12"])
        for payload in ({}, {"inputs": {"full_matrix": True}}, {"inputs": {"full_matrix": "true"}}):
            self.assert_matrix(policy.plan_ci("workflow_dispatch", payload), ["3.11", "3.12", "3.13"])

    def test_invalid_manual_mode_and_unknown_event_are_errors(self):
        with self.assertRaises(ValueError):
            policy.plan_ci("workflow_dispatch", {"inputs": {"full_matrix": "sometimes"}})
        with self.assertRaises(ValueError):
            policy.plan_ci("push", {})

    def test_ready_open_reopen_use_pr_base_and_synchronize_uses_latest_push(self):
        for action in ("opened", "ready_for_review", "reopened"):
            self.assertEqual(policy.comparison(event(action=action)), ("a" * 40, "b" * 40))
        self.assertEqual(policy.comparison(event(action="synchronize")), ("c" * 40, "b" * 40))

    def test_missing_zero_or_invalid_revisions_are_unavailable(self):
        for value in (None, "", "0" * 40, "--all", "not-a-sha"):
            payload = event(action="synchronize")
            payload["before"] = value
            with self.subTest(revision=value), self.assertRaises(ValueError):
                policy.comparison(payload)


class OutputTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repo = Path(directory.name)
        self.git("init", "-q")
        self.git("config", "user.name", "CI policy test")
        self.git("config", "user.email", "ci-policy@example.invalid")
        self.base = self.commit({"pyproject.toml": PROJECT, "uv.lock": LOCK, "README.md": "base\n"})
        self.version = self.commit({"pyproject.toml": PROJECT.replace("0.6.1", "0.6.2"),
                                    "uv.lock": LOCK.replace("0.6.1", "0.6.2")})
        self.docs = self.commit({"README.md": "updated documentation\n"})

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.repo, text=True, stderr=subprocess.PIPE).strip()

    def commit(self, files):
        for name, data in files.items():
            (self.repo / name).write_text(data, encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "policy fixture")
        return self.git("rev-parse", "HEAD")

    def run_policy(self, before, after, *, draft=False, base="feature/m4"):
        payload = event(draft=draft, base=base, action="synchronize")
        payload["before"] = before
        payload["pull_request"]["head"]["sha"] = after
        event_file, output_file = self.repo / "event.json", self.repo / "output.txt"
        event_file.write_text(json.dumps(payload), encoding="utf-8")
        output_file.write_text("", encoding="utf-8")
        env = {**os.environ, "GITHUB_EVENT_NAME": "pull_request", "GITHUB_EVENT_PATH": str(event_file),
               "GITHUB_OUTPUT": str(output_file)}
        result = subprocess.run([sys.executable, str(SCRIPT)], cwd=self.repo, env=env,
                                text=True, capture_output=True, check=True)
        output = dict(line.split("=", 1) for line in output_file.read_text().splitlines())
        plan = json.loads(result.stdout)
        self.assertEqual(json.loads(output["matrix"]), plan["matrix"])
        self.assertEqual(output["run_portable"], str(plan["run_portable"]).lower())
        return plan

    def test_real_git_version_change_emits_two_jobs(self):
        plan = self.run_policy(self.base, self.version)
        self.assertTrue(plan["run_portable"])
        self.assertEqual(len(plan["matrix"]["include"]), 2)

    def test_real_git_docs_update_to_mixed_pr_emits_skip(self):
        self.assertFalse(self.run_policy(self.version, self.docs)["run_portable"])

    def test_real_git_missing_history_fails_to_full_checks(self):
        plan = self.run_policy("f" * 40, self.version)
        self.assertTrue(plan["full_matrix"])
        self.assertTrue(plan["run_portable"])

    def test_real_git_main_integration_emits_six_jobs(self):
        self.assertEqual(len(self.run_policy(self.base, self.version, base="main")["matrix"]["include"]), 6)

    def test_draft_needs_no_comparison_history(self):
        self.assertFalse(self.run_policy(None, self.version, draft=True)["run_portable"])


if __name__ == "__main__":
    unittest.main()
