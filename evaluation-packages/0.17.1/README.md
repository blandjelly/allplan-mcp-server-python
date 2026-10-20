# 0.17.1 — correct fire resistance classification binding

This package is a historical candidate. Its [retained owner observation](../../docs/test-results/m4-column-layer-observation-0.17.1.md)
records two W1 writes and incomplete highlight behavior. It does not accept the
full workflow or later candidate behavior; do not repeat the trial.

The 0.17.0 owner report was BLOCKED before highlighting or writes: default names
resolved the unrelated `Odporność ogniowa` attribute (1398), absent on all six
Columns. The owner clarified the intended `Klasa odporności ogniowej` field with
F30/F60 values. This package resolves exactly that name or the documented English
`Fire resistance classification`, then checks the native ID/name roundtrip.
It does not fall back to 1398 or hardcode 935. F30/F60 remain nonmatching; only
observed null/empty/explicit undefined values qualify. Genuine ReadAll omissions
and read errors still block Apply. The launcher reports the bound name/ID and
unknown-value counts. Broad property discovery remains quarantined.

Validation for clean source **4287e472661dba9e21e60b9eb0e65ffe05d153df**:

- **270 portable tests PASS**, CPython 3.12.14, including real MCP HTTP paths;
  [full log](portable-tests.log). Six-column regression includes both the correct
  and legacy catalog fields, missing legacy values, F30/F60 nonmatches, exact
  targets, old-only catalogs, custom IDs and unreadable/missing criteria.
- Frozen dependency sync and wheel/sdist builds PASS; [build log](build.log).
- Exact ZIP verification and portable installation/upgrade from 0.17.0/restore
  PASS; all **29 bridge hashes** checked, journal and trace bytes preserved.
  [Verification](package-verification.json), [verification script](verify_package.py).
- [Source CI](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38780900814):
  **6/6 PASS**, Windows/Ubuntu × Python 3.11–3.13, including frozen sync,
  tests and package builds; [recorded results](source-ci-0.17.1.json).

[Delivery manifest and artifact hashes](delivery-0.17.1.json).
The ZIP is frozen from the clean source above. Subsequent delivery commits only
add artifacts/evidence and do not rebuild or change the packaged source.
Historical 0.17.0 archives remain unchanged; its original uploaded logs are in
[the owner evidence directory](../0.17.0/native-acceptance/20261015-owner/).
Portable fakes/CI do not establish native Allplan behavior. The 0.16.0 crash's
cause is still unproven; this is a correction of the demonstrated semantic
binding bug, not a native crash fix or main release.
