# 0.18.2 — isolated Wall root adapter correction

Download [the complete Windows ZIP](allplan-mcp-0.18.2-windows-evaluation.zip).
This corrects `wall_sample` stopping with “ambiguous adapter representations”
when M1 resolves axes/tiers to distinct Python wrappers of the same Wall root.
The regression reproduces the original 0.18.1 error; the supplied owner logs do
not include a native trace proving the exact adapter hierarchy in that run.

The probe selects one wrapper only after M1 establishes one foreground drawing,
model UUID, view UUID and consistent root fields. Multiple views, conflicting
fields, unresolved identities and cross-file hierarchy still block before Wall
properties are read. The report adds `sample.adapter_resolution` for diagnosis.
No new native API is called. Columns, host transport and write guards remain
unchanged; no Wall highlighting or material write is added.

Validation of clean source **47ec1ad5ccc494452d2bdcd5c7252f8969facbd5**:

- **312 portable tests PASS**, CPython 3.12.14, 103.714 seconds.
  [Full log](portable-tests.log). Coverage includes duplicate root wrappers,
  conflicting fields/types, multiple views, unresolved hierarchy, retained
  native enumeration owners and a single request through real MCP HTTP.
- Frozen sync, wheel/sdist and Windows ZIP builds PASS. [Build log](build-0.18.2.log).
- Exact ZIP checksum/payload verification, 30 installed bridge hashes, frozen
  sync/import from the extracted ZIP, upgrade from 0.18.1 and restore PASS.
  The journal, native trace and bridge log were preserved. The only changed
  native payload file is `wall_probe.py`.
  [Verification](package-verification.json), [script](verify_package.py),
  [log](package-verification.log).
- [Source CI 39027996719](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39027996719):
  **6/6 PASS**, Windows/Ubuntu × Python 3.11–3.13, including frozen sync,
  full tests, wheel/sdist and ZIP builds. [Recorded results](source-ci-0.18.2.json).

[Delivery manifest and artifact hashes](delivery-0.18.2.json).
Artifacts are frozen from the clean source above. Later documentation/delivery
commits do not rebuild them. All older archives remain unchanged.

**PASS / accepted_on_build 0.18.2** for the observed single-tier Wall property
read on 2026-10-17: **240 mm**, raw material **`Beton`**, owner-confirmed against
UI. M1 found two Walls and intentionally sampled one by model UUID order;
`240 < 240` correctly returned false. Both health replies were healthy in one
session, with no requested setters or reported model change. The 20 cm Wall's
properties, full-Wall filtering/highlighting and material writes remain unverified.
[Observation and original JSON/TXT](../../docs/m4-wall-observation-0.18.2.md).
The original delivery/verification JSON files retain their pre-observation
`not_run` and `ready_for_owner_test` values; they are frozen build records.
The owner also confirmed 0.18.1 host recovery and Columns no-op highlighting; those
[observations and uploads](../../docs/m4-native-observation-0.18.1-2026-10-17.md)
retain their separate scope. Neither observation accepts the full M4/write workflow.

## Retained owner outcome

The completed observation returned **240 mm** and **`Beton`**, matching the UI.
It sampled one single-tier Wall and made no model changes. The owner record and
original reports are in [the retained observation](../../docs/m4-wall-observation-0.18.2.md).
Do not repeat the trial.
