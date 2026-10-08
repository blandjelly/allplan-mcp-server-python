# Compatibility and evidence

Package **0.1.2 evaluation**, **accepted_on_build: Allplan 2026-1-7** on the
owner's Windows setup with local Codex. UAT-00 and UAT-01 PASS; M0 is closed.
[Acceptance record and exact artifact](test-results/m0-acceptance-0.1.2.md).
This is evidence for the tested setup, not every Allplan 2026 hotfix or client.

Current package **0.5.3** includes the bounded M1 read contract implemented in 0.5.0
and the observed native-family correction.
**56 targeted portable checks PASS; final Allplan exit gate pending**.
[Completion evidence](test-results/m1-completion-portable-0.5.0.md),
[final card](m1-final-batch.md). Fake geometry does not accept native coordinates
or offset conventions. Named demo resources bind for reads after UI setup;
write eligibility remains not_checked.

Earlier package **0.4.0** adds bounded attribute/layer metadata and full-response
capture, with **12 targeted portable checks PASS; bounded owner batch PASS**.
[Runtime evidence](test-results/m1-metadata-runtime-0.4.0.md) verifies raw resource
reads and the observed active/passive comparison on the two-column scene.
[New evidence](test-results/m1-metadata-portable-0.4.0.md) and
[owner card](m1-metadata-batch.md). No broader build support or profile activation
is inferred from fake resources.

Earlier package **0.3.0** adds the read-only scope/query/selection slice, with
**24 relevant portable checks PASS and three bounded owner query cases PASS**.
[Query contract](tool-reference.md), [portable report](test-results/m1-query-portable-0.3.0.md).
Owner supplied three diagnostics and a query results report, correlated by host
session and model/view UUIDs. Scope, metadata, pages/full summary and observed-
value predicates pass on the two-column scene. The report states no model edits;
independent geometry/visual readback is not claimed.
[Runtime evidence and limits](test-results/m1-query-runtime-0.3.0.md).
The **0.2.1** context correction remains accepted. Its **31 portable tests pass**.
Owner 0.2.0 logs verify loaded-file states/passive inclusion and
model/view GUIDs; project lookup fails. The **0.2.1 correction batch PASS** verifies
project lookup, unload exclusion and project switching; owner confirms matching
names and unchanged model. Full M1 acceptance remains pending.
Accepted 0.1.2 evidence does not automatically accept the new package.
[Current runtime evidence](test-results/m1-context-runtime-0.2.1.md).

| Capability | Evidence | Limit |
| --- | --- | --- |
| M1 dimensional/AABB/frame queries | 0.5.0 portable contracts/native-reader checks and 2026 signatures; 0.5.3 native A/B read gates PASS | Owner confirms A beam/slab UI dimensions and unchanged appearance. B mm-to-metres display change preserves all canonical boxes/dimensions and result identities. Nonzero-offset C and final owner UI observations pending. BBoxes are broad phase and axis aligned, not native rotated cross-sections or exact solid intersections. |
| M1 top-level native components | 0.5.0 parent-chain/cycle/scope checks; 0.5.3 observed-type fixture regressions | Six root types: original four plus SkeletonBeam and MultiSlab. Child axes/tiers map to roots; no arbitrary framing/group hierarchy support. 0.5.3 native ten-component count/read PASS for the bounded owner tree. Other hierarchy shapes remain unverified. |
| M1 demo read profile and configured levels | 0.5.0 schema and fresh resource round-trip checks, packaged template/UI recipe | 0.5.2 native read binding PASS for demo text attributes and owner layers. Profile-unbound errors block reads. Native BWS, writability, active repair/audit profile and full fixture acceptance pending. |
| Resource metadata inspection / captured query responses | 0.4.0 bounded Allplan batch PASS: complete inspect JSON, attribute 498 Nazwa obiektu with raw codes 67/69, layer 3736 AR_SŁUP, passive omission versus active Słup | Two known columns only; sessions also changed. No universal passive-access rule, normalized units, semantic binding or profile activation. |
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
| Read-only model_query / explicit scope / predicates | Bounded 0.3.0 owner batch PASS on two native columns: loaded/passive scope, type GUID/layer and raw attribute 498 equality | Other predicate combinations retain portable evidence. That 0.3.0 evidence does not accept the new 0.5.0 spatial/geometry/component readers. Passive attribute 498 returned missing; native absence is not established. |
| Reusable selections / paging / summary / staleness | Two distinct pages/full-selection summary and unchanged-source reuse PASS; other behaviors portable-tested | Changed-source stale rejection, TTL/eviction/restart and larger-model limits lack owner runtime evidence. Memory-only, read-only, field-bound references; no write authorization or downstream audit/edit consumer. |
| Remaining workflow tools / active demo profile | Planned only | M2–M7 pending; new M1 geometry/hierarchy/demo binding awaits its final runtime gate; no write profile is activated. |
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
