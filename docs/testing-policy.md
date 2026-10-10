# Shorter validation cycle for M3

Adopted by the owner on 2026-10-10. Preserve meaningful regression tests;
choose when to run them according to the change. A request to postpone tests
overrides this default schedule: do not run local tests, builds used as checks,
native owner gates or manually dispatch CI until testing is authorized again.
This policy update itself runs no tests and changes no acceptance result.

## Local work and publication

| Change or milestone | Required work when testing is authorized |
| --- | --- |
| Iterative M3 implementation | Focused M3 tests plus tests of other affected modules; add HTTP tests when MCP/transport/launchers change. |
| Documentation-only change | Read the edits, check links and git diff formatting. Do not repeat runtime tests, package builds or old evidence/hash verification. |
| New owner-test package | Run the full portable suite once for the final code candidate, frozen dependency sync, wheel/sdist build and exact package/installation checks. Use source CI as evidence for its tested commit. |
| Dependency, installer, package builder or workflow change | Full portable suite and the six-configuration compatibility matrix. |
| Release/main integration | Full portable suite and six-configuration compatibility matrix for the final candidate; required native acceptance remains separate. |
| Native Allplan observation | Test new behavior or a materially affected accepted behavior. Do not repeat unchanged accepted gates; preserve their original evidence and scope. |

The 0.11.0 baseline has 178 automated tests. Its focused M3 set has 44 tests;
these are baseline counts, not permanent gates. New implementation may add tests.
Recorded Linux timings: full suite 47.607 seconds, focused set 3.215 seconds,
23 HTTP/MCP tests 40.598 seconds. These are existing measurements, not guarantees
for another machine. A module selection cannot replace dependent read/audit tests
when those contracts change.

Focused command, for future use from the repository root:

```bash
PYTHONPATH=tests .venv/bin/python -m unittest test_model_repair test_repair_execution test_standard_preview test_mark_preview test_supported_execution
```

On Windows PowerShell, set `$env:PYTHONPATH = "tests"` and invoke the same module
list using `.venv\Scripts\python.exe`. Restore the previous environment value
afterward. This document does not request execution of either command now.

Run one full suite after the final implementation changes, rather than after
each edit or documentation/artifact commit. Repeat only when a new relevant
change, failure or unresolved concern justifies it. Record which checks actually
ran, their commit/package and result; do not describe a focused run as full PASS.

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

The policy/configuration commit is marked `[skip ci]` to honor the owner's
request to run no tests now. Historical six-job results remain scoped to their
original commits; this revised workflow has not been exercised by this update.

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
