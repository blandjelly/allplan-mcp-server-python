# M1 query batch — 0.3.0

Status: **three bounded owner query cases PASS**, based on the supplied query
results report correlated with 0.3.0 diagnostics. [Recorded evidence and limits](test-results/m1-query-runtime-0.3.0.md).
The prompts below are retained for reproducibility; no repeat is needed without
a relevant change or defect. This is a bounded query
batch, not full UAT-02/UAT-03 or M1 acceptance. Do not repeat the accepted M0 or
0.2.1 context correction batch. New tool behavior is the only target here.

Package: `allplan-mcp-0.3.0-windows-evaluation.zip`, exact archive identified by
the adjacent SHA-256 file and embedded payload manifest. Previous UI build:
**Allplan 2026-1-7**; retain the actual build if it has since changed. Demo profile:
**unbound/inactive**. No six-column fixture or mark binding is required yet.

## Upgrade and model baseline

Close Allplan and the MCP console. Extract 0.3.0 into a new folder, run
**Setup.cmd**, selecting the same Allplan Local folder, then open Allplan,
StartPythonHost and **Launch Allplan MCP.cmd** from that folder. Existing Codex
configuration remains valid. Keep the accepted 0.1.2 and 0.2.1 archives for restore.
Seven tools should be discovered, including `model_query`; development execution
remains absent. The query does not create geometry or change file/layer visibility.

Use the earlier disposable `Nowy projekt 1` two-column scene if it is unchanged:
file **1 foreground**, file **2 passive**, one known ordinary column in each.
If that scene has changed, report actual file numbers and visible columns; the
implementation model adapts the next test rather than asking you to build an
unbound demo. Keep relevant layers visible. Save the baseline first.

## Three owner prompts

1. **Read/query and new metadata**

   > Call model_query with action=query, drawing_files=[1,2], include_passive=true,
   > visibility=api_select_all, fields=[display_name,layer_id], attribute_ids=[498],
   > page_size=1. Do not change anything. Preserve the full response, selection ID,
   > cursor, model/type/view UUIDs, coverage, omissions and not_checked samples.
   > Report attribute 498 as raw data or missing/not_checked, never as a bound mark.

   Expected for the unchanged two-column scene: one identifiable column per file,
   two file/model identities total; file 2's negative adapter number remains
   separate from normalized file 2. The page contains one identity, while the
   result count describes the whole selection. Type/name/layer reads are new
   runtime probes. Any excluded identities or read failures are feedback, not
   permission to silently adjust expected counts. Attribute 498 is documented
   Object_name; actual availability/value on these columns remains a probe.

2. **Paging and full-selection reuse**

   > Using that selection ID, read each remaining model_query page with page_size=1
   > and the returned cursor, then call action=summary for the same selection.
   > Compare the union of paged model UUIDs with matched_model_identities and the
   > summary counts by file/type. Do not substitute the first page for the full
   > selection. Report every read failure. Leave the model unchanged.

   Expected: each identity appears once, no missing/repeated page items; summary
   totals match the full result (two for the unchanged scene), and its source
   fingerprint stays the same. A restart/expiry makes the old selection
   unavailable; run a new query instead of claiming old selection acceptance.

3. **Explicit exclusion and observed-value predicates**

   > Run a fresh model_query over files [1,2] with include_passive=false and
   > visibility=api_select_all. Use an all predicate for the exact type_uuid and
   > layer_id observed on the file-1 column in the first response. Do not guess
   > identifiers. Report matches, passive-file omission and all not_checked fields.
   > If its attribute 498 was observed, run one more file-1 query for equality to
   > that exact typed value; otherwise report the attribute case as NOT_CHECKED.
   > Confirm that the visible model remains unchanged.

   Expected: the file-1 column matches its observed values; file 2 is explicitly
   `passive_excluded`. Coverage for requested [1,2] is incomplete even if the page
   is complete. Typed attribute equality is checked only against an observed
   value. No whole-project, mark/profile or top-level component count is claimed.

Reset: the tool makes no model changes. Return to the previous project/file states
if you changed them to establish the test preconditions. For rollback, close
Allplan/MCP, run **Restore bridge.cmd** from 0.3.0, reopen Allplan, and launch the
external MCP server from the matching earlier package folder. Bridge restore
does not downgrade the external server automatically.

## Copyable result

```text
Package: 0.3.0 / archive SHA-256 reference:
Allplan UI build:
Project / foreground and passive drawing files:
Visible baseline column count by file:
Query metadata/scope: PASS | FAIL | BLOCKED
Matched identities / omissions / not_checked:
Paging and full-selection summary: PASS | FAIL | BLOCKED
Paged UUID count / summary by file / same fingerprint:
Type/layer predicates and passive exclusion: PASS | FAIL | BLOCKED
Attribute equality: PASS | FAIL | NOT_CHECKED
Visible model unchanged: YES | NO
Unexpected behavior / request IDs:
Reset performed:
```

Keep tool responses in the local Codex chat; send the filled observations. The
implementation model records English runtime evidence and prepares any fixes.
You do not run developer commands or investigate API signatures. Stale-field
change tests, geometry/unit/offset probes, parent/child counting and bound-fixture
UAT are later targeted batches; portable tests are separate evidence for now.
