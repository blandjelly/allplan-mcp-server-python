# UAT-01 box and host restart — 0.1.2

Date: 2026-10-07. Tasks M0.3 / M0.4. Result: **PASS**, following the owner’s final confirmation that all requested tests work correctly; see [M0 closure](m0-acceptance-0.1.2.md). The owner reports that the solid looks correct in Allplan, reset the server connection and repeated the test. Three uploaded diagnostics plus the local Codex call history confirm box submission and a real host stop/restart. No new model action was issued while processing this evidence.

## Recorded sequence

| Local capture time (Europe/Warsaw) | Evidence | Observed |
| --- | --- | --- |
| 14:37:56 | [First report](evidence/diagnostics-20261007T123759Z.json) | Host and MCP health/version succeed; host session `528f7d87-1f3f-439d-99ce-13c5f67c0078`. |
| 14:40:59 | [Stopped-host report](evidence/diagnostics-20261007T124107Z.json) | MCP remains discoverable, but direct host and MCP health/version return `host_absent` with an instruction to open a project and start StartPythonHost. This is the expected negative result while the host is stopped. |
| 14:43:05 | [Restarted-host report](evidence/diagnostics-20261007T124308Z.json) | Health/version succeed again; new host session `51c71067-e52f-41cb-ae21-11d9465f33d8`, proving that this is a new bridge instance. |

Package and installed bridge: **0.1.2**. Allplan API release **2026.1**; owner UI build **2026-1-7**. External Python **3.14.8**; embedded CPython **3.13.13**. Successful reports show verified installed bridge integrity. Codex app version and project/file identity remain unspecified.

## Local Codex and geometry evidence

The local chat **Sprawdź zdrowie i wersję Allplan** records one completed `create_box` call in each of two separately requested test turns, both with length/width/height **1000 mm**:

- First tool record `exec-6f0ddaae-9494-4238-ae4b-e31dafbb0558`; reported bridge request ID `ce034e0b-59a3-478f-820e-45da082e06ac`.
- Repeated test after reconnection: `exec-c88782b6-a3db-4bec-bef5-ec2ac3be1afd`; bridge request ID `b883fcc0-9ebf-427d-b216-5558efef403f`.

There is one tool call per request turn and no recorded automatic write retry. Two intentional test requests are not evidence of a duplicate caused by one request. At the intermediate report, the owner confirmed visual appearance but had not yet supplied exact measurement/count or fixture-reset observations. The subsequent final owner confirmation covers all those requested checks. API readback remains unverified. The first assistant's statement that the box was created is not used as readback evidence.

Local Codex also records failed read-only health/version calls while the host was absent, followed by successful read-only calls after restart. Failed call bridge IDs: `f80cf07f-1b89-4d58-85cf-31fe2cc2e058`, `129f78e9-9724-47d7-81a4-9230ed2edaf3`. Thus the UAT-00 stopped-host error/recovery-message expectation is also verified.

## Initially remaining observations — now owner-confirmed

- Confirm the box measures 1000 × 1000 × 1000 mm and one box appeared per intentional request.
- Confirm whether the host was stopped using ESC; the supplied description says connection reset without specifying the UI action.
- Minimize Allplan, perform a read-only health/version call, restore it and observe responsiveness.
- Switch to a second disposable project/empty drawing file, restart StartPythonHost if the UI ends it, and read health/names for the current document.
- Delete test boxes or restore the test baseline; record the cleanup. No automatic cleanup is performed.

Do not repeat the box creation just to obtain these observations; inspect the existing test result and use read-only calls for lifecycle checks. The owner subsequently confirmed all these steps; the M0 integrated exit gate is accepted on the tested build. No profile/workflow feature is accepted by this baseline geometry test.
