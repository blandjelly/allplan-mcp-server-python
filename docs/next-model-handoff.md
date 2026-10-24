# Current M4 handoff

Development branch: **`develop/m4`**. Start topic branches there and target
PRs to it; integration with main is separate. Read [AGENTS](../AGENTS.md)
and the [documentation policy](documentation-policy.md),
[testing policy](testing-policy.md) and [development plan](office-editing-development-plan.pl.md)
before implementation.

## Next task — one bounded 0.33.0 Wall material trial

Candidate 0.33.0 is ready for the bounded native trial. Before preview, verify
the installed manifest/checksum and Allplan build, reload PythonHost, then run one
bounded preview on the original **240 mm Wall** for **`Silikat`**, capturing
raw MCP responses and fresh Wall/tier `component_identity`. The 0.32.0 preview was
BLOCKED before writes; do not infer that the 0.33.0 root-container support
addresses its reported native material-preservation cause. Linked container
and tier UUIDs were supplied, but their actual lineage is unknown.

- If blocked, preserve the first reason/stage/error type and diagnostics,
  record fresh identities, and stop without Apply.
- If eligible, perform one reviewed Apply, fresh material/preservation
  readback, one UI Undo and restoration readback. An unknown outcome requires
  recovery with the original execution ID, without retrying setters.
- Do not repeat the **200 mm Wall/opening** material preview or any write.
  Its `component_child_owner_mismatch` remains separate. Do not repeat already
  accepted journal, scalar, Enum, W1 or grouped Column delete/Undo trials.
- Record the native outcome in
  [validation status](validation-status.md); remaining work is in the
  [development backlog](office-editing-development-plan.pl.md).

## Current candidate — 0.33.0

Candidate 0.33.0 extends guarded Wall material preservation to direct root
`AttributeContainer_TypeUUID` leaves as well as the existing tier leaves. It
revalidates the complete parent lineage and `ReadAll` snapshots and records
`root_attribute_containers`; unsupported root/tier children report owner and
child identities. This does not establish field ownership or authorize
attribute writes. 118 focused checks and one additional HTTP check passed;
[full CI](../evaluation-packages/0.33.0/source-ci.json) passed 642 tests on each
Windows/Ubuntu Python 3.12 job and the package job. One clean exact-source
fallback build was used because CI artifact download returned HTTP 403;
[exact ZIP verification](../evaluation-packages/0.33.0/package-verification.json)
passed once, including upgrade/restore and journal preservation.

Source `5de0c318f10facd17eb220d5ca7de7bc3d394130`, [PR #33](https://github.com/blandjelly/allplan-mcp-server-python/pull/33).
[Download ZIP](../evaluation-packages/0.33.0/allplan-mcp-0.33.0-windows-evaluation.zip)
and [checksum](../evaluation-packages/0.33.0/allplan-mcp-0.33.0-windows-evaluation.zip.sha256).
Native Allplan acceptance remains pending.
[API details](m4-editing-api-0.32.0.md).

The 0.32.0 native trial on drawing 101, original 240 mm Wall
`Ściana, prosta`, material `Beton`, was BLOCKED before writes. The reported
`wall.native_material` preservation failure cites `wall_tier_child_unsupported`
at `material_tier_children`,
`ValueError`, with no evidence. That exact reason is absent from both current
source and the retained 0.32.0 ZIP, which use
`wall_material_tier_child_unsupported`; a live/installed host mismatch is
possible but unproven. Supplied tier UUID
`4db19151-9090-4b1c-bd50-b6fba6873aff` and container UUID
`abecfaf0-ad01-45e1-91df-4b32ed9960ae` have unverified lineage. See
[validation status](validation-status.md#evidence-for-unresolved-cases).
This observation does not identify the native preservation cause. Priorities
1–5 remain partial.

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
