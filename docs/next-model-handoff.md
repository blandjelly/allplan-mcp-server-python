# Current handoff

Updated **2026-10-13 Europe/Warsaw**. Working branch **codex/m4-property-discovery**,
based on **codex/m3-repair-preview**, package **0.16.1**; no main integration/release.
M3 [PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2) remains separate.

**M0–M3 are closed within the retained test project.** Bounded UAT-05/06 uses
existing one-/two-change evidence, not broader native acceptance. The owner
resumed work and narrowed closure to this fixture; older pause instructions
are historical. [Scope, test results, limits and evidence](validation-status.md).

## Preserve current state

The owner confirms the original MCP_QA_DEMO copy is saved after Undo:
**C02/C04=S02, C03 undefined, C05 structure, C06 NEW**. Keep package logs,
saved execution identities and **Local/.allplan-mcp/repairs**. No Redo or repeated
writing gate is requested. After an unknown result use [read-only recovery](diagnostics.md),
never a new Apply. At 128 journal records stop new writes; do not delete history.

## Next action

**0.16.0 failed natively on 2026-10-13:** health/integrity passed, then the first
/model-properties request crashed Allplan 2026-1-7. No metadata response or UI
stage followed. XML and bridge.log provide no inner exception/native stack;
the exact API cause remains unknown. [Incident](m4-native-crash-0.16.0.md).

The broad model_properties route is quarantined before native access. Its
unconditional GetEnumValues calls were removed without claiming that caused the
crash. **0.16.1** introduces model_property_probe with persistent before/after
reader records and client request_pending evidence. The delivery runs only one
Column sample in foreground file 101, then stops: no definitions/enums/UI/writes.

Next owner action: [0.16.1 delivery](../evaluation-packages/0.16.1/README.md) and
[short isolated observation](m4-isolated-probe-owner-test.pl.md), original retained
MCP_QA_DEMO on Allplan 2026-1-7. Return the sample JSON, m4-native-probe.jsonl and
bridge.log. Do not repeat 0.16.0 or advance to other phases before reviewing this.
Native discovery, fire-resistance/W1 binding, highlight and native selection remain
unaccepted; K1/K2/K3 stay open. Later attribute-name/definition/layer probes are
separate observations, never an automatic chain. Continue criterion-based W1
planning and thin-wall C35 work only after actual field ownership/support resolves.

Preserve the original project after Undo, all execution IDs and Local history.
The M3 guard/journal/write scope is unchanged. No writing-gate repetition is requested.

Read [architecture](architecture.md), [read/audit tools](tool-reference.md) and
[M3 execution](m3-execution-contract.md) before coding. The model researches APIs,
implements checks and prepares packages; the owner observes through Allplan/local
Windows Codex without editing Python/JSON or finding attribute IDs.
