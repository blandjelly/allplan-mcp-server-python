# Current M4 handoff

Development branch: **`develop/m4`**. Start topic branches there and target
PRs to it; integration with main is separate. Read [AGENTS](../AGENTS.md)
and the [documentation policy](documentation-policy.md),
[testing policy](testing-policy.md) and [development plan](office-editing-development-plan.pl.md)
before implementation.

The workflow provides required PR check `ci-required`; selection,
failure/skip handling and unchanged-source reuse have 49 focused policy/gate
checks passing. Branch protection still needs the owner to configure
`ci-required` for develop/m4. See the
[testing policy](testing-policy.md#required-github-check).

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

## Current candidate — 0.36.0 / PR 39

The test-only optimization continues from `ee831a0` on
`fix/m4-material-lifetime-trace`, based on `develop/m4` commit
`9553c8d10d6cd8f0987b1310d0ee89d3b519dc49`. The full
[CI run 40228207181](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/40228207181)
on `ee831a0` passed all 693 tests on Windows and Ubuntu, package production,
and `ci-required`. Windows tests took 2,418.236 s; Ubuntu took 225.682 s.
This run supersedes the earlier timeout failure on `c15ffaa` for that source
revision.

The focused Python 3.12.14 run passed 103 affected tests in 19.564 s across
`test_trace_test_support`, `test_wall_material_edit`,
`test_native_material_columns`, `test_wall_material_http`,
`test_property_probe`, `test_trace_cleanup` and `test_journal_cleanup`.
Fixture selection/cleanup, JSON rejection, real journal persistence and the
real-fsync spy passed. In a local Linux benchmark of the same cases, 6,200
real-trace disk records took 0.720 s; 6,200 in-memory events with zero disk
records took 0.269 s. This is a local result and does not estimate Windows
performance.

The test-only optimization uses fixture-scoped in-memory trace recording for
routine material workflows while retaining explicit durable trace, journal,
storage-failure and real-storage HTTP coverage. It does not change runtime
code, budgets, journals, guards or package version. These new test changes are
not covered by run 40228207181; required CI for the updated candidate remains
pending. See the [test selection policy](testing-policy.md#material-trace-selection).
The exact-ZIP check and bounded native preview also remain pending. After the
owner checks CI and the exact ZIP, run only the original 240 mm Wall preview
described above. No need to repeat the accepted Column Apply/readback or
request the missing crash dump.

Earlier M4 scopes remain partial and are summarized below.

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
