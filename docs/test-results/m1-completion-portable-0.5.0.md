# M1 implementation completion — portable evidence 0.5.0

Date: 2026-10-07. Linux, external Python 3.12.14, FastMCP 3.2.4.
**56 relevant distinct checks PASS**: 23 new pure/fake-native completion checks,
two new real MCP diagnostic tests, 21 query regressions, seven metadata
regressions, one existing MCP schema/transport regression and two package/lock
checks. The scan, predicate contract, action discriminator, context/profile
path and packaged payload changed; these regressions are necessary. The full
historical M0 suite and accepted owner batches are not repeated.

```bash
PYTHONPATH=tests .venv/bin/python -m unittest \
  test_m1_completion test_model_query test_model_metadata \
  test_package.PackageTests.test_deterministic_archive_integrity_and_fresh_install_from_extracted_payload \
  test_package.PackageTests.test_version_and_lock_agree -v
PYTHONPATH=tests .venv/bin/python -m unittest \
  test_mcp_smoke.MCPSmokeTests.test_final_batch_transports_geometry_profile_and_saves_summaries \
  test_mcp_smoke.MCPSmokeTests.test_diagnostic_repeated_cursor_is_bounded_and_preserves_partial_evidence \
  test_mcp_smoke.MCPSmokeTests.test_model_query_schema_transport_predicates_pages_and_summary -v
```

The initial groups passed 52 and 3 tests. A subsequent root-view regression
passed with two relevant hierarchy checks; two coordinate checks passed after
finite-range hardening. This totals 56 distinct passing tests. Socket tests use
explicit network capability
in the restricted executor. During implementation, the initial 18 completion
checks passed, then the completed group was run after four additional cases and
classification changes. The repeated-cursor test was rerun alone after improving
preservation of pages collected before a failure. The batch-transport check was
rerun alone after enforcing finite public box
coordinates. No unrelated checks were broadened or rerun after passing.

Coverage: finite mm/cm/m transforms with offset once and inverse round trip;
inclusive/exclusive/tolerant AABB tests; independent display units; global/local
boxes and dimensions; unavailable/nonfinite geometry; native error code handling;
geometry/offset/hierarchy/profile-sensitive stale rejection; ten supported
components without counting children/labels; wall-tier union; cycles/cross-file
parents; query and hierarchy budgets; no geometry outside scope or unless needed;
profile schema/version/rule references, name/type/ID round trips, aliases,
resource failures and configured-level provenance; captured batch responses,
summaries/pages and bounded repeated cursors; packaged profile data and installers.

Wheel/sdist and deterministic Windows evaluation ZIP build. Profile JSON is
present in the wheel; its copy in the evaluation archive matches the canonical
packaged profile. Registration installs the three new host reader/contract files
without native imports in the external process. No Windows/CI execution is
claimed here. The old 0.3.0 and 0.4.0 ZIP hashes are preserved.

2026 signatures were checked separately from runtime support:
[BaseElementAdapter](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapter/),
[CalcMinMax](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_Geometry/),
[eServiceResult](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_Geometry/eServiceResult/),
[parent service](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapterParentElementService/),
[child service](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapterChildElementsService/),
[read-access hierarchy/geometry](https://pythonparts.allplan.com/2026/manual/features/model_access/read_access/),
[AttributeService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeService/),
[LayerService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/LayerService/),
[UnitService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_AllplanSettings/UnitService/).

Notable documented details: CalcMinMax returns `(MinMax3D, eServiceResult)`;
NO_ERR is **2**, not a guessed zero; walls require tier geometry; GetModelGeometry
is independent of the view; resource methods use different document argument
types. The model-local API coordinate convention and nonzero-offset transform
still require independent Allplan evidence. Portable tests prove only the
declared arithmetic/orchestration, not that native coordinates follow it.

Implementation covers the bounded M1 read contract and prepares a validated,
freshly resolved demo profile. Real resources are project-specific and can bind
only after UI setup; write eligibility remains not_checked. **M1 exit gate is
pending UAT-02/UAT-03**, using the [final owner card](../m1-final-batch.md). No
full M1 runtime acceptance, numeric geometry proof or active write profile is
claimed. M2 audit and M3 mutation behavior are not included.
