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
Scalar fields: type_name/type_uuid, family, opening_kind, layer_id/display_name, drawing_file/file_state,
`attribute:<ID>`, sizes/centers in mm and min_z_mm/max_z_mm. mark/status require
the demo profile. bounding_box_mm/hierarchy are projections, not scalar predicates.
At most **32** distinct attribute IDs are read across predicate/projection.

Operators: eq/ne/in (typed comparison), lt/lte/gt/gte (numeric), contains
(literal string), exists and is_null. Strings default to case-sensitive/untrimmed;
trim/case_sensitive are explicit. Numeric tolerance is finite, nonnegative and
absolute; strict comparisons use < v-t / > v+t, inclusive use <= v+t / >= v-t.
Attribute values retain raw attribute units; no implicit mm conversion.
`family` uses exact supported native adapter names; `opening_kind` applies only
to `WindowDoor_TypeUUID`, uses runtime element-class checks, and returns
`not_applicable` for other adapters. Unsupported opening representations are
`not_checked` and keep predicates incomplete.
Null, empty, absent and failed reads remain distinct. Unknown stays unknown under
not; all/any use three-valued logic. exists=false requires observed absence,
not a failed/passive attribute read.

Query `attribute_read_mode=all_and_computable` opts into a paired
`ReadAll`/`ReadAllAndComputable` read for requested attribute IDs; `stored` stays
the default and the legacy path is unchanged. It can expose a value present only
in the computed-inclusive read as `computed_only=true`, which is read evidence,
not an editable stored value. Proven absence requires successful agreement and
complete coverage in both reads. The mode is included in source fingerprints so
revalidation cannot reuse evidence from the other mode. Query remains read-only.

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
[Incident and limits](test-results/m4-native-crash-0.16.0.md).

The dormant implementation has also stopped unconditional GetEnumValues calls.
That code issue is not a proven explanation of the crash. The former automatic
Column/Wall discovery, all sampled definitions and UI chain remain suspended.

## model_property_probe — isolated read phases

Bridge `/model-property-probe`, schema `m4-property-probe-1`. Exactly one phase
is required, with only its declared parameters:

| Phase | Parameter / native work |
| --- | --- |
| drawing_identity | drawing_file, optional offset/limit: bounded paged inventory for one exact foreground drawing; reports each API-enumerated adapter's model/view UUID, bounded lineage, and represented native type. Every page is a new scan; compare its membership/type/state fingerprint. Fingerprint agreement does not guarantee an atomic hierarchy snapshot. No attributes, property-owner inference, UI calls or setters. The page limit is at most 32. |
| column_sample | drawing_file: one explicit foreground file; existing M1 Column scan, then raw GetAttributes(ReadAll) on one unambiguous root adapter. |
| attribute_name | attribute_name: one exact project name; GetAttributeID and, if observed, GetAttributeName round trip. |
| attribute_definition | attribute_id: one ID observed from project metadata/sample; name/type/unit/control readers, stopping at first unavailable value. |
| element_attributes | drawing_file, model_uuid, view_uuid; optional name_contains, offset, limit: one exact foreground semantic component, paged ReadAll values and targeted name/ID roundtrip plus SDK scalar type metadata. |
| component_identity | drawing_file, model_uuid, view_uuid: one exact direct foreground adapter, bounded full parent chain and direct children, and represented native Python type from GetElement; no attributes, geometry, metadata, UI or setters. |
| layer_name | layer_name or legacy layer_short_name: exact full/short name lookup with fresh ID/name round trips; requests catalog search when the SDK lacks full-name lookup. |
| layer_catalog | layer_name, optional offset/limit (default/max 8192 IDs): read-only Allplan 2026 name search over bounded ID pages, with a 3-second soft page budget, continuation and user-confirmation candidates. |
| wall_sample | drawing_file (required integer) and optional model_uuid: one foreground file and one exact native Wall root; reads tier count and, only for a single-tier Wall, tier 1 thickness and raw material. |

The historical isolated Column observation invoked only `column_sample` in file
101. The later scoped `wall_sample` observation is recorded in the
[validation index](validation-status.md). No phase is a prerequisite for another
package's native trial.

`component_identity` retains direct Slab and MultiSlab identities separately.
It requires consensus across wrappers for the requested model/view pair; other
views are disclosed without being treated as property-owner evidence. Lineage
has at most 16 parent reads, children at most 256 entries, wrappers at most 64,
within the shared 5-second budget. Cycles, cross-file edges, inconsistent child
owners and unavailable representations fail with `probe_scope_unavailable`.
The native type, ancestry and children do not prove physical equivalence or
the owner of an attribute/material/layer. The optional query field
`component_ownership` returns observed/not_checked structural evidence; it
cannot be used as a predicate. Default query reads are unchanged.

Candidate 0.26.0 adds `drawing_identity` for a bounded inventory of one
foreground drawing. This inventories model/view identity, lineage, and native
representation across pages; it does not turn a structural inventory into
field ownership, nor merge Slab/MultiSlab targets. See the
[0.26.0 short trial](m4-single-drawing-0.26.0.pl.md).

From 0.24.0, typed model-edit plans include slab ownership evidence. Slab
children and all MultiSlab aggregate writes are blocked pending an explicit
property-owner adapter; no automatic redirection or bounds-based merging is
allowed. A standalone Slab binds its hierarchy into the plan, rechecks it
before writing, and rejects changed/unavailable ownership at fresh readback
or recovery. Old slab plans without ownership evidence cannot authorize new
setters; exact-ID journal replay remains setter-free.

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

`element_attributes` requires one active foreground drawing and exact nonzero
`model_uuid`/`view_uuid`; it resolves one unambiguous semantic root adapter
across the supported component families. `name_contains` is a case-insensitive
substring filter over names returned by `ReadAll` (maximum 64 characters).
`offset` is 0–255 and `limit` is 1–32 (default 32). Each returned row includes
the raw value, attribute ID, observed name and name/ID roundtrip, and targeted
`GetAttributeType` metadata when available. `supported_scalar_value_types`
contains only text/integer/real/boolean types matching loaded SDK members
directly. If any name roundtrip or page type is unavailable, completeness and
the total match count are unknown and `next_offset` is omitted. Omissions from
`ReadAll` remain unknown; this phase is not a project definition catalog and
does not establish attribute applicability or writability. It makes no writes
and does not read enum, control, or unit metadata.

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
not establish support. See [retained native observations](validation-status.md)
for scoped results; superseded trial instructions have been removed.

## model_selection — M4 UI probe

Bridge `/model-selection`, schema `m4-selection-1`; native selection remains
unsupported, while scoped highlighting has owner observations.
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
Native selection remains unsupported; highlighting does not prove UI selection.

API basis checked against Allplan 2026:
[AttributeService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeService/),
[HighlightService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/HighlightService/),
[CoordinateInput](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/CoordinateInput/).

## model_wall_filter — M4 wall thickness filter

Schema `m4-wall-filter-1`, bridge `/model-wall-filter`; 0.19.0 source, CI and exact
package checks passed; [scoped native filter/highlight/clear PASS](test-results/m4-wall-filter-observation-0.19.0.md). The request
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
reply. See the [0.19.0 owner observation](test-results/m4-wall-filter-observation-0.19.0.md).

## model_edit — typed edits, exact deletion and Wall material

Schema `m4-model-edit-1`, bridge `/model-edit`. This is an experimental
preview/apply path for edits selected by a criterion, independent of audit
findings. It supports exact attribute targets with `text`, `integer`, `real`,
`boolean`, or explicitly selected `enum` values and modes `replace`, `add`, or
`upsert`, plus a separate existing organizational layer target. Candidate
0.25.0 adds two exclusive operations: `target={"kind":"delete"}` with no
value, or `target={"kind":"native_material","tier_index":1}` with an exact
material string. Each must be the only change in its plan.
`value_type=auto` (the default) infers the type from the exact bound attribute's
loaded SDK type, including Enum when an exact display label passes the targeted
label/key round trip. JSON booleans for Integer fields are encoded as 1/0 only
when targeted SDK metadata confirms `AttributeControlType.CheckBox`; this codec
is hash-bound and rebound before Apply. Other integers do not accept booleans.
It never parses a string to infer a type. Attribute values such as
`Beton C37` remain distinct from a wall's native material and visual surface.
Date/vector/object attribute codecs and general attribute catalog discovery
are outside this contract.

### `delete` — exact component root only

The delete target is eligible only for a terminal supported component root in
one active foreground drawing, with one narrow exception: a `WindowDoor_TypeUUID`
opening is independently deletable when its complete lineage is exactly
`[opening, Wall root]` (no macro ancestors). The operation binds only that
opening and its owned subtree; it never redirects to the parent Wall. Slab
children remain blocked unless covered by the full subtree of an explicitly
selected `MultiSlab_TypeUUID` root. Planning binds the exact target identity
and its complete owned subtree, bounded to 256 adapters including the target.
A child selected without its owning root is blocked, except for the documented
opening case. If both a root and a child inside its reviewed subtree match, the
child is suppressed as covered by the root; an exclusion that crosses that
subtree blocks deletion of the root. Incomplete hierarchy, cycles, cross-file
ownership, or an over-budget tree block the plan.

Apply calls `DeleteElements(doc, [target_adapter])` once. Cascade behavior is
not assumed. Completion requires a fresh complete identity scan of the planned
target and every bound descendant and confirmation that all are absent. For an
opening target, its parent Wall must still be present; disappearance of the
parent makes the result unknown. A partial subtree, unreadable scan, or timeout
leaves an unknown result; recover the same execution ID without repeating
deletion. The shared journal, exact target binding, confirmation, and setter-free
replay/recovery safeguards apply.

Candidate 0.26.0 exposes delete diagnostics in
`blocked[].observation.reason` and `blocked[].observation.diagnostic` (`stage`,
`error_type`). One fresh read-only preview may inspect the exact existing
blocked target. This reporting does not relax exact lineage, subtree
completeness, exclusion, confirmation, fresh absence/parent checks, or
unknown-result recovery.

### `native_material` — experimental single-tier Wall only

The only accepted form is an exact nonempty string of at most 255 characters
and explicit `tier_index=1`. The target must resolve to a standalone
`Wall_TypeUUID` represented by `WallElement`, have exactly one tier, and have
no `WindowDoor_TypeUUID` children. No material catalog lookup, existence claim,
alias resolution, surface edit, or attribute substitution occurs.

The plan binds the current material, complete bounded hierarchy, valid tier
`Polyhedron3D` stream hash, and explicit tier/common scalar and axis/plane/
surface preservation representations. Apply rechecks this evidence, invokes
`SetMaterial(exact_string)` on tier 1, reattaches the same `WallProperties`,
and submits the existing Wall through `ModifyElements`. Fresh readback must
match the requested material and the bound preservation evidence. Drift or an
incomplete observation blocks Apply or leaves recovery to the same execution
ID; setters are never retried. This adapter is experimental and has no native
Allplan acceptance yet. The narrow trial is in
[the archived 0.25.0 instructions](m4-single-drawing-0.25.0.pl.md); SDK evidence
and its limits are in [the API note](m4-editing-api-0.25.0.md).

For candidate 0.26.0, a fresh read-only preview of the exact existing blocked
Wall exposes `blocked[].observation.reason` and
`blocked[].observation.diagnostic` (`stage`, `error_type`); when
`old_value_unknown`, retain `criteria.required_field_failures` as well. No Apply
is needed to inspect this diagnostic. It explains why a guarded path stopped
and does not authorize bypassing ownership, identity, revalidation, journal, or
readback guards.

The default native type list is Column, Beam, SkeletonBeam, Wall, Slab,
MultiSlab, and the documented `WindowDoor_TypeUUID` opening adapter. Without
an additional criterion, an opening is not classified as a door or a window.
The optional `opening_kind` predicate field can request `door` or `window`;
the reader resolves the element with `GetElement(adapter)` and checks the
documented `DoorOpeningElement` or `WindowOpeningElement` runtime class. If
the representation cannot be resolved or is another class, the field is
`not_checked` and the criterion is incomplete; non-opening adapters return
`not_applicable`. This defensive reader has not received native acceptance.
No undocumented `Door_TypeUUID` or
`Window_TypeUUID` is used; other adapter types remain outside the supported
set.

Preview defaults to `scope=open_drawings`; reads can include passive open
drawings, while Apply is limited to one active foreground drawing. A predicate
can use a resolved `attribute:<id>` field with `is_unset`. The default
`attribute_read_mode=stored` treats `ReadAll` omissions as unknown. The
explicit opt-in `all_and_computable` mode is required to treat an omission as
absent, and only after a complete read. A value found only by the computed read
is returned with `computed_only=true` and cannot be treated as an editable
stored attribute. A failed, partial, or unsupported read still blocks the
decision. Existing routes using the default `stored` mode retain prior
ReadAll behavior.

Resolve attribute names against the current document's metadata before
planning; never invent numeric IDs. The native path checks name/ID round trips
and compares targeted `GetAttributeType` results with actual loaded SDK enum
members for supported scalar values; it uses no guessed numeric type codes.
`value_type=auto` infers primitive scalar types and exact SDK Enum labels.
Integer/String-backed enumerations require explicit `value_type=enum` and an
exact display label. The host verifies the
loaded SDK attribute type is `Enum`, `Integer`, or `String`, resolves the label
with `GetEnumIDFromValueString`, roundtrips key to label with
`GetEnumValueStringFromID`, and verifies label to key again. It does not call
`GetEnumValues` or enumerate an enum catalog. The stored setter value and
readback remain the exact label; the hash-bound resource also records the
resolved `enum_binding` key/label and is rebound during preflight. Date and
vector attribute targets remain blocked: the documented attribute-container
classes do not establish an accepted existing-adapter setter payload and exact
fresh-readback codec for this contract.
Allplan's published metadata API does not itself establish that an arbitrary
attribute is writable. `ChangeAttributes` can append an existing attribute
definition to an element, but this route does not create project attribute
definitions or layers. Apply additionally re-resolves resources, checks old
values, records the request before setters, and performs a fresh readback.
Native acceptance of this new setter path is pending.

Layer targets accept either legacy `short_name` or `name` (full or short),
never both. Search both names with `model_property_probe` before declaring a
user-supplied name unresolved. Allplan 2026 lacks a documented direct full-name
lookup, so follow the `layer_catalog` page requests returned by `layer_name`.
The catalog verifies candidate IDs through short-name round trips, preserves
Polish diacritics, and reports range coverage and read errors separately.
When it requests confirmation, show the actual full name, short name and ID,
then use its returned `confirmed_targets` entry in a fresh preview, preserving
`expected_layer_id` and `expected_name` along with the short name. The binder
and Apply revalidation check those exact values. `continue_search` remains
available after a partial page finds a candidate, so later duplicate names can
be collected; partial search never implies a unique global match. A partial
scan never authorizes an edit or proves absence. No layer is created or renamed.

M4 recovery verifies the current project key and document ID, then observes
only the journal's exact targets. An unrelated incomplete criterion scan cannot
prevent that read-only reconciliation. It never resumes, retries or rolls back
setters. A known old/new value reconciles an unknown outcome; unreadable or
conflicting outcomes keep the journal block. Recovery reports blockers for the
whole journal and a next action. For SDK-bound real attributes, finite numeric
`5`/`5.0` compare equally during verification/recovery; raw values remain retained,
and boolean/integer identity is unchanged. Positive null/deleted wrappers are
counted and skipped before component hierarchy traversal; unknown hierarchy
remains incomplete. These changes also support recovery of retained 0.21.1
records without changing their execution IDs.

For multiple views, M4 recovery and post-write verification read all exact live
model/type/drawing roots, including distinct wrappers with the same view UUID.
`representation_consensus` records completeness, lifecycle/read evidence and
agreement. Per-representation readbacks use typed-observation hashes to bound
journal size; the common raw observation remains in the outcome. Only unanimous
typed values can reconcile a journal outcome; no view
is chosen to hide a conflicting read. New previews bind `target_view_uuid` into
the plan hash for one exact setter target, after agreement across representations.
A missing reviewed view or a disagreeing/unreadable representation blocks writes.
Legacy records need no view binding for read-only recovery.

Example shape for a simple Column: the `attribute:<ID_FROM_PROBE>` token below
is a placeholder for the numeric ID actually resolved in the current
document. An agent should derive this request from the user's natural-language
instruction, not ask the operator to guess IDs or write JSON.

```json
{
  "action": "preview",
  "scope": "open_drawings",
  "native_types": ["Column_TypeUUID"],
  "attribute_read_mode": "all_and_computable",
  "predicate": {"field": "attribute:<ID_FROM_PROBE>", "op": "is_unset"},
  "changes": [
    {"target": {"kind": "attribute", "name": "Klasa odporności ogniowej"},
     "value_type": "text", "value": "F120", "mode": "upsert"},
    {"target": {"kind": "layer", "short_name": "W1"}}
  ]
}
```

Preview and revalidate are read-only. The Apply acknowledgement is
`disposable_copy_reviewed_plan`; Apply requires the exact highlighted
`plan_id`/`plan_hash` and a persisted new `execution_id`. It is capped at 32
actual setters and one foreground drawing. More than 32 changes, multiple
write drawings, and uncertain coverage are blocked before setters; there is no
automatic batching or hidden partial multi-drawing Apply. Lost replies remain
unknown and require recovery with the same execution ID. This is not full K6
acceptance. See the [Polish operator guide](m4-model-edit.pl.md) and [Allplan
2026 API evidence](m4-attribute-api-evidence.md).

For this evaluation route, public `apply_available` reports whether the
evaluation Apply is offered. `evaluation_apply_available` is a compatibility
alias; `production_apply_available=false` separately records that production
write capability is unavailable. Pending native acceptance does not disable an
otherwise eligible evaluation Apply. Do not present an experimental Apply as
natively accepted. After the user authorizes the write, continue when
`apply_available=true` and the exact highlighted plan/hash, explicit
`disposable_copy_reviewed_plan` acknowledgement, fresh revalidation, execution
ID, and other Apply guards are satisfied. If a guard is missing, explain that
specific requirement; do not cite production unavailability or pending native
acceptance as the reason.

Preview/highlight responses distinguish evaluation from production through
`write_mode`, `usable_for_write`, `write_blockers`, and
`native_acceptance_blocks_evaluation=false`. They provide `required_steps` and
an actionable `next_action`; use its exact `model_edit` request after the user
has authorized the write and all listed requirements are satisfied. For Apply,
`next_action.required_request_fields` requires a newly generated UUID4 hex
`execution_id`, persisted before sending. Revalidate carries eligibility
forward only while the original plan remains eligible and unchanged.

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
The historical 0.17.1 native observation is retained in
[the observation record](test-results/m4-column-layer-observation-0.17.1.md).

The 0.17.1 native observation confirmed the field binding and two writes but
submitted only two highlight targets, omitting a matching no-op. The owner later
confirmed the corrected no-op highlighting through the same handler in 0.18.1.
See the [observation index](validation-status.md) for both scoped records.

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

## M4 0.20.1 — undefined numeric attributes and Wall layer owners

`model_edit` retains raw undefined strings in old_value. For exact
`<niezdefiniowany>` / `<undefined>` and metadata-bound integer/real/boolean
fields, a hash-bound old_value_state=undefined permits replace/upsert. Other
strings, computed-only values, failed reads and ReadAll omissions remain blocked.
The policy is reported in preview; it does not parse or normalize raw text.

Wall layer changes use internal operation `set_wall_layer` with a reviewed
resource.wall_layer_ownership manifest of the root and its directly owned
WallTier identities/layers. Every tier is checked before journal/setters; one
ChangeLayer targets tiers only, followed by fresh owner/aggregate layer readback.
Mixed tier layers and missing/conflicting ownership block the plan. Historical
set_layer journal records retain their legacy root-adapter readback.
Current layer IDs are valid throughout the inclusive range 0–65535; ID 0 is a
real value and must not be treated as absent or false. W1 is resolved by its
native name/ID round trip and is a positive ID. The 0.26.0 implementation change
is covered by automated tests; native verification is limited to a fresh
read-only current-layer observation if the exact Wall reports ID 0. See the
[0.26.0 short trial](m4-single-drawing-0.26.0.pl.md).

`model_query` adds optional layer_resolution=adapter (default) or component.
Component resolution requires semantic_component and reads Wall layer_id from
the directly owned tiers, returning not_checked for mixed/unknown layers.
Other component families use their existing layer reader. model_edit selects
component resolution for layer predicates/edits automatically. Neither mode
changes the native model. Current scope and next steps are in the
[M4 handoff](next-model-handoff.md).

`wall.total_thickness_mm` is a query/edit criterion read from native single-tier
Wall properties in mm, without geometry approximation. Multi-tier or unknown
representations return not_checked. A model_edit predicate such as `< 240`
binds thickness for the full Wall peer set and revalidates it before writing,
including previously nonmatching peers; use it instead of a separate UUID handoff.

## Confirmed journal maintenance — M4 0.23.0

The shared `fix_model_issues` tool offers storage maintenance without native
model/document access. Keep the three limits distinct: active diagnostic trace
`m4-native-probe.jsonl` is 1 MiB; active execution history holds 128 records;
each execution record has a separate 1 MiB verification/persistence limit.
A full trace can block a model-edit preview before any setters. A full execution
journal blocks new IDs while retained-ID replay remains available.

1. On a capacity error, call `preview_journal_cleanup` with `target=native_trace`
   or `target=repair_records`. The model-edit response provides the tool/request
   hint. `inspect_journal` also reports trace usage and both cleanup options.
2. Show the active bytes/count, archival scope and protected records; **ask the
   user whether to clean that journal**. Preview never modifies journal data.
3. Only after confirmation send the returned `after_user_confirmation` request:
   `cleanup_journal`, the same target and `snapshot_hash`, and
   `acknowledgement=confirmed_journal_cleanup`. No caller paths or delete flags.
   A changed snapshot requires a new preview and confirmation.

`native_trace` atomically moves the exact reviewed bytes into a sibling
`m4-native-probe-archive/<sha256>.jsonl`; subsequent trace events start a new file.
Appenders and rotation share an OS lock. No model operation is retried. Trace
archives are preserved; preview uses bounded metadata samples, explicitly
reporting incomplete archive coverage. They are not automatically expired.

`repair_records` moves only verified, resolved records to `repairs/archive/`.
Running/unknown, corrupt, oversized, unsafe and colliding entries stay active.
Their blockers remain; cleanup never reconciles them. Archived IDs remain
available for exact-request replay without setters, even after restart. Archived
Recover returns historical resolved state and does not claim current UI values.
Active+archived conflicts fail closed. A partial batch preserves every ID in one
location; inspect/preview again to see remaining candidates. A lost cleanup reply
can be resolved by fresh inspection; never retry the interrupted model edit
blindly. Archive retention/export and disk-space policy are separate work.

A cleanup inventory covers up to 1024 active records / 64 MiB. Trace inspection
accepts up to 16 MiB of legacy oversized data. Beyond these bounds or on I/O
failure, maintenance fails safely and keeps the data. Oversized/unverifiable
execution records are not deleted to unblock writes.

[Owner trial](m4-journal-cleanup-0.23.0.pl.md) ·
[Current development plan](office-editing-development-plan.pl.md).
