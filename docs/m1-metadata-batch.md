# M1 metadata and passive-attribute probe — 0.4.0

Status: **bounded owner batch PASS**.
[Recorded evidence and limits](test-results/m1-metadata-runtime-0.4.0.md) verify
complete replies, resource metadata and passive/active raw 498 comparison. Owner
confirms columns unchanged, file 2 restored passive and the same Allplan build.
The first attempts failed with host_absent; the later two captures succeed.
No repeat or extra capture is needed without a relevant change or defect.
The instructions below are retained for reproducibility. This is a resource/read probe,
not a repeat of the accepted 0.3.0 paging/predicate batch. M0 and the 0.2.1
context correction stay accepted. The demo profile stays unbound/inactive.

Package: `allplan-mcp-0.4.0-windows-evaluation.zip`; verify the adjacent SHA-256
and payload manifest. Keep the accepted 0.3.0 archive unchanged for restore.
Close Allplan and the MCP console, extract 0.4.0 into a new folder, run
**Setup.cmd** against the same Allplan Local folder, then reopen Allplan,
StartPythonHost and **Launch Allplan MCP.cmd** from the new folder. Existing
Codex configuration remains valid; the tool catalog remains seven tools.

## Two captures in the existing scene

Use the unchanged disposable `Nowy projekt 1` scene: one ordinary column in
file 1 and one in file 2, with the relevant layers visible. Save first. If the
scene/file numbers changed, report that instead of rebuilding a new fixture.
The packaged probe explicitly requests files **1 and 2**, passive inclusion,
attribute **498**, and at most ten file/model identities. No identifiers need
to be researched or copied by the owner.

1. Keep file **1 foreground** and file **2 passive**. Double-click
   **M1 Metadata.cmd**. Retain the generated `logs/diagnostics-*.json` as capture A.
2. Change only file **2** to **active background**, keeping file **1 foreground**.
   Double-click **M1 Metadata.cmd** again. Retain that JSON as capture B.
   Confirm that the two visible columns and their geometry remain unchanged.
   Restore file 2 to passive afterward; no third capture is needed.

These UI file-state changes are intentional test setup. The probe itself does
not change model data, file/layer states, resources or profiles. It never creates
or edits attributes. Restore 0.3.0 with its Setup.cmd if installation fails.

## What the captures resolve

Both reports must identify package **0.4.0** and include `model_query_request`
and `mcp.model_query` with request ID, scope/coverage, sampled model/view/type
identities, raw attribute 498, attribute metadata and layer metadata.
Expected unchanged scene: two identities, an untruncated two-item sample,
layer 3736, known Column_TypeUUID type and the previously recorded model UUIDs.
The native attribute name/unit and enum codes are evidence to collect, not
predefined expected values or a mark binding.

Compare the same file-2 model UUID and raw attribute observation across A/B.
If the attribute appears only when active, this supports an access-state
limitation. If it stays missing or fails, preserve that result; it does not
establish native absence. The source fingerprint is expected to change with
file state; comparing its equality across captures is not a success criterion.
Empty unit labels remain observed raw strings, without unit conversion.
Exceptions remain `not_checked`; no field failure may be reported as a pass.

Send the **two JSON files** and this short result form. There is no need to
copy model_query replies from Codex, repeat earlier tests, or construct the
six-column demo yet.

```text
Package: 0.4.0
Allplan UI build: [actual build]
Capture A: file 1 foreground; file 2 passive; [JSON filename]
Capture B: file 1 foreground; file 2 active background; [JSON filename]
Visible columns/geometry unchanged: yes / no / not checked
File 2 restored to passive: yes / no
Any errors or unexpected behavior: [...]
```

Geometry units/nonzero offset, native parent/child counts, profile schema and
validated resource binding remain separate M1 work. This batch cannot accept
full UAT-02/UAT-03 or M1.
