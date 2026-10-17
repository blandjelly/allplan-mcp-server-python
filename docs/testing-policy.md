# Testing and package policy

This policy is the source of truth for choosing checks and package builds.
At the start of each chat, read this file and [the current handoff](next-model-handoff.md).
First identify the checkout and branch, source state, and scope of the proposed
change. Keep focused test passes, full CI passes, and native Allplan passes
separate when reporting results. The model owns automated tests and GitHub CI;
the owner is asked only for a brief Allplan trial when a candidate needs it.
An explicit owner pause takes precedence over this procedure.

## During implementation

Run only focused affected tests and their dependent tests as you iterate. Use
HTTP checks for changes to MCP, transport, or launcher behavior. Do not run the
full local suite or build packages after every change. For documentation,
logs, or AGENTS-only changes, review the diff and links; skip runtime tests,
builds, hash checks, and reruns.

## Candidate and CI selection

For each new candidate or package, run the full GitHub CI matrix on Windows
and Ubuntu with Python 3.12. This full CI result replaces a full local test
run. Keep a pull request in draft while iterating and return it to draft when
development resumes. Mark it ready once the final candidate is ready for
review. A passing run for an earlier source revision does not validate later
runtime changes.

The workflow runs full jobs for ready pull requests or `workflow_dispatch`.
Draft pull requests run configuration checks only. On `synchronize`, CI checks
the latest push's diff; on `opened`, `ready_for_review`, or `reopened`, it
checks the full pull request diff. A docs-only update to a mixed pull request
skips product jobs. A ready pull request targeting the default `main` branch runs
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
For manual runs, the model must choose true for compatibility-sensitive changes;
false is only for an ordinary package candidate. Do not repeatedly dispatch an
unchanged candidate, or rerun passed checks without a relevant change or failure.

## Package build and installation

After all tests finish, run one separate build job to produce wheel, sdist,
and ZIP. Use that same source's CI artifact for installation or upgrade and,
if applicable, restore of the exact ZIP, once. Do not rebuild or repeat these
checks after the artifact succeeds. If the artifact is unavailable, one local
build may replace package production.

## Native Allplan checks

Request an owner trial only for new or materially changed native behavior.
Do not repeat observations already accepted in the handoff or expand their
acceptance scope. Keep native PASS distinct from automated test and CI PASS;
record the tested scope and evidence in the handoff after a completed stage.

Preserve all existing runtime write guards, revalidation, journaling, and hash
safeguards. Testing or packaging changes do not authorize weakening them.
