# Testing policy

Preserve meaningful regression coverage and test according to the change.
An explicit owner pause overrides the schedule; do not run tests/builds/native
gates or manually dispatch CI while paused. The prior M3 closure pause was
superseded by the owner's resumed, fixture-bounded work.

| Change | Required validation |
| --- | --- |
| Iterative implementation | Focused affected tests, including dependent read/audit modules; HTTP tests for MCP/transport/launcher changes. |
| Documentation only | Read/diff formatting and links. No runtime tests, builds or old artifact/evidence hash reruns. |
| New owner-test package | One final full portable suite, frozen sync, wheel/sdist build and exact package/installation verification; source CI evidence for the tested commit. |
| Dependency/installer/builder/workflow change | Full suite and six-configuration compatibility matrix. |
| Main integration/release | Full suite and full Windows/Ubuntu × Python 3.11–3.13 matrix for the final candidate; native acceptance remains separate. |
| Native observation | New/materially affected behavior only; retain unchanged completed-gate evidence and scope. |

Repeat a full final-candidate run only after relevant new changes/failures or
unresolved concerns. Focused PASS is not full PASS. The model owns automated
checks, diagnostics and packages; the owner receives a small version/build-bound
walkthrough with expected results, reset/recovery and PASS/FAIL/BLOCKED reporting.
Use ready_for_owner_test before observations, accepted_on_build only with evidence.
[Source commands](../README.md#source-development).

## CI

[portable.yml](../.github/workflows/portable.yml) runs PR updates once; pushes
trigger only on main. Docs/README/evaluation-packages-only updates skip product
jobs; a mixed PR may still run its lightweight configuration job to detect this.
Routine code updates use Windows/Ubuntu Python 3.12. Dependency, installer,
package-builder or workflow changes select the full **six-job** matrix.
Synchronize compares the latest update; missing comparison history selects the
full matrix conservatively. Superseded runs cancel; cancellation is not PASS.

Before main integration/release use workflow_dispatch with full_matrix=true,
even without matching paths. Results remain scoped to their tested source;
[current evidence](validation-status.md#portable-verification-and-delivery).

## Retained checks and hashes

Keep reviewed plan/request hashes, fresh source checks before Apply, journal
integrity/identity validation and installer/health hashes. Old PASS never replaces
fresh model authorization. No runtime protection is removed by this schedule.
For a new delivery, record manifest/checksum and verify the actual extracted
installation once. Later docs refer to that result without rebuilding old archives.
The existing package test already covers deterministic ZIP builds/registration;
do not redundantly repeat those checks on every job. Independent hash review is
appropriate for a suspected mismatch/corruption or explicit review request.
