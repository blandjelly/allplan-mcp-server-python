# M3 repair preview contract

Public tool fix_model_issues, bridge /fix-model-issues, request/plan schema
m3-repair-1. Preview/revalidation are side-effect-free. Layer/status preview
has [bounded native acceptance](validation-status.md); explicit mark proposals
are described in the [mark contract](m3-marks-contract.md).
Package **0.11.0** executes eligible reviewed layer/status plans through the
[shared executor](m3-execution-contract.md) and
[workflow contract](m3-workflow-execution-contract.md).
M3/UAT-05/UAT-06 remain open.

## Explicit preview

```json
{
  "action": "preview",
  "audit": {
    "scope": {"drawing_files": [101], "include_passive": false, "visibility": "api_select_all"},
    "profile_id": "native-model-qa-demo"
  },
  "repairs": [
    {"rule_id": "QA-003", "value": "structure"},
    {"rule_id": "QA-004", "value": "NEW"}
  ]
}
```

The nested audit supports M2's explicit typed profile instead of `profile_id`.
The public bridge expands profiles and adds both schema versions. Host preflight
validates the complete request before reading the current document or native
resources. The preview requires one drawing file and `include_passive=false`.
It evaluates a fresh **full** M2 audit, without using M1 pages or cached results.
No historical report is accepted as authorization.

There must be 1–32 distinct explicit repair choices for selected audit rules.
Supported choices are `required_layer` → that rule's expected named layer role,
and `allowed_attribute_values` on **status** → an explicitly supplied allowed
value. String comparison uses the audit's trim/case policy; the exact supplied
string is retained as the proposed value. Explicit per-model mark choices use
the [mark contract](m3-marks-contract.md) and always remain preview-only.
No default value, numbering, mark
assignment, duplicate resolution, graphical label or native-property edit is
inferred. Optional `finding_ids` contains 1–100 distinct hashes and restricts
the chosen rules to those exact current findings. Absent/stale/unselected IDs
reject with `finding_stale`. Omitting IDs selects all current failing findings
for the explicitly chosen repair rules.

Every proposed change records rule/finding IDs, full session/project/document/
file/model/type reference, model-local locator, relevant element fingerprint,
bound resource identity, operation/field and exact old observation/new value.
Unknown old values and inactive files are excluded; no absent attribute is
silently appended. Incomplete audit coverage produces `not_checked` and no
proposed changes. Scope/resource/input exclusions remain explicit. Multiple
rules targeting one element/property reject with `repair_conflict`; there is
no implicit last-writer policy. Passing rules generate no operations.

For the retained fixture, the preview contains **two** proposed changes:
C05/S05 layer SZ_OGÓ02 → SZ_OGÓ01, and C06/S06 status NWE → NEW.
Three mark findings remain excluded. An audit after preview alone retains **five** findings; preview performs no writes.

## Plan lifetime and revalidation

Plans live only in the current handler's cache: **300 seconds**, at most
**8 plans**, **4 MiB per stored entry** and **8 MiB total**. Entries include the
original expanded request and exact plan; the cache evicts oldest entries.
Restart, expiry and eviction require a new preview. Returned objects are copies,
so client changes cannot modify a stored plan. The plan hash binds its ID,
session, profile, scope, fingerprints, changes, exclusions and explicit request.
Transport request/host IDs are added outside that hash.

```json
{"action": "revalidate", "plan_id": "<32 hex characters>", "plan_hash": "<64 hex characters>"}
```

Revalidation requires the exact stored ID/hash and reruns the same full audit.
It compares both complete source and report fingerprints. Changes to audited
data (including other scope members), identity, file states or resource binding
produce `conflict` and discard the plan. Unchanged evidence returns `unchanged`.
Expiration is checked again after the scan; a slow call cannot revive an expired
plan. A hash mismatch rejects before enumeration. Failed scans return an error
and never establish validity. Portable tests cover manual edits, additions,
resource/project/document/file-state changes, selection limits and restart.

These fingerprints concern the **audited source fields**, not every native
property of the whole model. References still have
`durable_identity_verified=false`; revalidation is read evidence, not native
write re-resolution or per-element writability. Apply performs those checks
again at the execution boundary.

## Native API preparation and remaining gate

The host inspects the callable symbols and bounded docstrings of
`ElementsAttributeService.ChangeAttributes` and `ElementsLayerService.ChangeLayer`
without invoking them. This follows the
[2026 attribute API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsAttributeService/)
and [2026 format-property guide](https://pythonparts.allplan.com/2026/manual/features/format_properties/).
The layer path uses the dedicated `ChangeLayer` API rather than an assumed
universal common-properties setter. Missing symbols remain `not_checked`.
Symbol presence proves neither target writability nor mutation/Undo behavior.

Preview/revalidation return read_only=true, apply_available=false and
usable_for_write=false. Eligible layer/status plans separately advertise
evaluation_apply_available for the bounded executor. Mark plans always refuse
Apply. General writable profiles and durable references remain unimplemented.
The plan service invokes no setters; native Apply belongs to the shared executor.
See [accepted limits and remaining work](validation-status.md).
