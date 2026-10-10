# Shorter validation cycle for M3

Adopted by the owner on 2026-10-10. Preserve meaningful regression tests;
choose when to run them according to the change. A request to postpone tests
overrides this default schedule: do not run local tests, builds used as checks,
native owner gates or manually dispatch CI until testing is authorized again.

## Local work and publication

| Change or milestone | Required work when testing is authorized |
| --- | --- |
| Iterative M3 implementation | Focused M3 tests plus tests of other affected modules; add HTTP tests when MCP/transport/launchers change. |
| Documentation-only change | Read the edits, check links and git diff formatting. Do not repeat runtime tests, package builds or old evidence/hash verification. |
| New owner-test package | Run the full portable suite once for the final code candidate, frozen dependency sync, wheel/sdist build and exact package/installation checks. Use source CI as evidence for its tested commit. |
| Dependency, installer, package builder or workflow change | Full portable suite and the six-configuration compatibility matrix. |
| Release/main integration | Full portable suite and six-configuration compatibility matrix for the final candidate; required native acceptance remains separate. |
| Native Allplan observation | Test new behavior or a materially affected accepted behavior. Do not repeat unchanged accepted gates; record their evidence and scope; completed logs remain in Git history. |

Run one full suite for the final implementation candidate; repeat only for
new relevant changes, failures or unresolved concerns. Select affected modules
for focused iteration, including dependent read/audit/HTTP checks when contracts
change. [README](../README.md#source-development) holds current development
commands. Record actual checks/source/results; focused PASS is not full PASS.

## CI schedule

[Portable workflow](../.github/workflows/portable.yml):

- PR updates run CI once. Push-triggered CI is restricted to main, avoiding
  a second push run for the same feature-branch PR commit.
- Documentation-only changes under docs, README.md and evaluation-packages
  skip product tests/builds. A mixed code/documentation PR can still run the
  lightweight configuration job, because GitHub's PR path filter considers the
  full PR diff. The job checks the latest update and skips the product jobs.
  Runtime/source, tests, profiles and workflow changes remain eligible.
- Routine code changes use Windows and Ubuntu, Python 3.12. Each job runs the
  full portable suite, wheel/sdist build and Windows ZIP build; the shorter
  focused set is the local iteration check.
- Changes to pyproject.toml, uv.lock, windows, installer/package utilities or
  workflows automatically select all six Windows/Ubuntu Python 3.11–3.13 jobs.
  PR synchronize events compare the previous head with the new head, so an old
  dependency change does not force the full matrix on every later update.
  Opened/reopened PRs compare base/head; unavailable diff history selects the
  full matrix conservatively.
- workflow_dispatch exposes full_matrix, default true. Before release/main
  integration, explicitly request the full matrix even without matching paths.
  A manually requested basic run can set full_matrix=false.
- New updates cancel superseded runs for the same PR/ref. A cancelled run is
  not PASS. A configuration job chooses the matrix; it runs no product tests.

Historical CI results remain scoped to their original commits; see
[validation status](validation-status.md#portable-verification-and-delivery).

## Hashes and package checks

Keep exact plan hashes, fresh source/report checks before Apply and journal
record/request hashes. They bind authorization to reviewed data, detect source
conflicts and invalid records, and support exact-ID deduplication. Do not replace
fresh source validation with an old successful result or a cached model hash.

For a new delivered package, generate its checksum/manifest and verify the
actual extracted installation once. Later documentation/log summaries refer to
that recorded source, checksum and verification; do not rebuild the archive or
recompute all older archive/evidence hashes for each documentation edit.

Keep installer integrity checks and host health integrity checks. No runtime
hashing or native preflight/readback is removed by this policy. The cost of
hashing alone has not been profiled. Independent forensic recomputation remains
appropriate for a suspected mismatch/corruption or an explicit review request.

The package tests already exercise two identical ZIP builds and registration.
Do not additionally repeat those checks on every matrix job or local edit.
For delivery from a clean source, run one artifact verification pass and retain
its result; any added check should resolve a concrete remaining uncertainty.
