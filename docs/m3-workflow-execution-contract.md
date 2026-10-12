# M3 shared mark/status/layer execution — 0.15.0

Status **bounded native workflow-write gate PASS**, 2026-10-10 Europe/Warsaw.
[Validation status](validation-status.md):
ten steps, both separately reviewed changes/readbacks, exact-ID read-only replay,
complete audits 5 → 4 → 3 and same-session verified 0.11.0. Owner confirms both
changes, host survival, unchanged other elements and two-step Undo. Acceptance
covers the retained workflow pair, not every eligible 1–32-change plan/file.
[M3 / bounded UAT-05/UAT-06 are now closed for the retained test project](m3-closure.md).
The fixture evaluation MVP does not accept wider eligibility or office-project use.

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

0.12.0 additionally replaces existing string marks under validated full-scope
collision evidence; [numbering definition](m3-numbering-contract.md). Native
[bounded two-target mark/numbering acceptance passed](m3-numbering-acceptance-0.12.0.md),
including complete audits 3 → 0 → 3, exact-ID replay/no-op and two-step Undo/recovery.

Attribute roles are explicit plan metadata and participate in the immutable
plan hash. There is no append/delete/undefined attribute assignment. Duplicate
target/field changes, non-Column types, passive/background files, incomplete
coverage and invalid/incomplete mark_validation are rejected before setters.
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
fingerprint and full post-write verification. Invalidated plans remain blocked
from Apply. 0.13.0 preserves their evidence for one read-only source comparison
within shared original TTL/cache budgets;
[bounded same-session conflict gate](m3-conflict-acceptance-0.13.0.md) passed;
manual UI active-plan conflicts remain unaccepted.

Completed requires all proposed writes to read back correctly, a complete
post-audit and an exact comparison of the entire audited snapshot against the
original plus only authorized field/alias changes. The executor no longer
requires exactly three remaining findings: a valid single demo repair leaves
four. Unrelated mark/geometry changes fail verification. This verifies audited
fields within the requested scope, not every native property in the project.

No automatic retry, rollback, Undo or resume occurs. Exact-ID replay returns
historical saved outcomes without setters. Recover reads current observations
in the original disposable project/document; it does not prove write causality.
Native recovery additionally covers the [0.14.1 controlled unknown outcome](m3-recovery-acceptance-0.14.1.md)
after one C03 setter and host restart; crash/power-loss recovery remains unaccepted.
Two separate Undo steps remain the tested limit
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

## Work beyond the fixture closure

Actual mark assignment and deterministic versioned-standard numbering are
implemented in 0.12.0; [the bounded two-target native gate](m3-numbering-acceptance-0.12.0.md)
passed. The [bounded same-session conflict gate](m3-conflict-acceptance-0.13.0.md)
also passed. The [0.14.1 controlled recovery gate](m3-recovery-acceptance-0.14.1.md)
passed restart/reconciliation, no-resume replay and Undo. No completed gate needs repeat.
Do not repeat UI editing known to cancel the host. Broader journal maintenance,
identity guarantees and broader UAT remain open for office-project use;
[fixture UAT is closed](m3-closure.md). Main integration is separate. Graphic
labels, file moves and universal native properties are conditional extensions.

## Controlled recovery evaluation — 0.14.1

The [explicit diagnostic stop](m3-recovery-contract.md) uses the normal durable
write-ahead marker after the first C03 setter, before readback or C04. It requires
a separate typed acknowledgement and the retained two-mark numbering fixture.
Ordinary Apply retains its guards; generated numbering writes follow spatial
assignment order. Recover/exact-ID replay never resume skipped targets.
The [bounded native gate](m3-recovery-acceptance-0.14.1.md) passed
13/13 + 6/6 + 6/6: controlled C03-only interruption, restart/reconciliation,
read-only replay/no-resume and owner Undo, with audits 3 → 2 → 3.
No repeat is required; broader crash/identity/scope guarantees remain open.

## Bounded selected-mark/journal acceptance — 0.15.0

[Native PASS / accepted_on_build](m3-selected-mark-acceptance-0.15.0.md):
13/13 + 6/6 steps, one rule_based_edit C04 S02 → S04 with excluded C02,
full audited-field/snapshot checks, read-only replay, healthy journal history
6 → 7 → 7 and owner-confirmed UI/Undo, audits 3 → 1 → 3. A has a stable,
owner-confirmed uninterrupted host; B uses another session with unspecified cause.
Leave/save the same copy after Undo. No repeat is requested. Broader 1–32-change
scope, journal rollover and cross-copy identity remain unaccepted.
[M3 is now closed within the retained fixture scope](m3-closure.md) by the
owner's later decision. No completed gate needs repetition; wider work follows
the [office-project roadmap](office-project-roadmap.md). Main integration is separate.
