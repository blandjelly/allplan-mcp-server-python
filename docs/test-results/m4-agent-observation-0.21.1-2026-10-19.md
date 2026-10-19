# Owner trial of 0.21.1 — 2026-10-19

The owner identifies the tested package as **0.21.1**, says the agent's
observations/actions agree with the Allplan UI, and supplied the
[original conversation log](evidence/m4-agent-test-0.21.1-2026-10-19.md).
The attachment is retained as test evidence, not implementation instructions.
Raw MCP payloads, native traces and the installed manifest were not supplied.

The delivered 0.21.1 source is on PR #16 (`3dc090e`, runtime `41e0cab`),
which was still open when this work began; `develop/m4` remained at `b6810f9`
(0.21.0). The new topic starts from develop/m4 and includes that exact 0.21.1
history. This distinction does not dispute the owner's installed version.

| Operation | Owner-confirmed observation |
| --- | --- |
| Wall thickness `<240 mm` → W1 | The 200 mm Wall moved; the 240 mm Wall stayed unchanged. |
| Remaining Walls → `ogólne03` | Full name lookup failed. The user supplied short name `SZ_OGÓ03`; the move then blocked on an unreadable old layer. |
| Beam attribute listing | Two Beams, 44 attributes each; length 6 m and section name 300X500. Highlighting was submitted. |
| Both Beams: section name 450X450 and length 5 m | User explicitly requested attributes only. First Beam readback conflicted; remaining setters were skipped. Recovery read the second Beam's original values but could not read the first Beam. |
| First Beam → SZ_OGÓ01 | Correct target was clarified by its position. An unresolved earlier execution blocked the new write. |
| Both Beams: Element nośny = true | Integer attribute rejected JSON boolean; no boolean encoding was established. The unresolved execution also blocked writes. |
| Slab highlight, then → SZ_OGÓ01 | Slab was found and highlighting submitted. Layer write remained blocked by the earlier Beam execution. |

Execution `4388b04e39a14fac811db4f58723d01f` remained unresolved after
read-only recovery. The log does not prove whether the first setter persisted,
whether native element identities changed, or which exact read/resolution step
failed. Keep its journal and original execution ID; do not delete records or
retry the setter to make the block disappear.

This is scoped native evidence for the owner's successful Wall move and the
reported failures. It does not establish universal attribute writability,
geometry edits, native selection or UI visibility from tool output alone.
Retain the previously accepted fire/U/query/highlight observations without
asking the owner to repeat them.
