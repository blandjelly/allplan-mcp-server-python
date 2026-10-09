# M3 plan invalidation after UI cancellation/restart — 0.8.1

Recorded **2026-10-10 Europe/Warsaw**. First capture: **00:35:48.998** local
(2026-10-09 22:35:48.998 UTC); second capture: **00:38:45.545** local
(22:38:45.545 UTC). The owner states that clicking in the UI interrupted the
host after the first test, the host was restarted before the second test, and
**the other columns remain unchanged**.

Decision: **PASS for native old-plan rejection after host restart**.
**BLOCKED for same-session manual-edit conflict**, because the UI interrupted
the host. No repeated attempt at that same-session scenario is requested on
this build. This result preserves the accepted
[two-target execution/Undo/recovery gate](m3-execution-acceptance-0.8.1.md).
M3/UAT-05/UAT-06 remain open; this capture does not execute stale Apply.

## Original evidence

All four uploaded files are preserved byte-for-byte in
[the evidence directory](evidence/m3-plan-restart-0.8.1-20261009T223548/).
[Original-file manifest](evidence/m3-plan-restart-0.8.1-20261009T223548/evidence-manifest.json)
and [independent verification](evidence/m3-plan-restart-0.8.1-20261009T223548/verification.json)
record the following:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| allplan_readonly_preview.json | 22990 | `fcd317458ae4427c3d8451045be2379ee42e57823fb666f2c460ffe7baf1ec50` |
| allplan_readonly_preview.txt | 555 | `dafd46446bac46fa9b1e03a4cdc30b38f74592bd1f1cc81d153fe3a54ac19e8a` |
| allplan_revalidate_after_manual_change.json | 9170 | `5e5669bc0129437ba1c8bf55f3974c1283d7d86243bba7e21b9cb89ca4fcd6f2` |
| allplan_revalidate_after_manual_change.txt | 846 | `0d53d1692b7e42ba0f51b4a2d3374cb7589cd36e2134d6569099f8afc18a4567` |

Both health responses report **0.8.1**, installed integrity verified without
mismatches, clean source `8074905536ff5c95e20de4a59a70d513f8694314`.
All **22 bridge hashes in each session** independently match the unchanged
[0.8.1 Windows ZIP](../../evaluation-packages/0.8.1/README.md), SHA-256
`b31909379244cc085168cc1b5283fa08284954f19334261779ea766fbbf36c47`.
API 2026.1, embedded Python 3.13.13, external Python 3.14.8, executable
file/product resources 16.1617.8659.814 / 2026.0.1.0. No new UI version claim.

Successful MCP text content parses to exactly the stored structured content;
TXT identifiers/outcomes agree with JSON. The plan hash independently recomputes
using the owner-card preview request and bundled audit profile. The original
expanded request and full model audit are not directly included in these files;
the verification records that reconstruction rather than claiming their capture.

## What the two captures establish

Plan ID: `500b57e169df4a6d99e982d413282542`.
Plan hash: `8687e394b90923fd99ca666fdc3f3ee588fe92dec7b5effdd483e16268dfa420`.

| Capture | Host session | Result |
| --- | --- | --- |
| Preview and immediate revalidation | `fdca1b5c-b147-4ac4-9c9e-4019eda2203b` | preview_ready; 0 changes, 3 excluded findings, 3 audit findings; complete coverage; read_only=true; revalidate unchanged/source_unchanged=true, 296 seconds left |
| After UI cancellation and restart | `22d3d4d9-7334-4260-9126-97960bffb6fc` | health OK; same_host_session=false; old plan revalidation returns plan_expired |

The first plan proposes no writes: no findings match the selected layer/status
repairs, consistent with the previously repaired fixture. It does not separately
return S06's exact current value. Revalidation retains its source/audit fingerprints. General and
evaluation apply availability are false for this zero-change plan.

The second file retains the exact first plan ID/hash/session. Its revalidation
error is:

```text
Plan expired, was evicted or belongs to another host session. Preview again.
[code=plan_expired, request_id=b08304cb-6028-4c8b-b204-4716c0331fca]
```

The tool error has no structured `conflict`, `source_unchanged` or `read_only`
fields; do not invent them. The native handler checks its session-local plan
cache before rereading the audit. The differing sessions and owner-confirmed
restart account for the absent plan; this is not proof of TTL expiry or a
same-session source comparison. Requests in the supplied result capture are
health, preview and revalidate; no Apply or Recover result is present.

## Host lifecycle, owner observations and next boundary

`StartPythonHost.py` starts an interactive PythonPart. Its cancellation callback
stops the bridge, closes the palette and stops the dispatcher timer. A fresh
RequestHandler creates a new RepairPlanService with an empty plan cache.
The owner-observed UI interruption is consistent with that supported lifecycle;
these files do not contain a callback trace proving which native UI event fired.
Do not keep the previous plan alive, persist/re-authorize it, or reuse native
adapters across restart to make a same-session test appear to pass.

The owner confirms other columns are unchanged, adding a UI observation for
the retained fixture. The log filenames describe a manual-change test, but
neither capture reads S06 after the UI action or proves that it was restored
to NEW. No post-edit model audit or whole-model property proof is supplied.
No additional manual edit/restoration is inferred from the filename.

Next native boundary: [stale Apply rejection after restart](../m3-stale-apply-batch.md).
Use the current installed 0.8.1 and same disposable copy, without UI editing,
new preview or new repair. Retain the expired plan ID/hash; save a fresh
execution ID before sending a single Apply request, expecting
`rejected / native_setters_started=false / plan_expired`. Fresh complete audits
before/after must match. This tests the mutation entry point's refusal in the
supported restarted-host workflow, rather than repeating the blocked UI test.
Unknown outcomes, grouped Undo, wider writes and M3.3 retain their separate gates.
