# M1 observed native-family correction — 0.5.3

2026-10-09 (Europe/Warsaw). Full M1 exit gate remains pending. Sanitized
technical findings only; no raw diagnostics/environment paths are published.

## Owner native evidence, separate from portable tests

Component-type report diagnostics-20261008T222009Z.json on verified 0.5.2
successfully enumerates sixteen unique model identities in 101 from seventeen
raw adapters including one outside 101. Raw hierarchy/fields are readable.

| Observed root family | Roots in 101 | Observed child family | Root type GUID |
| --- | --- | --- | --- |
| Column_TypeUUID | 6 | none | ac9415e3-4337-4860-8cd4-2f0d48596f12 |
| SkeletonBeam_TypeUUID | 2 | SkeletonAxis_TypeUUID | 53808df6-89e0-427e-81d6-1bd662823db1 |
| Wall_TypeUUID | 1 | WallTier / WallAxis / WallAxisLine | ec7f50b0-1a27-49d6-b6a2-007b854513c7 |
| MultiSlab_TypeUUID | 1 | Slab_TypeUUID | 40910db6-25b8-43e3-8704-8bbf285143aa |

Slab child type GUID: 48722469-d049-4617-b171-4286eb0037c5. UUIDs here identify
native **types**, not particular owner project elements. Root/component count
10 is derived from the observed tree, not sixteen raw identities. Geometry was
not requested by this probe. The user's structural-beam hypothesis is confirmed.
The existing filter excluded SkeletonBeam and MultiSlab after parent resolution;
this explains the three missing top-level results in the previous capture.

## Read correction

0.5.3 supports the four original root names plus these two observed families.
Skeleton axes map to beam roots. MultiSlab geometry unions direct Slab child
solids, including hidden tiers, using the same 256-child/file-scope bound as
walls. Missing/cross-file/invalid/budget-exceeding tier reads remain not_checked.
Beam geometry uses root GetModelGeometry/CalcMinMax; axes are never substitutes.
No fabricated geometry, arbitrary framing support, durable write identity,
profile change or native mutation is added.

## Portable validation

Fourteen targeted checks PASS: six new NativeFamilyTests cases, six justified
wall/hierarchy/scope/C01 regressions, version-lock agreement and deterministic
package integrity/fresh registration. Wheel/sdist build PASS. New cases model
the observed root/child tree, ten components plus one passive reference, exact
root type GUID preservation, hidden/multi-tier slab union, changed-tier staleness,
unavailable beam solid behavior and rejection of other framing families.
These fake geometry/resource services do not prove native solid readback.
The module inventory contains only the six new tests, without importing the
previous TestCase into automatic discovery.

## Owner next action

Install 0.5.3 in a new folder with Allplan/MCP closed. Preserve the existing
fixture, structural beams, slab and bound resources; no rebuild is required.
Restore 102 passive, 101 foreground, 103 unloaded; C05/S05 must use SZ_OGÓ02.
Keep C03's literal undefined text as recorded evidence; future M2 semantics
are separate. Restart the host after UI setup and run M1 Final.cmd as capture A.
Expected: 10 supported roots in 101 plus one accessible reference in 102;
readable beam/slab bounds and dimensions, six columns/two S02/one C01 unchanged.
If solids fail, retain the report; root identity success alone is insufficient.
After A passes, continue B (display metres) and C (independent nonzero-offset
copy) using the [owner card](../m1-final-batch.md). Do not repeat standalone
resource/type checks or already accepted old owner batches.

Targeted commands:

```text
PYTHONPATH=tests .venv/bin/python -m unittest \
  test_m1_native_families.NativeFamilyTests \
  test_m1_completion.M1CompletionTests.test_wall_bounds_union_all_tiers_and_do_not_require_parent_geometry \
  test_m1_completion.M1CompletionTests.test_top_level_counts_ten_fixture_components_without_children_or_labels \
  test_m1_completion.M1CompletionTests.test_parent_root_views_stay_separate_without_false_component_conflict \
  test_m1_completion.M1CompletionTests.test_hierarchy_cycle_and_cross_file_parent_do_not_become_components \
  test_m1_completion.M1CompletionTests.test_unrequested_or_outside_scope_geometry_is_never_read \
  test_m1_completion.M1CompletionTests.test_combined_dimension_and_spatial_filter_observes_one_c01 \
  test_package.PackageTests.test_version_and_lock_agree -v
PYTHONPATH=tests .venv/bin/python -m unittest \
  test_package.PackageTests.test_deterministic_archive_integrity_and_fresh_install_from_extracted_payload -v
UV_CACHE_DIR=/workspace/.cache/uv uv build --offline
```
