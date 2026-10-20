# Current M4 handoff

Current development branch: **`develop/m4`**. Start M4 topic branches there
and target pull requests to `develop/m4`. Main remains separate. Read
[AGENTS.md](../AGENTS.md) and the [testing policy](testing-policy.md) before
implementation. The policy is the source of truth for automated checks and
package builds.

## Current candidate: 0.23.0

The owner confirms the latest reported Allplan results: two queried Slab
attributes, `Priorytet` on two results, and ordered `MCP_QA_MARK` values on six
Columns. The [scoped observation](test-results/m4-agent-observation-2026-10-20.md)
retains the supplied log. Earlier replies and the exact installed manifest are
absent, so do not claim an exact artifact/build for those operations. Slab and
MultiSlab equal bounds do not establish common ownership or two distinct
physical targets. Resolve model/view identity and ownership before another
write to those results.

The owner also encountered a full journal and cleared it manually. The supplied
log omits the error and the measured state; do not infer whether the cause was
the 1 MiB active diagnostic trace, 128 active execution records, or the 1 MiB
per-record limit. Candidate 0.23.0 adds preview and confirmed archival for the
trace or resolved execution records. Unknown/running, corrupt, and oversized
records remain protected and blocking. Cleanup does not access the model or
retry a setter. Native acceptance of this maintenance path is pending the
[short 0.23.0 trial](m4-journal-cleanup-0.23.0.pl.md).

Source `8c71de958c47ab4cb418a62fbd2d55ce76cbc4db` passed CI 39336895867:
505 tests per Windows/Ubuntu Python 3.12 job, then one package job. The original
CI ZIP was verified and passed checksum/payload, registration, frozen sync and
import, upgrade from 0.22.1, and restore. The exact package check confirmed 38
bridge hashes and preserved journal, trace/log, and archive markers. Focused
checks cover 140 affected/dependent cases, including maintenance tests through
native fakes and MCP HTTP. The delivery commit adds docs/artifacts only.
[0.23.0 package evidence](../evaluation-packages/0.23.0/README.md).

## Next work

1. Complete only the pending native 0.23.0 journal-maintenance trial; preserve
   existing journal state and follow its explicit snapshot/confirmation steps.
2. Resolve Slab/MultiSlab target identity read-only before planning another
   write to those results.
3. Follow the [development plan](office-editing-development-plan.pl.md) for
   remaining single-drawing gaps: layer W1 ownership/readback, native selection,
   native material, remaining families/types, then multi-file and whole-project
   work. Do not repeat accepted Column/Slab attribute outcomes or historical
   query/highlight observations.

M4 remains partially accepted. The latest results do not establish native
selection, native material updates, all six families, multi-file execution, or
whole-project access. Preserve target binding, write revalidation, journaling,
unknown-result blocking, replay and Undo safeguards.

For earlier bounded native outcomes and historical evidence, use
[validation status](validation-status.md) and the retained owner observations in
`test-results/`. Do not use superseded owner-test instructions or commands.
