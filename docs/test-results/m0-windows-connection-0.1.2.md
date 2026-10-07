# M0 Windows connection evidence — 0.1.2

Date: 2026-10-07. Tasks M0.1 / M0.2 / M0.3 / M0.5. Evidence: [owner-uploaded diagnostics](evidence/diagnostics-20261007T122721Z.json), captured at 12:27:18 UTC (14:27:18 Europe/Warsaw).

## Observed on the owner's Windows machine

- External MCP package and installed bridge: **0.1.2**.
- Installed bridge integrity: **verified**, no mismatches.
- API release: **2026.1**; main release **2026**.
- Owner's UI version observation: **2026-1-7**. The diagnostic hotfix field remains `not_checked`; do not infer a marketing hotfix from numeric executable metadata.
- Running executable file version: **16.1617.8659.814**; product version: **2026.0.1.0**, recorded literally.
- Embedded CPython: **3.13.13**; external Python: **3.14.8**.
- Host session: `528f7d87-1f3f-439d-99ce-13c5f67c0078`; direct request `8983796a-4027-4ac1-bd40-f4e96ace20be`; MCP health request `faa51183-d378-4d2e-8aa5-1f54198cc15c` reaches the same session.
- Streamable HTTP tool discovery succeeds and exposes the five intended baseline tools. Diagnostic client calls `allplan_health` and `get_allplan_version` successfully against the real Allplan host.

This establishes working read-only host/MCP connectivity from Windows and the observed runtimes. It does not establish Codex tool invocation, names, box geometry, UI cancellation/restart, minimize/restore or project-switch behavior. The diagnostic's generic `allplan_acceptance: not_run` and `runtime_verified: false` are static release fields, not evidence that its recorded read-only calls failed.

## Codex test-chat diagnosis

The owner ran Connect Codex.cmd, restarted Codex and tried a new chat. The related chat **Sprawdź wersję Allplan** was inspected through the app's read-only thread tools: it is cloud-backed (`hostId: durable`, cwd `/workspace`). Its response says Allplan tools are absent; no tool call was executed. A user configuration on Windows cannot make that cloud chat access Windows loopback.

UAT-00 remains pending for local Windows Codex. Keep the 0.1.2 host and launcher running, select a local Windows folder and local execution for the test chat, then repeat the existing read-only prompt. No reinstall is justified by this log. If that local chat also lacks tools, inspect its MCP configuration/status and `logs/connect-result.json`; do not collect the entire user config, which may contain unrelated credentials.

UAT-01 is NOT_RUN. M0's integrated exit gate remains pending.
