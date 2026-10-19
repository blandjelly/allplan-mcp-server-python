# Owner agent observation — 2026-10-18

The owner identifies the installed candidate as **0.21.0**. No exact build hash,
raw MCP payloads, plan IDs or execution journal were retained, so these are
owner-reported native observations for that version and do not establish the
precise request/response or a source-level cause. The complete supplied log is
preserved [verbatim](evidence/m4-agent-test-2026-10-18.md).

## Confirmed changes and refusals

- On a Column, `Wartość U` changed to `0.2`; the owner reported Allplan readback
  confirmed the value.
- On a 200 mm Wall, `Wartość U` changed to `0.15`; the owner reported Allplan
  readback confirmed the value.
- On a Column, fire class changed from F60 to F90 and was confirmed.
- The same two-field operation did not change `Poziom_Górny` from 500 to 300.
  Execution stopped after the confirmed fire-class write. This was a partial
  write, not a rollback; generic editing of `Poziom_Górny` remains unsupported
  or unverified and is not claimed fixed by 0.21.1.
- For a Wall, the `<240 mm` query selected the 200 mm Wall and excluded the
  240 mm Wall. W1 was resolved, but the layer plan was blocked and no write
  occurred. A later request to move the Wall to W1 was also blocked. The owner
  appropriately did not bypass the refusal after asking whether consent could
  skip the write checks.
- The owner confirmed visible highlighting of the Column on layer SZ_OGÓ03.
  The log does not establish native selection; preserve the visible-highlight
  observation without repeating the accepted highlight trial.

Earlier Wall attribute discovery failed on an ambiguous representation and
exact-name lookup. Later successful Wall U editing confirms that the earlier
lookup failures did not establish that the attribute was absent. The transcript
also shows the Column attribute listing, but reading an attribute does not
prove it is writable.

## 0.21.1 follow-up boundary

The candidate is intended to compare attribute values across equivalent Wall
wrappers, preserve raw attributes and pagination through metadata failures,
resolve lower-initial Polish names through project roundtrip without
translation, and scope completeness failures to matching targets with complete
source-peer revalidation. Diagnostics include `required_field_failures` and
`criterion_failures`. Unknown Wall-tier API remains guarded. The missing raw
payloads mean the 0.21.0 transcript cannot establish the cause of its layer
refusal.

Generic scalar attribute-ID editing remains present for Column, Wall, Beam and
Slab; 0.21.1 does not add native family support. Native Wall-layer acceptance,
native material/property writes, and `Poziom_Górny` editing remain unaccepted.
The 0.21.1 CI and package/delivery checks are pending; the new native trial is
also pending.

## Next owner trial

Check only new behavior: list attributes on one Wall using the wrapper
comparison, inspect pagination/raw values and metadata-failure diagnostics,
and resolve the project name using lower-initial `materiał`. Optionally perform
representative read-only Beam and Slab listings. Then preview the W1 edit for
`wall.total_thickness_mm < 240`, inspect completeness diagnostics and verify
200 mm inclusion / 240 mm exclusion. Apply only if the response explicitly
allows it after full revalidation; check UI, fresh readback and Undo. If blocked,
retain the exact response and stop. Do not repeat the confirmed Column/Wall U,
fire-class, query or highlight observations.
