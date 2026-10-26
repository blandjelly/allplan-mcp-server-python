# Current M4 handoff

Development branch: **`develop/m4`**. Start M4 topic branches there and target
PRs to it; integration with main is separate. The prepared 0.38.0 candidate is
on `fix/m4-material-recovery`, based on `develop/m4` SHA
`24a0b342f576f331924a55b6c33e36e8d595d3c3`. Version metadata, lock entry and
server constant agree on 0.38.0.
Read [AGENTS](../AGENTS.md), the
[documentation policy](documentation-policy.md), [testing policy](testing-policy.md)
and [development plan](office-editing-development-plan.pl.md) before implementation.
The required `ci-required` check is prepared; branch protection still needs the
owner to configure it for `develop/m4`.

## Next task — validate 0.38.0 material recovery

The candidate captures the full optional preservation snapshot only on the
reviewed exact wrapper. Other live representations still must prove the same
native material and bound owner. Material observation, consensus and setter
preflight each use a separate 10-second material evidence budget; M1 scanning
remains 5 seconds. Required owner/material disagreement, missing views or
unreadable representations continue to block or leave results unknown.
Preservation drift remains strict during preview, revalidation and ordinary
Apply readback, which stays unknown on drift.

The 0.37.0 owner observation was PASS for the intended value on the 240 mm Wall
without openings: the user and independent probe/UI saw `Beton1`, while its
execution journal remained unknown. The 200 mm Wall with a door/opening stayed
blocked by `scan_limit_exceeded`; no setter ran. Column, Beam and Slab native
material were not tested in 0.37.0. Do not repeat the earlier accepted Column
Apply/readback. See the [preserved conversation log](test-results/evidence/0.37.0-2026-10-26/allplan-conversation-log.md).

Focused checks: **188 distinct passed** — 177 unit checks across 10 affected
modules and 11 MCP/HTTP checks. Version consistency across metadata, lock and
server is 0.38.0. The opening Wall regression covers a new same-view wrapper
without its own optional child graph: baseline consensus returns unknown, while
the candidate applies with one setter and recovery unblocks. This confirms the
fixture path only; native root cause remains unproven. Required Windows/Ubuntu
CI, `ci-required`, exact package and upgrade/restore verification, and native
validation remain pending.

After required CI and exact-package verification, install 0.38.0 and reload
PythonHost as required by the setup procedure; keep the original Allplan
session/project open. Do not assume host code hot-updates in place. Inspect the
current Wall and recovery evidence first. Recover execution
`87a45065d5e14e3a9ac8c54756e273a0` without reconciliation acknowledgement. If
the response offers `recovery.reconciliation`, review each exact target,
`meaning`, `changed_sections`, and before/current preservation hashes against
the current model; inspect UI/geometry when a difference needs that check. Only
then submit the returned `request` unchanged, with its `reconciliation_hash`
and `acknowledgement="reviewed_material_reconciliation"` in the same session.
The bridge re-reads all exact views under the journal lock and accepts only if
the previously offered hash is unchanged. If evidence changes, recover again
without acknowledgement and review the new proposal.

An accepted reconciliation records
`reviewed_material_preservation_conflict`, retains `original_outcome`, stores
`reconciliation_evidence`, the exact `reconciliation_hash` and `acknowledgement`,
and sets `preservation_verified=false`. It is a read-only journal reconciliation: it
does not prove setter causality, report applied success, verify the old
preservation snapshot, or delete history. Missing views/owners, unreadable
material, or disagreement keep the lock. After reconciliation removes the
recovery blocker, make a fresh preview for the Wall with a door/opening; do not
reuse the failed plan or retry its setter. Native root cause remains unproven;
native acceptance is pending. See [validation status](validation-status.md#evidence-for-unresolved-cases).

## Current candidate — 0.38.0

The 0.38.0 candidate is prepared on `fix/m4-material-recovery`. Full
Windows/Ubuntu CI, `ci-required`, exact-package and upgrade/restore verification,
and native validation are pending. Do not infer package acceptance or native
PASS from focused checks or SDK API availability.

## Prior work needed for continuation

M0–M3 are accepted only for their recorded fixture scopes. Prior M4 observations
include bounded journal archival; W1 read/write and no-op reports; one grouped
delete/Undo of three Columns; four scalar family/type pairs; and Wall Enum ID
120. Boolean/CheckBox lacks raw Apply evidence. The 0.36.0 Column native
Apply/readback is one completed scope and must not be repeated. Native validation of Slab/MultiSlab
field ownership and the earlier unresolved execution remain open; see
[validation status](validation-status.md).

Preserve exact target binding, complete owner evidence, fresh revalidation and
readback, journals and trace history, replay protection and all write/Undo
guards. Never retry setters after an unknown result or delete unresolved records
to free capacity.
