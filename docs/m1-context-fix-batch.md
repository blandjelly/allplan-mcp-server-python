# M1.1 follow-up — 0.2.1

**Completed: bounded follow-up batch PASS**, recorded 2026-10-07.
[Owner evidence](test-results/m1-context-runtime-0.2.1.md). The steps below are
retained for reproducibility; no repeat is needed for the current owner setup.

This read-only batch verifies the project-reader correction after the 0.2.0
feedback. No profile binding, model editing or developer commands are required.

1. Close Allplan and the old MCP console. Extract **0.2.1** into a new folder,
   run **Setup.cmd**, choose the same Allplan Local folder, reopen Allplan and
   StartPythonHost, then run **Launch Allplan MCP.cmd** from 0.2.1. Existing Codex
   configuration stays valid. Keep older ZIPs for restore.
2. In the first disposable test project keep file 1 in foreground and file 2
   **passive in background**. Run **Diagnostics.cmd** and retain the JSON. Expect
   `project.value.name` to match the project name. A resolved key has
   `key_status=observed`; a missing key retains independent `path_lookup_attempts`
   for investigation. Model contents must remain unchanged.
3. In the drawing-file dialog **fully deactivate/unload file 2**; passive mode
   still counts as loaded. Restart StartPythonHost if needed, run diagnostics
   again. Expect file 2 to be absent from `loaded_drawing_files`.
4. Switch to a second disposable project, restart StartPythonHost and run
   diagnostics a third time. Expect the project name and, when resolved, key to
   differ. Note whether the displayed input units and offset match the report.

Send these three diagnostic JSONs and report whether the project names match
and the visible model remained unchanged. A missing path/key is an implementation
follow-up, not a request for the owner to inspect APIs or edit scripts.

Reset: return to the first project and restore the prior drawing-file states.
For rollback, close Allplan/MCP, run **Restore bridge.cmd** from 0.2.1, then reopen
Allplan and launch the external server from the matching previous package folder.
Bridge restore does not automatically downgrade the external server.
