# Bounded M3 Conflict acceptance — 0.13.0

**PASS, 2026-10-11 Europe/Warsaw**, in the retained disposable Allplan 2026-1-7 fixture.
Owner confirms correct UI values, unchanged other elements, no host interruption
and restoration of the changes in one Undo. M3/UAT-05/UAT-06 remain open.

## Recorded observations

All **12/12** launcher steps passed. Two selected immutable previews were created
without changing the model. Execution `dffa3c94da434fddbda4cf146e18ef96`
completed one existing string attribute 5001 write on C03:
`<niezdefiniowany>` → `S03`, with exact readback and full audited-field verification.
Six-column complete audits changed **3 → 2** findings; C04 and C02 stayed S02.
The separate stale C04 Apply was rejected with `plan_expired` before native setters.
Read-only revalidation of retained C04 evidence reported both execution invalidation
and an actual changed source/report caused by the excluded C03 peer. Apply remained
unavailable. The post-rejection full audit matched the post-write audit.

The gate used one host session `6ad09618-52c5-4054-b2ca-37063f2d3211` throughout.
Read-only Recover after owner Undo observed C03's old value, with **3** findings
again and all audited checks matching the original snapshot after excluding only
fresh query-session reference IDs. Recover used another host session
`651e561c-3771-4096-a0f9-327057dc04c0`; its cause is not inferred.
Historical completed/applied journal outcomes remain historical after Undo.

This gate contains **one setter**. One Undo confirms that case; it does not establish
grouped Undo for multiple writes or change the earlier 0.12.0 two-step Undo evidence.
This is controlled typed source mutation and completed-execution recovery, not
manual UI conflict on an active plan or native partial/unknown recovery.

## Evidence and inspection

[Original eight uploads](../evaluation-packages/0.13.0/native-acceptance/20261011-owner/),
[upload sizes/hashes](../evaluation-packages/0.13.0/native-acceptance/20261011-owner/uploads-manifest.json)
and [inspection](../evaluation-packages/0.13.0/native-acceptance/20261011-owner/inspection.json)
retain the check, execution identity pointers and Recover JSON/TXT byte-for-byte.
MCP text agrees with structured responses; human reports agree with gate steps.
New evidence inspection recomputed both plan hashes, the Apply request hash and
five audit-report hashes, and matched the 23 reported bridge hashes to the existing
delivered manifest. Package/source identity is 0.13.0 /
`752e54795a1cfa676217b5ffba0ce5d301383269`, installed integrity verified.
Runtime reports API 2026.1, file/product 16.1617.8659.814 / 2026.0.1.0,
embedded CPython 3.13.13. No runtime tests, builds or old archive checks were repeated.
Original delivery records, archives and embedded owner instructions remain unchanged;
their pre-test status is historical. [Delivery](../evaluation-packages/0.13.0/README.md).

## Preserve the project

Leave and save the same disposable project **after Undo**: C03 undefined,
C04/C02=S02; retain C05's structure layer and C06=NEW. No Redo or new Apply.
Preserve logs and `Local/.allplan-mcp/repairs` with the original copy.
No repeat of this completed gate is required. Next prepare the separately reviewed
controlled partial/unknown-result recovery gate and resolve remaining scope,
journal/identity and final UAT/main integration requirements.
