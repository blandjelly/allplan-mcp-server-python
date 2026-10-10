# M3 bounded execution contract — accepted 0.8.1 baseline

This records the original exact-two-target gate. Package 0.11.0 extends eligible
layer/status plans and standard/selection execution while retaining the journal
and native adapter guards; [current contract and lifecycle](m3-workflow-execution-contract.md).
The older native acceptance below does not accept that expanded scope.

The first 0.8.0 native write gate was **BLOCKED before setters**,
[evidence and correction](test-results/m3-apply-rejection-0.8.0.md).
0.8.1 records the broad IsInMacro parent-object flag as diagnostic evidence;
required native hierarchy must terminate at the reviewed Column root. Explicit
known pre-setter apply errors become `rejected`, not `unknown`; transport,
unexpected and journal errors retain conservative unknown handling.

Status **bounded native execution gate PASS**, 2026-10-10 Europe/Warsaw:
[original evidence and decision](test-results/m3-execution-acceptance-0.8.1.md).
The two retained Column repairs, audited-field verification, exact-ID read-only
replay across host sessions, manual **two-step Undo**, and recovery after
owner-confirmed Redo pass. Grouped Undo is unavailable. Native manual-edit
conflicts and broader execution remain pending. The owner-observed UI action
cancelled the host; [old-plan revalidation after restart passes](test-results/m3-plan-restart-acceptance-0.8.1.md),
while native same-session conflict is blocked in that lifecycle.
[Native stale Apply rejection PASS](test-results/m3-stale-apply-acceptance-0.8.1.md);
no repeat of that completed card is requested.
The accepted [0.7.0 preview](test-results/m3-preview-acceptance-0.7.0.md)
and its unchanged archive remain separate. [Polish owner gate](m3-apply-batch.md).
This slice advances M3.1/M3.2/M3.4; M3 and UAT-05/UAT-06 remain open.

## Eligibility correction and rejected requests

IsInMacro=true alone is not a macro classifier. Macro/container ancestors cannot
match the required terminal Column root in the native parent traversal; unknown
or cyclic/unreadable hierarchy still fails closed. Successful preflight records
contain exact root identity and raw flag observations. Other required native
null/deleted/valid/active-document/active-layer/label checks are unchanged.

The public MCP wrapper uses categorized AllplanHostError codes, never message
text, for a small set of known pre-setter failures. `rejected` responses include
`native_setters_started=false`, execution ID, request ID and the host error.
That statement concerns this request; it does not erase earlier historical
executions. CLI recovery pointers record the final rejection and recovery sends
no apply replay for them. Journal/transport/unexpected failures cannot be
classified as pre-write safety because they may happen after a setter.

## Disposable-copy apply

`fix_model_issues` / `/fix-model-issues` retains schema `m3-repair-1` and the
side-effect-free preview/revalidate actions. General `apply_available` and
`usable_for_write` remain false. A preview additionally advertises
`evaluation_apply_available` when it matches the bounded fixture gate.
This experimental execution route has bounded native acceptance for the retained
fixture; it does not provide a generic writable profile/reference registry.
Generic profiles remain inactive for writes.

```json
{
  "action": "apply",
  "plan_id": "<exact reviewed 32-hex ID>",
  "plan_hash": "<exact reviewed 64-hex hash>",
  "execution_id": "<new 32-hex ID saved before sending>",
  "acknowledgement": "disposable_copy_reviewed_two_repairs"
}
```

The host preflights the full typed request before native document access.
Apply supports exactly two native Column roots in foreground file **101**:
S05's layer to freshly bound `SZ_OGÓ01` and S06's existing named string
`MCP_QA_STATUS` from `NWE` to `NEW`. The plan must contain 2 changes,
3 exclusions and 5 complete audit findings. Other preview scopes remain read-only.
No attribute append, mark assignment, graphical label, component replacement,
passive/background write, or repair choice is inferred.

Under an OS writer lock per `Local/.allplan-mcp/repairs`, apply reruns the full
audit and compares source/report hashes, expiry and exact reviewed hash.
It takes another fresh audited snapshot, re-resolves every root by
file/model/type UUID without retaining adapters across requests, and checks
old values plus native IsNull/IsDeleted/IsValid/IsInActiveDocument/
IsInActiveLayer/IsLabelElement booleans. IsInMacro is diagnostic only. Unknown or ambiguous
resolution blocks writes. Each target is checked again immediately before its
setter. These documented eligibility checks are provisional; they do not prove
all permission/property restrictions on the installed build.

The [2026 ChangeAttributes API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
receives one `(attribute ID, exact value)` pair, one BaseElementAdapterList and
both undef/delete flags false. The
[2026 layer guide](https://pythonparts.allplan.com/2026/manual/features/format_properties/)
requires a short layer name; ChangeLayer receives `SZ_OGÓ01`, never its ID.
Returned adapters/return values do not establish success. Fresh resolution and
typed field readback determine applied/failed/unknown. A mismatch, exception,
conflict or time budget stops later writes. No automatic retry or rollback runs.
There is a 20-second boundary before starting each setter, 5-second individual
read budgets and 10,000-adapter resolution limits; an executing native setter
cannot be forcibly interrupted. HTTP timeout may therefore have an unknown result.

All plans/selections are invalidated when an execution starts. A full re-audit
and snapshot compare all six returned elements' audited fields with the original
snapshot plus only the two authorized values; this includes mark and geometry
observations, but not every native property or out-of-scope model data. Two
readbacks alone cannot report completed if that verification fails. Successful
fixture execution leaves three mark findings; collateral changes or unreadable
verification produce `verification_failed` rather than acceptance.

## Durable execution identity and recovery

The dependency-free host stores schema `m3-execution-1` records atomically:
temporary file, flush/fsync and replace; POSIX also fsyncs the directory.
Records retain request/plan hashes, exact changes, per-target outcomes and
post-audit evidence. Content hashes detect malformed/tampered accidental state;
they are not authentication. The journal must be writable before the first setter.
A write-ahead `unknown` marker is persisted before each setter; post-readback
states are persisted before another target. Journal failures stop execution.

The interactive host's cancellation stops its server; restarting creates a new
session-local plan cache. A preview from before the UI cancellation cannot be
continued after restart: native revalidation returns plan_expired in the accepted
restart capture. Fresh previews after restart are separate plans, not renewals
of the old authorization. Persisted executions remain a separate mechanism.

The same execution ID with the same apply request returns saved outcomes
without invoking setters, even after host restart, plan expiry or UI Undo.
Reusing an ID with another request conflicts. Request transport IDs are separate.
Up to 128 records and 1 MiB per record are stored; they are never automatically
evicted. A full/corrupt/unwritable journal or competing writer blocks new writes.
Unresolved running/unknown records require recovery before new execution.
The lock covers this repair route; unrelated baseline box/development operations
do not acquire it. The UI dispatcher serializes native callbacks, and the owner
gate forbids concurrent model operations.

```json
{"action": "recover", "execution_id": "<saved 32-hex ID>"}
```

Recover reads the original audit and checks project key/document/file/model/type
identity. It reports `new_value_observed`, `old_value_observed`, `conflict` or
`unknown`. Previously unknown outcomes may become `reconciled` with their current
observations; this does not prove mutation causality. Recover never resumes a
skipped target or invokes a setter/Undo. Historical applied outcomes remain
historical after UI Undo; current observations are recorded separately.
Cross-copy identity and durable element identity are unproven, so recovery is
restricted to inspection in the original disposable project/document. There is
no cross-machine guarantee when the Local journal is removed/copied or storage
rolls back. Windows atomic replace/fsync is implemented, but native persistence
and sudden power loss are unaccepted. Preserve the journal with the package logs.

## Owner CLI and remaining gates

`M3 Apply.cmd` displays the plan and requires `NAPRAW KOPIE`. It saves the
execution request before contacting the host, tests readback and exact-ID replay,
and records JSON/TXT. `M3 Recover.cmd` verifies persisted replay/current values;
`M3 Check Undo.cmd` observes both original values and five findings after manual
native UI Undo. None of the recovery/check commands requests a new write.
The owner observes whether Undo needs one or two steps; no grouping API or
transaction/automatic rollback is claimed. Loss of reply never triggers retry.

Portable fake adapters and real HTTP/MCP checks are separate from Allplan
acceptance. Native writability, setter readback, audited collateral verification,
exact-ID persistence across the observed host sessions and two-step Undo pass
for the retained fixture. Whole-model collateral UI verification, native
manual-edit conflicts, unknown-outcome recovery and crash/power-loss persistence
remain outside that acceptance. M3.3 office-standard/rule-based execution is
implemented in 0.11.0 with native acceptance pending; broader mutation/registry
guarantees remain unaccepted. No repeated two-write gate
is required. The same-session manual-edit card was blocked by UI host
cancellation, with restart invalidation correctly observed; do not repeat that
scenario on this build. Stale Apply rejection is already accepted. The next card
is [two separately reviewed workflow writes](m3-workflow-apply-batch.md).
