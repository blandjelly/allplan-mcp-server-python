# M3 execution, native guards and recovery

Package **0.12.0** shares this executor across fix_model_issues,
apply_office_standard and rule_based_edit. [Current eligibility/workflow metadata](m3-workflow-execution-contract.md)
cover 1–32 existing string mark/status and layer changes on Column roots in one foreground
file. [Native acceptance](validation-status.md) remains narrower: the earlier
two-target gate and latest two separately reviewed single-target workflows.
Two separate Undo steps are accepted; grouped Undo, native same-session conflicts
and unknown-outcome recovery remain open.

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
`evaluation_apply_available` when it matches current bounded execution eligibility.
This experimental execution route has bounded native acceptance for the retained
fixture; it does not provide a generic writable profile/reference registry.
Generic profiles remain inactive for writes.

```json
{
  "action": "apply",
  "plan_id": "<exact reviewed 32-hex ID>",
  "plan_hash": "<exact reviewed 64-hex hash>",
  "execution_id": "<new 32-hex ID saved before sending>",
  "acknowledgement": "disposable_copy_reviewed_plan"
}
```

The host preflights the full typed request before native document access.
Apply supports 1–32 native Column layer/existing-string mark/status changes in one
active_foreground file with complete evidence and current native capabilities.
The demo profile remains bounded to file 101; other scopes require validated
explicit profiles. The legacy acknowledgement disposable_copy_reviewed_two_repairs
is accepted only for its original exact unselected/unwrapped two-target gate:
S05 layer → SZ_OGÓ01 and S06 status NWE → NEW, 2 changes/3 exclusions/5 findings.
It cannot authorize expanded plans. Mark assignment is implemented in 0.12.0 with collision validation;
no attribute append/delete,
label, component replacement or passive/background write is inferred.

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
requires a short layer name; ChangeLayer receives the freshly resolved short
name (for example `SZ_OGÓ01`), never its ID.
Returned adapters/return values do not establish success. Fresh resolution and
typed field readback determine applied/failed/unknown. A mismatch, exception,
conflict or time budget stops later writes. No automatic retry or rollback runs.
There is a 20-second boundary before starting each setter, 5-second individual
read budgets and 10,000-adapter resolution limits; an executing native setter
cannot be forcibly interrupted. HTTP timeout may therefore have an unknown result.

All plans/selections are invalidated when execution starts. Full post-audit
verification compares the entire audited snapshot to the original plus only
reviewed field/alias changes, including excluded peers, marks and geometry.
It does not cover every native property or out-of-scope element. Readbacks alone
cannot report completed if that verification fails. The old two-target fixture
leaves three findings; general execution has no fixed finding-count requirement.
Collateral changes/unreadable verification produce verification_failed.

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
do not acquire it. The UI dispatcher serializes native callbacks; avoid concurrent
model operations during these bounded writes.

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

## Recovery tools and remaining work

[M3 Recover.cmd and M3 Workflow Recover.cmd](diagnostics.md) retain access to
saved local executions. Recovery sends no new write, automatic retry, resume,
rollback or Undo. Exact-ID replay returns saved outcomes; it does not establish
current state after UI Undo.

Native acceptance covers the recorded layer/status writes/readbacks, audited-field
verification, exact-ID replay, separate Undo and completed recovery after Redo.
Restart invalidation and stale Apply rejection also pass. Native same-session
conflicts, controlled partial/unknown recovery, broader scope/identity and
crash/power-loss persistence remain open. Do not repeat the UI-edit scenario
known to cancel the host. Mark assignment/numbering now await their new native gate; then obtain
the missing native evidence; see [handoff](next-model-handoff.md).
