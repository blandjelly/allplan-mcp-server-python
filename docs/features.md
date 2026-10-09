# Workflow features and status

The roadmap contains the following 13 workflow tools. Bounded
`get_model_context` and `model_query` reads are implemented and accepted on
Allplan 2026-1-7; see [acceptance and limits](test-results/m1-acceptance-0.5.3.md)
and [read contracts](tool-reference.md). `model_audit` is implemented and accepted
within the retained fixture scope in 0.6.1, **UAT-04 PASS**; see
[native evidence and limits](test-results/m2-acceptance-0.6.1.md) and the
[audit contract](m2-audit-contract.md). Other workflow tools are planned for main. The separate
[M3 draft PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2)
contains read-only repair preview; native verification is pending and apply is unavailable. M0 utilities are `allplan_health`,
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

[Fixture setup](fixture-guide.md) is the single reference for project resources,
the six-column scene, native roots, display units/offset and expected findings.
[Read profile 1.0.2](../profiles/examples/native-model-qa.demo.json) binds resources
freshly; [audit profile 2.0.0](../profiles/examples/native-model-qa.audit.json)
checks only the six file-101 columns. C03's raw `<niezdefiniowany>` remains in
evidence and is missing only under the explicit M2 policy.

M2 returns five findings on five columns: C03 mark, C02/C04 duplicate marks,
C05 layer and C06 status. No model repair is performed. The separate M3 preview
proposes only C05 layer SZ_OGÓ02 → SZ_OGÓ01 and C06 status NWE → NEW.
Applying those repairs remains future work, would leave three mark findings and
must include reviewed-plan freshness, native write/readback and Undo evidence.
