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

## Next task — 0.35.0 native material trial on Wall and Column

After the owner checks required CI for the final PR commit, verifies its exact
0.35.0 ZIP and required upgrade/restore procedures, and reloads PythonHost,
use the original 240 mm Wall and the Column at X=0, Y=0. Capture raw preview,
Apply, readback and recovery responses with fresh exact root identities. Test a
same-material no-op and controlled revalidation drift. Apply only after a
qualifying preview; for every actual write, capture the requested native
material readback, one UI Undo, and restoration readback. If a result is
unknown, recover with its original execution ID without retrying setters. Stop
any blocked case after retaining its first stage/reason/diagnostic.

The owner reports that 0.34.0 blocked the Wall at tier geometry; no raw report
is available. The Column reported `old_value_unknown` because 0.34.0 used a
Wall-only material adapter. These are owner reports, not verified native
evidence. Do not repeat them as accepted observations. For a separate generic
attribute edit, run target-scoped `element_attributes` searches for `material`
and `materiał`, then inspect the returned exact name, ID, type and name/ID
roundtrip. Use that path only if the intended attribute is found. Do not
hard-code ID 508, use ID 1371 (`Materiał łatwopalny`) as Material, or infer
that a Material attribute changes native material.

Candidate 0.35.0 uses request
`target={"kind":"native_material","tier_index":1}` and the exact string;
the report field is `native.material`, with state in
`resource.native_material_state`. Standalone Walls require one tier; Columns
use their native properties. Unavailable geometry, formatting, axis
representations, metadata or auxiliary hierarchy are diagnostic
`not_checked` evidence rather than preview blockers. Available evidence remains
bound into fingerprints and revalidation. Exact root/type, readable material,
setter availability, active drawing and existing journal/write guards remain
required. Post-write drift remains unknown; recovery never retries a setter.

Do not retry the earlier 200 mm Wall/opening fixture: its
`component_child_owner_mismatch` remains unresolved. Do not repeat accepted
journal, scalar, Enum, W1 or grouped Column delete/Undo trials. Record native
results in [validation status](validation-status.md); remaining work is in the
[development backlog](office-editing-development-plan.pl.md).

## Current candidate — 0.35.0

Prepared on `fix/m4-material-unblock`, based on `develop/m4` commit
`6a6798cc865ce617d4c768964df297164e787293`, for a PR into `develop/m4`.
153 distinct affected/dependent tests and 4 MCP HTTP tests passed on Python
3.12. Project metadata, editable lock entry and server version agree on
0.35.0. Full CI and package production run in GitHub Actions; the owner
supervises them and verifies the exact ZIP. Native acceptance remains pending.
See the
[API details](m4-editing-api-0.32.0.md).

0.34.0 remains the last packaged candidate. Its native Wall geometry block and
Wall-only Column limitation are recorded above as owner reports without raw
responses; the 0.33.0 raw preview remains historical evidence only. The
separate 200 mm opening ownership mismatch remains unresolved. Optional
evidence from the chosen exact view is fingerprinted; other views must agree
on required material/owner rather than view-specific diagnostics. Completed
Wall component observations survive a later optional-read failure. Prior M4 scopes
remain partial and are summarized below.

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
