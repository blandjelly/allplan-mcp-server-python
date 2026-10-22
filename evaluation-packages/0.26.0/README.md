# Allplan MCP 0.26.0 — drawing identity and guarded edit diagnostics

Candidate source: `48e64b1a06bef005c26a143860d9257038cccde3`, PR #24 targeting
`develop/m4`, merged as `40f71b737616b9dde4b3f6804b774c0e5f76ac40`.

[Windows ZIP](allplan-mcp-0.26.0-windows-evaluation.zip) ·
[Checksum](allplan-mcp-0.26.0-windows-evaluation.zip.sha256).

**CI: PASS.** Run [39822585188](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39822585188)
passed the full Windows and Ubuntu Python 3.12 jobs, with **580 tests on each**,
and the package job. The original CI artifact (ID 12445232990, digest
`4e2617cf34cf2269663942ac193a526eac3e0fcb2743e0da78712333ec4bfbfd`) could not
be transferred because the execution proxy returned CONNECT 403. Under the
testing policy's single local-fallback allowance, the wheel, sdist and ZIP here
were built once from clean detached worktree source
`48e64b1a06bef005c26a143860d9257038cccde3` with `source_modified=false`.

The delivered ZIP is that local fallback build, **not the original CI ZIP**.
The exact delivered ZIP passed verification on the first run. It contains 180
payload files; checksum and payload integrity, exact registration, frozen sync
and import, `drawing_identity` schema validation, upgrade from 0.25.0 and
restore all passed. All 42 bridge hashes matched, and journal/trace/bridge-log
plus archived execution/trace markers were preserved. Native Allplan was not
run.

**Focused checks: PASS.** The affected/dependent iteration runs covered 166
unique tests, including 154 in the combined run, two additional delete-preview
diagnostic tests, and ten `drawing_identity` inventory tests (eight unit, two
HTTP). The full local suite was not run; full CI passed.

## Candidate scope

- `model_property_probe phase=drawing_identity` provides a paged, read-only
  inventory for one foreground drawing: exact `(model_uuid, view_uuid)` pair,
  bounded lineage and represented native type for API-enumerated adapters.
  Each page is a new scan; source fingerprints are advisory membership/type/state
  evidence, not an atomic hierarchy snapshot. Screen visibility remains
  `not_checked`, and the inventory does not establish property ownership.
- Wall layer resolution and reviewed W1 plan/apply accept the full legal layer
  ID range 0–65535, including ID 0. Focused tests cover planning/applying from
  current ID 0; the native W1 Undo observation remains missing. This does not
  establish that ID 0 caused the historical `repair_conflict`, whose raw trace
  is unavailable.
- Blocked delete/material criteria expose diagnostic reason, stage and error
  type. This improves diagnosis only. It does not relax ownership, identity,
  revalidation, journaling, recovery or readback safeguards, and does not enable
  the native material setter.

The [short native trial](../../docs/m4-single-drawing-0.26.0.pl.md) is limited to
paged identity inventory, a read-only layer-0 observation, the missing W1
no-op/Undo, and one fresh read-only diagnostic preview for an exact previously
blocked target. The successful 0.25.0 subtree deletion, identity observations
and 200 mm Wall W1 readback are retained in the
[owner observation](../../docs/test-results/m4-owner-observation-0.25.0-2026-10-22.md)
and must not be repeated.

## Acceptance boundary

Native acceptance for 0.26.0 was not run. Priority 1's bounded journal-cleanup
PASS remains accepted; priority 2's inventory does not establish field
ownership; priority 3's layer-0 plan/apply fix still lacks native Undo; priority
4's native selection remains unsupported, material remains blocked, and the
0.25.0 deletion PASS does not establish broader coverage or Undo; priority 5
adds matrix detail but no date/vector codecs. Priorities 1–5, the single-drawing
gate, native material updates, full typed-deletion coverage/Undo, all six
families, and multi-file/project work remain open.
`AttributeDate` exists as an SDK payload for `SetAttributes`, but the current
adapter still lacks an accepted `ElementsAttributeService.ChangeAttribute`
payload and exact fresh-readback codec for date, vector and other unsupported
values. SDK property representations and diagnostics do not substitute for
those contracts or for native evidence.

## Local fallback build provenance

The proxy denial was followed by one local fallback build from the clean source
commit using CPython 3.12.14, `uv sync --frozen`, `uv build`, and
`utils/build_windows_package.py`, with `source_modified=false`. The exact ZIP
verification passed. See [build log](build.log), [CI record](source-ci.json),
[focused checks](focused-verification.json), [artifact hashes](artifact-hashes.json),
[verification summary](package-verification.json), and
[verification log](package-verification.log). Delivered ZIP SHA-256:
`4c0dd3ed9c9c038320fe08032a26ef61d8be7a57ed4169d5cdd3bc5952b292a9`.
