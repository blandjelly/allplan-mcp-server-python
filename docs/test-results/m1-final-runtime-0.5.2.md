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
