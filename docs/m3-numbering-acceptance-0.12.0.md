# M3 mark numbering — bounded native acceptance, 0.12.0

**PASS**, 2026-10-10 Europe/Warsaw, retained disposable fixture on Allplan
2026-1-7. Exact delivered package 0.12.0, clean source
fd78700378eceb6f217e4ca30a83b88004b73a57; original ZIP unchanged.
M3/UAT-05/UAT-06 remain open. This closes the requested mark-numbering gate;
no repeat of it or the earlier accepted layer/status gates is requested.

## Native observations and owner confirmation

All ten gate steps passed in host session 46818eaa-91eb-446b-9762-bb4bbab88e95.
The bridge reported 0.12.0, exact source and verified installed integrity at both
ends. All 23 reported bridge hashes match the existing package manifest using
the documented Library/PythonParts → Library/PythonHost installation mapping.
Observed API release 2026.1, executable file/product resources
16.1617.8659.814 / 2026.0.1.0 and embedded CPython 3.13.13 match the retained
setup. The hotfix label is owner-reported; resources do not independently map it.

The initial complete six-column audit contained only three mark findings;
layer/status rules already passed. Two fresh numbered previews returned the
same exact assignments and retained C02/S02; another full audit after previews
was unchanged. Exact reviewed-plan revalidation passed.

Execution a5595bfb9bed4d9c9f848526177ec8b8 replaced existing string attribute
**5001 / MCP_QA_MARK**, in executor order:

| Target | Model UUID / model-local center | Old → new | Native readback |
| --- | --- | --- | --- |
| C04 | 4f3cc27e-5224-403d-939d-7b4e0cedf9a2 / (0,6000,1500) mm | S02 → S04 | S04, applied |
| C03 | 65ab07fe-d37a-4adf-b1b6-3040fdde84a2 / (12000,0,1500) mm | `<niezdefiniowany>` → S03 | S03, applied |

Completed execution reported audited_fields_match_plan=true and a complete audit
with **0 findings, 24 pass, 0 not_checked**. Exact-ID replay was read-only with
the same saved outcomes. A subsequent numbered preview had zero changes and
evaluation_apply_available=false. Owner confirmed correct marks, host survival
and unchanged other elements. That UI confirmation is distinct from the
executor's bounded audited-field verification.

Owner observed two separate Undo steps in reverse write order:

| State | C03 | C04 |
| --- | --- | --- |
| After Apply | S03 | S04 |
| After first Undo | `<niezdefiniowany>` | S04 |
| After second Undo | `<niezdefiniowany>` | S02 |

Read-only Recover subsequently ran in host session
b8573f81-b40b-4951-85b7-e10f264836c5. It returned old_value_observed for both
targets and a complete six-column audit with the original **3 findings**;
all rule/model state and raw audited values agree with the pre-Apply audit.
Historical outcomes remain completed/applied. This reads current values after
Undo, does not request another mutation, and does not prove native unknown-result
recovery. The changed recovery host session is recorded without inferring its cause.

## Evidence and inspection

Eight original uploads are retained byte-for-byte in
[the evidence directory](../evaluation-packages/0.12.0/native-acceptance/20261010-owner/),
with [upload sizes/hashes](../evaluation-packages/0.12.0/native-acceptance/20261010-owner/uploads-manifest.json)
and [inspection](../evaluation-packages/0.12.0/native-acceptance/20261010-owner/inspection.json).
Three newly captured plan hashes, the Apply request hash and four captured audit
report hashes recompute. Original MCP text matches all structured responses and
the human-readable gate report. New evidence inspection invokes no Allplan,
runtime test, package build or repeated old archive/evidence hash verification.

The per-execution apply_pending JSON/TXT is the immutable intent saved **before**
the request. The latest pointer records completed; full gate/recovery reports
record the later results. The earlier intent snapshot is not a failed execution.
The m3-marks-preview filename contains the full numbering write gate, including
Apply and replay; its filename alone does not describe read-only behavior.

## Project state and remaining work

**Leave the original disposable project after the two Undo operations.**
Keep C03 missing, C04=S02, C02=S02; leave the already accepted C05 structure
layer/C06 NEW status unchanged. The current complete audit has three mark
findings. No Redo or new Apply is requested. Preserve the original project,
Local/.allplan-mcp/repairs and logs; do not remove historical execution records.
Future work starts with fresh health/context/audit and new reviewed plans/IDs.

Acceptance covers this two-target numbered existing-string-mark execution,
deterministic/unchanged preview, readback/audited verification, read-only exact-ID
replay, subsequent no-op, owner-confirmed two-step Undo and completed-execution
recovery after Undo. It does not accept arbitrary numbering standards/scopes,
every explicit mark request/workflow, grouped Undo, graphical labels, attribute
append, supported-lifecycle same-session source conflicts, controlled native
partial/unknown outcomes, journal maintenance or broader durable/copy identity.
Those remaining items and final UAT/main integration remain open.
