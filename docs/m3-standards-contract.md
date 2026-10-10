# M3 office standards and selected repairs

Current **0.13.0** tools apply_office_standard and rule_based_edit share the
repair planner/executor. They accept preview, revalidate, apply and recover.
[Native boundaries](validation-status.md) distinguish the earlier no-op previews
from the latest two separately reviewed single-target writes.
[Workflow execution](m3-workflow-execution-contract.md) defines Apply eligibility
and journal/recovery limits. M3/UAT-05/UAT-06 remain open.

## Versioned preset and public requests

Office preview requires standard ID **native-model-qa-demo-layer-status**,
version **1.0.0**, explicit scope and include_passive=false. The packaged resource
allplan://standards/native-model-qa-demo-layer-status uses schema m3-standard-1.
It chooses QA-003 → structure layer and QA-004 → NEW for invalid existing string
status. Already allowed EXISTING is compliant and is not overwritten.
A separate [versioned numbering standard](m3-numbering-contract.md) now assigns marks;
[its bounded two-target native gate passed](m3-numbering-acceptance-0.12.0.md). Labels/file moves remain conditional.

Rule preview uses the typed audit and explicit layer/status choices from
[repair preview](m3-repair-contract.md), plus required selection. It also accepts
[explicit mark choices](m3-marks-contract.md), which require full-scope collision validation for evaluation Apply.
Optional finding_ids narrow proposals to exact current findings. Office previews
optionally accept selection. Example rule preview:

```json
{
  "action":"preview",
  "audit":{"profile_id":"native-model-qa-demo","scope":{
    "drawing_files":[101],"include_passive":false,"visibility":"api_select_all"}},
  "repairs":[{"rule_id":"QA-003","value":"structure"},{"rule_id":"QA-004","value":"NEW"}],
  "selection":{"where":{"field":"layer_id","op":"eq","value":3700},
    "exclude_model_uuids":["<canonical UUID from the fresh audit>"]}
}
```

The UUID placeholder is descriptive; actual requests require a lowercase UUID.
Workflow metadata, selection, standard ID/version and definition fingerprint
participate in the immutable plan hash. Preview alone authorizes no write.

## Full snapshot, predicates and exceptions

Both tools plan from the full fresh audit snapshot in the same call. No second
scan, external page, cached selection or retained adapter narrows source evidence.
where uses three-valued all/any/not predicates, at most 64 nodes/depth 8, over
mark/status/layer_id/file_state and dimensions explicitly covered by selected
rules. Other fields reject before native lookup. At most 100 distinct UUID
exceptions are allowed; each must exist unambiguously in the complete scope.

Predicates classify selected/false/not_checked; exceptions run before predicates.
Unknown remains unknown under negation and blocks readiness/evaluation Apply.
Selection counts and exact criteria enter the plan. Excluded findings retain
reasons; all peers remain in uniqueness/source validation and post-write checks.
Any audited change, including an excluded element, invalidates revalidation.
TTL/eviction/restart require a fresh preview; an old authorization is not renewed.

## Execution boundary

Previews retain read_only=true, apply_available=false and usable_for_write=false.
Eligible existing-string mark/status and layer plans advertise evaluation_apply_available.
Mark plans require validated full-scope collision evidence; the numbered
two-target native gate passed, while wider mark request scope remains unaccepted. Apply requires reviewed ID/hash, saved new execution ID and current
explicit authorization. Standard/rule Apply checks matching workflow provenance;
generic fix_model_issues can execute an eligible workflow plan.
Recover observes the saved execution without setters, resume or Undo.
See [execution contract](m3-workflow-execution-contract.md).
