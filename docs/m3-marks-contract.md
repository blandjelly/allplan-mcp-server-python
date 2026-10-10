# M3 explicit mark repair preview — 0.10.0

Explicit mark previews have [bounded native acceptance](validation-status.md).
The owner confirms unchanged model and uninterrupted host. They reuse audit,
planner, selection, hashing and revalidation; writes and deterministic numbering
remain required open M3 work.

## Explicit rule and target, no automatic numbering

`fix_model_issues` preview and `rule_based_edit` preview accept mark
choices alongside the existing layer/status choices. Each mark choice names a
selected required_attribute/unique_attribute **mark** rule, an exact canonical
lowercase `model_uuid` and the explicit proposed string:

```json
{"rule_id":"QA-001","model_uuid":"65ab07fe-d37a-4adf-b1b6-3040fdde84a2","value":"S03"}
```

The UUID above comes from the retained fixture's captured audit. Actual clients
must use current fresh audit evidence, never transfer references between copies.
Both required-mark and unique-mark rules must be selected in the audit request.
The string must be 1–128 characters, nonmissing under the explicit audit policy,
nonblank and without ASCII control characters. Validation rejects malformed
choices before native context lookup. Each element gets at most one explicit
mark assignment, even across two rules. Distinct elements may use the same rule;
layer/status choices retain one rule/value each and cannot contain model_uuid.
The overall choice limit remains 32.

A target must have a current finding under its chosen rule. Absent, already
compliant or wrong-rule targets raise finding_stale without storing a plan.
Optional finding_ids, predicate and UUID exceptions still narrow proposals,
with explicit `mark_target_not_selected` and existing exclusion reasons.
Read-only mark proposals use the freshly resolved mark attribute resource and
retain exact raw old values, new values, identity, source hash and location.
This changes attribute data only in a **hypothetical plan**; graphical labels,
automatic numbering/renumbering and office mark presets are not implemented.

## Collision simulation includes all peers

The planner gets the complete fresh snapshot from the same audit call. It
simulates all eligible proposed marks simultaneously and retains current marks
for every other element, including predicate-false elements, UUID exceptions,
unchosen duplicate-group members and excluded findings. No second document scan
or separately cached selection is used.

`mark_validation` uses the audit policy's trim/case handling and the exact
**drawing_file/element_family** uniqueness scope. It records total inspected
and unchecked elements, proposed marks, remaining missing marks/duplicate groups,
and complete collision-group member references. A collision involving a
proposed mark sets validation/plan state **conflict**; unknown marks or incomplete
audit prevent validated readiness. Existing duplicate groups unaffected by a
proposal are counted without being claimed repaired. Counts describe the
hypothetical final values, not a post-write audit. Conflicting candidates remain
visible in changes for review; they cannot be applied.

Selection never narrows audit/revalidation or uniqueness evidence. Any audited
peer/source/resource/context change conflicts on fresh exact-ID/hash revalidation.
The unchanged TTL, eviction and host-restart invalidation rules apply. The
assignment request, validation result and all plan metadata enter the plan hash;
caller mutation cannot modify the stored reviewed plan.

## Native write boundary

Every plan containing mark-validation metadata is **preview-only**, including
when filtering leaves zero mark proposals and only the formerly accepted
layer/status pair. The executor refuses such plans before setters/journaling;
using generic fix_model_issues Apply cannot bypass this boundary. No new native
setter, graphical operation or write capability is introduced. Package 0.11.0 separately enables reviewed selected/standard layer/status writes;
[expanded execution boundary](m3-workflow-execution-contract.md). Mark plans
remain read-only in 0.11.0.

Native acceptance covers positive C03/C04 proposals, a selection exception,
collision against an excluded peer and unchanged revalidations/full audits.
No repeat of that completed gate is required. Next implement actual mark
assignment and deterministic numbering with these full-scope safeguards.
