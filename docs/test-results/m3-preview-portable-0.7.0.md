# M3 preview portable validation — 0.7.0

Date **2026-10-09**, Linux external Python **3.12.14**, FastMCP **3.2.4**,
uv **0.12.19**. Baseline accepted M2 commit `bedb264`; working branch
`codex/m3-repair-preview`. **Ready for owner testing, not native acceptance.**
The initial GitHub push was blocked by automatic approval review. The owner
then explicitly approved publishing all prepared work. Exact delivery artifacts
are retained under `evaluation-packages/0.7.0`; the Windows ZIP was not rebuilt.
This record describes the local test run and does not claim remote CI results.

The baseline full suite passed **121 tests** before changes. The updated suite
passes **134 tests**, including 11 new host/public planning checks and two new
real MCP/HTTP/CLI tests. Socket-based checks require this cloud executor's
network permission; an initial sandbox-only run could not create sockets and
was rerun with that permission. It was an executor restriction, not an Allplan
run or a skipped test. Full rerun: all 134 pass.

Validation covers exact two-change preview and three exclusions; raw old/new
values and locators; no native setters; fresh full-scope unchanged revalidation;
status/mark/layer/manual edits, added elements, changed metadata/project/document/
file states; plan hash mismatch, expiration (including expiry during a read),
eviction and restart; selected/stale finding IDs; unloaded/inactive/incomplete
scope; passing-rule no-op; unsupported repair rules/values; overlapping rules;
oversize plan rejection; unavailable API symbols and false write capability.

The real external FastMCP server communicates through Streamable HTTP with the
bridge transport and a fake native `RequestHandler`. `--m3-preview` captures
the two proposals, revalidation, identical five-finding audit and same-session
health, saves JSON/TXT, and rejects public invalid requests without contacting
the host. A lost/error preview stops the owner batch without retry or audit.
Existing M0/M1/M2 and callback-containment tests continue to pass.

Build/delivery checks: frozen sync; wheel/sdist build; deterministic Windows ZIP
with **M3 Preview.cmd**; SHA-256 manifest verification and fresh registration of
both new host modules. The delivered archive's exact hash is in its companion
`.zip.sha256` file. No previously accepted archive was rebuilt or overwritten.

The [contract](../m3-repair-contract.md) defines boundaries and the
[owner card](../m3-preview-batch.md) provides the pending native test. No native
0.7.0 targets/value correspondence, unchanged UI, setter behavior, Undo,
readback, long-term stability, durability or repair acceptance is inferred from
portable mocks. M3.1/M3.2 are partial; M3.3/M3.4 and UAT-05/UAT-06 remain open.
