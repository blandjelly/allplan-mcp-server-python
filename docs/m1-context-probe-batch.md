# M1.1 context probe — package 0.2.0

Status: **ready for owner runtime testing; not accepted**. This is the first
M1 slice, before UAT-02/UAT-03 and profile binding. It changes no model data.

## Upgrade

1. Close Allplan and the previous **Launch Allplan MCP.cmd** window.
2. Extract `allplan-mcp-0.2.0-windows-evaluation.zip` into a new writable folder.
3. Run **Setup.cmd** and select the same Allplan **Local** folder used for 0.1.2.
   Setup backs up the installed bridge. Keep the accepted 0.1.2 archive.
4. Reopen Allplan and a disposable test project. Start **StartPythonHost** from
   the private library and run the new **Launch Allplan MCP.cmd**.
5. Refresh the existing MCP connection in a local Windows Codex chat. The
   existing `allplan_m0` config entry remains valid; no second server is needed.
   Discovery should show six tools, including `get_model_context`.

## Small read-only batch

Use a disposable project with two known drawing-file numbers: one active in
foreground and one passive in background. An empty passive file is valid;
loaded-file inventory must not depend on whether the file contains elements.
For the identity probe, keep at least one existing 3D element in the active file
(an M0 test box or an ordinary column is enough).

1. Ask local Codex: **“Call get_model_context with identity_sample_size=10.
   Report project name, active file, loaded file states, input units, project
   offset, model/view UUIDs and all not_checked fields. Do not modify the model.”**
   Expect the visible project and active/passive file numbers. An observed field
   is an API read, not runtime acceptance. Passive adapters, if returned, retain
   their signed negative file number. UUIDs are distinct fields and may coincide
   for a direct model representation. No component count is claimed.
   Run **Diagnostics.cmd**; retain this first JSON.
2. In the UI unload the passive file. Restart StartPythonHost if necessary, then
   run **Diagnostics.cmd** again. Expect that file to disappear from the loaded
   inventory. It must not become a successful whole-project empty result.
3. Switch to a second disposable project, restart StartPythonHost and run
   **Diagnostics.cmd** again. Expect the project name/key to change. A host
   restart also changes `host_session_id`. No old project is cached by the tool.

Each new diagnostic includes `mcp.get_model_context` and a bounded identity
sample. Logs provide the facts needed to refine the implementation; if an API
read is `not_checked`, retain its reason and send the JSON. Do not edit scripts,
research API names or manually assign attribute IDs.

## Expected limits and reset

- Offset is raw `api_native`; conversion and coordinate application are
  **not_checked**. Compare the raw values with the project settings and report
  the UI unit. Do not change the project offset for this first batch.
- Input units are the Allplan enum codes. Geometry conversion, floor levels,
  durable project GUID, write eligibility and native component counts are not
  verified. These are explicit limits rather than successful empty readings.
- The sample uses raw `SelectAllElements` adapters; hierarchy, view duplicates,
  visibility and passive inclusion require runtime evidence. It is bounded to
  20 returned adapters but the native API may enumerate the entire loaded model.
  Use the small test project for this probe.
- `model_query`, reusable selections and the demo profile are not active yet.

Restore the original loaded-file configuration and return to the first project.
No geometry cleanup is needed for these reads. To revert the bridge, close
Allplan/server, use **Restore bridge.cmd** from 0.2.0, reopen Allplan, and launch
the preserved 0.1.2 server folder. Restoring the bridge does not downgrade the
external server automatically.

## Copyable owner result

```text
M1.1 context probe, package 0.2.0, Allplan UI build:
Project A / active file / passive file:
Initial project and loaded states match UI: PASS / FAIL
Input length/angle UI units:
Project offset UI values and unit:
Identity sample has readable model/view UUIDs: PASS / FAIL / NOT_CHECKED
After unload, passive file absent: PASS / FAIL
Project B name/key updated: PASS / FAIL
Visible model unchanged: PASS / FAIL
Attached diagnostics: initial / unloaded / project B
Unexpected behavior:
```
