# Testing and package policy

This policy is the source of truth for choosing checks and package builds.
At the start of each chat, read this file and [the current handoff](next-model-handoff.md).
First identify the checkout and branch, source state, and scope of the proposed
change. Keep focused test passes, full CI passes, and native Allplan passes
separate when reporting results. Codex owns implementation and focused tests;
GitHub Actions runs full CI and builds; the owner supervises CI, verifies
delivery and merges after all required gates pass.
An explicit owner pause takes precedence over this procedure.

M4 topic branches and PRs use **develop/m4** as their base; main integration
is a separate task. Ref/PR consolidation with unchanged runtime follows the
documentation-only checks, without repeating accepted product or native gates.
See the [current handoff](next-model-handoff.md) for branch and scope.

## Responsibilities and handoff

Codex analyzes and implements changes, runs focused affected/dependent tests,
checks version consistency, commits, pushes and prepares the PR. Version
checks include agreement between project metadata, the self editable lock
entry and the server version constant. Codex marks the final candidate
**Ready for review**, provides the commit SHA and PR link, then ends the task.

The owner monitors CI, checks that all required jobs passed for the intended
source commit, downloads and verifies the ZIP and all applicable installation,
upgrade and restore procedures, and merges into **develop/m4** only after all
required conditions pass. Downloading an artifact alone does not satisfy any
package verification gate. The owner sends failed-test logs to Codex; Codex
can then diagnose and fix the failure and hand off a new candidate.

Unless explicitly instructed by the owner to perform the specific action,
Codex does not poll GitHub Actions status, wait for Windows/Ubuntu jobs,
repeatedly retrieve logs, download CI artifacts, perform a fallback ZIP build
(including after HTTP 403), rerun full CI, or merge PRs. This responsibility
split does not waive any required validation or native Allplan gate.

## During implementation

Run only focused affected tests and their dependent tests as you iterate. Use
HTTP checks for changes to MCP, transport, or launcher behavior. Do not run the
full local suite or build packages after every change. For documentation,
logs, or AGENTS-only changes, review the diff and links; skip runtime tests,
builds, hash checks, and reruns.

## Candidate and CI selection

For each new candidate or package, GitHub Actions must run the full CI matrix
on Windows and Ubuntu with Python 3.12. This full CI result replaces a full local test
run. Keep a pull request in draft while iterating and return it to draft when
development resumes. Mark it ready once the final candidate is ready for
review. The current [workflow](../.github/workflows/portable.yml) handles
`ready_for_review`; this event compares the full PR diff and selects the
required matrix through [ci_policy.py](../utils/ci_policy.py). Codex must mark
final product candidates Ready for review to trigger that validation before
handoff. Documentation-only PRs run configuration and the lightweight
`ci-required` gate; they require only diff and link checks, without product
tests or builds. A passing run for an earlier source
revision does not validate later runtime changes.

The workflow runs full jobs for ready pull requests or `workflow_dispatch`.
Draft pull requests run configuration and the lightweight gate only;
`ci-required` fails because a draft is not a validated merge candidate.
On `synchronize`, CI checks
the latest push's diff; on `opened`, `ready_for_review`, or `reopened`, it
checks the full pull request diff. A docs-only update to a mixed pull request
skips product jobs, but the gate requires accepted validation of unchanged
product source. Matrix requirements also consider the full PR diff, so a later
ordinary push cannot downgrade a compatibility change to two jobs.
A ready pull request targeting the default `main` branch runs
the full six-job matrix before integration; code changes to a feature branch use two jobs, and
critical changes use six. `workflow_dispatch` has `full_matrix` defaulting to
true: use false for a standard two-platform draft-candidate run, and true
for main or release validation. There is no push trigger, so merging does not
duplicate pull-request CI. A direct push to `main` requires manual full CI.

Use the full six-job matrix only for true dependency, interpreter, install,
builder, or workflow changes, and for `main` integration or release. A
`project.version` bump in `pyproject.toml` together with the self editable
package version in `uv.lock` does not by itself require six jobs. Changes to
actual dependencies or other `pyproject.toml`/lock settings conservatively
require six jobs. Use six jobs when the relevant change history is incomplete.
For manual runs, the owner (or Codex when explicitly instructed) must choose
true for compatibility-sensitive changes;
false is only for an ordinary package candidate. Do not repeatedly dispatch an
unchanged candidate, or rerun passed checks without a relevant change or failure.

## Required GitHub check

For PRs to **develop/m4**, configure **ci-required** (GitHub Actions) as the
required status check. It runs after configuration, portable and package even
on failure or skip, and requires successful configuration, every selected
Windows/Ubuntu matrix job and the package job for a product candidate. It
checks concrete job results for the current run attempt; `skipped`, cancelled,
missing or incomplete mandatory validation fails. Documentation-only PRs
explicitly exempt product tests and package builds. Marking a draft Ready for
review compares the full PR and starts the required validation.

For a docs-only `synchronize` on a mixed PR, the gate searches at most 20
first-parent revisions for a successful run of this workflow in the same PR
and with the same base SHA/ref. Every file outside the policy's documentation
paths must be unchanged, including runtime, tests, dependencies and workflow.
It requires concrete successful matrix/package jobs and a successful prior
gate; a successful skip is only a link to the actual test evidence. It inspects
the latest attempt and rejects failed, missing, inaccessible or excessive
evidence (over 100 runs per SHA or 1,000 jobs per attempt). It never starts
replacement tests or builds. Without proof, the gate fails and the owner
decides the next validation action. Older runs without this gate are not proof.

Changing a PR's base triggers selection and validation against the new base.
Other PR metadata edits reuse existing validation without new product jobs.
Manual runs expose **ci-manual**, so a manually selected two-job run cannot
replace the required PR check. Only the gate has extra `actions: read` access;
all workflow permissions remain read-only. This check covers automated CI and
package production; the owner's exact-ZIP and applicable native gates still
apply. Configure conditional matrix/package jobs through this aggregate check
instead of requiring their skipped contexts on documentation-only PRs.

## Package build and installation

After all tests pass, GitHub Actions automatically runs one separate build
job to produce wheel, sdist and ZIP. The owner uses that same source's CI
artifact and verifies the exact delivered ZIP once, including installation
or upgrade and, if applicable, restore. All existing integrity/hash and
installation/upgrade/restore checks remain mandatory in their existing scope.
Do not rebuild or repeat these checks after the artifact succeeds. If the
artifact is unavailable, the owner may perform one local build to replace
package production, or explicitly assign that fallback to Codex. HTTP 403
alone does not authorize Codex to build a replacement.

## Native Allplan checks

Request an owner trial only for new or materially changed native behavior.
Do not repeat observations already accepted in the handoff or expand their
acceptance scope. Keep native PASS distinct from automated test and CI PASS;
record the tested scope and evidence in the handoff after a completed stage.

Preserve all existing runtime write guards, revalidation, journaling, and hash
safeguards. Testing or packaging changes do not authorize weakening them.

[Verification of this procedure](test-results/testing-policy-2026-10-17.md)
records the full workflow-change candidate and the draft-PR skip behavior.
