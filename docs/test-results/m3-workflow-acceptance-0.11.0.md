# M3 office-standard and selected writes — native acceptance, 0.11.0

Recorded **2026-10-10 Europe/Warsaw**; filename capture **18:13:51.828559 local**
(16:13:51.828559 UTC). Decision **PASS for two separately reviewed single-target
workflow writes on the retained six-column disposable copy in file 101**.
All ten steps pass. The owner confirms both changes applied, host survived,
other elements unchanged and **two Undo operations** to undo both changes.
M3/UAT-05/UAT-06 remain open. No repeat of this gate is requested.

## Original evidence and runtime

[Original four uploads](evidence/m3-workflow-0.11.0-20261010-owner/),
[manifest/owner statement](evidence/m3-workflow-0.11.0-20261010-owner/evidence-manifest.json),
[inspection](evidence/m3-workflow-0.11.0-20261010-owner/verification.json).
All original bytes, including Windows line endings, are preserved.

| Original file | Bytes | SHA-256 |
| --- | ---: | --- |
| m3-last-workflow-execution.json | 460 | 58922839ce03e9644104a42987681f59fa3c8d9cd4fecced378b1cb36747c3c0 |
| m3-last-workflow-execution.txt | 82 | f20c4facbb0a7eb19ad37ff38bbe09038322e266ce8ac4584f378bd5f4012d67 |
| m3-workflow-apply-20261010T161351828559Z.json | 851890 | 80772560e5be3335cb7ddc96ed1db8262222355ae565d5d32d4223e8acf24e6c |
| m3-workflow-apply-20261010T161351828559Z.txt | 4270 | f8d4b5aa37c065eeed7180e1c67a57df65434a27b96be47cd37bac4bb5d1f9fa |

The last pointer equals the second execution in the full report and its TXT
matches its completed summary. Full JSON/TXT agree; original MCP text equals
decoded responses for every step. The pointer alone lacks the full observations.

Both health captures report MCP/bridge **0.11.0**, clean source
**26d70b27bd06e2916cda74213cb8995aa9f0f19a**, verified installation and no
integrity mismatches. All ten responses identify host session
**8e702add-3178-469c-9fb3-af276f79533a**. All **22** reported bridge hashes match
the existing exact delivery's embedded package manifest. The archive is neither
rebuilt nor rehashed; previous artifact verification remains separate.
Allplan API 2026.1; executable resources 16.1617.8659.814 / 2026.0.1.0;
embedded CPython 3.13.13. These strings do not independently identify the UI
hotfix; previous accepted Allplan 2026-1-7 observations remain separate.

## Ten native steps

| Step | Observed result |
| --- | --- |
| health_preflight, health_after | Verified matching 0.11.0, same session |
| audit_before | Six columns, 5 findings, complete, 0 unchecked |
| standard_preview | Standard 1.0.0, S06 exception, exactly one S05 layer change |
| standard_apply | Completed; layer 3701 → 3700 / SZ_OGÓ01, exact readback, audited fields match plan; 4 findings |
| standard_replay | Exact same request/ID, replayed=true/read_only=true, same saved outcome |
| selected_preview | Status=NWE selection, S05 exception, exactly one S06 status change |
| selected_apply | Completed; existing MCP_QA_STATUS attribute 5002 NWE → NEW, exact readback, audited fields match plan; 3 findings |
| selected_replay | Exact same request/ID, replayed=true/read_only=true, same saved outcome |
| audit_after | Six columns, only QA-001/QA-002/QA-002 mark findings; complete, 0 unchecked |

S05 model **51db6258-4f95-4fab-ac80-8948e13bfd21**, center
(6000, 6000, 1500) mm. S06 model **d26a3d87-2981-4657-b592-65c894ce41ba**,
center (12000, 6000, 1500) mm. Standard selection: 5 selected, 1 exception,
0 unknown predicates. Rule selection: 1 selected, 4 false, 1 exception,
0 unknown predicates. Both previews are read-only and evaluation-eligible.

| Workflow | Execution ID | Plan ID | Plan hash |
| --- | --- | --- | --- |
| apply_office_standard | 750655bf38ee458792b375dcb413f24d | db8cdfe9ad2b43e0b469286051b46f20 | d355765ff055aed13fbf04d79c5c3038db2d3de51d3b852fa62546bbe9280bf9 |
| rule_based_edit | 69326f48d8724ae7abb6105f3263ba23 | 038e1f21b36743d8ab0b4ef94b6f58ab | 9c8737dcc57a39415a11ee778f68357e2920810d97324ae3d5a6595783fad5b9 |

Both plan hashes and workflow-bound Apply request hashes independently recompute
from the captured plans and expanded requests/profile. All four audit report
hashes recompute. Fresh source observations chain from initial audit to standard
preview, standard post-audit to selected preview, selected post-audit to final
audit. Finding counts are **5 → 4 → 3**, then final audit reconfirms 3.
Final 24 checks: 20 pass, 3 fail, 1 not_applicable, 0 not_checked. Audit fail is
expected because the three mark findings remain.

## Acceptance limits and continuation

The owner confirms both requested changes, host survival and unchanged other
elements. Logs additionally verify audited fields in the six-column scope.
Two separate Undo operations are the observed limit; there is no grouped
transaction or automatic rollback. The owner did not specify whether the model
was left repaired, undone or redone. A future current-state read must establish
that; completed/replay history does not prove current values after UI Undo.

[Completed procedure](../m3-workflow-apply-batch.md); do not repeat writes/Undo.
Preserve the original Local journal, project copy and package logs. Raw flags
allplan_acceptance=not_run, runtime_verified=false and ready_for_ui_observation
remain historical and unmodified. This separate record supplies scoped acceptance.

Next implementation: actual mark assignment and deterministic versioned-standard
numbering, retaining full-scope collision/source checks. Then supported-lifecycle
native conflicts and controlled partial/unknown recovery. The broader 1–32-change
or other-file scope, grouped Undo, crash/power-loss and project-copy identity are
not accepted by this gate. Final UAT and main integration remain open.
This documentation update runs no new tests, builds or native operations,
changes no runtime/version and rebuilds no delivered archive.
