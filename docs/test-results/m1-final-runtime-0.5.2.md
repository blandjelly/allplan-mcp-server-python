# M1 final runtime captures — 0.5.2

2026-10-08. **Capture A NOT ACCEPTED; full M1 exit gate pending.**
Sanitized technical findings only; the original owner upload is not published.
Portable tests and the accepted read-resource preflight remain separate.

## First capture A

Owner upload: diagnostics-20261008T192549Z.json. Package 0.5.2, installed
integrity verified, MCP batch/summary/pages successful, read-resource binding
bound_for_read. Active file 101; file 102 active_background (recipe requires
passive_background); 103 omitted as unloaded_or_unavailable. Raw project offset
is zero. All five scans visited just one raw adapter, identified as a Column in
102. No identity/hierarchy/geometry-read failures were reported for that adapter.

| Request | Expected recipe | Observed |
| --- | --- | --- |
| Broad top-level scan | 10 in 101 plus 1 accessible reference in 102 | 1 column in 102, none in 101 |
| Profile columns in 101 | 6 | 0 |
| S02 profile filter in 101 | 2 | 0 |
| Dimension/spatial C01 filter in 101 | 1 | 0 |
| Global-frame scan in 101 | 10 supported components | 0 |

The single file-102 column has mm AABB min approximately (0,0,0), max
(400,400,3000), implying dimensions 400x400x3000 and XY center (200,200).
This is not an identified C01 result in file 101. It does not independently
verify the owner C01 coordinates or the ten-component hierarchy fixture.
Near-zero bounds (~9e-15 mm) are ordinary floating-point residuals, not an offset.
Zero-result returned_fields_complete does not establish geometry acceptance.

Owner reports C01 400x400x3000 mm, center XY=(0,0); follow-up confirms all ten
recipe components are in 101 and both relevant layers are visible. Owner is
unsure whether the placement uses the center or a corner reference. Do not
blame an absent fixture or move/rebuild C01 without identifying it in 101.

## Diagnosis and next bounded step

The adapter list was already limited to one element before scope/profile/
geometry/hierarchy filtering; the basic context sample independently agrees.
Code resolves GetInputViewDocument per request, not a cached document, and uses
the documented SelectAllElements(document) signature. The report does not
establish why the input-view enumeration omits the visible file-101 model.
No speculative code/API change or automatic test rerun is justified yet.

Keep the model and package unchanged. Save it, stop StartPythonHost, restore
101 foreground / 102 passive / 103 unloaded, focus the model view containing
101, then start a fresh StartPythonHost after the file-state setup. Repeat only
capture A using M1 Final.cmd. Its new context/adapter inventory can distinguish
input-view/session scope from the later component/geometry logic. If 101 still
has no adapters, retain the new report and a view/file-state screenshot for an
implementation fix. Do not proceed to B/C until the file-101 read is resolved.
The prior resource gate and accepted older owner batches need no separate repeat.

## Capture A after file reassignment — partial PASS, 2026-10-08

Owner clarified the elements were not correctly assigned to drawing files.
No cached-document/native selection defect is established from the first capture.
The intervening report diagnostics-20261008T193822Z.json had host connectivity
but no MCP connection, so no final requests ran; it is not model evidence.

Latest upload diagnostics-20261008T193947Z.json completes all six requests,
summaries and pages on verified 0.5.2. Seventeen raw adapters are enumerated,
sixteen from 101 and one from 102. The broad supported-root scan returns
7 components in 101 (6 columns plus 1 wall) and 1 column in 102. Three duplicate
representations and six non_component_adapters are reported, with no
identity/hierarchy/field-read failure. The prepared fixture expects 10 supported
components in 101; the two beams and slab are not returned as supported roots.
The context sample contains a slab display name and component axes, so do not
ask the owner to recreate missing objects or infer raw native type names.

| Bounded check | Latest result |
| --- | --- |
| Read-resource binding | bound_for_read |
| Profile columns in 101 | 6; all dimension readbacks approximately 400x400x3000 mm |
| S02 predicate | 2 columns, at (6000,0) and (0,6000) XY |
| Height/spatial C01 predicate | 1 column S01 at XY=(0,0) |
| C01 AABB | approximately (-200,-200,0) to (200,200,3000) mm |
| Zero-offset local/global read | identical boxes/dimensions for the same returned roots |
| Unloaded 103 | explicit unloaded_or_unavailable omission |

C01 dimensions and XY center now agree with the owner's prior UI report;
the placement-reference concern is resolved for this column. Bounded column
geometry/projections/filters/summary-page consistency pass on this capture.
No acceptance is inferred for display-unit changes, nonzero offset or beam/slab
hierarchy, nor for an independent visible-unchanged claim not yet supplied.

Recipe discrepancies remain: 102 is still active_background instead of passive;
C05/S05 uses layer 3700 (SZ_OGÓ01) instead of 3701 (SZ_OGÓ02); C03's raw mark
is the literal string <niezdefiniowany>, not an empty/missing value. Preserve
this literal evidence; M1 does not silently normalize it or execute future QA.

Next: read raw model identities/types and root hierarchy in 101 using the
new docs/probes/m1-component-types.json and M1 Component Types.cmd add-on.
This removes supported-root filtering and geometry/profile predicates without
changing the model or host code. Public and host typed request validation plus
ZIP-content checks pass; no unrelated tests are rerun. The original 0.5.2 archive
is unchanged. Resolve the native types before fixture changes/full A rerun;
B/C remain pending. Raw reports/environment paths are not published.
