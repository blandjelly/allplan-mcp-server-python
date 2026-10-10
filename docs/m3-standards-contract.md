# M3.3 standard and selected repair previews — 0.9.0

Status **native read-only owner gate PASS** for the repaired fixture;
[acceptance and originals](test-results/m3-standards-acceptance-0.9.0.md).
This document records the 0.9.0 contract; 0.10.0 separately adds
[explicit mark previews](m3-marks-contract.md).
Accepted 0.8.1 [writes/Undo/recovery](test-results/m3-execution-acceptance-0.8.1.md),
[restart invalidation](test-results/m3-plan-restart-acceptance-0.8.1.md) and
[stale Apply rejection](test-results/m3-stale-apply-acceptance-0.8.1.md) remain
separate. Their archives and original logs are unchanged. This is the first
M3.3 slice; M3/UAT-05/UAT-06 remain open.

## Public entry points and versioned preset

`apply_office_standard` accepts **action=preview only**, explicit standard ID
`native-model-qa-demo-layer-status`, version **1.0.0** and one active drawing-file
scope with include_passive=false. Its packaged resource is
`allplan://standards/native-model-qa-demo-layer-status`, schema `m3-standard-1`.
The preset uses native-model-qa-demo audit rules and explicit choices:
QA-003 → structure layer role, QA-004 → NEW for invalid existing string status.
An already allowed status such as EXISTING is compliant and is not overwritten.
Mark assignment, numbering, graphical labels and file moves are deferred.

`rule_based_edit` accepts **action=preview only**, the same typed audit and
explicit layer/status repair choices as fix_model_issues, plus a required
`selection`. Optional exact finding_ids further narrow targets. No general
attribute/native-property assignment or family conversion is added.

```json
{
  "action": "preview",
  "audit": {"profile_id":"native-model-qa-demo","scope":{
    "drawing_files":[101],"include_passive":false,"visibility":"api_select_all"}},
  "repairs": [{"rule_id":"QA-003","value":"structure"},{"rule_id":"QA-004","value":"NEW"}],
  "selection": {"where":{"field":"layer_id","op":"eq","value":3700},
    "exclude_model_uuids":["<exact canonical model UUID from the fresh audit>"]}
}
```

The example exception placeholder is descriptive; actual requests require a
canonical lowercase UUID. Office previews optionally accept the same selection.
The returned plan carries immutable workflow metadata; standard ID/version and
definition fingerprint are included in the native plan hash. This metadata
describes the preset and authorizes no write.

## One full snapshot, selected findings and exceptions

Both tools use the shared `/fix-model-issues` planner. For selection, the audit
returns its internal full snapshot to the planner within the same call; no
second scan, selection cache, retained native adapter or separate external query
can introduce a race between selection and finding creation.

`where` uses the existing bounded three-valued predicate contract: all/any/not,
at most 64 nodes and depth 8. It can reference audited mark/status/layer_id/
file_state and dimension fields explicitly included by selected audit rules.
Other fields reject before native context lookup. Exact model UUID exceptions
are bounded to 100 distinct entries and must exist in the complete audited scope.
Unknown/ambiguous exception identity is not silently ignored.

Predicates classify elements as selected, false or not_checked; explicit
exceptions exclude an element before predicate evaluation. Unknown survives
negation and blocks plan readiness/evaluation apply. The plan returns
`selection_result` counts and retains exact selection criteria. Findings outside
the choices, predicate or exceptions retain distinct exclusion reasons. The full
audit still includes every element; selection never changes uniqueness scope
or hides the excluded elements from source revalidation.

Fresh fix_model_issues action=revalidate uses the exact plan ID/hash and full
original audit request. Any audited change, including an excluded element,
invalidates the plan. Restart creates a new plan cache; the accepted restart
protection is preserved. No old plan is resumed after a UI cancellation.

## Write boundary and remaining work

All standard/selected previews return read_only=true, apply_available=false,
usable_for_write=false and **evaluation_apply_available=false**. The native
executor also rejects workflow/selection plans even if their proposed changes
happen to equal the previously accepted two-column fixture. Calling generic
fix_model_issues Apply with that plan cannot bypass the preview-only boundary.
The old bounded unselected/unwrapped evaluation route and durable execution
journal are preserved; new tools add no setter or replay route.

Portable verification covers fresh same-scan selection, exception source
conflicts, unknown predicates, pre-context validation, immutable metadata,
native executor refusal and real MCP/HTTP tools plus the owner CLI.
[Owner gate](m3-standards-preview-batch.md) checks three read-only scenarios on
the current repaired copy: standard preview, selection excluding S06, and empty
selection, each revalidated with identical complete before/after audit.
Broader office standards/numbering and selected native writes require future
implementation and a separate owner gate.
