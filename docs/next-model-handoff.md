# Current M4 handoff

## Next task — verify the candidate, then resolve the Column journal entry

After the final source and documentation are marked Ready, CI runs
automatically. The owner monitors required CI, verifies the exact ZIP and
applicable upgrade/restore procedure, installs it, and reloads PythonHost while
keeping the Allplan project open. Do not infer these gates from SDK docs, user
UI observations or focused checks. See the [testing policy](testing-policy.md).

Then use `inspect_journal` to identify the current unresolved Column execution;
the preserved 0.38.0 conversation log does not include its execution ID. Recover
that exact ID read-only, without setter retry. Review each offered target,
meaning, changed section and before/current preservation hash against the
current model. If a hash-bound reviewed reconciliation is offered, submit its
returned request unchanged with its hash and acknowledgement in the same
session. A reconciled record remains unknown about setter causality and
preservation; it is not applied success and does not remove history. Missing
required material/owner evidence or disagreement keeps the recovery lock.

After Column recovery clears the journal guard, run fresh preview-only trials
for the two Beam targets and the MultiSlab. Each is a new family/target scope;
inspect runtime owner/material and plan evidence first. A preview that qualifies
may proceed only through the existing reviewed Apply procedure, with readback
and preservation evidence. Never retry a setter after an unknown result. Do not
repeat the completed Wall writes or prior accepted Column Apply/readback.

The preserved [0.38.0 conversation log](test-results/evidence/0.38.0-2026-10-26/allplan-conversation-log.md)
records the user's observations: both Wall targets read as `TEST` in UI/readback
and their preservation conflicts were reconciled; one Column's UI showed the
requested change, but readback remained unknown because the planned view was
missing; two Beam previews failed on `AttributeError` before any setter; one
MultiSlab had empty material and a ready preview, but Apply was blocked by the
unresolved Column. The log contains no Column execution ID. These observations
do not establish CI, ZIP or full native acceptance. Separately, the owner
reported a project Material attribute value matching native material; the
report gives no attribute ID. Treat this as correlation/reflection evidence,
not equivalent setter behavior.

## Current candidate — 0.39.0

Development base: **`develop/m4`**. Candidate is on
`fix/m4-native-material-readback`, based on `develop/m4` at `fb67fab`.
Runtime/test commit `811a1bde33d8867e9595d35d59a92e4d9bb162ca` is in
[PR #42](https://github.com/blandjelly/allplan-mcp-server-python/pull/42).
Focused checks passed: 188 unit checks across `native_material_columns`,
`native_material_families`, `wall_material_edit`, `native_model_edit`,
`model_edit`, `model_edit_contracts`, `edit_ownership`, `multiview_recovery`,
`repair_execution` and `recovery_control`; 10 MCP/HTTP checks across
`wall_material_http` and `model_edit_recovery_http` (198 distinct total).
Version metadata, `uv.lock`, self editable package and `__version__` agree on
0.39.0. HTTP checks confirmed unknown Column → blocked Slab Apply → reviewed
reconciliation → fresh empty-MultiSlab Apply/readback/replay, with two setters
total; this is fixture evidence. Strict StructuralBeam fake and HTTP checks
passed. Full CI, exact ZIP, upgrade/restore and native acceptance remain
pending with the owner.

0.39.0 reads `StructuralBeamElement.StructuralBeamProperties` and writes through
`SetStructuralBeamProperties`; `GetStructuralBeamProperties()` is an alias.
Before a setter, the exact reviewed view and bound owner remain required. If the
view is missing after a setter, readback/recovery attempts a preservation
snapshot on every current wrapper for that owner. Optional unavailable fields
remain `not_checked`; missing required owner/material or disagreement blocks
recovery. View/preservation changes remain unknown until hash-bound reviewed
reconciliation. This path is read-only and never retries setters. See the
[API note](m4-editing-api-0.32.0.md).

## Earlier cases to retain

- `87a45065d5e14e3a9ac8c54756e273a0` is an earlier Wall execution. The new log
  records Wall recovery/reconciliation but no execution ID; it cannot prove
  that this exact journal record was resolved.
- `4388b04e39a14fac811db4f58723d01f` remains an earlier unresolved multiview
  recovery case. Preserve its journal and use only read-only recovery under
  that same ID; do not retry its setter.
- Broad property discovery remains suspended after the native crash; do not
  resume that probe.
- M0–M3 and earlier M4 PASS results remain limited to their recorded fixtures
  and operations. Do not generalize them to other element families or types.

Preserve exact target binding, owner/material consensus, fresh revalidation,
journals and trace history, replay protection, write/Undo guards, and unknown
results. Never delete unresolved records to free capacity. Read [AGENTS](../AGENTS.md),
the [documentation policy](documentation-policy.md) and the [development
plan](office-editing-development-plan.pl.md) before implementation. The
`ci-required` check is prepared; branch protection still needs owner setup for
`develop/m4`.
