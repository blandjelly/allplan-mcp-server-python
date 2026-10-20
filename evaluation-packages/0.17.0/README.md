# 0.17.0 — Column fire resistance → highlight → W1

Candidate for a new Allplan 2026-1-7 observation. **Native acceptance: not_run.**
The owner explicitly accepts highlighting in place of native selection.

This package and its planned owner trial are historical. The later 0.17.1
observation found that the initial field binding was incorrect; see the retained
[validation record](../../docs/validation-status.md). Do not repeat this trial.

This candidate builds direct criterion-based plans, resolves exact project names,
highlights only changing targets and shares the M3 executor/journal. ReadAll
omission and unreadable values remain unknown and block writes. Existing W1 is
required, one foreground drawing, at most 32 Column layer changes. No broad
definition/enum calls or native UI-selection claim. Native container lifetimes
are preserved through reads/setters/readback; this is not proof of the 0.16.0
crash's root cause. The old broad route remains quarantined.

The uploaded [0.16.1 observation](inspection-0.16.1.json) supports one successful
Column read and healthy same-session replies, not acceptance of this workflow.
Local full portable suite: **261 tests PASS**. [Source CI](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38531667116): **6/6 PASS**
(Windows/Ubuntu × Python 3.11–3.13; frozen sync, tests, wheel/sdist and Windows package build).
Source/build/package/CI evidence is recorded in [delivery-0.17.0.json](delivery-0.17.0.json).
The downloadable artifacts are frozen from clean source commit
`2e7967218f51bdea14fc36b566a8d588799f47f2`; the following delivery commit adds evidence only. Source distributions omit historical
evaluation archives; runtime dependencies are unchanged.
Historical packages and native acceptance remain unchanged. No main merge/release.
