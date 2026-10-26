# Current M4 handoff

Development branch: **`develop/m4`**. Start M4 topic branches there and target
PRs to it; integration with main is separate. This candidate is on
`fix/m4-material-assignment`, based on `develop/m4` commit
`c666b3288c6fd22aa0b635498fdfb0d30eb21553`. Read [AGENTS](../AGENTS.md), the
[documentation policy](documentation-policy.md), [testing policy](testing-policy.md)
and [development plan](office-editing-development-plan.pl.md) before implementation.
The required `ci-required` check is prepared; branch protection still needs the
owner to configure it for `develop/m4`.

## Next task — 0.37.0 native material and selected attribute owner

The owner checks the final candidate's required CI and exact ZIP, then performs
the bounded native trial described below.
The candidate extends native material observation/write to Beam and
SkeletonBeam when the live SDK object is a `BeamElement` or
`StructuralBeamElement`, and Slab/MultiSlab represented by `SlabElement` using
the exact `SlabProperties.Material` / `SetMaterial` owner. It does not redirect
between Slab and MultiSlab or substitute `SlabTierProperties` for that root
field. A Slab child is eligible only with its directly observed MultiSlab
parent; parent and child may not both be edited in one plan. Wall remains
single-tier; Column remains supported.

Project attribute edits can now state
`target.property_owner="selected_element"` to bind the exact selected element.
Planning requires complete lineage and child evidence; old requests without an
explicit owner remain blocked for Slab children and MultiSlab aggregates. The
owner change never selects a parent automatically. The source and safety changes
also reduce repeated Wall scalar reads (594 to 454 trace events for the simple
Wall case), skip native destination reads for excluded/nonmatching peers while
retaining the M1 source fingerprint and drift detection, and provide a bounded
10-second material evidence allowance. The M1 scan remains 5 seconds and the
client timeout remains 30 seconds. Existing write guards, journals, replay
protection and trace retention remain in force.

The 0.36.0 trial reported no PythonHost interruption or Allplan crash. The user
reported successful project `Materiał` attribute edits on Wall, Column and Beam,
but not Slab. Native Beam success is disputed: the user reported that it worked,
while the supplied 0.36.0 conversation log records a completed Column
Apply/readback, `native_material_type_unsupported` for SkeletonBeam and
MultiSlab, and a Wall preview timeout at 5 seconds. Treat this discrepancy as
unresolved; do not claim native Beam PASS. Do not repeat the completed Column
native Apply/readback. The unchanged [0.36.0 conversation log](test-results/evidence/conversation-log-0.36.0-2026-10-26.md)
is the source for the tool outcomes.

After the owner verifies required CI for the final 0.37.0 commit, the exact ZIP,
and the required upgrade/restore procedures, run a short native flow only for
the changed routes. Preserve the first blocked/unknown result and exact refs;
never retry a setter after an unknown result. Any write requires fresh readback
and the appropriate UI Undo/restoration check. Do not repeat the accepted
Column scope, request missing dumps, or change unresolved journal history.
Native 0.37.0 acceptance remains pending.

## Current candidate — 0.37.0

The candidate starts from `c666b3288c6fd22aa0b635498fdfb0d30eb21553` on
`fix/m4-material-assignment`. **263 distinct focused checks passed** on Linux,
Python 3.12.14: 243 material/edit/ownership/contracts/identity/property/trace
checks including version consistency, plus 20 HTTP/MCP checks for material,
recovery, Column launcher and component identity. The launcher checks passed
after `uv sync --frozen` replaced stale local editable metadata (0.1.0) with
0.37.0. Diff, local documentation links and the unchanged attachment check
also passed.
Full Windows/Ubuntu CI, `ci-required`, exact-ZIP verification, upgrade/restore
verification and the bounded native trial are pending. Do not infer full CI,
package acceptance or native PASS from focused tests or SDK API availability.

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
