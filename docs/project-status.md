# Project status

Updated: 2026-10-07. **M0 CLOSED**, accepted on **Allplan 2026-1-7**, package
**0.1.2 evaluation**. **UAT-00 PASS; UAT-01 PASS**. The owner confirmed all
remaining tests work correctly. [Acceptance and evidence](test-results/m0-acceptance-0.1.2.md).

## Baseline and tested environment

- Fork: `blandjelly/allplan-mcp-server-python`; upstream: `AlejoDuarte23/allplan-mcp-server-python`. Implementation baseline `f98bef8a2fc030216408b2b7dbbba1ce02684f9f`; initial checkout fast-forwarded without discarding owner edits. No applicable AGENTS.md found.
- Owner Windows setup: Allplan UI build **2026-1-7**, API release **2026.1**, embedded CPython **3.13.13**, external Python **3.14.8**, local Windows Codex app. App/Windows version and project/file names not supplied.
- Portable validation: Linux, external Python **3.12.14**, FastMCP **3.2.4**, uv **0.12.19**; **25 tests passed**, wheel/sdist and ZIP built/verified. GitHub Actions matrix not executed here.
- Exact accepted archive and SHA-256 are recorded in the acceptance report. The original ZIP is unchanged; later evidence/closure docs are separate. No release has been published.

## Completed tasks

| Task | Status | Evidence |
| --- | --- | --- |
| M0.1 | Complete | Fork/upstream, baseline and license inspected; external/embedded runtimes recorded separately. Full UI build reported by owner; release/executable metadata observed through host. |
| M0.2 | Complete | Recursive registration, caches excluded, custom/redirected folder support, repeat install, version/integrity, backups, restore and rollback tested. Library-path defect in 0.1.1 fixed and accepted in 0.1.2. |
| M0.3 | Complete | Health/version/names and box called through local Windows Codex. Categorized errors and stopped-host recovery verified. Development execution disabled by default; docs reconciled. |
| M0.4 | Complete for tested setup | Owner confirms ESC/restart, minimize/restore and project switching. Logs prove stopped-host failure and a new host session. Portable queued-request cancellation probe retains UI dispatch without UI joins. |
| M0.5 | Complete | Versioned evaluation package, launcher, Codex setup, read-only diagnostics, restore instructions and portable checks delivered. Owner acceptance recorded. |

The integrated M0 exit gate is met. Automatic box readback and durable deduplication
are not implemented. The in-flight race is portable-probe evidence, separate from
owner UI tests. License/public redistribution remains unresolved; neither fork
nor upstream reports a license and none was invented. [Support matrix](support-matrix.md).

## Next concrete action

**M1 STARTED — M1.1 in progress**, current package **0.2.1** context/identity probe.
`get_model_context` is implemented as a bounded read-only probe; project/file
states, units, raw offset and optional model/view identity sampling are included
in diagnostics. **31 portable tests pass**. Owner 0.2.0 logs verify file-state
reads, passive inclusion and separate model/view GUIDs, but project lookup fails.
[Runtime findings and correction](test-results/m1-context-runtime-0.2.0.md).
**0.2.1 context correction batch PASS**: project names/keys resolved, file 2
excluded after unload, project switch reflected, readable separate model/view
GUIDs. Owner confirms names match and model unchanged.
[0.2.1 runtime evidence](test-results/m1-context-runtime-0.2.1.md).
[Implementation and limits](test-results/m1-context-probe-0.2.0.md).

No repeat of the correction batch is needed. Next: finish
scope/unit/offset/identity contracts and implement M1.2–M1.3 query predicates and
reusable paginated selections. M1.4 profile binding requires actual metadata.
The demo profile remains **unbound and inactive**; M1 is not accepted.
