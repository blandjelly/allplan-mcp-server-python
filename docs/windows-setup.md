# Windows setup — 0.16.0 evaluation

Use the [complete 0.16.0 ZIP](../evaluation-packages/0.16.0/README.md) on the
Windows machine running Allplan and Codex. External Python **3.11+** (normal
distribution with Tcl/Tk/launcher) and internet access for locked dependencies
are required. Allplan/Python/Codex are not bundled. [Acceptance is fixture-bound](validation-status.md).
The new property/highlight probe is ready_for_owner_test; follow the
[M4 observation guide](m4-properties-owner-test.pl.md). Existing M3 writing gates need no repeat.

1. Extract the whole ZIP into a writable versioned folder; never run inside the ZIP.
2. Close Allplan/MCP and run **Setup.cmd**. Select the actual existing user Local
   folder from Allmenu/Explorer, commonly Documents/Nemetschek/Allplan/2026/Usr/Local,
   not Prg/Std/the project folder. Setup checks hashes, installs isolated external
   dependencies and replaces owned Library/PythonPartsScripts host trees with backup.
3. Open the original test project. Library → Private → PythonHost → **StartPythonHost**.
   Keep it running; ordinary UI commands may cancel it. Restart from Library if needed.
4. Run **Launch Allplan MCP.cmd**, then **Connect Codex.cmd**, restart Codex and
   select local Windows execution. A cloud chat at /workspace cannot use Windows localhost.
5. Run **Diagnostics.cmd**; retain logs/installation.json and diagnostics.

Endpoints: bridge **127.0.0.1:5679**, MCP **http://127.0.0.1:8888/mcp**.
The connection helper preserves existing Codex configuration, backs it up and
adds mcp_servers.allplan_m0. Report custom config paths/conflicts; do not overwrite
another server by guess. No tunnel or remote deployment is configured.

## Update and restore

Close Allplan/MCP, extract each version separately and run Setup. Reopen Allplan
to clear loaded modules. **Restore bridge.cmd** verifies and restores this
package's previous host backup, then use the previous package launcher.
Bridge backups are under Local/.allplan-mcp/backups; they do not back up models
or repair records. Preserve **Local/.allplan-mcp/repairs**, original project,
package logs and saved IDs. Never mix files from different package versions.

## Common failures

| Result | Action |
| --- | --- |
| host_absent / session_unavailable | Open the intended project, start/restart StartPythonHost; repeat a read-only check. |
| Port busy / MCP cannot connect | Close previous hosts/consoles, verify launcher endpoints and restart Codex; use Diagnostics. |
| Missing Library item | Clear filters; check installed Local/Library/PythonHost and logs/installation.json, not another Local by guess. |
| Integrity failure | Extract a complete fresh ZIP; keep versions separate. |
| Lost reply / execution_unknown | Preserve saved identity/history and use [read-only recovery](diagnostics.md); do not retry Apply. |
| Incompatible build / invalid payload | Report version/prompt/request ID; the model diagnoses/corrects the typed request. |

Keep the [fixture](fixture-guide.md) saved after accepted Undo. Completed writing
gates need no repeat. Native API release/executable strings do not alone establish
the exact UI hotfix; include About/version information when diagnosing a new build.
