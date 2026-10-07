# Testing and evaluation package build

M0/M1 use the standard-library unittest runner. External-server dependencies stay pinned in `uv.lock`; build backend and bootstrap uv versions are pinned. The CI matrix in `.github/workflows/portable.yml` covers ordinary Python 3.11–3.13 on Linux and Windows. Adding this workflow is not evidence that GitHub Actions or Windows checks have already run.

The 0.2.0 M1.1 slice passes 29 portable tests. New checks cover typed context
reads, missing data, loaded empty/passive files, raw bounded identity sampling
and context calls through MCP. The 0.2.1 correction passes **31 tests**, including
path-lookup fallback and preserving project name/host when lookup fails. Owner
0.2.0 feedback is [recorded separately](test-results/m1-context-runtime-0.2.0.md).
The [short correction batch](m1-context-fix-batch.md) subsequently passed on the
owner's Allplan setup; [0.2.1 runtime evidence](test-results/m1-context-runtime-0.2.1.md)
is separate from UAT-02/UAT-03 and complete M1 acceptance.

The **0.3.0** slice passes **24 relevant targeted portable checks**: 21 new query
checks, one new MCP schema/transport test and two distribution/version checks.
[Commands, evidence and limits](test-results/m1-query-portable-0.3.0.md).
The full historical suite was not rerun; CI discovery now includes 53 distinct
test methods. This count is inventory, not evidence that all 53 were rerun here.
The [three bounded owner query cases PASS](test-results/m1-query-runtime-0.3.0.md),
based on the supplied existing query results report correlated with diagnostic
session/UUIDs. Two column identities, distinct pages/full summary, observed type/
layer/attribute equality and passive omission are verified within that scope.
Changed-source stale rejection, TTL/restart, geometry and full M1 remain separate.
Evidence-only follow-ups run no developer tests. The batch does not repeat
accepted M0 or context correction tests and does not accept full M1.

The **0.5.0** M1 completion slice passes **56 distinct relevant portable checks**:
23 new completion cases, two new MCP cases and 31 relevant regression checks.
The scan/schema/profile/payload changed; these repetitions are justified.
[Commands and limits](test-results/m1-completion-portable-0.5.0.md). The full
historical M0 suite and accepted owner batches were not repeated. The
[remaining final Allplan gate](m1-final-batch.md) is separate and pending.

Developer commands:

The **0.4.0** resource-probe slice passes **12 targeted checks**, including eight
new tests and four existing checks relevant to changed validation/transport/
packaging. [Exact commands and evidence](test-results/m1-metadata-portable-0.4.0.md).
No historical full-suite or accepted owner batch was repeated. The updated CI
inventory has 61 distinct methods; this is inventory, not a local full run.
The [two metadata captures](m1-metadata-batch.md) subsequently PASS within their
bounded scope, with owner unchanged-column/build and restored passive-state
confirmation. [Runtime evidence](test-results/m1-metadata-runtime-0.4.0.md) is
separate from the automated checks. This evidence-only follow-up runs no tests
and rebuilds no archive.

```bash
uv sync --frozen
uv run --frozen python -m unittest discover -s tests -v
uv build
uv run --frozen python utils/build_windows_package.py
```

A restricted Codex executor needs loopback socket access for transport checks and a writable uv cache (`--cache-dir /tmp/allplan-uv-cache` was used here). No test imports a real Allplan installation or needs model access.

Portable coverage:

- Real temporary-folder installation from source and extracted ZIP: complete `sandbox`, cache exclusion, redirected/custom paths, repeat installation, stale-file removal, backup restoration, missing/corrupt packages and rollback on copy failure.
- Package integrity: payload SHA-256 manifest, missing/extra/tampered files, backup integrity and deterministic archive bytes for the same source state. Timestamps and entry order are fixed. Manifest `source_modified` makes uncommitted builds explicit; hashes identify the exact payload. Dependencies are obtained from the lock during setup; this is not an offline or bundled-runtime installer.
- Codex setup: preserve existing TOML, create a backup, avoid duplicate entries and reject conflicting configuration without overwriting it.
- Live loopback HTTP bridge: JSON validation, request IDs, dispatch through a supplied callback, nonblocking cancellation with a request queued behind a simulated UI dispatcher, suppression of that cancelled operation, same-port restart and idempotent shutdown.
- Fake Allplan adapters: correct dimension forwarding, current-document resolution per request, wrong-major rejection, missing session, disabled execution and honest missing hotfix fields. These checks do not demonstrate native geometry correctness, actual API signatures or UI behavior.
- A real FastMCP 3.2.4 Streamable HTTP subprocess connected through the FastMCP client to a fake bridge: discovery, resources, health, version, names, exactly one forwarded box request, diagnostics and stopped-host errors. This is protocol evidence, not a Codex-in-Allplan acceptance result.
- Client error categorization: distinguish host absence from unknown execution after a timeout, preserve request IDs, reject nonfinite JSON, and never retry writes automatically.

`uv build` checks wheel/sdist construction. The ZIP builder uses explicit payload directories; it excludes runtimes, caches, credentials, logs and Git internals. The pure-Python wheel contains the external MCP server and bundled skills. The separate evaluation ZIP also contains the host, installer, launcher, docs and draft profile.

The owner runs no developer commands. [UAT-00 / UAT-01](m0-acceptance-batch.md) supplies UI steps, exact prompts, reset instructions and a result form. The owner subsequently confirmed UAT-00/UAT-01 on Allplan 2026-1-7 with package 0.1.2; see [M0 acceptance](test-results/m0-acceptance-0.1.2.md). Windows installation/connection, UI lifecycle and visible box dimensions are accepted for that setup. The in-flight race remains portable-probe evidence and GitHub Actions execution is not claimed.
