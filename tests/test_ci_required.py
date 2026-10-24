"""Focused merge-gate scenarios using Actions fixtures and real Git history."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils"))
import ci_policy as policy
import ci_required as gate


def event(*, action="opened", draft=False):
    return {"action": action, "number": 42, "before": "c" * 40,
            "repository": {"default_branch": "main"},
            "pull_request": {"draft": draft,
                             "base": {"ref": "develop/m4", "sha": "a" * 40},
                             "head": {"sha": "b" * 40, "repo": {"full_name": "owner/M4"}}}}


def needs(*, full=False, mode="candidate"):
    plan = policy.plan_ci("workflow_dispatch", {"inputs": {"full_matrix": full}})
    outputs = {"matrix": json.dumps(plan["matrix"]), "full_matrix": str(full).lower(),
               "validation_mode": mode, "run_portable": str(mode == "candidate").lower()}
    return {"configuration": {"result": "success", "outputs": outputs},
            **{name: {"result": "success" if mode == "candidate" else "skipped"}
               for name in ("portable", "package")}}


def jobs(*, full=False, prior=False):
    names = gate.expected_jobs(needs(full=full)["configuration"]["outputs"]) | {"configuration", "package"}
    if prior:
        names.add("ci-required")
    return [{"name": name, "status": "completed", "conclusion": "success"} for name in sorted(names)]


class FakeActions:
    def __init__(self, *, full=False):
        self.current = {"id": 100, "run_attempt": 1, "workflow_id": 7}
        self.prior = {"id": 90, "run_attempt": 2, "workflow_id": 7,
                      "event": "pull_request", "head_sha": "c" * 40,
                      "status": "completed", "conclusion": "success",
                      "head_repository": {"full_name": "owner/M4"},
                      "pull_requests": [{"number": 42, "base": {"ref": "develop/m4", "sha": "a" * 40}}]}
        self.current_jobs = jobs(full=full)
        self.prior_jobs = jobs(full=full, prior=True)
        self.calls = []
        self.no_runs = False

    def get(self, path, **query):
        self.calls.append((path, query))
        if path == "runs/100":
            return self.current
        if path == "workflows/7/runs":
            return {"total_count": 0 if self.no_runs else 1,
                    "workflow_runs": [] if self.no_runs else [self.prior]}
        raise AssertionError(path)

    def jobs(self, run):
        self.calls.append(("jobs", (run["id"], run["run_attempt"])))
        return self.current_jobs if run["id"] == 100 else self.prior_jobs


class GateTests(unittest.TestCase):
    def evaluate(self, required=None, api=None, payload=None, revisions=None):
        return gate.evaluate("pull_request", payload or event(), required or needs(), api or FakeActions(),
                             100, 1, revisions=revisions or (lambda _: ["c" * 40]))

    def test_standard_windows_ubuntu_and_zip_pass(self):
        self.assertIn("passed", self.evaluate())

    def test_failed_windows_or_ubuntu_or_package_fail(self):
        for name in ("portable (windows-latest, 3.12)", "portable (ubuntu-latest, 3.12)", "package"):
            for result in ("failure", "cancelled", "skipped"):
                api = FakeActions()
                next(job for job in api.current_jobs if job["name"] == name)["conclusion"] = result
                with self.subTest(name=name, result=result), self.assertRaises(ValueError):
                    self.evaluate(api=api)

    def test_aggregate_failure_cancel_or_skip_fail_even_if_api_has_old_success(self):
        for job in ("configuration", "portable", "package"):
            for result in ("failure", "cancelled", "skipped", ""):
                required = needs()
                required[job]["result"] = result
                with self.subTest(job=job, result=result), self.assertRaises(ValueError):
                    self.evaluate(required=required)

    def test_docs_only_intentional_skip_passes_without_api(self):
        api = FakeActions()
        self.assertIn("Documentation-only", self.evaluate(needs(mode="documentation"), api))
        self.assertEqual(api.calls, [])

    def test_unexpected_skip_or_missing_policy_outputs_fail(self):
        for key in needs()["configuration"]["outputs"]:
            required = needs()
            del required["configuration"]["outputs"][key]
            with self.subTest(key=key), self.assertRaises((ValueError, TypeError)):
                self.evaluate(required)
        with self.assertRaises(ValueError):
            self.evaluate(needs(mode="unknown"))

    def test_six_jobs_pass_only_when_complete(self):
        self.assertIn("passed", self.evaluate(needs(full=True), FakeActions(full=True)))
        for api in (FakeActions(), FakeActions(full=True)):
            api.current_jobs.pop()
            with self.assertRaises(ValueError):
                self.evaluate(needs(full=True), api)

    def test_duplicate_configuration_cannot_replace_missing_configuration(self):
        api = FakeActions(full=True)
        api.current_jobs[-1] = deepcopy(api.current_jobs[-2])
        with self.assertRaises(ValueError):
            self.evaluate(needs(full=True), api)

    def test_incomplete_matrix_output_does_not_downgrade_requirement(self):
        required = needs(full=True)
        required["configuration"]["outputs"]["matrix"] = needs()["configuration"]["outputs"]["matrix"]
        with self.assertRaises(ValueError):
            self.evaluate(required)

    def test_draft_fails_without_product_jobs_or_api(self):
        api = FakeActions()
        with self.assertRaisesRegex(ValueError, "Draft"):
            self.evaluate(needs(mode="draft"), api, event(draft=True))
        self.assertEqual(api.calls, [])
        with self.assertRaisesRegex(ValueError, "Draft"):
            self.evaluate(needs(), api, event(draft=True))

    def test_docs_update_reuses_successful_same_source_ci(self):
        api = FakeActions()
        self.assertIn("Reused", self.evaluate(needs(mode="reuse"), api, event(action="synchronize")))
        self.assertIn(("jobs", (90, 2)), api.calls)

    def test_six_config_reuse_rejects_prior_two_job_run(self):
        with self.assertRaises(ValueError):
            self.evaluate(needs(full=True, mode="reuse"), FakeActions(), event(action="synchronize"))
        self.assertIn("Reused", self.evaluate(needs(full=True, mode="reuse"), FakeActions(full=True),
                                              event(action="synchronize")))

    def test_missing_or_failed_or_wrong_source_run_cannot_validate_docs_update(self):
        mutations = [("head_sha", "d" * 40), ("event", "workflow_dispatch"), ("workflow_id", 8),
                     ("conclusion", "failure"), ("conclusion", "cancelled"), ("status", "in_progress"),
                     ("head_repository", {"full_name": "different/M4"}),
                     ("pull_requests", []),
                     ("pull_requests", [{"number": 42, "base": {"ref": "develop/m4", "sha": "d" * 40}}])]
        for key, value in mutations:
            api = FakeActions()
            api.prior[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.evaluate(needs(mode="reuse"), api, event(action="synchronize"))
        api = FakeActions()
        api.no_runs = True
        with self.assertRaises(ValueError):
            self.evaluate(needs(mode="reuse"), api, event(action="synchronize"))

    def test_skipped_or_failed_prior_tests_or_package_are_not_evidence(self):
        for name in ("portable (windows-latest, 3.12)", "package", "ci-required"):
            for result in ("failure", "skipped"):
                api = FakeActions()
                next(job for job in api.prior_jobs if job["name"] == name)["conclusion"] = result
                with self.subTest(name=name, result=result), self.assertRaises(ValueError):
                    self.evaluate(needs(mode="reuse"), api, event(action="synchronize"))

    def test_api_error_or_changed_attempt_fails(self):
        api = FakeActions()
        api.current["run_attempt"] = 2
        with self.assertRaises(ValueError):
            self.evaluate(api=api)
        with patch.object(FakeActions, "get", side_effect=OSError("unavailable")):
            with self.assertRaises(OSError):
                self.evaluate()

    def test_reuse_not_allowed_on_ready_or_retarget(self):
        for action in ("ready_for_review", "opened", "reopened", "edited"):
            payload = event(action=action)
            payload["changes"] = {"base": {"ref": {"from": "another"}}}
            with self.subTest(action=action), self.assertRaises(ValueError):
                self.evaluate(needs(mode="reuse"), payload=payload)

    def test_metadata_edit_reuses_same_head_without_new_product_jobs(self):
        payload = event(action="edited")
        with patch.object(policy, "comparison_plan", return_value=policy.plan_ci(
                "pull_request", payload, ["source.py"])):
            self.assertEqual(policy.select_ci("pull_request", payload)["validation_mode"], "reuse")
        api = FakeActions()
        api.prior["head_sha"] = "b" * 40
        self.assertIn("Reused", self.evaluate(needs(mode="reuse"), api, payload,
                                              revisions=lambda _: ["b" * 40]))

    def test_manual_candidate_checks_real_jobs(self):
        self.assertIn("passed", gate.evaluate("workflow_dispatch", {}, needs(full=True),
                                               FakeActions(full=True), 100, 1))


class HistoryTests(unittest.TestCase):
    def test_repeated_metadata_edits_find_actual_tests_on_the_same_sha(self):
        api = FakeActions()
        skipped = {**deepcopy(api.prior), "id": 95}
        skipped_jobs = [{"name": name, "status": "completed", "conclusion": result}
                        for name, result in (("configuration", "success"), ("package", "skipped"),
                                             ("portable", "skipped"), ("ci-required", "success"))]
        actual_jobs = api.prior_jobs
        original_get = api.get
        api.get = lambda path, **query: ({"total_count": 2, "workflow_runs": [skipped, api.prior]}
                                        if "head_sha" in query else original_get(path, **query))
        api.jobs = lambda run: skipped_jobs if run["id"] == 95 else actual_jobs
        self.assertIn("run 90", gate.evaluate("pull_request", event(action="edited"), needs(mode="reuse"),
                                              api, 100, 1, revisions=lambda _: ["c" * 40]))

    def test_reuse_walks_docs_chain_but_never_crosses_runtime_change(self):
        with tempfile.TemporaryDirectory() as directory:
            def git(*args):
                return subprocess.check_output(["git", "-C", directory, *args], text=True).strip()
            def commit(path, content):
                file = Path(directory, path)
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(content, encoding="utf-8")
                git("add", ".")
                git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                    "commit", "-qm", "fixture")
                return git("rev-parse", "HEAD")
            git("init", "-q")
            old = commit("source.py", "old runtime")
            accepted = commit("source.py", "validated runtime")
            docs1 = commit("docs/notes.md", "first docs update")
            docs2 = commit("docs/notes.md", "second docs update")
            payload = event(action="synchronize")
            payload["before"] = docs1
            payload["pull_request"]["head"]["sha"] = docs2
            original = gate.git
            with patch.object(gate, "git", side_effect=lambda *args: original("-C", directory, *args)):
                revisions = list(gate.reusable_revisions(payload))
                self.assertEqual(revisions, [docs1, accepted])
                self.assertNotIn(old, revisions)
                runtime = commit("source.py", "unvalidated runtime")
                payload["pull_request"]["head"]["sha"] = runtime
                self.assertEqual(list(gate.reusable_revisions(payload)), [])
                payload["before"] = runtime
                payload["pull_request"]["head"]["sha"] = docs2
                with self.assertRaises(subprocess.CalledProcessError):
                    list(gate.reusable_revisions(payload))

    def test_successful_skipped_run_is_only_a_link_to_concrete_test_evidence(self):
        api = FakeActions()
        accepted_jobs = api.prior_jobs
        skipped_jobs = [{"name": name, "status": "completed", "conclusion": result}
                        for name, result in (("configuration", "success"), ("package", "skipped"),
                                             ("portable", "skipped"), ("ci-required", "success"))]
        api.jobs = lambda _: skipped_jobs if api.prior["head_sha"] == "c" * 40 else accepted_jobs
        original_get = api.get
        def get(path, **query):
            if "head_sha" in query:
                api.prior["head_sha"] = query["head_sha"]
            return original_get(path, **query)
        api.get = get
        self.assertIn("Reused", gate.evaluate("pull_request", event(action="synchronize"),
                                              needs(mode="reuse"), api, 100, 1,
                                              revisions=lambda _: ["c" * 40, "d" * 40]))


class ExecutionTests(unittest.TestCase):
    def test_jobs_api_paginates_and_pins_attempt(self):
        with patch.dict(os.environ, {"GITHUB_API_URL": "https://api.github.com",
                                     "GITHUB_REPOSITORY": "owner/M4"}):
            api = gate.Actions()
        with patch.object(api, "get", side_effect=[{"jobs": [{"name": "first"}], "total_count": 2},
                                                   {"jobs": [{"name": "second"}], "total_count": 2}]) as get:
            self.assertEqual(len(api.jobs({"id": 90, "run_attempt": 2})), 2)
            self.assertEqual([call.args[0] for call in get.call_args_list],
                             ["runs/90/attempts/2/jobs"] * 2)
            self.assertEqual([call.kwargs["page"] for call in get.call_args_list], [1, 2])

    def test_main_process_passes_docs_and_exits_nonzero_on_draft_or_missing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = Path(directory, "event.json")
            summary = Path(directory, "summary.md")
            for mode, draft, expected in (("documentation", False, 0), ("draft", True, 1),
                                           ("candidate", False, 1)):
                required = needs(mode=mode)
                if mode == "candidate":
                    required["portable"]["result"] = "skipped"
                payload.write_text(json.dumps(event(draft=draft)), encoding="utf-8")
                env = {**os.environ, "GITHUB_EVENT_NAME": "pull_request", "GITHUB_EVENT_PATH": str(payload),
                       "GITHUB_STEP_SUMMARY": str(summary), "CI_NEEDS": json.dumps(required),
                       "GITHUB_API_URL": "https://api.github.com", "GITHUB_REPOSITORY": "owner/M4",
                       "GITHUB_RUN_ID": "100", "GITHUB_RUN_ATTEMPT": "1"}
                result = subprocess.run([sys.executable, str(Path(gate.__file__))], env=env,
                                        text=True, capture_output=True)
                with self.subTest(mode=mode):
                    self.assertEqual(result.returncode, expected, result.stderr)

    def test_retarget_selects_full_comparison_and_new_tests(self):
        payload = event(action="edited")
        payload["changes"] = {"base": {"ref": {"from": "another"}}}
        plan = policy.plan_ci("pull_request", payload, ["utils/ci_required.py"])
        with patch.object(policy, "comparison_plan", return_value=plan):
            selected = policy.select_ci("pull_request", payload)
        self.assertTrue(selected["run_portable"])
        self.assertTrue(selected["full_matrix"])


if __name__ == "__main__":
    unittest.main()
