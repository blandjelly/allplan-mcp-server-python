# 0.19.0 — native Wall thickness filter and highlight

[Complete Windows ZIP](allplan-mcp-0.19.0-windows-evaluation.zip) ·
[Polish owner guide](../../docs/m4-wall-filter-0.19.0.pl.md).

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

Native Allplan testing is **not_run / ready_for_owner_test**, limited to this
new bounded observation. Earlier 0.18.2 single-Wall and Column/M3 evidence retain their
original scopes.

## Owner observation

Install the complete ZIP to the same Local folder using Setup, with Allplan and
MCP closed; then restart the host and MCP from this package. On the retained
MCP_QA_DEMO drawing **101 foreground**, run **M4 Thin Walls.cmd** once.
Expect both 200/240 mm records, only 200 mm matching, and same-session healthy
before/after replies. Observe only the 20 cm Wall highlighted, then use
**M4 Clear Highlight.cmd** and check continued host operation and no model change.
Save JSON/TXT, native trace and bridge.log. A lost reply stops the trial without
retry or another native call. Follow the linked guide for details and restore.

The source documentation inside the frozen ZIP was prepared before final CI
and retains pending automated-check wording. This delivery record holds the
subsequent source-bound results; no artifact is rebuilt for documentation updates.
Main integration and material writes remain separate.
