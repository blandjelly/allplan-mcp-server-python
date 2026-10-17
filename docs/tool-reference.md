# Read and audit tools

Native acceptance is bounded to the [recorded fixture/build](validation-status.md).
Query/audit/property tools do not write or load/activate files. General query
selection presentation uses `model_selection`; the bounded M4
`model_wall_filter` action combines its own fresh Wall scan/read with highlight
submission as described below.
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

## model_properties — suspended after native crash

Bridge `/model-properties`, schema `m4-properties-1`. The 0.16.0 native gate
failed with an Allplan crash on its first request. Valid requests now return
native_probe_blocked **before build/document/API reads**. Do not repeat the broad
experiment. No runtime/writable support may be inferred from its portable tests.
[Incident and limits](m4-native-crash-0.16.0.md).

The dormant implementation has also stopped unconditional GetEnumValues calls.
That code issue is not a proven explanation of the crash. The former automatic
Column/Wall discovery, all sampled definitions and UI chain remain suspended.

## model_property_probe — isolated read phases

Bridge `/model-property-probe`, schema `m4-property-probe-1`. Exactly one phase
is required, with only its declared parameters:

| Phase | Parameter / native work |
| --- | --- |
| column_sample | drawing_file: one explicit foreground file; existing M1 Column scan, then raw GetAttributes(ReadAll) on one unambiguous root adapter. |
| attribute_name | attribute_name: one exact project name; GetAttributeID and, if observed, GetAttributeName round trip. |
| attribute_definition | attribute_id: one ID observed from project metadata/sample; name/type/unit/control readers, stopping at first unavailable value. |
| layer_name | layer_short_name: one exact short name; native ID/name round trip, no creation. |
| wall_sample | drawing_file (required integer) and optional model_uuid: one foreground file and one exact native Wall root; reads tier count and, only for a single-tier Wall, tier 1 thickness and raw material. |

The historical isolated Column observation invoked only `column_sample` in file
101. The new 0.18.0 wall candidate invokes only `wall_sample` in file 101; its
289 portable tests, six CI jobs and exact package installation passed, making it
**ready_for_owner_test**. No phase is a prerequisite for another package's native test.

For `wall_sample`, `drawing_file` is required and must identify one foreground
file. Optional `model_uuid` must be canonical and nonzero; explicit null is
invalid. The M1 query includes required `type_name`, `type_uuid`, and identity
fields plus `display_name` and `file_state`; it requests no attributes or
geometry. It counts matched Wall roots while retaining native container owners,
then selects the exact requested UUID or, when omitted, the first accepted Wall
in deterministic UUID order. A requested UUID with no exact match has no
fallback. The host imports `NemAll_Python_ArchElements`, resolves only the
selected element with `GetElement`, verifies `isinstance(WallElement)`, and
reads `.Properties` and `.TierCount`. A tier count other than 1 returns
unsupported before any tier read. Otherwise it reads only
`GetWallTierProperties(1).Thickness` and `.Material`; it does not read native
thickness from every matched Wall.

Thickness must be positive and finite; the bounded material is returned as a
raw string. `sample.criterion.matches_assuming_native_mm` reports strict `<240`
only after both fields are valid and under an API-mm assumption. The response keeps
`units_runtime_verified=false`, `material_target_binding=not_checked`, and
`material_write_available=false`. There is no all-walls filter, highlight,
Apply, resource/metadata/enum discovery, or model write. A native wall read must
be observed before enabling material writes.

No batch or automatic continuation is invoked. Raw absence/null/empty/undefined/
error values retain their distinction. Adapters and containers are never saved
in the JSON query cache.

Before every new native reader a started record is appended, flushed and fsynced
in **Local/.allplan-mcp/logs/m4-native-probe.jsonl**; returned/failed records follow.
The wall phase also flushes and fsyncs every new native boundary before moving
to its next read.
M1.column_scan / M1.wall_scan are recorded as existing service phases, not every internal API
call. Each phase has a probe_id and UTC timestamps; values/private environment
are not logged. Unwritable/full tracing (1 MiB) blocks further calls; it is not
pruned automatically and is separate from the M3 execution journal. No native
crash containment is promised by these file records.

The wall diagnostic atomically saves and fsyncs `request_pending` before sending
its one MCP call, then records the structured response. The launcher brackets
that request with `health_before` and `health_after` replies from the same host
session. A lost reply never causes an automatic retry or following native call.
Read budgets remain 5 seconds and inherited M1 scan limits; failed native observations do
not establish support. The 0.18.0 wall observation remains pending; automated
checks do not establish accepted_on_build. [Source and delivery evidence](../evaluation-packages/0.18.0/README.md).
[Wall guide](m4-wall-properties-0.18.0.pl.md). Historical isolated Column
[owner guide](m4-isolated-probe-owner-test.pl.md).

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

## model_wall_filter — M4 wall thickness filter

Schema `m4-wall-filter-1`, bridge `/model-wall-filter`; 0.19.0 source, CI and exact
package checks passed; [scoped native filter/highlight/clear PASS](m4-wall-filter-observation-0.19.0.md). The request
contains `action=query|highlight`, one explicit `drawing_file`, optional
`threshold={value,unit}` (`mm`, `cm`, `m`; default 24 cm), optional up to 100
distinct canonical nonzero `exclude_model_uuids`, and `max_walls` (default 20,
maximum 100).

```json
{"action":"highlight","drawing_file":101,"threshold":{"value":24,"unit":"cm"},"max_walls":20,"exclude_model_uuids":[]}
```

The handler freshly scans exactly one active foreground drawing with M1's
`Wall_TypeUUID` native type gate and `top_level_component` roots. It requires
complete requested-scope and returned-field coverage, and caps the full Wall
set before reading properties. Exclusions must be members of that full Wall
set; excluded roots are not read. It resolves all required root adapters before
the first property read, then reads each nonexcluded root once. Only
`NemAll_Python_ArchElements.WallElement` with exactly one tier is supported;
the only property read is tier 1 `Thickness`. Conversion is to millimetres,
then a strict `< threshold_mm` comparison is used. Threshold default is 240 mm.

Any incomplete M1 coverage, over-limit set, unresolved adapter, unsupported
type/tier, failed read, or exhausted budget stops before UI dispatch, so no
partial highlight is submitted. One fresh scan/read and, for `highlight`, one
UI dispatch occur per request; no cached selection or saved write plan is
created. `query` returns `state=observed` without UI calls. A complete
`highlight` result calls `CancelAllHighlightedElements` for the current
document, then submits matches if any. Thus zero matches clears prior document
highlights. This replaces all highlights in that document, including ones
from other sources. A UI exception after calls begin returns `state=unknown`;
do not retry automatically.

Responses report `criterion_complete`, coverage, per-Wall `status`,
`thickness_mm`, `match`, and counts for total/matched/excluded/unreadable and
unprocessed Walls. Highlight submission reports requested/submitted model and
adapter counts only. Native visible/selected/not-visible counts remain null;
they require owner observation. `native_selection=unsupported`,
`units_runtime_verified=false`, `model_data_changed=false`,
`usable_for_write=false`, and `material_write_available=false`. The handler
does not read material, attributes, or metadata and invokes no setters. The
owner workflow saves a pending record and fsyncs it before each MCP call,
brackets the filter call with same-session health, and never retries a lost
reply. See the [0.19.0 owner guide](m4-wall-filter-0.19.0.pl.md).

## column_layer (0.17.2 candidate)

`preview` requires one foreground `drawing_file`; defaults resolve the exact
candidate names `Klasa odporności ogniowej` / `Fire resistance classification`
and existing `W1`. IDs come only from native name/ID/name roundtrips; there is no
fallback to `Odporność ogniowa` (1398) and no hardcoded binding to 935.
An explicit `attribute_names` list, `undefined_values` and `exclude_model_uuids`
can refine the request. Multiple distinct resolved IDs block; no IDs are guessed.
Null/empty/explicit undefined values match. Absent from ReadAll, unreadable and
unsupported values remain unknown; no Apply on an incomplete plan.

The 0.17.2 plan binds both `highlight_targets` and `changes` into its hash.
`highlight_targets` contains references whose criterion decision is `change` or
`no_op`; `changes` contains only `set_layer` operations. `counts` reports
`highlight_targets`. A complete supported plan makes
`evaluation_highlight_available=true`, including a no-op plan, while
`evaluation_apply_available=false` when there are zero changes. A mixed plan
can apply its changes while its no-op matches remain unwritten. The
launcher verifies the reported count against `highlight_targets` and highlights
all matches, regardless of current W1 state. Zero matches clear old highlights.
Unknown criteria block the whole action; more than 32 changes remain blocked.

`highlight` / `revalidate` take `plan_id` and `plan_hash`. `apply` additionally
takes a persisted `execution_id` and `acknowledgement=disposable_copy_reviewed_plan`.
Only changes can be confirmed and sent to setters. A no-op plan still runs
highlight, with no confirm/Apply path. Confirmation lists all matched targets
and separately lists the changes. Both full source and resource bindings are
checked again. Shared M3 journal/preflight/readback/recovery limits apply (up to
32 Column layer changes). `recover` takes only the original execution_id and
never invokes setters. This is highlighting, not native selection, as agreed
for this workflow.
[0.17.2 owner guide](m4-column-layer-0.17.2.pl.md).

The 0.17.1 native observation confirmed the field binding and two writes but
submitted only two highlight targets, omitting a matching no-op. See the
[observation report](m4-column-layer-observation-0.17.1.md). The 0.17.2 candidate
is **ready_for_owner_test** after 275 portable tests, six CI jobs and exact ZIP
installation verification passed. Source and evidence scopes are in the
[delivery README](../evaluation-packages/0.17.2/README.md). Native observation is pending.

The 0.17.0 owner run bound the wrong field, 1398, and stopped with six unknown
ReadAll omissions before setters. A healthy `health_before` and available journal
do not establish a healthy full run without `health_after`. See
[validation status and original evidence](validation-status.md).
Official [2026-1 attributes](https://help.allplan.com/Allplan/2026-1/1034/Allplan/326206.htm)
identify 935 as Fire resistance classification (String), and the
[SDK example](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/BasisExamples/MacroWithElementGroup.py#L164)
sets it to F30. The [attribute tutorial](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
instead illustrates 1398 as Fire risk factor with A1/A2. These distinguish the
fields; runtime project resources still determine the binding.
