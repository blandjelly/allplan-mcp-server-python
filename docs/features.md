# Features to implement

The toolkit contains the following 13 workflow tools. Only the bounded
`get_model_context` probe exists today; its limits and verified behavior are in
[the handoff](next-model-handoff.md). M0 utilities are `allplan_health`,
`get_allplan_version`, `get_all_object_names`, `create_cube` and `create_box`.
Names are display values; baseline boxes have no automatic readback/deduplication.

## Workflow scope

| Tool | First deliverable | Stage | Deferred or conditional scope |
| --- | --- | --- | --- |
| `get_model_context` | Project/session, files/states, units, offset, levels, capabilities and missing data. | M1 | Full BWS, closed projects and automatic floor discovery. |
| `model_query` | Type/file/layer/attribute/dimension/spatial-box predicates; reusable, paginated selections. | M1 | Arbitrary native grids and complex spatial relations. Define null, case, tolerance and containment/intersection semantics. |
| `model_audit` | Required/allowed values, layers, scoped duplicate marks and simple dimensions with evidence. | M2 | Unavailable rule inputs remain `not_checked`. |
| `fix_model_issues` | Selected findings → preview → writable attribute/layer changes → readback and re-audit. | M3 | Native material, graphical labels and component repairs require separate adapters. |
| `apply_office_standard` | Versioned attributes, marks, layers and numbering through shared audit/repair services. | M3 | File moves/copies need relation/Undo probes; full BWS restructuring deferred. |
| `rule_based_edit` | Query selection → attribute/layer changes with exceptions; later supported native properties. | M3–M4 | No universal setters or implicit component-family conversion. |
| `generate_structural_frame` | Explicit rectangular grid/elevations, sections/materials and omissions; native columns/beams. | M4 | Bracing, arbitrary native grid extraction and destructive regeneration. |
| `generate_foundations_from_structure` | Rule-sized native pads under selected base columns, then strips under straight walls. | M4 | General support inference, combined/stepped foundations and design calculations. |
| `populate_layouts` | Prepared files/crops on specified sheets, one template, scales/margins and deterministic overflow. | M5 | Arbitrary existing-layout rearrangement and automatic sheet metadata discovery. |
| `documentation_audit` | Known layout/profile requirements; later managed roles, freshness, dimensions and title-block fields. | M5–M6 | Semantic completeness of arbitrary third-party drawings. |
| `prepare_issue_package` | Explicit layouts, preflight, revision/date/description, PDF/DWG and hashed manifest in a new issue directory. | M5 | Native revision history and arbitrary title-block updates; sending files is outside the tool. |
| `create_documentation_package` | One foundation profile: plan, two UVS sections, role-based labels/dimensions and own schedule. | M6 | Arbitrary complete drawing sets, standard reports and preservation of every manual adjustment. |
| `generate_coordination_openings` | Proven straight pipe/duct crossings through vertical walls/horizontal slabs, clearance, host link and repeat detection. | M7; early M1 spike | Imports, oblique crossings, layered walls and merging need further evidence. |

Native supported components are preferred; any agreed generic-solid fallback must
be labeled. Structural/geotechnical sizing is outside scope. Missing critical
issue-audit data blocks automated readiness unless the profile defines explicit
manual-review evidence. Keep supplied, verified and uncheckable metadata distinct.

## Demonstration fixture for M1–M3

Profile: [native-model-qa.demo.json](../profiles/examples/native-model-qa.demo.json).
It is illustrative, unbound and inactive. Reject unbound profiles. Resolve actual
native-type, writable mark/status attribute and layer IDs, validate the schema,
record the bound version/build and supply exact UI field names before owner tests.

Use a disposable `MCP_QA_DEMO` project or copy. Reserve empty files **101**
(active/editable), **102** (loaded passive) and **103** (unloaded); these are
examples, not permission to overwrite contents. Initial units: mm, zero offset,
visible relevant layers. Later tests use changed display units/nonzero offset.

File 101 contains six ordinary columns: **400 × 400 × 3000 mm**, bottom 0,
center insertion, consistent sample material such as `C30/37`.

| Fixture | Center X/Y (mm) | Mark | Layer | Demo status |
| --- | --- | --- | --- | --- |
| C01 | 0 / 0 | S01 | MCP_QA_STRUCTURE | NEW |
| C02 | 6000 / 0 | S02 | MCP_QA_STRUCTURE | NEW |
| C03 | 12000 / 0 | Empty | MCP_QA_STRUCTURE | NEW |
| C04 | 0 / 6000 | S02 | MCP_QA_STRUCTURE | NEW |
| C05 | 6000 / 6000 | S05 | MCP_QA_REVIEW | NEW |
| C06 | 12000 / 6000 | S06 | MCP_QA_STRUCTURE | NWE |

Add two 300 × 500 mm native beams spanning C01–C02 and C02–C03 at a documented
common elevation, one separate 200 × 4000 × 3000 mm single-layer wall, and one
separate 4000 × 4000 × 200 mm slab. Expect **10 top-level components** in file 101;
raw adapters/representations must not inflate component counts. Add one column
marked S02 in passive file 102 and another column in unloaded file 103.
Record actual UUIDs in a test manifest; save a clean copy before repairs.

Audit only the six file-101 columns: **QA-001** required mark → C03;
**QA-002** unique nonempty mark per file/family → C02/C04 (two findings, one group);
**QA-003** required structure layer → C05; **QA-004** status NEW/EXISTING → C06.
Expected: **5 findings on 5 columns**, C01 passes. Outside-scope columns do not
create duplicates. Missing bindings/data produce `not_checked` or a profile error.

First repair preview contains exactly two changes: C05 layer → MCP_QA_STRUCTURE
and C06 status NWE → NEW. Leave marks unchanged; after apply/readback, **3 findings**
remain. Repeating apply must not repeat writes. A later explicit reviewed plan
assigning C03=S03 and C04=S04 gives zero findings. These values are fixture choices,
not an inferred production office standard.
