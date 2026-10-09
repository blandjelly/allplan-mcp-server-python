# M3 0.8.0 native apply — rejected before setters

Status **BLOCKED**, not write/Undo acceptance. Capture: 2026-10-09 **23:54
Europe/Warsaw** (filename 21:54 UTC). Owner reports that the tool did not work,
Allplan and server remain running, and no model changes are visible. The batch
has no post-apply audit/health/UI capture; that observation is not a whole-model proof.

All four uploaded files are preserved byte-for-byte in
[the evidence folder](evidence/m3-apply-0.8.0-20261009T215455/evidence-manifest.json).
The manifest records original sizes and SHA-256; files are diagnostic evidence.

## Evidence and cause

- MCP/host package **0.8.0**, clean source
  `d1b406318a24b52792cacc8560745e4a596cd1f3`. All **22 installed bridge hashes**
  match the unchanged delivered ZIP. Installed integrity is verified.
- API release 2026.1, embedded CPython 3.13.13, executable versions
  16.1617.8659.814 / 2026.0.1.0. The previous owner-identified UI build is
  2026-1-7; this message does not independently restate the hotfix.
- All five read-only preview/preflight/revalidation/audit/health steps pass.
  Preview contains two changes/three exclusions, unchanged complete audit five findings.
  Plan and audit fingerprints independently recompute; client pointer and final
  apply report contain identical preview evidence and the exact same apply request.
- Host session `9ca5501a-1a1d-4f42-bc10-965580366f81`;
  plan `7b4b698ae0814989832411ec28f3f985`, hash
  `b5bd3b62091261bcee06543558f8f4e5a9cb5083c0293870294e3f50ce372b93`;
  execution `9232c4149bd9497496b42c92a5dc0aed`.
- Apply request `58643917-d05c-4223-b0bf-b383c2ff565f` returns
  `target_not_writable`: `Target fails IsInMacro; no write requested.`

In 0.8.0 that outward error occurs only while checking all targets **before**
persisting a mutation record or invoking either setter. Neither setter was called
by this rejected request. The original error does not identify which target
returned the flag. The user observation of no visible changes is consistent.

The implementation incorrectly treated IsInMacro=true as a macro-only exclusion.
The [official 2026 reference](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapter/#IsInMacro)
describes an element having a parent object. At least one reviewed native Column
root returns true on this build; the flag does not establish a user macro or
target writability. The exact underlying parent-object semantics remain unproven.

The CLI separately mislabels the explicit pre-write rejection as `unknown`,
because it applies that state to every exception after allocating an execution ID.
`m3-last-execution.json` is a client pointer saved before sending; `apply_pending`
does not prove a host journal entry or mutation. No UI Undo or replay of the
old plan is required. The original logs are retained without rewriting their status.

## Correction and next gate — 0.8.1

IsInMacro is diagnostic evidence. Required bounded parent traversal must still
terminate at the reviewed Column root with exact file/model/type identity;
macro or unknown container ancestors cannot match it. Other eligibility checks,
fresh sources/old values and durable write-ahead execution identity remain.
Successful execution retains resolved-root and native-flag preflight evidence.

The MCP wrapper maps only known pre-setter host rejection codes to structured
`rejected` responses with `native_setters_started=false`; the CLI stores the final
state and sends no recovery/replay for it. Transport/unexpected/journal errors
retain unknown handling because they may follow a setter. No text matching is used.

149 portable tests pass, including the observed Column flag=true case, rejection
of macro/unknown ancestors and real MCP/HTTP explicit rejection without recovery
or replay. Native writes/readback/restart/Undo remain unaccepted. Use the
[0.8.1 write card](../m3-apply-batch.md) on the same unchanged disposable project
copy, with a fresh plan. M3/UAT-05/UAT-06 remain open.
