# 0.21.1 — attribute discovery and edit coverage fixes

[Complete Windows ZIP](allplan-mcp-0.21.1-windows-evaluation.zip) ·
[Owner observation](../../docs/test-results/m4-agent-observation-2026-10-18.md) ·
[PR #16](https://github.com/blandjelly/allplan-mcp-server-python/pull/16).

This candidate fixes equivalent Wall adapter wrappers in attribute listing,
retains raw IDs/values and pagination when metadata fails, and resolves bounded
initial-case spelling differences against actual project metadata. It does not
translate attribute names or enumerate project definitions.

Edit plans require complete criteria and destination fields on matching targets.
Irrelevant unreadable fields on definite nonmatches no longer block the plan.
All peers remain fingerprinted and revalidated; unknown criteria and target
fields still block. Reports expose the individual failing observations.

Generic scalar/explicit enum editing remains available for the existing supported
Wall, Column, Beam and Slab variants. Native geometry/Poziom_Górny, native
material changes, date/opaque codecs and multi-file writes remain outside this
candidate. Readability alone does not establish writability.

## Validation

Runtime source: `41e0cabf1352ffc54b5e35b68adbf3fed498e8d4`.
Candidate [CI 39146255209](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39146255209).
Both Windows and Ubuntu Python 3.12 passed **448 tests each**, followed by one
successful package job. CI artifact 12143373687 was retrieved by the connector,
but transfer to this workspace returned HTTP 403. One permitted local fallback
build used the same clean source; byte equality to the CI archive is not claimed.
[CI record](source-ci.json) · [Artifact hashes](artifact-hashes.json).

The exact delivered ZIP passed checksum/payload verification, fresh bridge
registration, frozen dependency sync/import, upgrade from **0.21.0** and restore.
All **36 bridge hashes** verified; journal, probe trace and bridge log were
preserved. Wheel/sdist payload checks passed too.
[Verification](package-verification.json) · [Script](verify_package.py) ·
[Log](package-verification.log).

ZIP SHA-256: `a522ef686e596f36cf957f5be74c92d246663b0177d8e70e703d27da9ca20c21`.
Focused validation: 96 affected/dependent tests, four model-edit/catalog MCP
HTTP flows, and 19 HTTP launcher tests after correcting the version constant.
The earlier CI run found a version mismatch; it was corrected before this source.

## Native status and installation

The owner identifies the supplied observation as 0.21.0 and confirms U writes
on Column/Wall, F90, highlighting, the unchanged upper level and refused Wall
layer operation. Preserve those scoped observations; no raw payload/build hash
was supplied. New 0.21.1 native behavior is **not_run**.

Close Allplan and MCP, extract the complete ZIP, run Setup with the existing
Local folder, then restart the host and MCP from this package. Use the short
Polish trial for new Wall attribute listing/name lookup and the Wall-to-W1 plan,
then UI/readback/Undo only when the guarded plan offers Apply. Do not repeat
the accepted U/fire/highlight trials. Keep the exact execution ID for read-only
recovery after a lost reply; never retry setters automatically.

The archive contains source documentation before final CI/delivery evidence.
This later delivery record does not rebuild or modify that archive.
