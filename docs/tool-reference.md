# Read and audit tools

Native acceptance is bounded to the [recorded fixture/build](validation-status.md).
Query/audit/property tools do not write or load/activate files. UI presentation
uses the separate `model_selection` tool described below.
Use typed MCP requests; the wrapper supplies host schema versions.

## Context, scope and identity

`get_model_context` reports session/project/document, file states, units/offset,
capabilities and omissions. Optional profile_id=native-model-qa-demo exposes
configured levels, labelled profile_configuration_not_native_BWS.

New queries default to `scope=open_drawings` (scope may be omitted): the host
resolves the current loaded-file inventory, includes passive files for reads and
reports the explicit list/states. Added/closed files invalidate reusable results.
Empty/ambiguous/over-100 inventory rejects; unknown states remain omissions.
This default never loads files or expands to the whole project.
Audits and metadata action=inspect retain explicit scope: 1–100 distinct positive drawing_files,
include_passive and visibility=api_select_all. Only loaded files with known states
are included; unloaded/unknown/excluded-passive scope is reported as omissions.
SelectAllElements(doc) enumerates the current document, so budgets include
outside-scope candidates. No hidden-layer/screen/whole-project completeness is inferred.

References carry session/project key/document/file/model/type identity; view UUID
is separate. Normalize passive signed file numbers while retaining state.
Missing/conflicting identities are excluded. References are read evidence with
durable_identity_verified=false and usable_for_write=false, not durable write keys.
top_level_component follows bounded parent chains and deduplicates Column,
Beam, Wall, Slab, SkeletonBeam and MultiSlab roots; arbitrary trees and other
Structural Framing families remain unaccepted.

## model_query

Schema m1-query-1, bridge /model-query.

| Action | Inputs/result |
| --- | --- |
| query | `open_drawings` default or explicit scope, optional predicate/fields/attribute_ids/profile_id/spatial_box; returns a full cached selection and first page. |
| page | selection_id and returned opaque cursor; reads a page of the revalidated full selection. |
| summary | selection_id; counts the entire revalidated selection, independent of page size. |
| inspect | Explicit scope and attribute_ids (0–32), sample_limit 1–20 (default 10); raw sampled fields/resource metadata, no cached selection. |
| profile | profile_id=native-model-qa-demo; freshly resolves named read resources, creates none. |

```json
{"action":"query","scope":{"drawing_files":[101],"include_passive":false,"visibility":"api_select_all"},"profile_id":"native-model-qa-demo","fields":["mark","status","layer_id"],"page_size":100}
```

Predicates use all/any/not or typed leaves, at most **64 nodes/depth 8**.
Scalar fields: type_name/type_uuid, layer_id/display_name, drawing_file/file_state,
`attribute:<ID>`, sizes/centers in mm and min_z_mm/max_z_mm. mark/status require
the demo profile. bounding_box_mm/hierarchy are projections, not scalar predicates.
At most **32** distinct attribute IDs are read across predicate/projection.

Operators: eq/ne/in (typed comparison), lt/lte/gt/gte (numeric), contains
(literal string), exists and is_null. Strings default to case-sensitive/untrimmed;
trim/case_sensitive are explicit. Numeric tolerance is finite, nonnegative and
absolute; strict comparisons use < v-t / > v+t, inclusive use <= v+t / >= v-t.
Attribute values retain raw attribute units; no implicit mm conversion.
Null, empty, absent and failed reads remain distinct. Unknown stays unknown under
not; all/any use three-valued logic. exists=false requires observed absence,
not a failed/passive attribute read.

Page size is **1–200** (default 100). page.complete means the last page;
is_full_selection means that page contains the whole selection. Neither proves
scope coverage. page/summary rerun the original relevant-source query, including
rejected peers; changes invalidate the cache with selection_stale. Failed
revalidation returns selection_unverifiable. Unrequested fields are not a
freshness guarantee. No cached selection/page authorizes an M3 write.

Limits: **300-second creation TTL**, **8 selections**, **5-second cooperative scan**,
**4 MiB source/report**, max_adapters **1–10000** (default 5000). Restart/expiry/
eviction require a new query. Budget failures return no partial successful count;
a blocking native call cannot be interrupted. Paging does not reduce scan cost.
Metadata samples limit output, not scanning, and do not establish writability.

Geometry uses GetModelGeometry and checked CalcMinMax; wall/slab direct-tier
unions have a **256-child** bound. Axis-aligned box extents are not rotated
cross-sections. model_local is default; project_global adds the offset once.
spatial_box uses AABB intersects/contained, inclusive/exclusive boundary and
optional tolerance_mm with a matching coordinate frame; it is not exact solid
intersection. Display-unit invariance and nonzero XY offset passed; Z offset
and arbitrary native geometry/levels remain unaccepted.

## model_audit

Schema m2-audit-1, bridge /model-audit; profile schema m2-profile-1. Exactly one
profile_id or typed profile is required; rule_ids optionally selects 1–32 rules.
Scope must be within the profile. Invalid public/host requests and unbound
resources reject before enumeration rather than returning zero findings.

```json
{"scope":{"drawing_files":[101],"include_passive":false,"visibility":"api_select_all"},"profile_id":"native-model-qa-demo"}
```

Every audit reads a fresh full snapshot, not cached selections/pages. Supported
rules: required_attribute, allowed_attribute_values, unique_attribute,
required_layer and dimension_range (AABB dimensions, not engineering checks).
Uniqueness is drawing_file + element_family + normalized value: every duplicate
member gets a finding; a singleton passes only with complete known peer data.
Raw inputs and comparison policies remain in evidence.

Demo [audit profile 2.0.0](../profiles/examples/native-model-qa.audit.json) embeds
[read profile 1.0.2](../profiles/examples/native-model-qa.demo.json). It freshly
binds MCP_QA_MARK/MCP_QA_STATUS strings and SZ_OGÓ01/SZ_OGÓ02 layer short names
by exact name/type/ID round trips. Attribute 498 is object name, not mark/status.
The demo trims, compares case-sensitively and treats absent/null/empty/whitespace/
`<niezdefiniowany>` as missing where observable. Passive absence/failed reads stay
not_checked. Binding is bound_for_read, active_for_write=false.

Report states are pass/fail/not_checked/not_applicable. Known violations can
coexist with incomplete coverage: check audit_complete, requested_scope_complete
and rule_inputs_complete, not just finding count. Findings include deterministic
context/profile-bound IDs, raw evidence, references, locations and readable remedies.
They are historical snapshots, not persistent authorization. Scan/report budgets
are the same **5 seconds / 4 MiB / adapter limit**; no partial successful audit.
For controlled repairs use the [M3 contract](m3-execution-contract.md).

## model_properties — M4 discovery probe

Bridge `/model-properties`, schema `m4-properties-1`, status **ready_for_owner_test**.
Defaults to `open_drawings` and ordinary Column/Wall roots; `native_types` may
explicitly include the other supported M1 root variants. It samples 1–20 roots
(default 10), reads up to 256 raw attribute pairs per representation, and compares
duplicate representations instead of selecting the first differing value.
Definition output is bounded to 1–128 IDs (default 64), with explicit omissions.
This is not enumeration of every attribute definition in the project.

Optional `attribute_names` (up to 16 exact names) and `layer_short_names` (up to
16 names) bind through API ID/name round trips. No resources are created. Requested
attribute IDs take precedence in the metadata budget; sampled definitions report
name, raw type/control codes, unit labels and up to 100 raw enum labels. Unavailable
fields remain not_checked. Empty enum output is an observed response, not proof
that arbitrary strings are valid writes. No raw unit/enum conversion is guessed.

The report includes runtime/package identity and a family × property × operation
support registry. `observed_in_sample` is distinct from native ownership and
accepted_on_build (still null). This tool supports no replace/add/native_update.
Material attributes, native.material, visual.surface and organizational.layer
are separate. Native wall.total_thickness is unavailable here; AABB dimensions
must not substitute for wall thickness. Door/window and wider Structural Framing
variants require later probes. Read budgets remain 5 seconds/4 MiB/5000 adapters
(explicit max_adapters up to 10000); failure returns no partial successful report.

## model_selection — M4 UI probe

Bridge `/model-selection`, schema `m4-selection-1`, status **ready_for_owner_test**.
`highlight` takes a session-bound query selection_id and optional 0–100 distinct
model-UUID exceptions. Every exception must belong to the full result. It freshly
scans the original query including rejected peers, compares full-source evidence
and resolves adapters across every page; expired/stale/unresolved data rejects
before UI calls. No live adapter is cached.

Highlight replaces **all highlights in the current document, including other
sources**. `clear_highlight` performs the same document-wide clear without a
selection ID. Documented HighlightService calls have no visibility/readback result:
state=submitted records submission counts only. selected/highlighted/not_visible
remain null until native observation; passive not_editable count is known, other
editability is not_checked. unreadable summarizes query read issues, not a claim
about native UI visibility. Incomplete scope coverage remains explicit.

`select` returns unsupported with no UI call; it never silently highlights.
CoordinateInput.GetSelectedElements describes cursor identification and is not
proof of an arbitrary native UI selection. Exceptions from highlight/clear return
state=unknown without retry; submitted counts remain null when completion is unknown.
Presentation changes no model data, activates no files and grants no write authority.
See [owner guide](m4-properties-owner-test.pl.md).

API basis checked against Allplan 2026:
[AttributeService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeService/),
[HighlightService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/HighlightService/),
[CoordinateInput](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/CoordinateInput/).
