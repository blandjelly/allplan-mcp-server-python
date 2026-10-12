# Bounded selected-mark and journal acceptance — 0.15.0

**PASS / accepted_on_build, 2026-10-12 Europe/Warsaw**, for the retained
Allplan fixture previously identified as **2026-1-7**. Runtime observations
remain API 2026.1, executable file/product 16.1617.8659.814 / 2026.0.1.0,
embedded CPython 3.13.13 and external Python 3.14.8. Executable strings do not
independently identify the UI hotfix. The owner confirms UI results match the
walkthrough in A and B, and the host was uninterrupted in A.
**M3/UAT-05/UAT-06 and the first MVP remain open.**

## Selected write and Undo observations

All **13/13 A + 6/6 B** steps pass. Execution
`b5b397c7f7134b27b9304259e53e6bc4` uses the reviewed and freshly revalidated
rule_based_edit plan `c292745b598f4adb8c7933bd9fca66a0`.
Its sole change replaces C04's existing string mark attribute **5001**,
**S02 → S04**, at center (0,6000,1500) mm in foreground file 101.
C04 model UUID is `4f3cc27e-5224-403d-939d-7b4e0cedf9a2`.

The mark=S02 predicate selects C04 while C02
`80211557-a3c1-4ccd-84d9-1274ec533776` is explicitly excluded. Selection counts
are one selected, one excluded, four predicate-false and zero unchecked.
Collision validation inspects all six columns, reports no proposed collisions
and retains C03's missing mark. The two excluded findings have reasons
rule_not_selected (C03) and mark_target_not_selected (C02); the explicit UUID
exception is separately recorded in selection metadata/counts.

Preview leaves the complete snapshot unchanged. Apply completes with one
applied outcome/readback S04 and audited_fields_match_plan=true. Exact-ID
replay returns historical outcomes read-only. Independent full-snapshot
comparison shows only C04's mark alias and attribute:5001 changing; C02 remains
S02 and other audited fields/columns match the baseline. Full audits have
**3 → 1 → 3** findings, six columns and zero unchecked checks. After the write,
the sole finding is C03's missing mark; an audit state of fail is expected.

In B, read-only Recover uses the same execution ID and observes the old C04
value **S02**. The entire six-column snapshot equals the baseline after omitting
only query_session_id from references. No B request sends Apply. Historical
applied/readback S04 remains in the completed execution; it does not claim
current S04 after Undo. The final pointer is **undo_checked**, and latest and
per-execution JSON/TXT copies match. The owner's B confirmation and restored
snapshot support the walkthrough's single Undo within this bounded scope.

## Journal and sessions

Journal inspection reports **6 → 7 → 7** verified records, **122 → 121 → 121**
remaining slots, no blockers and complete inventory within the 128-record limit.
Responses declare read_only=true, native_model_access=false and
records_modified=false. The new entry matches the execution/plan IDs and hash,
completed state and one historical applied outcome. All reported journal
summaries after the write remain identical after Undo.
This verifies the healthy installed journal inspection in this fixture; no
standalone native journal file was uploaded. It does not establish native
capacity, corruption, unresolved-record handling, pruning or migration behavior.

| Phase | Host session |
| --- | --- |
| A — preview/write/replay/journal | fcf043b3-f963-4da0-997b-360754fbc0a3 |
| B — Undo inspection | 3fea2376-1758-4f51-b56b-aa34f25288fa |

Sessions are stable within each phase. B uses another session; its cause was
not specified. Owner-confirmed uninterrupted host life concerns A only; do not
infer uninterrupted operation across Undo.

## Evidence, publication and stop point

[Eight original uploads](../evaluation-packages/0.15.0/native-acceptance/20261012-owner/),
[upload sizes/hashes](../evaluation-packages/0.15.0/native-acceptance/20261012-owner/uploads-manifest.json)
and [independent inspection](../evaluation-packages/0.15.0/native-acceptance/20261012-owner/inspection.json)
retain reports and pointer copies byte-for-byte. Review recomputed the plan
hash, workflow Apply request hash and five audit hashes; compared all 19 MCP
text responses with structured data; independently compared full snapshots;
and matched all 23 reported bridge hashes against the delivered manifest.
Observed source/package: **7e3657bc33ecf913376d302da900af386b3b8a23 / 0.15.0**.
The existing delivery's 219-test and 6/6 CI results keep their original scope.

Delivered ZIP, wheel, checksum, delivery record, embedded instructions and
original local/CI verification logs remain unchanged. This update performs
only evidence review, documentation/link/diff checks and publication; no
runtime tests, builds or old archive checksum reruns.

Leave/save the same original copy after Undo: C04/C02=S02, C03 undefined,
C05 structure and C06 NEW retained. Preserve package logs, installed
Local/.allplan-mcp/repairs and the saved execution identity. No Redo, repeat
writing gate or additional owner batch is requested. **Further implementation,
new tests and main integration are paused at the owner's explicit request.**
Broader 1–32-change scope, manual UI active-plan conflict, cross-copy identity,
crash/power-loss durability, grouped Undo and journal rollover remain unaccepted.
