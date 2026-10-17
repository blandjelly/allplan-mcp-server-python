# Current handoff

Updated 2026-10-17 Europe/Warsaw: **0.18.1 transport candidate** on
`fix/m4-host-timeout`, based on `codex/m4-0.18.0` at `0dbe7cf`.
The supplied MCP and bridge logs correlate a health timeout with an incomplete
HTTP 200 response. A timer-driven Python UI queue, cooperative worker scheduling,
pre-start cancellation and stage timing replace the synchronous CLR dispatch
round trip. The underlying native scheduling/socket cause remains unproven.
[Incident evidence, changes and short Polish health-only check](mcp-timeout-0.18.1.md).
Clean source **f477f138231f2a8f45690c03bd761364c7e94ab6** passed **306 portable
tests**, frozen sync, builds, exact ZIP installation/upgrade from 0.18.0/restore,
and [source CI 39026387338](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39026387338),
**6/6 Windows/Ubuntu × Python 3.11–3.13**. Thirty bridge hashes verified;
journal/trace/bridge log preserved. [Frozen delivery](../evaluation-packages/0.18.1/README.md).
Status **ready_for_owner_test** for health/response delivery only; native recovery
is **not_run**. [Draft PR #7](https://github.com/blandjelly/allplan-mcp-server-python/pull/7)
targets `codex/m4-0.18.0`, without main integration.
All original 0.18.0 artifacts remain frozen. The preceding Wall/Columns work and
its limits below remain applicable after transport verification.

Prior 2026-10-15 Europe/Warsaw record: **0.18.0**, **ready_for_owner_test** for its Wall read.
Clean source **5ea4bcfd88f500bbf137e361ba5d6cc3d83710b5** passed **289 portable
tests**, six Windows/Ubuntu × Python 3.11–3.13 CI jobs, frozen sync, builds and
exact ZIP install/upgrade from 0.17.2/restore verification (30 bridge hashes;
journal/trace preserved). The package carries the
0.17.2 `column_layer.py` and `column_layer_diagnostics.py` runtime unchanged,
and adds the isolated wall-property phase, its diagnostic and
**M4 Wall Properties.cmd**. The [0.18.0 delivery README](../evaluation-packages/0.18.0/README.md)
and [short owner guide](m4-wall-properties-0.18.0.pl.md) record the bounded next observation.
No main integration.

Source-only work after that delivery adds `wall_report_analysis`, a stdlib-only
CLI for an already saved 0.18.0 report. It recomputes strict `<240`, compares the
exact native material text and applies file+UUID exceptions. It checks complete
same-reported-host steps, source/ref agreement and field provenance, but never
proves report authenticity, live model state, native units or material binding.
Every result is non-executable: no plan/Apply IDs, no native/HTTP calls, and
`usable_for_write=false`. **10 focused tests PASS**; this is not a full-suite
result. Source **0c3a2987df164254d03cd749bcb72b71a79716ee** additionally passed
[standard Windows/Ubuntu Python 3.12 CI](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38824865834),
**2/2 jobs**, with the full **299-test** portable suite and standard builds.
[Usage and limits](m4-wall-report-analysis.md). No new owner package,
version bump or rebuild of the frozen archives is needed for this source-only
step. The supported material setter remains blocked pending native evidence.

The 0.17.2 artifacts, README, source and CI evidence remain unchanged. Its
native observation was **not run**. The owner deferred native checks for both
versions to a later time: either package may be tested first, independently.
The 0.17.2 native check is not a prerequisite for 0.18.0, and the wall read is
not a prerequisite for the retained Columns workflow.

The new `wall_sample` phase is limited to one existing, single-tier native Wall
in foreground drawing 101. It reads the first tier's thickness and raw material
after confirming the object type and `TierCount == 1`. For the fixture wall,
expect 200 mm under the API-mm assumption and
`sample.criterion.matches_assuming_native_mm=true` only when both fields are
valid. Runtime unit verification and material
target binding remain false/not checked; no material write is available. A
native wall read must be observed before material writes can be enabled.

The owner requested the full first scenario and explicitly accepted highlighting:
Columns without fire resistance classification → matching targets highlighted →
existing W1. The owner clarified the field as **Klasa odporności ogniowej**, with
F30/F60 values. The [0.17.1 observation](m4-column-layer-observation-0.17.1.md)
confirmed the exact binding and two writes but exposed that the already-W1
matching no-op was omitted from highlighting.

The retained 0.17.2 runtime assigns hash-bound `highlight_targets` to all matched `change` and
`no_op` Columns, while `changes` contains only layer setters. A full plan with
no changes can still highlight all matches; it cannot be confirmed or applied.
Unknown values block the action, and more than 32 changes remain blocked.
Native highlighting behavior for 0.17.2 remains unobserved; use the
[short 0.17.2 owner guide](m4-column-layer-0.17.2.pl.md) if testing that
package later. It does not gate the independent 0.18.0 wall observation.

The 0.17.0 owner run on **2026-10-15 at 19:40 Europe/Warsaw** was **BLOCKED**.
It bound `Odporność ogniowa` (1398), absent from ReadAll on all six Columns;
the six unknown states blocked before highlighting/Apply/setters. This is a
semantic field-binding error, not acceptance of the requested criterion merely
because the write guard stopped. `health_before` was healthy; `journal_before`
was available with seven records and no blockers. There is no `health_after`, so
the report does not establish host health throughout or after the run.
[Original JSON](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.json),
[original TXT](../evaluation-packages/0.17.0/native-acceptance/20261015-owner/m4-column-layer-check-20261015T174011580242Z.txt).

0.17.1 defaults to exact names `Klasa odporności ogniowej` /
`Fire resistance classification`, with runtime ID/name roundtrip and no fallback
to 1398. Official 2026-1 documentation identifies 935 as Fire resistance
classification and the SDK uses 935 with F30; 935 is evidence, not a hardcoded
runtime binding. Keep the existing ReadAll reader and genuine omissions unknown.
Do not add computed reads or broad metadata discovery to compensate for the wrong name.

The uploaded 0.16.1 report contains one successful raw Column read bracketed by
healthy replies from the same host. The owner reports no crash. Names, layers,
UI and writes were not requested, so this is not acceptance of the new workflow.
The 0.16.0 native root cause is still unknown; retain its FAIL_CRASH record and
quarantine. New workflow avoids broad definition/enum calls and retains native
container owners through writes/readback. Do not infer native crash containment.

`column_layer` previews criteria directly, without fake audit findings, and uses
the shared RepairExecutor/journal. Unknown/absent-from-ReadAll values block the
action; matched Columns already on W1 are no-op. 0.17.2 highlights all matched
Columns (changes plus no-ops), but applies setters only for changes. Full
source/resource revalidation, native writability, readback and bounded journal
guards remain. The old isolated probe launcher remains available, but the new
task uses **M4 Columns to W1.cmd** and **M4 Columns Recover.cmd**.

The next native observation, after 0.18.0 has its automated and package records,
is exactly one wall read using **M4 Wall Properties.cmd**. Bracket the request
with `health_before` and `health_after` in the same MCP session; preserve
`logs/wall-properties-*.json` and `.txt`, `bridge.log`,
`Local/.allplan-mcp/logs/m4-native-probe.jsonl`, and
`Local/.allplan-mcp/repairs`. The pending request must be saved before sending;
lost replies do not trigger another native call. If Allplan crashes, retain the
trace and do not rerun. See the [wall guide](m4-wall-properties-0.18.0.pl.md).
This bounded read does not accept material writes or the broader M4 workflow.

M3 acceptance remains limited to its historical fixture/build/single- and
two-change cases. See [validation](validation-status.md) and [testing policy](testing-policy.md).
