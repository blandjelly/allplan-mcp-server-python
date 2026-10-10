# Validation status and limits

Current package **0.13.0**; status recorded **2026-10-10 Europe/Warsaw**.
Its [same-session conflict gate](m3-conflict-owner-test.md) is
**ready_for_owner_test** and has no native acceptance yet. It preserves invalidated
plans for one read-only source comparison, never restoring authorization.
Partial/unknown native recovery remains a separate subsequent gate.
Mark assignment and deterministic numbering have **bounded two-target native PASS**;
[0.12.0 acceptance/evidence](m3-numbering-acceptance-0.12.0.md). Native acceptance
below remains scoped to its recorded packages, fixture and supported behaviors.
Native acceptance concerns the retained disposable fixture and observed Allplan
**2026-1-7** setup with local Windows Codex. It is separate from portable tests.
M3/UAT-05/UAT-06 and the first MVP remain open.

## Accepted baseline

| Stage | Accepted behavior | Boundary |
| --- | --- | --- |
| M0 / 0.1.2 | Install, integrity, backup/restore, correctly sized box, ESC/restart, minimize/restore, project switching; UAT-00/UAT-01 PASS | Baseline box tools lack automatic readback and durable write deduplication. |
| M1 / 0.5.3, profile 1.0.2 | UAT-02/UAT-03 PASS: fresh named read bindings, ten file-101 roots, passive 102, unloaded 103 omission, counts 10/6/2/1, geometry/hierarchy, display-unit invariance and XY offset once | Six columns, two SkeletonBeam roots, Wall and MultiSlab; offset (100000,200000,0) mm. Native BWS, arbitrary trees, nonzero Z offsets, durable references and generic write eligibility are unaccepted. |
| M2 / 0.6.1, audit profile 2.0.0 | UAT-04 PASS: six columns, five findings, one duplicate group, complete coverage; repeated audits, invalid public/host scope rejection and post-error health | Fixture file 101 only. Callback exceptions are contained; the precise earlier CLR crash cause remains unproven. Native log rotation and long-term/concurrent stability are unverified. |

Observed API release **2026.1**, executable file/product versions
**16.1617.8659.814 / 2026.0.1.0**, embedded CPython **3.13.13**, external
Python **3.14.8**. Executable strings do not independently identify the
owner-reported UI hotfix. Windows/Codex app versions remain unspecified.
Read profiles remain inactive for general writes. Static diagnostic flags
`runtime_verified=false` / `allplan_acceptance=not_run` are capture fields,
not a live acceptance registry.

## Accepted M3 slices

| Package | Native gate | Remaining boundary |
| --- | --- | --- |
| 0.7.0 | Explicit two-change layer/status preview, exact values/targets, unchanged revalidation and follow-up audit | Preview does not establish writable native properties. |
| 0.8.1 | Two layer/status writes, readback/full audited-field verification, exact-ID replay across host sessions, two separate Undo steps, recovery after owner-confirmed Redo | Recovery concerns a completed execution, not a native unknown outcome. Grouped Undo and whole-project verification are unaccepted. The earlier 0.8.0 rejection before setters used an overly broad IsInMacro check, corrected with root-hierarchy validation. |
| 0.8.1 restart/stale Apply | Old-plan revalidation returns plan_expired after UI cancellation/restart; stale Apply rejected before setters, identical full audits, unchanged owner-observed model | Same-session manual-edit conflict was blocked because UI ended the host; restart protection does not prove that case. |
| 0.9.0 | Three no-op standard/selection previews, exceptions, revalidations and identical full audits | Zero-proposal observations do not establish positive writes. |
| 0.10.0 | C03 → S03 / C04 → S04 mark proposals, selection exception, collision with excluded S06 peer, unchanged revalidations/audits; owner confirms unchanged model and uninterrupted host | All mark plans refuse Apply. Assignment, numbering and graphical labels are unimplemented. |
| 0.11.0 | Ten steps: two separately reviewed single-target standard/selected writes, exact readbacks, audited fields match plan, exact-ID read-only replays, complete six-column audits 5 → 4 → 3 in one verified host session | Owner confirms both changes, host survival, other elements unchanged and two-step Undo. Broader 1–32-change/other-file execution is unaccepted. Final repaired/undone/redone state was unspecified. |
| 0.12.0 | Two numbered mark writes on existing string attribute 5001, exact readback/audited verification, same-session unchanged deterministic previews, read-only replay and subsequent no-op; complete audits 3 → 0 → 3 after Undo/recovery | Owner confirms correct marks, unchanged other elements, host survival and two-step Undo. Recovery observes old values after a changed host session; it concerns completed execution, not unknown-outcome recovery. Broader mark/workflow scope is unaccepted. |

Final 0.11.0 findings: **QA-001 / QA-002 / QA-002**, with 24 checks:
20 pass, 3 fail, 1 not_applicable, 0 not_checked. Failure is expected because
mark issues remain. Native same-session conflicts, controlled partial/unknown
recovery, crash/power-loss durability and cross-copy identity remain open.
No unchanged accepted owner gate needs repetition.

## Portable verification and delivery

0.13.0 source **752e54795a1cfa676217b5ffba0ce5d301383269**: one full
**195-test PASS** on Linux CPython 3.12.14 after focused plan/HTTP checks.
Frozen sync and wheel/sdist build PASS. Exact extracted registration/restore
fixture PASS: all 23 bridge hashes match, the journal sentinel is preserved and
the previous bridge fixture is restored. Native Allplan and Windows Setup UI
were not run locally. [Exact 0.13.0 delivery](../evaluation-packages/0.13.0/README.md)
retains source/artifact identity and separate source-CI observations.
Invalidated evidence is covered for actual excluded-peer changes, old-value
restoration without renewed authorization, shared TTL/byte/count limits and
restart; HTTP checks cover cancellation, stale rejection, lost write/probe
replies, identity preservation and read-only recovery. Native acceptance is pending.
Source [CI 38079063575](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38079063575)
**6/6 PASS** on Windows/Ubuntu Python 3.11–3.13, including tests and builds;
[original job/step observations](../evaluation-packages/0.13.0/source-ci-0.13.0.json).


0.12.0 final implementation candidate: **187 portable tests PASS** on Linux
CPython 3.12; one full run after focused repair/mark and 26 HTTP/MCP checks.
Frozen dependency sync PASS. Coverage includes deterministic order/no-op,
excluded duplicate keepers and normalized reservations, pre-context policy
rejection, missing/unknown mark boundaries, fresh source conflicts, explicit
mark readback, durable replay after restart/Undo, stopped partial writes and
read-only recovery after a lost HTTP reply. These fakes do not execute Allplan.
Wheel/sdist build and exact extracted package/23 bridge hashes PASS;
Setup/Restore preserved the journal and restored the prior bridge in the fixture.
[0.12.0 delivery](../evaluation-packages/0.12.0/README.md) records the exact source,
artifact identity and six-configuration source CI. Old 0.11.0 evidence below
remains unchanged; no archives are rebuilt for publication.
Source **fd78700378eceb6f217e4ca30a83b88004b73a57**, source_modified=false;
[CI 38075847420](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38075847420)
**6/6 PASS** on Windows/Ubuntu Python 3.11–3.13, including tests, wheel/sdist and
Windows package builds. This code update exercises the revised PR/full-matrix
selection schedule; documentation publication runs no new checks/builds.

Delivered 0.11.0 source **26d70b27bd06e2916cda74213cb8995aa9f0f19a** has
**178 portable tests PASS**, frozen sync, wheel/sdist builds, deterministic ZIP
and extracted installation/integrity checks. Setup/Restore preserved the journal
in the portable fixture; all 22 registered bridge hashes matched.
[Source CI 38063710029](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38063710029)
passed **6/6** Windows/Ubuntu Python 3.11–3.13 jobs for that source.
The revised CI schedule from **1e36945** was not exercised by its documentation
update; the earlier result does not validate that workflow revision.

The [0.11.0 delivery](../evaluation-packages/0.11.0/README.md) and immutable
delivery manifests retain artifact identity. Documentation cleanup does not
rebuild existing archives; their embedded docs/launchers reflect original source.
New source packages use the current tree.

## Historical records

Completed test cards, raw JSON/TXT logs, prior handoffs and superseded reviews
are archived at documentation baseline
[5ec1f57](https://github.com/blandjelly/allplan-mcp-server-python/tree/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74).
[Original acceptance records](https://github.com/blandjelly/allplan-mcp-server-python/tree/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/docs/test-results)
retain exact evidence hashes and separately attributed owner observations.
[Original delivery records](https://github.com/blandjelly/allplan-mcp-server-python/tree/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/evaluation-packages)
retain removed build/test logs listed by historical delivery manifests.
These are reference evidence, not instructions to rerun old batches.
