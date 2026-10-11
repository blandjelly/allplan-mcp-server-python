# Bounded controlled recovery acceptance — 0.14.1

**PASS / accepted_on_build, 2026-10-12 Europe/Warsaw**, in the retained
Allplan fixture previously identified by the owner as 2026-1-7. Runtime reports
API 2026.1, executable file/product 16.1617.8659.814 / 2026.0.1.0 and embedded
CPython 3.13.13. Owner confirms that the walkthrough worked in the UI, no other
changes occurred and Undo worked. M3/UAT-05/UAT-06 remain open.

## Recorded observations

All **13/13 + 6/6 + 6/6** steps passed. Execution
`d8a1baca4f7e487395af40119a386586` used the reviewed, freshly revalidated
C03/C04 numbering plan and the explicit controlled-stop acknowledgement.
Only C03's existing string mark attribute 5001 changed from
`<niezdefiniowany>` to `S03`. The gate returned before readback/second setter,
with the actual **running / unknown, skipped** result. Diagnostic metadata
identifies a controlled interruption, not a native crash. Exact-ID replay
returned that history read-only. Separate identity
`40ba179b95b840238d4ebfe8a061ee75` was rejected before setters with
`repair_recovery_required`. C04 and C02 remained S02.

After host restart, read-only Recover changed the record to **stopped**, with
**reconciled / new_value_observed** for C03 and **skipped / old_value_observed**
for C04. Exact-ID replay did not resume the skipped target. Full six-column
field snapshots show only the authorized C03 mark change: status, layer,
file state, geometry and other columns match the baseline.

After the owner's Undo, Recover observed **old_value_observed** for both
changes. The final complete snapshot equals the original baseline after
omitting only the fresh query-session reference ID. Six-column complete audits
have **3 → 2 → 3** findings and zero unchecked inputs. The final saved pointer
is **undo_checked**; its latest and per-execution JSON/TXT copies agree.
Reconciled outcomes remain historical after Undo; they do not claim current S03.

Host sessions were stable within each phase:

| Phase | Host session |
| --- | --- |
| A, controlled write | 45d7bfab-6b30-4140-bcb1-b1254480ba5e |
| B, restart inspection | a3b0cfec-8571-4abf-a439-3fd62ba92ddd |
| C, Undo inspection | 95772e5b-4c28-4123-aeb3-313416d3c962 |

Part B verifies a different session from Part A. Part C also used another
session; its cause was not specified. Successful health checks establish the
reported sessions within each phase, without inferring uninterrupted host life
across Undo.

## Evidence and limits

[Ten original uploads](../evaluation-packages/0.14.1/native-acceptance/20261012-owner/),
[upload sizes/hashes](../evaluation-packages/0.14.1/native-acceptance/20261012-owner/uploads-manifest.json)
and [inspection](../evaluation-packages/0.14.1/native-acceptance/20261012-owner/inspection.json)
retain the three phase reports and both execution pointers byte-for-byte.
MCP text matches structured responses and human-readable reports. Evidence
inspection recomputed the plan hash, Apply request hash and seven audit-report
hashes, independently compared complete field snapshots and matched all 23
reported bridge hashes to the delivered manifest. Verified package/source:
**0.14.1 / 1810e4fa284311e204b9133deee3245f8427697b**.
Original [delivery records](../evaluation-packages/0.14.1/README.md), archives,
logs and embedded owner instructions remain unchanged; their pre-test status
is historical. No runtime tests, builds or archive checksum reruns were needed.

Acceptance covers this controlled interruption after one setter, restart,
read-only reconciliation/replay and Undo in the original copy. It does not
establish native exceptions, process crash/power-loss durability, grouped
multiple-write Undo, cross-copy identity, manual UI active-plan conflict or
broader write scope. The earlier 0.14.0 pre-Apply block remains recorded
separately; it does not invalidate this corrected gate.

## Preserve the project

Leave and save the same disposable project **after Undo**: C03 undefined,
C04/C02=S02; C05 structure and C06 NEW retained. Preserve logs and
`Local/.allplan-mcp/repairs`. No Redo or repeated writing gate. No repeat of
this completed test is required. Remaining work concerns declared-scope
acceptance, journal/identity limits, final UAT and draft integration into main.
