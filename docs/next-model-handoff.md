# Current M4 handoff

## Next task — diagnose Beam discovery and Slab material persistence

Continue on **develop/m4**; main integration is separate. Priorities 1–5 and
their closure evidence are in the [development plan](office-editing-development-plan.pl.md).
First inspect current journal state read-only and retain exact execution IDs
for anything still unresolved. The owner reports reconciliation of the recent
Wall/Column/Slab operations, but the supplied log has no IDs or journal export;
do not assume that every historical record is cleared. Never retry a setter
to resolve an unknown result.

On the next Windows session, capture one bounded, read-only comparison for
the two existing SkeletonBeams and the MultiSlab/Slab: exact file/model/view,
lineage, query coverage/conflicts, runtime native class and property owner,
native Material and the resolved material attribute ID/name/type/value.
Explain why native-material queries returned zero Beams while the attribute
route subsequently found two SkeletonBeams. For Slab, establish which owner
retained the blank native value after the attempted write. Inspect existing
plans/journals/traces before proposing a runtime change. Broad property
discovery remains suspended; this diagnostic step issues no setters. A later
changed native route needs the usual fresh preview, reviewed Apply, readback
and preservation evidence on its exact owner.

Do not repeat the completed Wall, opening-Wall or Column material writes,
or the reported successful material-attribute writes merely to recreate
evidence. Preserve the owner's PASS for the requested values separately from
unverified preservation and Undo. Attribute success cannot replace a failed
native-material result. SDK methods and UI material controls exist for Beam
and Slab; they do not prove persistence on the tested build. See the
[material/API comparison](m4-editing-api-0.32.0.md#native-material-material-attribute-and-surface).

Scalability analysis (2026-10-27) is in the
[implementation plan, S0–S5](implementation-plan.md#analiza-skalowania-developm4-i-ergonomii-mcp).
The 200-result bound is per page; repeated scans and independent scan/cache
budgets limit larger reads. More than 32 changes should use a reviewed durable
manifest and sequential batches, initially in one drawing. Start that work
with profiling and MCP ergonomics; larger writes depend on the relevant native
gates above. This is documentation only, with diff/link checks and no runtime
tests, builds or new native acceptance; the current limits are unchanged.

Native selection research for priority 5 is in the
[API analysis](m4-native-selection-api.md). The inspected public 2026 API
documents interactive pick, but no complete arbitrary replace/clear/current-state
readback contract was found. Next selection step: resolve that contract for the
installed SDK and the scope/lifecycle of `GetPreSelectedElements` with the bounded
experiment in the note. Cursor identification and consumed pick results are not
global selection readback. `select` remains unsupported; interactive pick would
be a separate feature. This is documentation only, with no new native acceptance;
the Beam/Slab diagnostic task above and accepted delete scope remain unchanged.

## Latest tested version — 0.39.0

[PR #42](https://github.com/blandjelly/allplan-mcp-server-python/pull/42) is merged
into develop/m4 at `1a461f4cd3686674b286855bea7a601e8268239a`.
Runtime/test source: `811a1bde33d8867e9595d35d59a92e4d9bb162ca`.
Recorded focused validation remains **188 unit + 10 MCP/HTTP checks PASS**;
metadata, lock entry and server version agree on 0.39.0. These are fixture
checks, including strict StructuralBeam accessors and read-only reconciliation.
This documentation update runs no product tests or builds. Full CI and exact
ZIP/upgrade/restore evidence are not supplied by the new owner log and are
not inferred from the merge or the native test.

**Owner report, 2026-10-26:** PASS for native material on the Wall without
openings, Wall with door/window, and Column. The
[owner-supplied conversation log](test-results/evidence/0.39.0-2026-10-26/allplan-conversation-log.md)
is published unchanged with the owner's explicit consent. It reports the
requested values after recovery; preservation remains unverified because
hierarchy/components changed. Beam native material did not succeed: queries
returned zero Beam/SkeletonBeam
matches with two representation conflicts. Slab native readback remained
blank after two reported attempts. Material-attribute success was
reported on two SkeletonBeams and both MultiSlab/Slab representations of one
assembly. The log contains no raw requests, IDs, preservation hashes or Undo
readback. Allplan reports 2026.1 and bridge integrity; exact hotfix, installed
manifest and runtime compatibility were not established. Details and evidence
limits are in [validation status](validation-status.md#latest-owner-observations).

## Unresolved context to retain

- `87a45065d5e14e3a9ac8c54756e273a0` is an earlier Wall execution;
  `4388b04e39a14fac811db4f58723d01f` is an earlier multiview recovery case.
  The new log reports reconciliations without IDs and cannot establish that
  either exact historical record is resolved. Inspect/recover read-only under
  its original ID if it remains outstanding.
- Wall/Column intended-value PASS does not turn a reconciled unknown result
  into ordinary applied success or verify preservation. Keep original outcomes
  and changed sections; investigate remaining preservation gaps without
  repeating accepted writes.
- Earlier broad-property and native preview crashes remain of unproven cause;
  do not resume broad discovery or repeat historical crash trials.

Preserve target/owner binding, consensus, fresh revalidation, journals/traces,
replay protection, write/Undo guards and unknown results. Never remove records
to free a recovery lock. Read [AGENTS](../AGENTS.md), the
[documentation policy](documentation-policy.md) and [testing policy](testing-policy.md).
The `ci-required` check is prepared; required-check configuration for
develop/m4 still needs confirmation.

