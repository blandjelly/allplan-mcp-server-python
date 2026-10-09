# Diagnostic commands

Run these on the Windows machine running Allplan, with the installed bridge and
MCP launcher active. [Windows setup](windows-setup.md) covers installation and
recovery; [fixture setup](fixture-guide.md) defines the demo's exact resources.
Restart StartPythonHost after UI/file-state commands that end its interactor.
No accepted M1/M2 batch needs repetition without a relevant change or defect.

| Packaged command | Purpose and explicit scope |
| --- | --- |
| Diagnostics.cmd | Read-only health, versions and bounded context; no model mutation. |
| M1 Metadata.cmd | Inspect files 1/2 with passive reads and attribute 498, using `docs/probes/m1-metadata-1-2.json`. These IDs are a diagnostic example, not demo mark bindings. |
| M1 Profile.cmd | Fresh demo resource compatibility, using `docs/probes/m1-profile.json`; creates no attributes/layers. |
| M1 Component Types.cmd | Native root/type diagnostic, using `docs/probes/m1-component-types.json`. |
| M1 Final.cmd | Six explicit query requests from `docs/probes/m1-final.json`, with summaries and bounded page traversal over the reference fixture. |
| M2 Audit.cmd | Read-only file-101 demo audit from `docs/probes/m2-audit.json`, with JSON and readable TXT findings. |
| M2 Stability.cmd | Loaded-boundary preflight, two file-101 audits, public/direct-host scope rejection and post-error health; stops on failure. |

M1 Component Types.cmd is in `windows/`; run it there in a source checkout.
The other commands are also placed at the evaluation ZIP's top level.

Reports are written under the extracted package's ignored `logs/` directory.
The bridge separately keeps UTC request/error logs at
`Local/.allplan-mcp/logs/bridge.log`, with a 1 MiB limit and two backups.
Log-write failure falls back to the console. Native rotation/traceback behavior
has not been accepted from the owner-supplied reports.

For an explicitly prepared source diagnostic:

```sh
uv run --frozen allplan-mcp-diagnostics --query-request docs/probes/m1-profile.json
uv run --frozen allplan-mcp-diagnostics --audit-request docs/probes/m2-audit.json
uv run --frozen allplan-mcp-diagnostics --m2-stability
```

Input validation precedes network reads. Lost responses are never automatically
retried by these launchers. The stability preflight requires matching 0.6.1
host/MCP versions, verified installed hashes and the loaded marker
`ui_dispatch_exception_boundary=contained_result_error_v1`; an old loaded bridge
must be restarted before probing. Scope [101,102] is deliberately rejected by
the file-101 profile. Do not treat this negative test as an accepted passive audit.

Report flags such as runtime_verified=false/allplan_acceptance=not_run are not
an automatic UAT decision. [Acceptance records](validation-and-history.md)
separate portable checks, native results and owner UI observations. Keep new
raw diagnostic/crash files outside tracked documentation; summarize relevant
scope, hashes, findings and unresolved limits when a new record is needed.
