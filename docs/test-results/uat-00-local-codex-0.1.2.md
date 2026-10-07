# UAT-00 local Windows Codex — 0.1.2

Date: 2026-10-07. Tasks M0.1 / M0.2 / M0.3 / M0.5. Result: **PASS**; final owner acceptance recorded in [M0 closure](m0-acceptance-0.1.2.md). The stopped-host negative check was subsequently verified in the [UAT-01 follow-up](uat-01-box-restart-0.1.2.md), including the recovery instruction and successful restart. The complete M0 exit gate is now accepted after the owner confirmed all remaining UAT-01 tests.

## Received evidence

- [Diagnostics at 14:32:53 Europe/Warsaw](evidence/diagnostics-20261007T123256Z.json).
- [Diagnostics at 14:35:34 Europe/Warsaw](evidence/diagnostics-20261007T123537Z.json).
- Read-only inspection of the local Codex chat **Sprawdź zdrowie i wersję Allplan**, host `local`, Windows working directory. The chat records completed MCP calls to `allplan_m0.allplan_health`, `get_allplan_version` and `get_all_object_names`. Its responses report healthy host, version 2026.1 and an empty names list. No mutation tool was called in those turns. Raw MCP response bodies are not included in the thread snapshot; the uploaded diagnostics corroborates health/version.

Both reports identify package/bridge **0.1.2**, verified installed hashes, all five default tools, successful diagnostic health/version and host session `528f7d87-1f3f-439d-99ce-13c5f67c0078`. These are repeated observations of one session; they do **not** prove cancellation/restart.

| Field | Observed |
| --- | --- |
| Owner's Allplan UI build | 2026-1-7 |
| Allplan API release | 2026.1 |
| Executable file / product version | 16.1617.8659.814 / 2026.0.1.0 |
| External / embedded Python | 3.14.8 / CPython 3.13.13 |
| Codex client | Local Windows Codex app; app version not supplied |
| Fixture | Current document returns no display names; project/file identity not supplied |
| Changes | None requested by the recorded read-only calls |

Request references:

- 14:32:53 direct host `77b93bb6-914b-49b1-ace1-21ee08bc97c0`; diagnostic MCP health `6f90ae8c-a2a8-4d06-bee0-cc22d4ca4c9a`.
- 14:35:34 direct host `4279d955-36c8-48cf-8a2b-021dc838b77a`; diagnostic MCP health `b22f084e-c4b3-4616-9de2-92b45c14def7`.
- Local Codex call records: health `exec-cb79da96-62b2-4696-b3dd-ac877b018d8c`; version `exec-ba0ed3ca-3ff4-4c90-ae49-dfeb5d00f74a`; names `exec-99cefa10-5b77-44b3-a954-434ab943a4d9`.

The earlier cloud-chat tool-absence problem is resolved by using local execution. The UI-reported hotfix remains distinct from automatic release/executable-version metadata. Empty display-name results alone do not prove full model emptiness or stable identity.

## Next owner case

Continue [UAT-01](../m0-acceptance-batch.md) in the same local chat and a disposable empty active drawing file. Submit one 1000 × 1000 × 1000 mm box once, inspect count/dimensions, then perform ESC/stopped-host health, restart/new session, minimize/restore and project-switch checks. Record the reset. No write is authorized or executed by this evidence-processing step.
