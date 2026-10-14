# 0.17.0 — Column fire resistance → highlight → W1

Candidate for a new Allplan 2026-1-7 observation. **Native acceptance: not_run.**
The owner explicitly accepts highlighting in place of native selection.

Download the complete `allplan-mcp-0.17.0-windows-evaluation.zip` from this directory,
extract it and follow [the short Polish walkthrough](../../docs/m4-column-layer-0.17.0.pl.md).
Run **M4 Columns to W1.cmd** for the new workflow and **M4 Columns Recover.cmd**
for saved-ID read-only recovery. The older **M4 Properties.cmd** still runs only
the isolated raw-attribute sample; it is not the new workflow.

This candidate builds direct criterion-based plans, resolves exact project names,
highlights only changing targets and shares the M3 executor/journal. ReadAll
omission and unreadable values remain unknown and block writes. Existing W1 is
required, one foreground drawing, at most 32 Column layer changes. No broad
definition/enum calls or native UI-selection claim. Native container lifetimes
are preserved through reads/setters/readback; this is not proof of the 0.16.0
crash's root cause. The old broad route remains quarantined.

The uploaded [0.16.1 observation](inspection-0.16.1.json) supports one successful
Column read and healthy same-session replies, not acceptance of this workflow.
Local full portable suite: **261 tests PASS**. Source/build/package/CI evidence
is recorded in `delivery-0.17.0.json`. Source distributions omit historical
evaluation archives; runtime dependencies are unchanged.
Historical packages and native acceptance remain unchanged. No main merge/release.
