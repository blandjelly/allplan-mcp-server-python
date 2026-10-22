# Validation status and retained evidence

This page indexes accepted baselines and native observations. Current M4 status
and next steps are in the [handoff](next-model-handoff.md) and
[office editing plan](office-editing-development-plan.pl.md). Keep automated
tests, GitHub CI and native Allplan results distinct.

## Accepted M0–M3 fixture baseline

M0–M3 are accepted only within the retained `MCP_QA_DEMO` test project and
recorded scopes. M3 covers demonstrated one- and two-change scenarios in
foreground drawing 101; it does not establish arbitrary combinations,
multi-file writes, durable cross-copy identity or general-purpose office use.
See the [fixture guide](fixture-guide.md), [M3 execution contract](m3-execution-contract.md),
and preserved [0.15.0 delivery record](../evaluation-packages/0.15.0/README.md).
The original M0–M2 acceptance reports remain in the historical baseline at
[commit 5ec1f57](https://github.com/blandjelly/allplan-mcp-server-python/tree/5ec1f57dd0ebb08e0e2bc19ef23c7440333c7b74/docs/test-results).

## Retained M4 native observations

Each observation has a narrow scope. A pass for one sample or UI action does not
accept the full M4 workflow.

| Evidence | Recorded scope |
| --- | --- |
| [0.16.0 crash](test-results/m4-native-crash-0.16.0.md) | Broad property discovery crashed; its cause remains unknown and the route stays suspended. |
| [0.16.1 isolated Column read](https://github.com/blandjelly/allplan-mcp-server-python/blob/96033359842271cc7dd487adca8fcb737042fc95/docs/next-model-handoff.md) | The owner reported one raw Column read between healthy replies in one session; names, layers, UI and writes were not accepted. |
| [0.17.1 Column observation](test-results/m4-column-layer-observation-0.17.1.md) | Original field binding, two W1 writes and incomplete highlight behavior; see the report for exact limits. |
| [0.18.1 observations](test-results/m4-native-observation-0.18.1-2026-10-17.md) | Host response and Columns highlight were observed; the Wall sample was blocked before reading. |
| [0.18.2 Wall observation](test-results/m4-wall-observation-0.18.2.md) | One single-tier Wall read returned 240 mm and `Beton`, matching the UI. |
| [0.19.0 Wall filter observation](test-results/m4-wall-filter-observation-0.19.0.md) | In drawing 101, 200 mm matched `<240 mm`, 240 mm did not, and the owner confirmed highlight and clear. |
| [2026-10-17 agent observation](test-results/m4-agent-observation-2026-10-17.md) | Owner-reported fire-classification, query and highlight outcomes plus failed/thin-wall and unsupported operations. |
| [2026-10-18 observations](test-results/m4-agent-observation-2026-10-18.md) · [v2](test-results/m4-agent-observation-v2-2026-10-18.md) | Owner logs and their interpretation; no exact build claim. |
| [2026-10-19 observation](test-results/m4-agent-observation-0.21.1-2026-10-19.md) · [follow-up](test-results/m4-agent-followup-2026-10-19.md) | Layer lookup and the multiview recovery blocker; preserve original execution state. |
| [2026-10-20 observation](test-results/m4-agent-observation-2026-10-20.md) | Owner confirms Slab and Column attribute outcomes; exact installed manifest is absent. |
| [0.23.0 journal PASS](test-results/m4-journal-cleanup-0.23.0-owner-pass-2026-10-21.md) | Owner-reported preview and confirmed archival of both journals; no exact manifest, native replay/restart or snapshot-conflict evidence supplied. |
| [0.25.0 owner observation](test-results/m4-owner-observation-0.25.0-2026-10-22.md) | Owner confirms the log matches Allplan 2026.1 during the 0.25.0 run. Limited PASS: Wall and MultiSlab identity reads, one confirmed Wall subtree deletion with fresh complete absence scan, and one 200 mm Wall W1 readback. The exact manifest, raw MCP responses and Allplan build ID are absent; opening/owning-Wall deletion, material/hatch, bulk W1 and no-op/Undo remain blocked or unobserved. Do not repeat successful deletion, identity reads or the 200 mm Wall readback. |
| [0.27.0 owner observation](test-results/m4-owner-observation-0.27.0-2026-10-23.md) | Owner-reported PASS for lowercase attribute lookup and native-material diagnostics; limited W1 read/write and one UI Undo per changed element. The supplied log reports one separate Wall 240 mm subtree deletion with five descendants absent on a fresh complete scan and two Beam moves/readbacks on W1. Three W1 Columns were blocked at delete preview by `component_child_owner_mismatch`; Slab/MultiSlab lineage remains unresolved. No explicit W1 no-op/zero-setter result, raw MCP responses, exact manifest or Allplan build ID. Do not repeat accepted lookup, diagnostic, deletion or Beam writes. |

Raw owner logs are retained unmodified under
[test-results/evidence](test-results/evidence/). Source CI and package checks
are recorded separately in each [evaluation package](../evaluation-packages/).

## Safeguards and limits

- Keep exact project/document and target identity checks, preview binding,
  revalidation, journaling, replay, fresh readback and controlled recovery.
- A lost write response or unknown outcome remains blocked under the original
  execution ID. Do not retry setters or discard journal state to free capacity.
- Candidate 0.28.0 sets active execution history to 512 records, retains the
  1 MiB per-record bound, raises the active diagnostic trace limit to 8 MiB and
  trace-inspection limit to 32 MiB, and bounds archive inventory at 1 GiB / 1024
  files. Full CI and exact fallback ZIP verification passed; see the
  [0.28.0 evaluation record](../evaluation-packages/0.28.0/README.md). Confirmed
  archive cleanup continues to preserve unresolved, corrupt and unverifiable
  records. The 0.23.0 owner PASS covers its original bounded archival scope
  only; native restart/replay remains unobserved.
- Native selection, native material writes, full typed-delete coverage/Undo,
  the complete six-family matrix,
  multi-file writes, whole-project access, long-term/concurrent stability,
  broader Undo and cross-copy identity remain unaccepted.

The exact delivered packages and their verification records are immutable
historical evidence. Documentation cleanup does not authorize rebuilding,
reinstalling, or repeating their native trials.
