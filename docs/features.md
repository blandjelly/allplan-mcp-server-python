# Features to implement

The toolkit contains the following 13 workflow tools. Bounded
`get_model_context` and `model_query` reads are implemented and accepted on
Allplan 2026-1-7; see [acceptance and limits](test-results/m1-acceptance-0.5.3.md)
and [read contracts](tool-reference.md). `model_audit` is implemented and accepted
within the retained fixture scope in 0.6.1, **UAT-04 PASS**; see
[native evidence and limits](test-results/m2-acceptance-0.6.1.md) and the
[audit contract](m2-audit-contract.md). `fix_model_issues` preview/revalidation is
implemented in 0.7.0, [bounded native preview gate PASS](test-results/m3-preview-acceptance-0.7.0.md).
0.8.1 has [bounded native execution/Undo/recovery PASS](test-results/m3-execution-acceptance-0.8.1.md).
Standard/selection and mark previews have native PASS in 0.9.0/0.10.0.
0.11.0 adds reviewed single/multi-target layer/status execution through
fix_model_issues, apply_office_standard and rule_based_edit;
[current limits and pending native gate](m3-workflow-execution-contract.md).
Mark writes/numbering remain open M3 scope. Other workflow tools are planned. M0 utilities are `allplan_health`,
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
Revision 1.0.2 validates schema m1-profile-1 and resolves MCP_QA_MARK /
MCP_QA_STATUS plus layer short names SZ_OGÓ01 / SZ_OGÓ02 freshly for reads.
The accepted fixture is bound_for_read; active_for_write=false and native write
eligibility remain not_checked. Missing/incompatible resources reject profile
queries. The [completed owner recipe](m1-final-batch.md) records exact UI names;
no repeated owner batch is requested.

Use a disposable `MCP_QA_DEMO` project or copy. Reserve empty files **101**
(active/editable), **102** (loaded passive) and **103** (unloaded); these are
examples, not permission to overwrite contents. Initial units: mm, zero offset,
visible relevant layers. Later tests use changed display units/nonzero offset.

File 101 contains six ordinary columns: **400 × 400 × 3000 mm**, bottom 0,
center insertion, consistent sample material such as `C30/37`.

| Fixture | Center X/Y (mm) | Mark | Layer | Demo status |
| --- | --- | --- | --- | --- |
| C01 | 0 / 0 | S01 | SZ_OGÓ01 | NEW |
| C02 | 6000 / 0 | S02 | SZ_OGÓ01 | NEW |
| C03 | 12000 / 0 | Empty | SZ_OGÓ01 | NEW |
| C04 | 0 / 6000 | S02 | SZ_OGÓ01 | NEW |
| C05 | 6000 / 6000 | S05 | SZ_OGÓ02 | NEW |
| C06 | 12000 / 6000 | S06 | SZ_OGÓ01 | NWE |

Add two 300 × 500 mm native beams spanning C01–C02 and C02–C03 at a documented
common elevation, one separate 200 × 4000 × 3000 mm single-layer wall, and one
separate 4000 × 4000 × 200 mm slab. Expect **10 top-level components** in file 101;
raw adapters/representations must not inflate component counts. Add one column
marked S02 in passive file 102 and another column in unloaded file 103.
The accepted roots include SkeletonBeam and MultiSlab with Slab tiers.
The original zero-offset baseline is retained; no model repair is requested.
C03 was observed as the literal `<niezdefiniowany>`. M2 audit profile 2.0.0
explicitly classifies it as missing while retaining the raw value in evidence.

The M2 audit examines only the six file-101 columns: **QA-001** required mark → C03;
**QA-002** unique nonempty mark per file/family → C02/C04 (two findings, one group);
**QA-003** required structure layer → C05; **QA-004** status NEW/EXISTING → C06.
Expected: **5 findings on 5 columns**, C01 passes. Outside-scope columns do not
create duplicates. Missing bindings/data produce `not_checked` or a profile error.

The 0.7.0 M3 repair preview contains exactly two proposed changes: C05 layer → SZ_OGÓ01
and C06 status NWE → NEW. It leaves the model unchanged; its follow-up audit
retains **5 findings**. The bounded native preview gate passes. Accepted
0.8.1 evaluation apply/readback leaves **3 findings**. In the next 0.11.0
workflow gate, separately reviewed layer then status writes must leave 4 then 3. Repeating apply must not repeat writes. An explicit reviewed preview
assigning C03=S03 and C04=S04 simulates zero findings; mark setters are not yet
implemented or accepted. These values are fixture choices,
not an inferred production office standard.
