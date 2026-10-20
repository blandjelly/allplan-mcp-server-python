# 0.18.0 — one native Wall thickness/material sample

This package is a historical single-Wall read candidate. Its read was later
observed on 0.18.2; see the [retained observation](../../docs/m4-wall-observation-0.18.2.md).
Do not repeat the earlier candidate trial.

This adds an independent next M4 step towards walls thinner than 240 mm → native
C35. It reads **one existing single-tier Wall**, not all wall thicknesses:
`GetElement` → native Wall type check → `Properties` → `TierCount` → tier 1
`Thickness` / raw `Material`. Multi-tier/invalid/failed reads stop without
fallback or retry. It uses no bounding-box thickness, material attribute or
surface substitution. The strict `<240` comparison is informational under an
explicitly unverified API-mm assumption. Native material binding/writes,
highlighting and Apply are unavailable. Broad discovery remains quarantined;
the 0.16.0 native crash cause is still unknown.

The client saves the pending request atomically with fsync before sending one
wall request, bracketed by same-session health replies for structured results.
After a lost reply it sends no following native request. Each new native read
has a durable before-call trace. These records do not establish crash containment.

The [0.17.2 package](../0.17.2/README.md) and its evidence remain unchanged;
its native highlighting check is still **not_run**. The two Column runtime files
in this ZIP are byte-identical to 0.17.2. Neither native test is a prerequisite
for the other. Both can be performed later, as requested by the owner.

Validation for clean source **5ea4bcfd88f500bbf137e361ba5d6cc3d83710b5**:

- **289 portable tests PASS**, CPython 3.12.14, 115.171 seconds;
  [full log](portable-tests.log). New coverage includes single-tier/raw-property
  reads, strict thresholds, UI-unit independence of the raw API value, rejected
  invalid lengths, exact requested root, retained native owner lifetime, trace
  guards, unsupported tiers/types and no writes. Actual MCP HTTP tests cover
  pending evidence, health, old bridge rejection and lost reply without retry.
- Frozen sync, wheel/sdist and Windows package builds PASS; [build log](build.log).
- Exact ZIP checksum and payload verification, fresh installation, upgrade from
  0.17.2 and restore PASS: **30 bridge hashes**, journal/trace preserved, Column
  runtime byte identity and wheel/sdist contents checked. This is portable
  installation simulation. [Verification](package-verification.json), [script](verify_package.py).
- [Source CI 38823160113](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38823160113):
  **6/6 PASS**, Windows/Ubuntu × Python 3.11–3.13, including frozen sync, tests,
  wheel/sdist and Windows package builds; [recorded results](source-ci-0.18.0.json).

[Delivery manifest/artifact hashes](delivery-0.18.0.json).
Artifacts are frozen from the clean source above. Later documentation/delivery
commits do not rebuild them or expand the recorded source/test scopes.

The delivery's native status fields record `not_run` at build time. A later
0.18.1 attempt blocked before the Wall read; the corrected 0.18.2 candidate
returned one single-tier Wall's 240 mm thickness and raw material `Beton`,
matching UI. See the [scoped observations](../../docs/validation-status.md).
Material writes, C35 resource binding and general M4 acceptance remain separate.
