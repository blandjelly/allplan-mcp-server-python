# M1 scope and model query contract — 0.4.0

Status: **implemented; three bounded owner query cases PASS**. Schema
`m1-query-1`, public MCP tool `model_query`, typed bridge route `/model-query`.
This is a bounded M1.1–M1.3 slice. The accepted 0.2.1 context reader is reused;
its raw units/offset and context probe schema retain their earlier meaning.
[0.3.0 evidence and limits](test-results/m1-query-runtime-0.3.0.md) verify scope,
metadata, two distinct pages/full summary and observed-value predicates on the
owner's two-column scene. Other predicate variants, changed-source stale checks,
TTL/restart and geometry do not gain runtime acceptance from that batch.

## Scope and identity

Every new query requires `scope.drawing_files` (1–100 distinct positive numbers),
an explicit `include_passive` boolean and `visibility: api_select_all`. No default
current-file or whole-project query is inferred. Only requested, currently loaded
files with known foreground/background/passive states are included. Unknown,
unloaded and deliberately excluded passive files are reported in `omissions`.
An included empty loaded file has an observed zero result. No files are loaded,
activated, selected on screen, highlighted or edited by this tool.

The 2026 API exposes `SelectAllElements(doc)`, without a documented drawing-file
parameter. The host enumerates that current-document candidate list, checks its
signed file number, and reads requested properties only inside the resolved
scope. Adapter/time limits therefore cover the entire candidate enumeration,
including outside-scope adapters. This does not establish hidden-layer, screen,
occlusion or whole-project coverage. No visibility state is changed.

References contain the query-handler session ID, current project name/host/path
key, document ID, normalized drawing-file number, model UUID and observed adapter
type UUID. View UUIDs are stored separately. Negative passive numbers are retained
as evidence while normalized identity uses the positive file number. A negative
number inconsistent with the inventory is excluded and reported. Project names
and `document_id=0` are never treated as unique project identities on their own.
If project key, document ID or file inventory cannot be read, querying fails with
`context_unavailable`; it does not reuse previous context.

Identical file/model UUIDs are combined across returned representations. If
requested/mandatory fields disagree, that identity is excluded as a conflict.
Missing model/type UUIDs are excluded; an unavailable view UUID is separately
reported. Counts describe **unique file/model UUIDs**, not top-level native
components, children, wall tiers or geometric solids. Parent/child resolution is
pending. References are session-bound read evidence with
`durable_identity_verified: false` and `usable_for_write: false`.

## Predicates and fields

`predicate` is optional (all identifiable in-scope candidates). Use exactly one
of `all: [...]`, `any: [...]`, `not: {...}`, or a leaf `{field, op, ...}`. Groups
must be nonempty; the complete tree is validated before enumeration, with at
most 64 nodes and depth 8. Unsupported keys, geometry/dimension/spatial predicates
and profile arguments are errors, never ignored filters.

Supported fields: `type_name`, `type_uuid`, `layer_id`, `display_name`,
`drawing_file`, `file_state`, and `attribute:<positive integer ID>`. Type names
come from `GetTypeName()`, type GUIDs from `GetGuid()` and layers from common
properties. Use observed values; localized display names are not unique IDs.
Defaults project `display_name` and `layer_id`. Model/type identity is mandatory;
predicate fields are also returned. `attribute_ids` adds explicit projected
attributes. At most 32 distinct attribute IDs are read across predicates and
projection. No attribute call occurs without an attribute request. The 2026
adapter provides `GetAttributes(ReadAll)`; only requested IDs/values are retained
or returned. Attribute metadata/profile bindings are not guessed.

| Operator | Meaning |
| --- | --- |
| `eq`, `ne` | Typed equality/inequality; numbers compare numerically, booleans differ from numbers, strings are never converted to numbers. |
| `lt`, `lte`, `gt`, `gte` | Numeric only. With absolute tolerance `t`, strict boundaries use `< v-t` / `> v+t`, inclusive boundaries `<= v+t` / `>= v-t`. |
| `in` | Equality against 1–100 scalar alternatives, without numeric tolerance. |
| `contains` | Literal string substring, without patterns or regular expressions. |
| `exists` | True for a successful present value (including null), false for an observed missing attribute. |
| `is_null` | True only for an observed null; a missing field is unresolved. |

Strings are case-sensitive and untrimmed by default. `case_sensitive: false`
uses Unicode casefold; `trim: true` strips leading/trailing whitespace. Numeric
`tolerance` is finite, nonnegative and absolute; default zero. Attribute numeric
values remain **raw attribute units**. They are not native geometric dimensions
in mm: the documentation's dimensional attributes can use metres. No implicit
unit conversion occurs. Null is supported in the JSON predicate contract; this
does not claim native Allplan attributes normally return null.

Each read has `observed`, `missing` or `not_checked` status. Empty string, zero
and null remain distinct. Failed reads and comparisons of incompatible ordered
types evaluate to unknown (`not_checked`). Missing values compare as unknown
except `exists=false`. `not` preserves unknown; `all` is false if any child is
false, otherwise unknown if any child is unknown; `any` is true if any child is
true, otherwise unknown if any child is unknown. Unknown identities/predicates
are counted and excluded, with up to ten diagnostic samples. Do not interpret
zero matches as a successful complete audit when coverage is incomplete.

## Paging, full selections and staleness

`action: query` creates a JSON snapshot with a random `selection_id` and the
first page. `page_size` is 1–200 (default 100). `action: page` takes that ID and
an opaque returned `cursor`; omit the cursor to read the first page. Cursor
ownership is checked. Ordering is deterministic by file number/model UUID.
`page.complete` means the last page was reached;
`page.is_full_selection` means this single page contains the whole selection.
Neither means the requested scope was complete: inspect `coverage` and omissions.

`action: summary` reads **all** selected identities, independent of page size,
and returns counts by drawing file and observed type name. There is no downstream
audit/edit consumer yet. The cached selection contains the full result, not just
the page, but never authorizes a future write.

Before every page or summary, the host resolves current context and repeats the
original bounded query reads. SHA-256 fingerprints cover the context binding,
resolved file states/omissions and every in-scope candidate's identity plus
requested/predicate/mandatory fields, including candidates previously rejected.
Adding/deleting elements, changed relevant values, or a project/document/scoped
file-state change causes `selection_stale` and removes the cache entry. Failed
revalidation returns `selection_unverifiable` and also removes it. Unrequested
attributes/geometry and valid outside-scope properties are not a freshness
promise. Creation timestamps are not used as modification counters.

Selections expire **five minutes from creation** (reads do not extend TTL),
are limited to eight per host handler (oldest-created eviction), and disappear
on host restart. Unknown/expired/evicted IDs return `selection_unavailable`.
They are not persisted. A five-second cooperative scan budget, 4 MiB serialized
source budget and `max_adapters` of 1–10000 (default 5000) reject excessive scans
with `scan_limit_exceeded`, with **no partial selection or complete count**.
The timer cannot interrupt a blocking native API call. Paging reduces response
size; revalidation still scans the bounded candidate set. Runtime performance
remains unmeasured.

## Metadata inspection (new in 0.4.0; Allplan pending)

`action=inspect` requires the same explicit `scope` and an explicit
`attribute_ids` list (0–32 distinct positive IDs). `sample_limit` is 1–20,
default 10; `max_adapters` retains the query limits. Predicate, paging, field
projection and selection IDs are rejected for this action. The public typed
schema and dependency-free host both validate before native enumeration.

Inspection scans the bounded scope using the existing identity/conflict rules,
then samples in drawing-file/model-UUID order. It returns `counts`, original
scope/coverage/omissions, raw element fields and requested attributes,
`sample.is_full_selection`, and project resource metadata. The sample limit
limits returned elements, not the scan. It creates no reusable selection.
Layer names/short names cover only observed layer IDs in the returned sample;
attribute names, integer type/control codes and raw unit labels cover requested
IDs. Each field retains observed or not_checked independently. Empty labels
remain raw empty strings; enum codes have no guessed semantic labels.

`source_fingerprint` covers scanned candidate/context fields. A separate
`probe_fingerprint` also covers metadata and the sample report; it is evidence
identity, not a durable/write reference. Total inspection uses a five-second
cooperative budget and rejects responses above 4 MiB. Blocking native reads
cannot be interrupted by this timer. No partial success is returned on budget
failure. `metadata_reads_complete` concerns read failures and does not establish
attribute existence, semantic validity, writability or profile binding.

`missing` means a requested ID was absent from `GetAttributes(ReadAll)` output.
Passive native absence remains `not_checked`; null, empty string and zero retain
their observed raw values. No fallback read changes state or creates attributes.
`runtime_verified=false`, `usable_for_write=false`, `profile_binding=not_checked`
remain explicit. Units are metadata strings without conversion. The demo
profile remains unbound. [Owner card](m1-metadata-batch.md) is pending.

```json
{"action":"inspect","scope":{"drawing_files":[1,2],"include_passive":true,"visibility":"api_select_all"},"attribute_ids":[498],"sample_limit":10}
```

**M1 Metadata.cmd** captures this packaged request and its full MCP response
in `logs/diagnostics-*.json`. Ordinary **Diagnostics.cmd** retains basic
health/version/context behavior. Developer CLI `--query-request <JSON path>`
can capture another typed read-only request; it never automatically pages,
retries a write or marks acceptance. Raw results require separate interpretation.

2026 resource signatures checked:
[AttributeService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeService/)
uses a DocumentAdapter; [LayerService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/LayerService/)
uses an integer document ID. This documentation evidence is separate from
[portable checks](test-results/m1-metadata-portable-0.4.0.md) and Allplan verification.

## Units, offset and next boundary

Canonical future geometry uses millimetres/degrees in a declared model-local
frame. A later boundary must identify the API source unit/frame and apply any
project-offset transform exactly once when converting to another declared frame.
Input display units remain independent. This package reads no model geometry,
normalizes no geometry and applies no offset. Spatial filtering, dimensions,
nonzero-offset behavior and input-unit invariance remain pending Allplan probes.
Future bounding-box intersection/containment must explicitly state whether
boundaries are inclusive and whether the test is merely a broad-phase box check.
They must not imply exact solid intersection. Those operations are rejected now.

## Examples

MCP argument `request` (substitute actual loaded file numbers):

```json
{"action":"query","scope":{"drawing_files":[1,2],"include_passive":true,"visibility":"api_select_all"},"fields":["display_name","layer_id"],"attribute_ids":[498],"page_size":1}
```

To filter by a returned type name, add
`"predicate":{"field":"type_name","op":"eq","value":"<observed type name>"}`.
Do not infer a column type from a localized display name alone.

```json
{"action":"page","selection_id":"<returned ID>","cursor":"<returned cursor>","page_size":1}
{"action":"summary","selection_id":"<returned ID>"}
```

Host JSON also requires `schema_version: m1-query-1`; the MCP wrapper supplies it.
The schemas stay client-neutral. No arbitrary generated Python is involved.

2026 documentation checked for signatures, separately from runtime evidence:
[read access](https://pythonparts.allplan.com/2026/manual/features/model_access/read_access/),
[BaseElementAdapter](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapter/),
[ElementAdapterType](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/ElementAdapterType/),
[ElementsSelectService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsSelectService/).
