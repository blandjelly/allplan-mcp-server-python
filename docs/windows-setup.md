# Windows setup — 0.2.1 evaluation

M0.2 / M0.5. This is a local evaluation package. M0 is accepted on the owner’s Allplan 2026-1-7 setup with local Windows Codex; see [the acceptance record](test-results/m0-acceptance-0.1.2.md). The Linux portable checks are separate evidence. The package does not install or include Allplan, Python, or Codex. Initial setup needs internet access for the pinned external-server dependencies.

Version 0.2.1 corrects project-reader diagnostics in the M1.1 read-only probe.
Owner 0.2.0 evidence is partial; the bounded **0.2.1 correction batch PASS** is
recorded [here](test-results/m1-context-runtime-0.2.1.md). Full M1 is in progress.
Follow the [M1 correction batch](m1-context-fix-batch.md). Keep the accepted
0.1.2 archive.

## Upgrade from 0.1.1 after a missing Library item

Version 0.1.1 installed the PYP file into `Local\PythonParts\PythonHost`, which
Allplan does not scan as its private library. Version 0.1.2 corrects this to
`Local\Library\PythonHost`, following the [official 2026 file layout](https://pythonparts.allplan.com/2026/manual/key_components/#file-locations).
Close Allplan, extract 0.1.2 into a new folder and run **Setup.cmd**, selecting the
same actual user `Local` folder. The installer backs up the previous library,
scripts and legacy folder and removes the obsolete location. No manual file
copying or prior uninstall is needed. Restore can recover the previous layout.

Reopen Allplan. In the Library palette return to its root, then open **Private**
(the user library), **PythonHost**, **StartPythonHost**. Clear any library filter
that hides PythonParts. If needed, the installed `StartPythonHost.pyp` can also
be dragged from Explorer into the Allplan drawing area, as documented by Allplan.
If it remains missing, send `logs\installation.json` from the new package; it
contains the exact installed path. Do not choose a different user folder by guess.

## Install through Explorer

1. On the Windows machine running Allplan, install the normal Windows distribution of [Python 3.11 or newer](https://www.python.org/downloads/windows/) if needed. Keep its Tcl/Tk and launcher components. This is the external MCP runtime; Allplan's embedded Python is detected independently. The local automated run used Python 3.12.14.
2. Extract `allplan-mcp-0.2.1-windows-evaluation.zip` into a writable folder, for example `Documents\Allplan MCP\0.2.1`. Extract it completely; do not run scripts from inside the ZIP. Keep the resulting `allplan-mcp-0.2.1` folder intact.
3. Find your actual Allplan user **Local** folder using Allmenu's user-folder information / Windows Explorer. A common location is `Documents\Nemetschek\Allplan\2026\Usr\Local`; redirected Documents and custom paths are supported. Select the existing `Local` folder, not `Prg`, `Std`, or the project folder. The `2026` example is a target path, not evidence of your installed build.
4. Close Allplan. Double-click **Setup.cmd**. It checks the package hashes, creates isolated external environments, installs the locked dependencies and opens a folder chooser for the actual `Local` folder. No administrator rights or manual module copying should be needed. Cancel the chooser to leave the bridge unchanged.
5. Setup replaces `Library\PythonHost` and `PythonPartsScripts\PythonHost` and removes the old `PythonParts\PythonHost` installation after backing it up, copying their full contents, including `sandbox`. The previous contents and absence of either folder are recorded under `Local\.allplan-mcp\backups\<backup-id>`. Other PythonParts are preserved. Setup prints the installed package version and backup ID; `logs\installation.json` records them.
6. Open Allplan and a disposable empty test drawing file. In the **Library** palette, open **Private** (the user library), then **PythonHost** and start **StartPythonHost**. Its palette shows that the Python host is started. Keep the interactor running. An ordinary command may end it; restart from Library when necessary.
7. Double-click **Launch Allplan MCP.cmd** and keep the console open. It starts Streamable HTTP at `http://127.0.0.1:8888/mcp`, with the Allplan bridge at `http://127.0.0.1:5679`. `execute_python` is disabled in the evaluation launcher.
8. Double-click **Connect Codex.cmd** on the same Windows machine. It adds the `allplan_m0` server to the standard user `.codex\config.toml`, preserving existing settings and saving a timestamped backup. Restart Codex and use a **local Windows chat** for [the M0 acceptance batch](m0-acceptance-batch.md). A conflicting pre-existing server entry produces a readable error and is left intact. The Codex application itself can be running on Windows while the selected chat executes in the cloud. Choose local execution for a Windows folder; a chat whose working directory is `/workspace` is not this local Windows test.
9. Double-click **Diagnostics.cmd** with both windows/hosts running. It saves a read-only JSON report in `logs`, containing tool discovery, bridge session/request IDs, package version, external/embedded Python, release strings and executable version resources. It does not create a box or retry a mutation.

Codex's documented [Streamable HTTP configuration](https://developers.openai.com/codex/mcp/) uses this table, which the connection script supplies automatically:

```toml
[mcp_servers.allplan_m0]
url = "http://127.0.0.1:8888/mcp"
```

If Codex uses a custom configuration location, report that location so the implementation model can configure it; the supplied helper targets the standard user configuration. Do not copy this URL into a cloud chat expecting it to reach your Windows computer. Each machine has its own localhost. No tunnel, shared service or remote deployment is part of this batch.

## Update and restore

Close Allplan and the MCP console before an update. Extract the next package into its own versioned folder and run its Setup. Every real install makes a separate backup of the previous bridge, including stale files; the new installation replaces the owned trees, so obsolete modules do not stay active. Reopen Allplan to clear loaded Python modules.

To revert this installation, close Allplan and the MCP console, then double-click **Restore bridge.cmd** in this package. It uses this package's recorded backup ID, validates the backup, restores both previous trees (or removes them if previously absent) and makes a safety backup of the current bridge. Open Allplan again. For a full previous-version setup, start the previous version's launcher. Restoration does not modify Allplan models or remove test geometry. To undo the Codex connection, restore the config backup named in `logs\connect-result.json`; the model can perform that step in a local Windows chat.

Backups live outside the extracted package. Keep them until this batch is accepted. A missing/corrupt backup is rejected before replacing the current bridge. An interrupted machine shutdown during copying is not an atomic filesystem transaction; the retained backup is the recovery source.

## Readable failures and recovery

| Result | Next action |
| --- | --- |
| `host_absent` | Open a project, start StartPythonHost from Library, keep it running, then repeat a read-only check. |
| `session_unavailable` | Open the intended project/file and restart StartPythonHost; repeat a read-only check. |
| `incompatible_build` | Report the detected release. Model operations in this evaluation target major version 2026; diagnostic reads remain available. No hotfix is accepted yet. |
| `invalid_payload` | Report the prompt and request ID; the model corrects the request. |
| `execution_unknown` / lost response | Inspect the test area before any write retry. A timeout does not prove that no box was created. Do not automatically repeat the box prompt. |
| MCP cannot connect | Keep Launch Allplan MCP.cmd open, check the endpoint in its console, restart Codex after configuration, run Diagnostics. |
| Port already in use | Close the previous MCP console / old Allplan host and restart. Report persistent errors; do not launch duplicate hosts. |
| Integrity check fails | Extract a fresh package. Do not mix files from different versions. |

The [2026 AllplanVersion API](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_AllplanSettings/AllplanVersion/) provides release strings; these alone do not establish a full build/hotfix. The diagnostics also reads version resources from the running process executable on Windows. If the hotfix remains unavailable, include the value visible in Allplan's About / version dialog with your result. Do not infer it from a folder name or a Python version.
