# M3 shared layer/status execution — 0.11.0

Status **bounded native workflow-write gate PASS**, 2026-10-10 Europe/Warsaw.
[Original reports and decision](test-results/m3-workflow-acceptance-0.11.0.md):
ten steps, both separately reviewed changes/readbacks, exact-ID read-only replay,
complete audits 5 → 4 → 3 and same-session verified 0.11.0. Owner confirms both
changes, host survival, unchanged other elements and two-step Undo. Acceptance
covers the retained workflow pair, not every eligible 1–32-change plan/file.
This implements the first step of the owner's completeness review: remove the
exact two-demo-target gate and execute reviewed standard/selection plans through
the existing executor. [Review response](reviews/m3-completeness-response-0.11.0.md),
[178 portable tests PASS](test-results/m3-workflow-portable-0.11.0.md). [Completed native card](m3-workflow-apply-batch.md).
M3/UAT-05/UAT-06 and the first MVP remain open.

## Supported operations and typed actions

`fix_model_issues`, `apply_office_standard` and `rule_based_edit` share preview,
revalidate, apply and read-only recover. Standard/rule Apply additionally checks
that the stored plan came from the matching workflow. Generic fix_model_issues
can execute either eligible workflow plan. A caller supplies exact reviewed
plan ID/hash, a new execution ID durably saved before sending, and
`acknowledgement=disposable_copy_reviewed_plan`.

Eligibility requires 1–32 proposed changes, complete audit/scope/field evidence,
and exactly one included **active_foreground** file. All targets must be native
Column roots with supported observed setter capabilities. Changes may assign a
freshly resolved layer ID/short name or replace an **existing string status**
attribute with a value allowed by the validated audit profile. File 101, S05/S06,
NWE/NEW and the original finding/exclusion counts are no longer executor gates.
The supplied demo profile/preset remains bounded; another scope requires a
separately validated profile. Broad eligibility is not native acceptance of
every possible profile/value/target.

Attribute roles are explicit plan metadata and participate in the immutable
plan hash. There is no append/delete/undefined attribute assignment. Duplicate
target/field changes, non-Column types, passive/background files, incomplete
coverage and every plan carrying mark_validation are rejected before setters.
No universal native-property setter is introduced. The old acknowledgement
`disposable_copy_reviewed_two_repairs` is retained only for its original exact
unselected/unwrapped two-target gate; it cannot authorize expanded plans.

Preview remains read_only=true; evaluation_apply_available advertises this
bounded route. Generic apply_available/usable_for_write remain false because
general writable profile/reference guarantees are unimplemented. This explicit
evaluation flag does not mean that native Allplan has accepted the new scope.

## Preserved execution and recovery boundaries

The [existing execution contract](m3-execution-contract.md) still governs fresh
full source/report revalidation, expiry/hash, native hierarchy and writability,
all-target preflight, immediate per-target old-value checks, OS serialization,
write-ahead unknown markers, readback, stop after failure and durable exact-ID
replay. Selection changes proposals only; excluded peers remain in the source
fingerprint and full post-write verification.

Completed requires all proposed writes to read back correctly, a complete
post-audit and an exact comparison of the entire audited snapshot against the
original plus only authorized field/alias changes. The executor no longer
requires exactly three remaining findings: a valid single demo repair leaves
four. Unrelated mark/geometry changes fail verification. This verifies audited
fields within the requested scope, not every native property in the project.

No automatic retry, rollback, Undo or resume occurs. Exact-ID replay returns
historical saved outcomes without setters. Recover reads current observations
in the original disposable project/document; it does not prove write causality.
Native accepted recovery remains the earlier completed execution after Redo,
not unknown-outcome recovery. Two separate Undo steps remain the tested limit
of the earlier two-write gate. Two-step Undo is also owner-confirmed for the
0.11.0 workflow pair; grouped and broader-scope Undo remain unaccepted.

## Journal lifecycle and the 128-record limit

The journal is `Local/.allplan-mcp/repairs`, independent of the extracted ZIP
and the session-local plan cache. At most 128 records, 1 MiB each, are retained;
there is **no automatic eviction or pruning command**. A full journal rejects a
new execution before setters. Saved exact-ID replay and read-only recovery remain
available if the records are valid and accessible. Unresolved running/unknown
records block new execution until inspected/reconciled.

Setup/Restore replace the bridge's Library/PythonPartsScripts trees and preserve
this journal. Their bridge backups do **not** constitute a backup of repair
records. Before migration or machine restoration, close Allplan/MCP and preserve
the entire Local/.allplan-mcp/repairs directory together with package logs and
the original project copy. Do not delete records to gain slots: removing an
execution identity removes its deduplication protection. At capacity, stop new
writes and report the journal for a separately designed maintenance/migration
step; automatic rollover is not implemented.

An extracted-package copy alone carries no installed Local journal. Moving to a
different Local/machine does not transfer execution history automatically.
Project copies can share identity evidence; cross-copy uniqueness is unproven.
Do not replay/recover transferred identities against another copy. Restoring an
older Local backup may remove newer records: inspect model/logs and do not retry
their writes. Atomic writes/content hashes detect some storage failures but do
not establish authenticated history or sudden power-loss durability.

## Next native evidence and remaining M3 work

The completed card uses two **separately reviewed single-target** writes: office
standard with S06 excepted, then rule selection with S05 excepted. Complete
audits must progress 5 → 4 → 3, both exact-ID replays must be read-only and
the host session/integrity must remain unchanged. It tests the new route rather
than repeating the accepted 0.8.1 pair or asking for another Undo cycle. All
required observations now pass; no repeated batch is requested.

Next, implement actual mark assignment and deterministic
numbering under an explicit versioned standard, retaining full-scope collision
checks. These are required open M3 scope, not removed by calling them deferred.
Then design supported-lifecycle same-session source conflicts and controlled
native partial/unknown-result recovery. Do not repeat UI editing that is known
to cancel the host. Broader journal maintenance/identity guarantees and final
UAT/main integration remain separate work. Graphic labels, file moves and
universal native properties are conditional extensions, not new closure gates.
