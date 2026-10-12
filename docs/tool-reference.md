# Read and audit tools

Native acceptance is bounded to the [recorded fixture/build](validation-status.md).
These tools do not write, load/activate files, highlight or select on screen.
Use typed MCP requests; the wrapper supplies host schema versions.

## Context, scope and identity

`get_model_context` reports session/project/document, file states, units/offset,
capabilities and omissions. Optional profile_id=native-model-qa-demo exposes
configured levels, labelled profile_configuration_not_native_BWS.

New queries/audits require explicit scope: 1–100 distinct positive drawing_files,
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
| query | Explicit scope, optional predicate/fields/attribute_ids/profile_id/spatial_box; returns a full cached selection and first page. |
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
