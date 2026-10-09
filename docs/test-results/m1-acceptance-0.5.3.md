# M1 acceptance — 0.5.3

2026-10-09 (Europe/Warsaw). **M1 closed; UAT-02/UAT-03 PASS within the bounded
read contract**, on the owner's Allplan 2026-1-7 / local Windows Codex setup.
This record combines previously accepted query/context evidence, the resource
preflight, native A/B/C captures and independent owner UI observations. Raw new
diagnostics, private environment paths and element/session IDs are not published.

## Exact tested artifact

Package 0.5.3, demo profile schema m1-profile-1 / revision 1.0.2. Verified bridge
source commit `4f685766e1577cddb681ee3726bbabd3f2b3d743`, source_modified=false.
`allplan-mcp-0.5.3-windows-evaluation.zip` SHA-256:
`15262b1f029d818e5fea871a0b669603d90a5b6ca68e80d5355457b8656ed104`.
All three captures report installed integrity verified with no mismatches.
The original archive and older accepted artifacts are preserved unchanged;
this acceptance documentation does not rebuild the tested package.

## Allplan verification

| Gate | Evidence | Result |
| --- | --- | --- |
| Context/project/file identity and scope | Accepted [0.2.1 context batch](../next-model-handoff.md#earlier-context-evidence--021); A/B/C foreground 101, explicit unloaded 103 omission; B/C passive 102 | PASS |
| Fresh demo read resources | Accepted [0.5.2 preflight](m1-profile-correction-0.5.2.md); A/B/C profile bound_for_read | PASS |
| Native roots and geometry | A diagnostics-20261008T223235Z.json: 10 components in 101, one reference in 102, 17 raw adapters, six child representations deduplicated | PASS |
| Filters and complete read selections | A/B/C: six file-101 columns, two S02, one C01 spatial/height match; summaries/pages agree with queries | PASS |
| Small-page traversal | Previously accepted [0.3.0 query batch](m1-query-runtime-0.3.0.md): distinct pages and full-selection summary | PASS; no repeat |
| Display units | B diagnostics-20261008T224141Z.json: input enum 0 to 3 (mm to metres), exactly equal canonical geometry and result identities across all five queries | PASS |
| Corrected fixture setup | B/C: 102 passive, C05/S05 on review layer SZ_OGÓ02; these declared corrections are separate from display-unit invariance | PASS |
| Nonzero XY offset | C diagnostics-20261008T225219Z.json plus owner UI offset X=100 m, Y=200 m; all ten global boxes equal local boxes plus (100000,200000,0) mm exactly once | PASS |
| Independent UI coordinates | Owner reports C01 X=100 m, Y=200 m, Z=0 m; agrees with global center of its base cross-section | PASS |
| Appearance and baseline | Owner confirms A dimensions/unchanged appearance, then B/C unchanged appearance and original zero-offset project retained | PASS |

The source geometry stays model-local in mm despite metre display and nonzero
project offset. B/C local min/max coordinates are exactly equal. Every requested
global endpoint in C equals the corresponding local endpoint plus offset once;
no zero-offset or double-offset result appears. Counts stay 11/10/6/2/1 for
broad roots/file-101 roots/profile columns/S02/C01. All requested fields remain
complete; identity/hierarchy/predicate failure counters remain zero.

C01's global box is approximately (99800,199800,0) to (100200,200200,3000) mm.
The owner's Z=0 measurement is the base cross-section center; the center of the
whole AABB is (100000,200000,1500) mm. This distinction is not a height discrepancy.
The maximum B/C dimension residual is approximately 4.55e-13 mm, due to subtracting
translated floating-point endpoints; well below the documented 1 mm tolerance.
Beam extents remain 6000x300x500 mm, slab 4000x4000x200 mm, wall 4000x200x3000 mm.

Profile column scalar fields/type IDs and result identities agree between B/C.
Same element IDs in these captures are read evidence, not a guarantee that IDs
survive arbitrary project copies. Query/summary/page counts, coverage, fingerprints,
selection/session IDs and result IDs agree within each capture. Broad requested
scope is intentionally incomplete because 103 is unloaded; file-101 scans are
complete. No whole-project or screen-visibility coverage is inferred.

## Automated checks, recorded separately

The original M1 completion slice has [56 targeted portable checks](m1-completion-portable-0.5.0.md).
The observed-family correction has [14 targeted portable checks](m1-native-families-0.5.3.md),
plus wheel/sdist and clean-source Windows package validation. These are Linux
fake-native/contract/package checks, not owner Allplan tests or a Windows/CI run.
No accepted automated suite or owner batch was repeated to close M1; A/B/C report
comparison is analysis of native evidence. Runtime code and profiles are unchanged.

## Acceptance limits and next work

Acceptance covers the known fixture/build, six supported root type names,
bounded session reads, AABB geometry, configured levels, demo resource binding
and the tested zero/nonzero XY offset cases with Z offset zero. It does not prove
every hotfix, arbitrary framing/group trees, rotated cross-sections/exact solid
intersection, native BWS levels, every passive attribute, or large-model limits.
Changed-source staleness/TTL/eviction/restart retain their portable evidence;
durable references, write eligibility and native Undo are not established.

Static runtime_verified=false, geometry_conversion=not_checked and raw offset
api_native annotations remain unchanged; dated acceptance is the build/fixture
evidence registry, not a reason to globally mark every runtime verified.
The demo is bound_for_read and inactive for writes. C03 retains the literal raw
`<niezdefiniowany>` mark; M2 must define missing-value semantics explicitly rather
than silently normalizing it. M2 audit/M3 repair and their acceptance tests remain
unimplemented/unrun. Next: M2 profile/audit contracts and read-only findings.
