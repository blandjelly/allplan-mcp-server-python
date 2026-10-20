# 0.19.0 — native Wall thickness filter and highlight

The scoped native outcome is retained in
[the owner observation](../../docs/m4-wall-filter-observation-0.19.0.md).

`model_wall_filter` evaluates the complete Wall set of one explicit active
foreground drawing. It reads single-tier native Thickness and compares strictly
against a threshold in mm/cm/m. The default is `<24 cm`: 200 mm matches and
240 mm does not. Query reads only; highlight submits the complete nonexcluded
matching set and clears previous document highlights, including for zero matches.
No material/attribute discovery, setter, resource creation or write plan is added.

Incomplete scope, ambiguous views, a limit, unsupported tiers or failed native
reads block partial highlighting. Default limit is 20 Walls, maximum 100;
this is not acceptance of >200 results or multiple drawings. Every excluded
UUID must belong to the full Wall scope and is explicitly reported. Calls use
the durable native trace and a five-second cooperative budget. A blocking native
call cannot be interrupted. Visibility, units and native acceptance require the
owner observation; submitted counts are not confirmed visible counts.

## Source and automated checks

Final runtime source: **e455f35cf4d546d9b77cf6ae5f59edcc026cc875**.
[CI 39033571910](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39033571910)
passed **6/6 Windows/Ubuntu × Python 3.11–3.13** configurations, **356 tests**
each, followed by one successful package job. [CI metadata](source-ci-0.19.0.json),
[Ubuntu test log](ci-ubuntu-3.12.log), [Windows test log](ci-windows-3.11.log),
[CI build log](ci-package.log).

The connector retrieved CI artifact 12100969454, but transferring its bytes to
the workspace was blocked by proxy CONNECT HTTP 403. Per testing-policy, one
local frozen sync/build from a clean detached checkout of that exact commit
produced the delivered wheel, sdist and Windows ZIP. These are the verified
local fallback artifacts, not a claim of byte equality to the CI artifact.
[Delivery and hashes](delivery-0.19.0.json).

The exact delivered ZIP passed checksum/payload integrity, fresh registration,
frozen sync/import from its extracted contents, upgrade from 0.18.2 and restore.
**31 bridge hashes** verified; journal, native trace and bridge log preserved.
Only `PythonHostHandler.py` and the new `wall_filter.py` change in the native
payload. [Verification](package-verification.json), [script](verify_package.py),
[log](package-verification.log).

**Native PASS / accepted_on_build 0.19.0**, observed 2026-10-17 Europe/Warsaw:
two single-tier foreground-101 Walls read 200 mm (match) and 240 mm (nonmatch),
one submitted adapter, complete coverage and no exclusions/omissions. The owner
confirmed correct 20 cm highlighting, explicit clear and uninterrupted host
operation; four health replies share one session.
[Observation and original uploads](../../docs/m4-wall-filter-observation-0.19.0.md).
Original JSON/delivery flags retain `not_run`/`ready_for_owner_test` as build-time
or pre-confirmation records. Frozen artifacts are unchanged. No general unit,
native selection, write/Undo or full K2/M4 acceptance is inferred. Earlier
0.18.2 single-Wall and Column/M3 evidence retain their original scopes.

## Retained owner outcome

The scoped owner observation is complete: in drawing 101, **200 mm** matched
`<240 mm`, **240 mm** did not, and the owner confirmed highlight and clear with
no model change. The record and original reports are in
[the retained observation](../../docs/m4-wall-filter-observation-0.19.0.md).
Do not repeat the trial.

The source documentation inside the frozen ZIP was prepared before final CI
and retains pending automated-check wording. This delivery record holds the
subsequent source-bound results; no artifact is rebuilt for documentation updates.
Main integration and material writes remain separate.
