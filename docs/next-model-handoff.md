# Current M4 handoff

Development branch: **`develop/m4`**. Start topic branches there and target
PRs to it; integration with main is separate. Read [AGENTS](../AGENTS.md)
and the [documentation policy](documentation-policy.md),
[testing policy](testing-policy.md) and [development plan](office-editing-development-plan.pl.md)
before implementation.

The workflow now provides the required PR check `ci-required`; selection,
failure/skip handling and unchanged-source reuse have 49 focused policy/gate
checks passing. The owner must review this workflow candidate's six-job CI
and package, then configure `ci-required` for develop/m4; branch protection
has not been changed. See the [testing policy](testing-policy.md#required-github-check).

## Next task — bounded 0.34.0 Wall material edge-case trial

After candidate 0.34.0 is packaged, verify the installed manifest/checksum and
Allplan build, reload PythonHost, then use the original **240 mm Wall** for
`Beton` → `Silikat`, capturing raw MCP responses and fresh Wall/tier identities.
This fixture has no known opening edge case; separately use a disposable copied
or independent Wall with an opening and, if available, macro/nested metadata.
Do not retry the earlier **200 mm Wall/opening** fixture: its
`component_child_owner_mismatch` remains unresolved.

The public contract remains standalone single-tier Wall and `tier_index: 1`.
The candidate removes material child type whitelisting and blanket opening
rejection, snapshots bounded auxiliary identities, parent/children and nested
AttributeContainer `ReadAll` values, and retains target/lineage checks, valid
single-tier solid hashing, tier/common/axis/complex evidence, journaling,
revalidation and readback. Auxiliary geometry uses a bounded stream digest when
supported and reports `not_checked` otherwise; geometry alone being unchecked
does not establish complete hidden-child preservation. Multi-tier Walls remain
blocked.

Include a same-material no-op and a controlled drift/conflict case. Apply only
on a qualifying preview and a disposable fixture; for each actual write, capture
fresh material/preservation readback, one UI Undo and restoration readback. An
unknown result requires recovery with the original execution ID, without setter
retry. If a preview is blocked, retain its first reason/stage/error and
diagnostics, then stop that case without Apply. Do not repeat accepted journal,
scalar, Enum, W1 or grouped Column delete/Undo trials.

Candidate 0.33.0's native preview on the original 240 mm Wall was BLOCKED before
writes; [the raw log](test-results/evidence/0.33.0-2026-10-24/wall-native-material-preview-log.md)
records `native_material_preservation_unavailable` because the tier child was
unsupported. Do not treat automated checks or the 0.33.0 implementation as
native acceptance. Record each 0.34.0 native outcome in
[validation status](validation-status.md); remaining work is in the
[development backlog](office-editing-development-plan.pl.md).

## Current candidate — 0.34.0

Topic branch: `fix/m4-material-relaxed-guards`, based on `develop/m4`
`5c688f06192703a6ca05212aa0bdde8b6f4a6713`. The material adapter removes
shape/type-only blockers for auxiliary children and records bounded recursive
ownership, required stored metadata and optional geometry streams. The
public single-tier contract and execution safeguards remain. See the
[API details](m4-editing-api-0.32.0.md).

Focused validation: 131 affected/dependent tests and 3 HTTP tests passed.
Project metadata, editable lock entry and server version agree on 0.34.0.
Full Windows/Ubuntu Python 3.12 CI and package production are performed by
GitHub Actions for the Ready PR; the owner checks those results and verifies
the exact ZIP before the native trial. No 0.34.0 native acceptance or exact-ZIP
verification is claimed by these focused checks.

The 0.33.0 native preview was FAIL/BLOCKED with zero setters: its direct tier
child `WallAxis_TypeUUID` triggered `wall_material_tier_child_unsupported`.
The [log](test-results/evidence/0.33.0-2026-10-24/wall-native-material-preview-log.md)
contains owner/child identities, without an exception message. This confirms
the rejected shape but does not prove the relaxed route will preserve the
native object. Its installed manifest/build is not included in that log.
The prior 0.32.0 report has a different reason spelling and an unproven host
mismatch; retain its limits in
[validation status](validation-status.md#evidence-for-unresolved-cases).
The separate 200 mm opening ownership mismatch remains open. Priorities 1–5
remain partial.

## Prior work needed for continuation

M0–M3 are accepted only for their recorded fixture scopes. Retained M4
observations include bounded journal archival; W1 read/write and no-op reports;
one grouped delete/Undo of three Columns; four scalar family/type pairs; and
Wall Enum ID 120. Boolean/CheckBox has only post-Undo readback evidence,
without raw Apply, and is not a complete accepted cycle. Slab/MultiSlab
ownership and the earlier unresolved execution remain open.

[Validation status](validation-status.md) records these scopes and the raw
evidence needed to avoid repeating accepted work. Old release narratives and
trial instructions are available through Git history; use this handoff for
the next action. API research notes remain reference material for their stated
scope, not current release status.

Preserve exact target binding, fresh revalidation/readback, journal and trace
history, replay protection and all write/Undo guards. Never retry setters
after an unknown result or delete unresolved records to free capacity.
