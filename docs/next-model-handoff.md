# Current M4 handoff

Development branch: **`develop/m4`**. Start topic branches there and target
PRs to it; integration with main is separate. Read [AGENTS](../AGENTS.md)
and the [documentation policy](documentation-policy.md),
[testing policy](testing-policy.md) and [development plan](office-editing-development-plan.pl.md)
before implementation.

## Next task — one 0.32.0 Wall material trial

Native acceptance of 0.32.0 is pending. On the retained project copy, follow
the [single-path procedure](m4-single-drawing-0.32.0.pl.md) for the original
**240 mm Wall**, requested material **`Silikat`**. Record the installed
manifest/checksum, Allplan build, exact identities and raw MCP responses.

- If preview is blocked, retain the first reason/stage/error type and all
  diagnostic evidence, then obtain fresh `component_identity` for Wall and
  its exact tier. Record BLOCKED or `fixture_missing`; do not Apply.
- If eligible, perform one reviewed Apply, fresh material/preservation readback,
  one UI Undo and restoration readback. An unknown outcome requires recovery
  with the original execution ID, without retrying setters.
- Do not repeat the **200 mm Wall/opening** material preview or any write.
  Its `component_child_owner_mismatch` is a separate unresolved case;
  bounded read-only identity evidence may support later diagnosis.
- Record the outcome in [validation status](validation-status.md), update this
  next task and the [development backlog](office-editing-development-plan.pl.md).
  Do not repeat already accepted journal, scalar, Enum, W1 or grouped Column
  delete/Undo trials.

## Current version — 0.32.0

0.32.0 permits direct `AttributeContainer_TypeUUID` leaves under a single
Wall tier only after checking container → tier → Wall lineage. Stored
`ReadAll` values are preserved with bounded JSON codecs and rechecked during
revalidation/readback. This does not establish field ownership or authorize
attribute writes. Unsupported/nested children, unsupported values, openings
and other Wall children remain blocked.
[API details](m4-editing-api-0.32.0.md).

Runtime source `75cd26e31ae1e3ee0d6ef86411b55490cd457302` was delivered in
[PR #30](https://github.com/blandjelly/allplan-mcp-server-python/pull/30),
merged into `develop/m4` at `c42adf0377438dcb729df08b0527635301af2e50`.
161 unique focused checks passed; full CI passed 635 tests per Windows/Ubuntu
Python 3.12 job and the package job. One clean exact-source fallback ZIP
passed verification once. Delivery, checksum and provenance are in the
[0.32.0 package record](../evaluation-packages/0.32.0/README.md).
**These results do not establish native Allplan acceptance.**

The fake-adapter regressions do not prove the cause of the earlier native
`wall_material_tier_hierarchy_unsupported`. The material trial is still open;
priorities 1–5 remain partial. Remaining work and unresolved errors have one
backlog in the [development plan](office-editing-development-plan.pl.md).

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
