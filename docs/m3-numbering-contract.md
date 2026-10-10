# M3 mark assignment and deterministic numbering — 0.12.0

Status: **bounded native mark-numbering gate PASS**; [evidence](m3-numbering-acceptance-0.12.0.md).
Acceptance covers the retained two-target fixture, not every eligible mark plan. Earlier layer/status
and read-only mark evidence remains scoped to its original source/package.
The shared executor now accepts reviewed **existing string mark** replacements
on native Column roots, with the same one-foreground-file, 1–32-change boundary.
It never appends an absent attribute, converts null/non-string marks, edits a
graphical label, resumes writes or invokes Undo/rollback.

## Explicit assignment

The existing exact rule/model UUID/value mark choices through fix_model_issues
and rule_based_edit now advertise evaluation_apply_available when the plan is
complete, the old attribute is an observed string, native capabilities are
present and mark_validation is validated. Apply uses the same reviewed ID/hash,
saved new execution ID and disposable_copy_reviewed_plan acknowledgement.
The legacy two-repair acknowledgement cannot authorize mark plans.
Required-mark and unique-mark rules must both be selected. Whole-scope normalized
collisions, including excluded peers and simultaneous proposals, reject Apply.
Fresh full source checks occur again before writes. Readback and full audited-field
verification include both the attribute and its mark alias.

## Versioned standard

Public preview:

```json
{"action":"preview","standard_id":"native-model-qa-demo-mark-numbering",
 "standard_version":"1.0.0","scope":{"drawing_files":[101],
 "include_passive":false,"visibility":"api_select_all"}}
```

The definition is exposed at allplan://standards/native-model-qa-demo-mark-numbering.
It contains policy preserve-valid-fill-gaps version 1.0.0, prefix S, start 1,
minimum width 2, order center Y/X/Z in canonical model-local mm then model UUID,
required rule QA-001 and uniqueness rule QA-002. The existing layer/status
standard 1.0.0 keeps its original behavior. Numbering changes marks only.
The public request requires a known standard ID/version; it accepts no arbitrary
numbering code. The host validates the exact definition and selected mark rules
before native context access. Explicit mark choices cannot be mixed with numbering.

The host expands choices from the **same complete fresh audit snapshot**, after
selection/predicate/UUID exceptions are evaluated. Passing marks remain unchanged.
For each drawing-file/family duplicate group it retains an unselected peer first;
when all peers are selected it retains the first in canonical Y/X/Z/UUID order.
Other selected duplicate members and selected missing existing-string marks get
the first free S number in that order. Every current nonmissing peer mark reserves
its normalized number, including excluded peers and old duplicate values. Proposed
numbers are reserved immediately. Numbering does not compact or renumber valid marks.
Two unselected duplicates can remain; the plan reports remaining findings honestly.

Unavailable marks/order, incomplete audit or an eligible missing absent/null mark
block numbered-plan readiness. More than 32 expanded choices reject without
storing a plan; callers narrow proposals with selection. Scan time and cache size
budgets remain. Predicate-unknown blocks Apply. Empty/compliant numbered plans
return a read-only no-op and cannot Apply.

The plan contains definition, exact generated assignments and retained duplicate
keepers in numbering metadata. That metadata, workflow definition fingerprint,
full source, selection and original expanded request enter the immutable plan hash.
Revalidation never regenerates a different authorized plan. Changed peers/resources
conflict; restart/expiry require a new preview. Repeated execution IDs return the
durable historical result without setters, even after Undo. Recover only observes
current values in the original project copy.

## Completed bounded native gate

The completed [owner test](m3-numbering-owner-test.md) used the current retained fixture state.
With C03 missing and C02/C04 duplicate S02, numbering preserves C02 and proposes
C03 → S03 / C04 → S04. Preview is unchanged and deterministic; Apply must read
back both values, verify all audited fields, remove exactly three mark findings,
replay read-only and produce a subsequent empty numbering plan. Existing
layer/status defects can remain: total findings are 5 → 2 or 3 → 0 (also 4 → 1).
The owner checks fields/other elements and native Undo; grouped Undo is unimplemented.
Native unknown recovery, supported-lifecycle source conflicts and remaining
M3/UAT/main-integration work are still open.
