# M0 portable validation — 0.1.1 evaluation

Superseded installation layout: owner UAT-00 was blocked because the PYP target
was outside Library. These original portable tests missed that destination
defect. See [the 0.1.2 correction and owner observation](m0-library-fix-0.1.2.md).

Date: 2026-10-07. Tasks: M0.1–M0.5. Source baseline: `f98bef8a2fc030216408b2b7dbbba1ce02684f9f` plus the M0 working-tree implementation; the package manifest explicitly records modified sources. No GitHub release or Allplan acceptance is implied.

Environment: Linux, Python 3.12.14 (external), FastMCP 3.2.4, uv 0.12.19. The executor granted loopback/network access for live HTTP checks and dependency/build operations. uv cache: `/tmp/allplan-uv-cache`.

| Check | Actual result |
| --- | --- |
| `uv lock` / `uv sync --frozen` | PASS. Lock updated only the local package version to 0.1.1; external dependencies remain pinned. |
| `.venv/bin/python -m unittest discover -s tests -v` | PASS: **24 tests**, final run 3.065 seconds. |
| `.venv/bin/python -m compileall -q src python_host utils windows tests` | PASS. This does not import or execute Allplan APIs. |
| `git diff --check` | PASS. |
| `uv build --cache-dir /tmp/allplan-uv-cache` | PASS: 0.1.1 wheel and source distribution built. |
| Windows ZIP builder | PASS through automated byte-for-byte repeat-build, manifest/integrity verification and installation from extracted payload. Final deliverable generated separately after this report. |
| Real Streamable HTTP smoke test | PASS using FastMCP client/server and a fake bridge. Five default tools, skill resource index, health/version/names, exactly one forwarded 1000 mm box request, read-only diagnostics and readable stopped-host failure checked. |
| HTTP cancellation/restart probe | PASS with a request waiting behind a simulated UI dispatcher: stop returns without waiting for that callback; the queued request is rejected; the same port restarts. |
| GitHub Actions / Windows CI matrix | NOT_RUN here. Workflow prepared for Linux/Windows, Python 3.11–3.13. |
| UAT-00 / UAT-01 in Allplan and Codex | **NOT_RUN**. Windows installation, native UI dispatch/lifecycle, visible box size, current project behavior and real version/build remain pending. |

Installation coverage includes the previously omitted imported `sandbox` package, cache exclusion, custom/redirected path, repeat install and obsolete files, exact version metadata, restore after clean or repeat installation, integrity failure before changes, verified backups and rollback after simulated copy failure. Runtime diagnostics checks actual installed bridge hashes and reports modified or missing metadata explicitly.

Categorized errors retain request IDs. Timeouts/lost responses leave execution unknown; the baseline geometry tools do not retry or promise durable deduplication. Box responses now use `submitted: true` and `readback_verified: false` instead of claiming observed creation. Default development execution is disabled on both bridge and MCP; this acceptance batch uses typed handlers only.

The ZIP is a source-only local evaluation artifact with pinned dependency setup, no bundled runtimes and unresolved upstream licensing. Its manifest hashes and adjacent `.zip.sha256` identify the exact payload. Linux fake-adapter/protocol evidence is separate from Allplan acceptance.

Next action: the owner follows [Windows setup](../windows-setup.md) and [the two-case acceptance batch](../m0-acceptance-batch.md), then returns the Diagnostics reports and visible observations. Record the exact package checksum, actual build/hotfix and Codex version when that result arrives; keep M0's integrated exit gate pending until then.
