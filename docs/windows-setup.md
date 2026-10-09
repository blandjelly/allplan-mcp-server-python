# Windows setup — 0.6.1 evaluation

This is a local evaluation package. M0 is accepted on the owner’s Allplan 2026-1-7 setup with local Windows Codex; see [the verified baseline](next-model-handoff.md#accepted-baseline). Portable checks are separate evidence. The package does not install or include Allplan, Python, or Codex. Initial setup needs internet access for the pinned external-server dependencies.

**M1 is closed; UAT-02/UAT-03 PASS within the bounded read contract** on
Allplan 2026-1-7, package 0.5.3 and demo profile revision 1.0.2. Resource binding,
native geometry/hierarchy, display-unit invariance and nonzero XY offset are
accepted for the recorded fixture. See [acceptance, exact artifact and limits](test-results/m1-acceptance-0.5.3.md).
Keep the accepted 0.5.3 archive unchanged; no repeated M1 owner batch is
requested. **M2 / UAT-04 PASS** on the retained fixture with 0.6.1;
[native evidence and limits](test-results/m2-acceptance-0.6.1.md).
The setup steps below cover the accepted package. M2 read-only audit was implemented in 0.6.0; 0.6.1 contains callback exceptions
and preflights invalid scope, with the targeted native recovery test passed;
M3 repair is unavailable on main; the separate
[draft PR #2](https://github.com/blandjelly/allplan-mcp-server-python/pull/2) contains
read-only preview awaiting native owner verification.

## Install through Explorer

1. On the Windows machine running Allplan, install the normal Windows distribution of [Python 3.11 or newer](https://www.python.org/downloads/windows/) if needed. Keep its Tcl/Tk and launcher components. This is the external MCP runtime; Allplan's embedded Python is detected independently. The local automated run used Python 3.12.14.
2. Extract `allplan-mcp-0.6.1-windows-evaluation.zip` into a writable folder, for example `Documents\Allplan MCP\0.6.1`. Extract it completely; do not run scripts from inside the ZIP. Keep the resulting `allplan-mcp-0.6.1` folder intact.
3. Find your actual Allplan user **Local** folder using Allmenu's user-folder information / Windows Explorer. A common location is `Documents\Nemetschek\Allplan\2026\Usr\Local`; redirected Documents and custom paths are supported. Select the existing `Local` folder, not `Prg`, `Std`, or the project folder. The `2026` example is a target path, not evidence of your installed build.
4. Close Allplan. Double-click **Setup.cmd**. It checks the package hashes, creates isolated external environments, installs the locked dependencies and opens a folder chooser for the actual `Local` folder. No administrator rights or manual module copying should be needed. Cancel the chooser to leave the bridge unchanged.
5. Setup replaces `Library\PythonHost` and `PythonPartsScripts\PythonHost` and removes the old `PythonParts\PythonHost` installation after backing it up, copying their full contents, including `sandbox`. The previous contents and absence of either folder are recorded under `Local\.allplan-mcp\backups\<backup-id>`. Other PythonParts are preserved. Setup prints the installed package version and backup ID; `logs\installation.json` records them.
6. Open Allplan and a disposable empty test drawing file. In the **Library** palette, open **Private** (the user library), then **PythonHost** and start **StartPythonHost**. Its palette shows that the Python host is started. Keep the interactor running. An ordinary command may end it; restart from Library when necessary.
7. Double-click **Launch Allplan MCP.cmd** and keep the console open. It starts Streamable HTTP at `http://127.0.0.1:8888/mcp`, with the Allplan bridge at `http://127.0.0.1:5679`. `execute_python` is disabled in the evaluation launcher.
8. Double-click **Connect Codex.cmd** on the same Windows machine. It adds the `allplan_m0` server to the standard user `.codex\config.toml`, preserving existing settings and saving a timestamped backup. Restart Codex and use a **local Windows chat**. A conflicting pre-existing server entry produces a readable error and is left intact. The Codex application itself can be running on Windows while the selected chat executes in the cloud. Choose local execution for a Windows folder; a chat whose working directory is `/workspace` is not this local Windows setup.
9. Double-click **Diagnostics.cmd** with both windows/hosts running. It saves a read-only JSON report in `logs`, containing tool discovery, bridge session/request IDs, package version, external/embedded Python, release strings and executable version resources. It does not create a box or retry a mutation. **M1 Metadata.cmd** retains the explicit files 1/2 and attribute 498 probe; the [diagnostic reference](diagnostics.md) explains its scope.

Codex's documented [Streamable HTTP configuration](https://developers.openai.com/codex/mcp/) uses this table, which the connection script supplies automatically:

```toml
[mcp_servers.allplan_m0]
url = "http://127.0.0.1:8888/mcp"
```

If Codex uses a custom configuration location, report that location so the implementation model can configure it; the supplied helper targets the standard user configuration. Do not copy this URL into a cloud chat expecting it to reach your Windows computer. Each machine has its own localhost. No tunnel, shared service or remote deployment is part of this batch.

## Update and restore

Close Allplan and the MCP console before an update. Extract the next package into its own versioned folder and run its Setup. Every real install makes a separate backup of the previous bridge, including stale files; the new installation replaces the owned trees, so obsolete modules do not stay active. Reopen Allplan to clear loaded Python modules.

To revert this installation, close Allplan and the MCP console, then double-click **Restore bridge.cmd** in this package. It uses this package's recorded backup ID, validates the backup, restores both previous trees (or removes them if previously absent) and makes a safety backup of the current bridge. Open Allplan again. For a full previous-version setup, start the previous version's launcher. Restoration does not modify Allplan models or remove test geometry. To undo the Codex connection, restore the config backup named in `logs\connect-result.json`; the model can perform that step in a local Windows chat.

Backups live outside the extracted package. Keep the backups needed for rollback. A missing/corrupt backup is rejected before replacing the current bridge. An interrupted machine shutdown during copying is not an atomic filesystem transaction; the retained backup is the recovery source.

## Readable failures and recovery

| Result | Next action |
| --- | --- |
| `host_absent` | Open a project, start StartPythonHost from Library, keep it running, then repeat a read-only check. |
| `session_unavailable` | Open the intended project/file and restart StartPythonHost; repeat a read-only check. |
| `incompatible_build` | Report the detected release. Model operations target major version 2026; diagnostic reads remain available. Bounded M0–M2 acceptance covers the recorded Allplan 2026-1-7 build. |
| `invalid_payload` | Report the prompt and request ID; the model corrects the request. |
| `execution_unknown` / lost response | Inspect the test area before any write retry. A timeout does not prove that no box was created. Do not automatically repeat the box prompt. |
| MCP cannot connect | Keep Launch Allplan MCP.cmd open, check the endpoint in its console, restart Codex after configuration, run Diagnostics. |
| Port already in use | Close the previous MCP console / old Allplan host and restart. Report persistent errors; do not launch duplicate hosts. |
| Integrity check fails | Extract a fresh package. Do not mix files from different versions. |

The [2026 AllplanVersion API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_AllplanSettings/AllplanVersion/) provides release strings; these alone do not establish a full build/hotfix. The diagnostics also reads version resources from the running process executable on Windows. If the hotfix remains unavailable, include the value visible in Allplan's About / version dialog with your result. Do not infer it from a folder name or a Python version.

## Read diagnostics and missing Library item

[Diagnostic commands](diagnostics.md) cover resource preflight, metadata,
full selections, read-only audit and controlled error/recovery. Main exposes
eight tools; execute_python is development-only and disabled by the launcher.
No accepted M1/M2 batch needs repeating without a relevant change or defect.

If StartPythonHost is missing, return the Library palette to its root, clear
filters and open **Private → PythonHost → StartPythonHost**. Check
`logs/installation.json` for the actual Local/Library/PythonHost destination.
Very old 0.1.1 installations used an obsolete PythonParts/PythonHost location;
Setup backs it up and removes it during upgrade. Do not copy files or choose a
different user folder by guess. The installed StartPythonHost.pyp can also be
dragged from Explorer into the drawing area, per the official Allplan workflow.

The bridge keeps bounded logs under `Local/.allplan-mcp/logs`. Diagnostics remain
read-only; M0 create_box/create_cube are separate mutation tools without
automatic readback or durable write deduplication.
