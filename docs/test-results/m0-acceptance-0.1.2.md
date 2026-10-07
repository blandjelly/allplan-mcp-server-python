# M0 acceptance and closure — 0.1.2

Date: 2026-10-07. Status: **CLOSED — accepted_on_build: Allplan 2026-1-7**.
Task IDs: **M0.1–M0.5 complete**. **UAT-00 PASS; UAT-01 PASS**.

## Acceptance basis

The owner explicitly confirmed completion of all remaining tests and correct
behavior: “I completed all tests; everything works correctly. Can we close M0?”
This follows the uploaded Windows diagnostics, local Codex tool-call history and
previous confirmation of correct solid appearance and successful host restart.
The final confirmation covers the requested exact dimensions/count, ESC,
minimize/restore, project switching and test-fixture cleanup. These final UI
observations are owner-reported; no new machine-readable measurement or UI trace
was supplied. Automatic geometry readback is not claimed.

Accepted evaluation artifact: `allplan-mcp-0.1.2-windows-evaluation.zip`.
SHA-256: `d97b6761b13f8cd6e80c7954f1c91de513d4a813a5b236c6917b14b0882ac528`.
The archive is preserved unchanged; closure documentation added afterwards is not
part of its original payload. Its manifest records the baseline commit and
modified source payload. No GitHub release or public redistribution is implied.

| Check | Result / evidence |
| --- | --- |
| Installation and PythonHost startup | PASS on Windows after the 0.1.2 Library-path fix; installed bridge hashes verified in uploaded diagnostics. |
| Local Codex discovery and health/version/names | PASS; five intended tools, actual local MCP calls and successful diagnostics. |
| Known-sized generic solid | PASS; 1000 × 1000 × 1000 mm requested once per intentional test, owner confirms correct result/count. |
| Stopped-host error and recovery | PASS; uploaded `host_absent` report and readable StartPythonHost restart instruction. |
| ESC/cancel and restart | PASS; owner final confirmation plus before/after logs with distinct host-session IDs. |
| Minimize/restore | PASS; owner final confirmation. |
| Project switch/current session | PASS; owner final confirmation. |
| Fixture reset | Complete; covered by the owner's final confirmation of all requested steps. |
| Portable implementation checks | 25 tests passed; installation/migration/restore/integrity, live HTTP cancellation probe, fake adapters and real MCP transport. Wheel/sdist and evaluation ZIP built/checked. |

Observed setup: Allplan **2026-1-7** from the owner's UI; API release **2026.1**;
executable file/product versions **16.1617.8659.814 / 2026.0.1.0**; embedded
CPython **3.13.13**; external Python **3.14.8**; local Windows Codex app (app
version not supplied). Project/file names and Windows version were not supplied.
This acceptance applies to the tested setup, not every 2026 hotfix or client.

Linked evidence: [UAT-00](uat-00-local-codex-0.1.2.md),
[UAT-01 sequence and requests](uat-01-box-restart-0.1.2.md),
[portable 0.1.2 regression](m0-library-fix-0.1.2.md). Raw uploaded diagnostics
are retained under `evidence/`.

## Boundaries carried forward

The in-flight cancellation race has portable simulated-dispatch evidence; it was
not independently engineered inside Allplan. Baseline box tools have no automatic
readback or durable write deduplication. Release diagnostics' static
`runtime_verified: false` / `allplan_acceptance: not_run` fields predate this
acceptance and are not a live acceptance registry. Hotfix identification remains
UI-reported; executable version resources are recorded literally.

License/public redistribution remains unresolved; no license was invented.
GitHub Actions and the broader CI matrix were prepared but not run in this chat.
These are tracked limits, not outstanding owner tests for M0.

Next milestone: **M1 — context, identity, selection and query**. Start with M1.1:
portable contracts and host probes for model/session identity, loaded drawing-file
states, units and offset. The demo profile is still unbound/inactive; none of the
13 planned workflow tools is accepted by this baseline milestone.
