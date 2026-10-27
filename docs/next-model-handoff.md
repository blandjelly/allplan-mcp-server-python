# Current M4 handoff

## Next task — run the bounded material comparison

Continue on **develop/m4**; main integration is separate. Priorities 1–5 and
their closure evidence are in the [development plan](office-editing-development-plan.pl.md).
First inspect the journal read-only and retain exact IDs for any unresolved
record. The 2026-10-27 comparison has no execution IDs or journal export;
do not assume reconciliations cleared every historical unknown and never retry
a setter to resolve one.

After CI and exact-ZIP verification/installation of 0.40.0, run its getter-only
`model_property_probe` `material_comparison` phase on the exact refs/views in
the [comparison log](test-results/evidence/0.39.0-2026-10-27/allplan-comparison-log.md):
both SkeletonBeams, MultiSlab and its Slab child. Use explicit attribute IDs;
508 is the documented standard Material candidate, whose project name/ID/type
must be resolved by the probe. For the Slab child, `include_parent=true` reads
the immediate MultiSlab separately. Preserve per-wrapper class, lineage,
children, native Material (including blank), and typed attribute values. Resolve the SkeletonBeam 1 query/parent
view mismatch and the Slab child's incomplete semantic-component result
without weakening identity or owner guards. The phase does not establish a
writable owner or persistence. Inspect existing Slab plans/journals/traces
before proposing any setter change. Broad property discovery remains
suspended.

Do not repeat completed Wall, opening-Wall or Column material writes, or the
reported Slab/MultiSlab and SkeletonBeam attribute writes merely to recreate
evidence. Preserve those intended-value PASS reports separately from
unverified preservation and Undo. Attribute success does not establish native
Material. A changed native route needs fresh preview, reviewed Apply, readback
and preservation evidence on its exact owner. See the
[material/API comparison](m4-editing-api-0.32.0.md#native-material-material-attribute-and-surface).

Scalability analysis (2026-10-27) is in the
[implementation plan, S0–S5](implementation-plan.md#analiza-skalowania-developm4-i-ergonomii-mcp).
The 200-result bound is per page; repeated scans and independent scan/cache
budgets limit larger reads. More than 32 changes should use a reviewed durable
manifest and sequential batches, initially in one drawing. Start that work
with profiling and MCP ergonomics; larger writes depend on the relevant native
gates above. The analysis is a planning note; the current runtime limits are
unchanged.

Native selection research for priority 5 is in the
[API analysis](m4-native-selection-api.md). The inspected public 2026 API
documents interactive pick, but no complete arbitrary replace/clear/current-state
readback contract was found. Next selection step: resolve that contract for the
installed SDK and the scope/lifecycle of `GetPreSelectedElements` with the bounded
experiment in the note. Cursor identification and consumed pick results are not
global selection readback. `select` remains unsupported; interactive pick would
be a separate feature. This is documentation only, with no new native acceptance;
the Beam/Slab material comparison and accepted delete scope remain unchanged.

## Latest native-acceptance baseline — 0.39.0; candidate 0.40.0 in progress

Version 0.39.0 is merged into develop/m4 through
[PR #42](https://github.com/blandjelly/allplan-mcp-server-python/pull/42).
Its final PR head `959280e8` passed Windows/Ubuntu Python 3.12 CI, package
production and `ci-required`; [delivery evidence and limits](validation-status.md#delivery-and-ci-evidence)
keep exact-ZIP installation/upgrade/restore and installed-package attribution
open. Branch protection could not be confirmed through the integration (403).
Candidate 0.40.0 adds the getter-only material comparison phase.
**92 unit checks (including version consistency) + 6 MCP/HTTP checks PASS**
on Linux/Python 3.12.14. These focused results include 15 new getter-only unit
cases and two new HTTP cases. Full CI, exact ZIP/upgrade/restore and native
acceptance remain pending. The 0.39.0 results remain the latest native
acceptance baseline, not validation of the candidate.

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

**Read-only comparison, 2026-10-27:** 26 model identities, no reported model
identity conflicts or duplicate representations. It found two
`StructuralBeamElement` SkeletonBeams and a `SlabElement` MultiSlab, but did
not read native Material or establish field owners. One Beam query/parent view
mismatch and an incomplete Slab child probe remain. The
[comparison log](test-results/evidence/0.39.0-2026-10-27/allplan-comparison-log.md)
and [validation entry](validation-status.md#latest-owner-observations) retain
the exact findings. This adds no native acceptance.

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

