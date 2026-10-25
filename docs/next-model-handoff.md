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

## Next task — 0.36.0 native material crash candidate

Three 0.35.0 Wall material preview requests ended in Allplan `C0000005` read
access violations at address `690`: two requests targeted the original 240 mm
Wall and one targeted a 200 mm Wall. In each trace, M1 scan returned and
`Native.material_observation` started without a return or failure. The actual
root read during each crash is unknown because material observation precedes
the thickness filter. Stale tier ownership in `wall_material.snapshot` is a
candidate, not an established cause. No dump was found for these events: the owner
checked WER and CrashDumps; dumps dated 29.09 and 08.10 are earlier
`C0000374` events and do not diagnose this incident. Do not request another
0.35.0 crash or ask for a missing dump.

After the owner checks required CI for the final 0.36.0 commit, verifies the
exact ZIP and required upgrade/restore procedures, and reloads PythonHost, run
only a preview of the original 240 mm Wall. The first new trace or failure is
the stopping point: preserve its raw response and exact references, then stop.
Do not Apply when the preview is blocked or unknown. Do not repeat the
completed Column Apply/readback, and do not retry the 200 mm Wall/opening
fixture with its unresolved `component_child_owner_mismatch`. This is a
focused crash trial, not full native acceptance.

The candidate change retains both existing native reads and their material
comparison. It keeps the first owners alive through the full read, and
`_detailed_snapshot` also returns its `tier`, so `wall_material.snapshot` uses
one coherent final `native`/`props`/`tier` set. It adds durable
`model_edit.observe` tracing for preview, revalidation and source observations,
with the same root reference metadata on the traced SDK reads, while retaining all
existing guards. The public
request remains `target={"kind":"native_material","tier_index":1}` and the
exact string; field `native.material` is bound in
`resource.native_material_state`. See [API details](m4-editing-api-0.32.0.md)
and [validation status](validation-status.md).

The successful Column record is one completed Apply/readback only. The
supplied evidence does not include a no-op, drift, UI Undo or restoration
result. The trace upload measured
2,096,914 bytes against source `MAX_BYTES = 8 MiB`; preserve it and all journal
history. Do not add automatic trace deletion or cleanup. If a storage block
occurs, retain the snapshot and use the existing reviewed snapshot/confirmation
procedure. The owner-supplied raw archive is `crash log 0.35.0.zip` in the
local/chat attachments; its hash is recorded in the
[validation status](validation-status.md#evidence-for-unresolved-cases).

## Current candidate — 0.36.0

Prepared on `fix/m4-material-lifetime-trace`, based on `develop/m4` commit
`9553c8d10d6cd8f0987b1310d0ee89d3b519dc49`. On Python 3.12.14, 160 distinct
focused tests and 10 HTTP tests passed. A borrowed-owner regression failed
against 0.35.0 source and passed on this candidate. Full CI, exact-ZIP
verification and the bounded owner preview remain separate gates; these
focused results do not establish those outcomes. Earlier M4 scopes remain
partial and are summarized below.

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
