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

## Current M1 implementation and next action

**M1 in progress**, current package **0.3.0** scope/query slice. Work started from
current `origin/main` **d8bd1ef8388daa956e8b51863b17ac33d784dca9**, preserving
accepted evidence and original archive hashes. The **0.2.1** context/identity probe
and its accepted reader correction are reused.
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

No repeat of the correction batch is needed.

| Task | 0.3.0 state | Evidence / remaining scope |
| --- | --- | --- |
| M1.1 | Partial implementation | Explicit scope/identity/completeness contracts; session-bound model/type references, passive sign handling, missing identity exclusion. Geometry units/offset normalization, levels, durable refs and writability still pending. |
| M1.2 | Bounded runtime batch PASS; task remains partial | Two native column identities, passive scope, observed type GUID/layer and raw attribute 498 equality pass. Other predicate combinations have portable evidence only. Geometry/spatial/native hierarchy coverage pending. |
| M1.3 | Unchanged-source paging/full summary PASS; task remains partial | Two distinct pages and full cached selection summary pass. Changed-source staleness, TTL/eviction/restart and limits remain portable-only. No downstream audit/edit consumer or persistence yet. |
| M1.4 | Pending | Needs actual attribute/layer/type metadata and schema validation. No profile activation or final fixture claimed. |

**24 relevant portable checks PASS** on Linux/Python 3.12.14/FastMCP 3.2.4:
21 new query contract/fake-adapter checks, one new real MCP transport check,
and two package/version checks. Wheel/sdist and deterministic evaluation ZIP
build succeed. The full historical M0 suite was not rerun; a discovery import
initially repeated 11 handler checks and was corrected to avoid duplicate CI
discovery. Windows/CI automated execution is not claimed by that portable report;
owner Allplan evidence is recorded separately below.
[Portable report](test-results/m1-query-portable-0.3.0.md).

**Three bounded 0.3.0 owner query cases PASS**. The supplied query results report
matches the diagnostics' host session and column model/view UUIDs: two matched
identities, two distinct pages, full summary by file/type, exact type/layer and
raw attribute 498 predicates, and explicit passive-file omission with incomplete
requested scope. Native type Column_TypeUUID/GUID and layer 3736 are observed.
Attribute 498 is observed on file 1 and returned missing on passive file 2;
do not infer a bound mark or native absence under every access state.
The report states no model changes; independent geometry/visual readback is not
claimed. Static runtime_verified=false is not an acceptance registry.
[0.3.0 runtime record](test-results/m1-query-runtime-0.3.0.md).

Next: prepare focused metadata/passive-attribute, geometry/unit/offset and
parent/child counting probes. Do not repeat the passed
[0.3.0 query batch](m1-query-batch.md) without a relevant change or defect. Complete
M1.4 binding from verified resources before the six-column/ten-component UAT.
The demo profile remains **unbound and inactive**; **M1 is not accepted**.
