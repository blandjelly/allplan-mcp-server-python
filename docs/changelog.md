# Changelog

## 0.2.1 — 2026-10-07

Preserve project name/host when project-path lookup fails and retain each
read-only lookup's result. The tested Allplan 2026-1-7 runtime resolves paths
with host/name argument order; the fallback handles this documented-signature
discrepancy without switching projects. The owner follow-up batch passes project
lookup/switch, file unload exclusion and model/view identity reads and confirms
the model is unchanged. 31 portable tests pass.

M1 remains in progress. Geometry unit/offset normalization, levels, durable
references, queries, reusable selections and profile binding remain pending.
[Evidence](test-results/m1-context-runtime-0.2.1.md).

## 0.2.0 — 2026-10-07

Start M1 with typed read-only context/identity probing: current project/document,
foreground and loaded file states, input unit codes, raw project offset and
optional bounded raw-adapter model/view GUID samples. Include context in
diagnostics. 29 portable tests pass. Owner runtime verifies file states and GUIDs
but exposes project lookup failure, corrected in 0.2.1.

## 0.1.2 — 2026-10-07

Correct private-library installation to `Local/Library/PythonHost`, migrate the
earlier library location with backups and preserve restore support. Owner UAT-00
and UAT-01 pass on Allplan 2026-1-7 / local Windows Codex. **M0 closed**.
[Acceptance](test-results/m0-acceptance-0.1.2.md).

## 0.1.1 — 2026-10-07

Deliver recursive integrity-checked bridge installation, rollback/restore,
versioned Windows evaluation packaging and Explorer setup/launch/connect/
diagnostic helpers. Add typed baseline tools, structured errors, per-request
document access, UI dispatch and cancellation/restart handling. Separate embedded
and external runtime diagnostics; disable development Python execution by default.
The private-library target defect is corrected by 0.1.2. Portable installer,
transport and real HTTP MCP checks are included; GitHub Actions results are not
claimed as previously executed evidence.
