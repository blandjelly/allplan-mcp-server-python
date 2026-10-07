# Compatibility and evidence

Package **0.1.2 evaluation**, **accepted_on_build: Allplan 2026-1-7** on the
owner's Windows setup with local Codex. UAT-00 and UAT-01 PASS; M0 is closed.
[Acceptance record and exact artifact](test-results/m0-acceptance-0.1.2.md).
This is evidence for the tested setup, not every Allplan 2026 hotfix or client.

Current package **0.2.1** continues the read-only M1.1 context probe. **31 portable
tests pass**. Owner 0.2.0 logs verify loaded-file states/passive inclusion and
model/view GUIDs; project lookup fails. The **0.2.1 correction batch PASS** verifies
project lookup, unload exclusion and project switching; owner confirms matching
names and unchanged model. Full M1 acceptance remains pending.
Accepted 0.1.2 evidence does not automatically accept the new package.
[Current runtime evidence](test-results/m1-context-runtime-0.2.1.md).

| Capability | Evidence | Limit |
| --- | --- | --- |
| Complete host installation / repeat install / restore | Recursive installer and rollback/migration/restore pass portable tests; actual Windows installation/startup accepted | Restore logic is portable-tested; no separate owner Windows restore case was required or reported. |
| Windows setup / launcher / Codex configuration | Owner installation and local Windows Codex connection accepted | Codex app and Windows version not supplied. |
| FastMCP Streamable HTTP / baseline tools | Real Windows diagnostic and Codex calls accepted; FastMCP 3.2.4 | Bundled skill resources have portable protocol evidence; no separate owner skill-reading test is claimed. |
| Allplan release information | Real host reports API release 2026.1; owner UI reports 2026-1-7 | Full hotfix is UI-reported, not inferred from API release strings. |
| Executable version probe | Observed file version 16.1617.8659.814 and product version 2026.0.1.0 | Numeric metadata is retained literally; no hotfix mapping is assumed. |
| Separate Python runtimes | Observed external 3.14.8 / embedded CPython 3.13.13 on Windows | Portable Linux run uses 3.12.14. No FastMCP dependencies are installed into Allplan. |
| Names / baseline generic box | Local Codex calls and owner UAT accepted; 1000 mm box checked by owner | Names are not stable model identity. Box has no automatic readback or durable deduplication; inspect before retrying. |
| ESC/restart, minimize/restore, project switching | Owner confirms all requested UI tests; logs prove host absence and restart with a new session ID | In-flight queued-request rejection is portable simulated-dispatch evidence only. Closing the listener does not undo a running write. |
| Development Python execution | Opt-in on both sides; absent from evaluation catalog | AST filtering is not isolation. No tunnel/shared setup support. |
| Context workflow tool | 0.2.1 bounded runtime batch PASS: project lookup/switch, loaded file states, unload exclusion and model/view GUIDs; 31 portable tests pass | Raw zero offset only; unit/offset normalization, levels, durable references and component counts pending. |
| Remaining workflow tools / active demo profile | Planned only | M1.2–M7 pending; draft profile unbound and inactive. |
| Claude / cloud-to-Windows connection | Not tested / not provided | Accepted first client is local Windows Codex. Cloud localhost is another machine. |

This evaluation rejects model operations outside major 2026 while allowing
read-only diagnostics. Its static `runtime_verified: false` and
`allplan_acceptance: not_run` diagnostic fields predate acceptance and are not a
live acceptance registry; the dated acceptance record identifies the tested build.
Official version API: [AllplanVersion, 2026](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_AllplanSettings/AllplanVersion/).

Provenance inspected on 2026-10-07: [fork](https://github.com/blandjelly/allplan-mcp-server-python)
and [upstream](https://github.com/AlejoDuarte23/allplan-mcp-server-python). Neither
reports a license or has a root LICENSE. No license was added or inferred.
Public redistribution remains unresolved. No GitHub release is published by
this task. GitHub Actions matrix execution is not claimed; local portable checks
and owner runtime evidence are recorded separately.
