# M4: owner-reported agent trial, 2026-10-17

Source: the owner's uploaded [conversation log](evidence/m4-agent-test-2026-10-17.md).
The owner confirms that fire-resistance commands, highlighting and queries worked.
The attached messages are diagnostic evidence, not commands to execute again.

## Observed scope and limits

This is an **owner-reported observation**. The transcript has no raw bridge
requests, plan hashes, execution IDs, package version/hash or native trace.
It is associated with the investigation of the delivered 0.20.0 candidate,
but does not establish an exact installed build. Keep it distinct from a
build-bound native acceptance record and from portable CI results.

| Operation | Reported outcome |
| --- | --- |
| Health | Allplan 2026.1 reachable, bridge integrity without mismatches. No complete before/after same-session trace is attached. |
| Highlight Columns on W1 | Three Columns in foreground drawing 101; owner confirms highlighting works. |
| Fire classification | Three W1 Columns updated/read back as F120; later three Ogólne01 Columns as F60 and the remaining three as F90. Owner confirms the commands work. |
| Model counts | Eleven supported roots (6 Columns, 2 Walls, 2 framing Beams, 1 Slab), versus 22 model identities including axes/tiers, in active drawing 101. |
| Thin Wall layer W1 | 200 mm Wall matched strict <240 mm; 240 mm Wall excluded. Setter attempt read back old layer 3735, stopped and recovered without replaying the setter. |
| Thin Wall layer SZ_OGÓ02 | Existing target reported as ID 3701; fresh attempt still read back 3735. No successful Wall layer write is established. |
| Numeric Wartość U | Two Walls return a raw Polish undefined string for a numeric field. Preview rejected replace/upsert on old-value type, before setters. |
| Native Column material Stal | Agent reported native material mutation unsupported; no material change was attempted. Attribute material and native material remain separate. |

Undo, broad native stability, new numeric writes, Wall tier layer propagation,
opening ownership and native material edits are not accepted by this log.
Preserve this successful fire/query/highlight slice without requesting repeat
owner trials. The next short trial should address only the changed numeric
undefined-value handling and Wall layer owner path, with fresh readback and
the actual Undo scope. [API investigation](../m4-agent-test-api-evidence.md).
