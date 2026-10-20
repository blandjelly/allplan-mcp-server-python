# Allplan MCP 0.22.0 — evaluation candidate

Runtime source: `4cc0a752960c6f05293891208c4122b4e21f00c7`.
The original [CI 39294288929](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39294288929)
artifact was downloaded and its GitHub SHA-256 verified. **No local rebuild**
was performed. The delivered Windows ZIP contains that clean source.

[Download Windows ZIP](allplan-mcp-0.22.0-windows-evaluation.zip) ·
[ZIP checksum](allplan-mcp-0.22.0-windows-evaluation.zip.sha256) ·
[Owner observation](../../docs/test-results/m4-agent-observation-0.21.1-2026-10-19.md) ·
[Owner 0.21.1 observation](../../docs/test-results/m4-agent-observation-0.21.1-2026-10-19.md)

This candidate addresses the owner's persistent Beam write/recovery block,
Integer checkbox values and full/short layer-name lookup. M4 recovery verifies
project/document identity and reads exact journal targets without a new global
criterion scan. Positive null/deleted wrappers are skipped; genuine unknowns
remain blocked. SDK-bound real numeric readback accepts finite int/float
representation differences, preserving raw evidence. Recovery never retries.

Layer searches retain continuation after finding candidates and disclose
partial coverage. User confirmation binds the displayed ID, short name and
API name; preview and Apply freshly verify them. Integer boolean inputs require
an actual SDK CheckBox control. Enum labels use targeted round trips. There is
no attribute-name allowlist, but dates/vectors and computed-only writes remain
unsupported; attribute edits do not modify Beam geometry.

Validation:

- **480 tests PASS on each Windows/Ubuntu Python 3.12 CI job**, then one
  successful package job. [Source CI evidence](source-ci.json).
- Focused tests include lost-reply recovery, continued Beam edits, later layer
  writes, Polish full-name search and confirmed target identity through MCP HTTP.
  [Focused evidence](focused-verification.json).
- The **exact delivered ZIP** passed payload/checksum, fresh registration,
  frozen sync/import, upgrade from 0.21.1 and restore, with **37 verified bridge
  hashes**. Journal, native trace and bridge log markers were preserved.
  [Verification](package-verification.json) · [log](package-verification.log) ·
  [verification script](verify_package.py) · [artifact hashes](artifact-hashes.json).
- **Native Allplan: not_run for the new behavior.** Existing owner observations
  remain scoped to their tested builds. Start the new trial by recovering
  execution `4388b04e39a14fac811db4f58723d01f` on the original project/document;
  preserve its journal and return raw diagnostics if it remains unresolved.

Install using `Setup.cmd` in the extracted ZIP. This is an evaluation candidate
for a reviewed disposable copy, one active foreground drawing and at most
32 setters. Keep the old package and native journal. Main integration is separate.

Delivered ZIP SHA-256: `7c5dd0147d6daa71f431ab41d18a91cfaf25a3e57a7bcdff20b15beca3feef41`.
