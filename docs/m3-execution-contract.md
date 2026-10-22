# M3 repairs, execution and journal

Package **0.15.0**. [Acceptance and limits](validation-status.md) cover the
recorded one-/two-change fixture scenarios; executor eligibility is broader.
`fix_model_issues`, `apply_office_standard` and `rule_based_edit` share the
planner/executor. Native general writable profiles remain disabled.

## Preview and selection

Preview requires a fresh full typed audit in **one explicit file** with
include_passive=false. fix_model_issues uses explicit repairs and optional
selection/finding_ids; rule_based_edit requires selection. Current finding IDs
narrow proposals, not audit/collision scope. Absent/stale choices reject.

Supported proposals replace an existing string mark/status or assign the rule's
expected named layer. Status values must satisfy the audit profile. Explicit
marks name a current model_uuid, require required-mark plus uniqueness rules,
and use nonmissing strings of **1–128** characters without control characters.
Absent/null/non-string attributes are not appended or converted. Duplicate
target/field proposals, incomplete evidence and unknown selection inputs reject.

Selection uses three-valued predicates (**64 nodes/depth 8**) on audited mark/
status/layer/file-state/dimension fields and up to **100** distinct UUID exceptions.
Exceptions run first; excluded peers remain in source/collision/post-write checks.
Unknown remains not_checked under negation and blocks readiness. A displayed page
or cached selection cannot narrow full-source authorization.

apply_office_standard accepts demo standard IDs
native-model-qa-demo-layer-status and native-model-qa-demo-mark-numbering,
version **1.0.0**, explicit scope and optional selection. The layer/status
standard repairs QA-003/QA-004 and leaves valid EXISTING status unchanged.
Numbering preserves valid marks, retains an unselected duplicate keeper first,
then orders center **Y/X/Z/model UUID**, filling available S01-style numbers.
All full-scope marks reserve normalized values. Generated writes follow that
spatial assignment order. Numbering cannot mix with explicit mark choices.
Unavailable order/marks or over 32 choices reject; compliant plans are read-only no-op.

Mark collision simulation checks simultaneous proposals and all excluded peers.
The immutable plan hash binds exact targets/old-new values, resources, full
source/report fingerprints, workflow/standard definition and selection/exclusions.
Preview alone invokes no setter. Generic apply_available/usable_for_write remain
false; evaluation_apply_available advertises eligible evaluation plans only.

## Plan lifetime and stale evidence

Plans live **300 seconds from creation**, with **8 entries**, **4 MiB per entry**
and **8 MiB total**. Copies returned to clients cannot mutate saved plans.
Revalidate reruns the full source/audit and requires exact plan ID/hash; changes
to audited peers/resources/context conflict. Expiry is checked after reads too.
Restart/eviction/expiry requires fresh preview; unchanged evidence does not extend TTL.

Starting execution invalidates all plans and cached selections. Invalidated
evidence remains for **one read-only revalidate** within the original shared
TTL/cache budgets. It always returns conflict/plan_invalidated, reports actual
source_unchanged independently and never restores Apply. Successful inspection
consumes it; a hash mismatch does not scan/consume it. Native active-plan manual
UI edit conflicts remain unaccepted.

## Apply guards and outcomes

```json
{"action":"apply","plan_id":"<reviewed 32-hex ID>","plan_hash":"<reviewed 64-hex hash>","execution_id":"<new 32-hex ID saved before sending>","acknowledgement":"disposable_copy_reviewed_plan"}
```

Eligibility: **1–32** complete mark/status/layer changes on native **Column roots**
in one **active_foreground** file, validated profile/resources and observed native
capabilities. Standard/rule Apply also checks matching workflow provenance.
The legacy disposable_copy_reviewed_two_repairs acknowledgement remains restricted
to its original two-layer/status-repair gate. No label/native-property/passive write
or arbitrary-family setter is inferred.

Under the installed Local journal's OS writer lock, Apply validates request,
hash/expiry and full source/report, re-resolves every root and checks hierarchy,
identity, active-document/layer and native null/deleted/valid/label flags. Unknown
or ambiguous resolution rejects. IsInMacro alone is not a macro classifier.
All targets preflight before setters; old values are checked again per target.
ChangeLayer receives the freshly bound short name; ChangeAttributes writes one
exact pair with undef/delete flags false. Return values/adapters do not prove success.

Persist a durable unknown marker before each setter; fresh resolution/readback
determines outcomes. Stop later writes after conflict/failure/unknown/time limit.
Completion requires full post-audit and the entire audited snapshot matching
only authorized field/alias changes, including excluded peers/geometry. This
does not verify every property or out-of-scope element. Verification failures
cannot report completed. No automatic retry, rollback, Undo or resume occurs.

Budgets: **20 seconds before starting setters**, **5 seconds per bounded read**,
**10000 adapters per resolution**. A running native call cannot be forcibly
interrupted; HTTP timeout may leave an unknown result. The lock protects this
repair route, not unrelated baseline box/development operations.

## Replay, recovery and controlled interruption

Same execution ID plus the same Apply request returns saved historical outcomes
without setters, even after restart/expiry/Undo. A different request with that
ID conflicts. Transport request IDs are separate. Recover checks original
project/document/file/model/type and observes old/new/conflicting/unknown values;
unknown outcomes may reconcile, but observations do not prove write causality.
Historical applied outcomes remain historical after Undo. It never resumes skipped
targets; use only the original project copy/Local. See [recovery tools](diagnostics.md).

The diagnostic evaluation_stop=after_first_setter_before_readback requires
acknowledgement=disposable_copy_reviewed_recovery_test and the retained unselected
two-mark numbering fixture: C03 undefined → S03 first, C04 S02 → S04 second,
three initial findings, original locations/shared resource. It leaves a real
running/unknown write-ahead record after C03 with C04 skipped. This accepted
controlled stop is not evidence for native crash/power-loss recovery.

## Journal lifecycle and inspection

Storage: **Local/.allplan-mcp/repairs**, schema m3-execution-1, maximum **512 records /
1 MiB each**. Atomic temp/flush/fsync/replace and content/structural hashes detect
some failures, not authenticated history or power-loss durability. Full/corrupt/
unwritable history or competing writers blocks new execution; unresolved
running/unknown records require saved-ID recovery. Valid replay/recovery remain
available at capacity. No automatic eviction, import, rollover or pruning exists.

fix_model_issues action=inspect_journal (**M3 Journal.cmd**) takes the writer lock
and validates installed records **before native API/document access**. Schema
m3-journal-inspection-1 reports verified historical summaries/remaining slots and
blockers: journal_full, capacity_exceeded, recovery_required, invalid_record.
A 129th record makes the inventory incomplete/count unknown. Unavailable storage
or lock returns repair_journal_unavailable. Inspection can create a missing
directory/lock but never changes records, scans the model or reconciles outcomes.
available means storage checks passed, not current values/writability/copy identity.

Setup/Restore preserve the journal; bridge backups do not back it up. Preserve
the entire journal, original project and logs before migration. Deleting IDs or
restoring older history removes retry protection; copying extracted packages
does not transfer installed history. Do not replay transferred identities or
retry newer writes after history rollback. Wider identity/journal/Undo guarantees
are prerequisites in the [editing development plan](office-editing-development-plan.pl.md).
