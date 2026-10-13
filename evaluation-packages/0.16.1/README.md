# M4 isolated Column probe after the native crash — 0.16.1

Status: **ready_for_owner_test only for one isolated Column read**.
The native cause of the 0.16.0 crash is **unknown**; broad `model_properties`
is blocked before native access. This is not an accepted native property catalog.
[Incident](../../docs/m4-native-crash-0.16.0.md).

Download the complete [Windows ZIP](allplan-mcp-0.16.1-windows-evaluation.zip)
([checksum](allplan-mcp-0.16.1-windows-evaluation.zip.sha256)), install it with
Allplan/MCP closed and follow the [short Polish guide](../../docs/m4-isolated-probe-owner-test.pl.md).
Use **M4 Properties.cmd from this new package once**. It now reads only one Column
in foreground drawing file 101, checks health and stops: no automatic attribute
definitions, enum calls, wall reads, W1 resolution, UI highlight or model writes.
Do not repeat the old 0.16.0 experiment or M3 writing gates.

Return its JSON, **Local/.allplan-mcp/logs/m4-native-probe.jsonl** and **bridge.log**,
plus whether Allplan/host stayed alive and PASS/FAIL/BLOCKED. Do not advance to
the other probe phases or Clear Highlight before reviewing this first result.
Preserve the original project after Undo, logs, IDs and Local repair history.

Clean final runtime source: **e06a605c2ab1f1a70170072a61f2280c82658aed**,
branch **codex/m4-property-discovery**, [draft PR #5](https://github.com/blandjelly/allplan-mcp-server-python/pull/5).
Final local suite: **243 tests PASS**, Linux CPython 3.12.14.
Frozen sync, final wheel/sdist build and exact ZIP install/restore simulation PASS:
132 payload files, 28 installed bridge hashes, journal/diagnostic trace bytes
preserved and previous portable installation fixture restored. The simulation
does not run the Windows setup UI or native Allplan.

## Source-scoped CI and artifacts

The package/launcher compatibility matrix on source **7b239b26342c60067ac7e0d4b790901916f36c40**
passed **6/6** Windows/Ubuntu × Python 3.11–3.13. Final runtime source
**e06a605c2ab1f1a70170072a61f2280c82658aed** receives the standard Windows/Ubuntu
Python 3.12 checks for the subsequent adapter-lifetime patch: **2/2 PASS**.
[Final runtime CI](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38451275058),
[package compatibility CI](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38450384581). These scopes are
distinct; neither is native Allplan evidence. [CI observations](source-ci-0.16.1.json).

- [Delivery manifest](delivery-0.16.1.json), [exact package verification](package-verification.json).
- [Portable tests](portable-tests.log), [build](build.log), [frozen sync](frozen-sync.log).
- [Wheel](allplan_mcp_server-0.16.1-py3-none-any.whl).
- [Walkthrough copy](TEST-ALLPLAN-0.16.1.md) / [plain text](TEST-ALLPLAN-0.16.1.txt).

Native readers write started/returned/failed boundaries with flush/fsync before
new calls. M1.column_scan is one existing service boundary, not a trace of every
internal API. The client persists request_pending before contacting the host.
Adapters and their enumeration owners live only through the UI request, with no
native cache. Tracing cannot guarantee containment of a native process fault.
Enum applicability/ownership/native selection and K1/K2/K3 remain unaccepted.

The ZIP is frozen at its clean source commit. Delivery-only documentation does
not rebuild old artifacts. A roughly 99 MiB sdist was built locally, not committed.
