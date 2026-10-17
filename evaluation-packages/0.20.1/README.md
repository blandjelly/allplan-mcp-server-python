# 0.20.1 — fixes from the owner agent trial

[Complete Windows ZIP](allplan-mcp-0.20.1-windows-evaluation.zip) ·
[Short Polish trial and limits](../../docs/m4-agent-fixes-0.20.1.pl.md) ·
[PR #14](https://github.com/blandjelly/allplan-mcp-server-python/pull/14).

The owner transcript exposed numeric Wartość U blocked on an undefined string
and Wall layer writes whose root-adapter readback stayed unchanged. This
candidate accepts only exact observed undefined markers for metadata-bound
numeric/boolean replacements, with the original raw value and fingerprints.
Wall layer changes bind direct WallTier identities, preflight all tiers and
read them back freshly. Explicit component-layer queries use the same owner
semantics. Historical root-layer journal records retain their original reader.

A native single-tier `wall.total_thickness_mm` criterion binds the `< 240 mm`
condition directly into a model_edit plan and revalidates all Wall peers before
writing. Multi-tier/unknown thickness and mixed/unknown tier layers block the
operation; there is no geometry approximation or arbitrary resource binding.
All existing reviewed-copy, highlight, durable journal, strict readback,
replay and recovery guards remain in place. There is no automatic retry,
rollback or claim of one combined Undo.

Native material editing remains unsupported. An explicit material attribute
and the native construction/material definition are separate targets; no
attribute is substituted for the requested native material.

## Automated evidence and delivery

Clean runtime source: **a0321dc40b52544b88e0f21724e523ab0c7bbb13**.
[CI 39057801089](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39057801089)
passed **Windows and Ubuntu, Python 3.12, 414 tests per platform**, followed
by one successful package job. [Source CI record](source-ci.json).

CI artifact 12110681110 was retrieved by the connector, but workspace transfer
returned HTTP 403. The permitted single local fallback build used a clean
detached checkout of that exact source, with frozen dependencies. These files
are that fallback build; no byte equality to the CI archive is claimed.
[Artifact checksums](artifact-hashes.json).

The exact delivered ZIP passed payload/checksum verification, fresh registration,
frozen sync/import from its extracted contents, upgrade from 0.20.0 and restore.
**35 bridge hashes** verified; journal, native trace and bridge log were preserved.
Wheel and sdist contents were also checked for the changed modules.
[Verification](package-verification.json), [script](verify_package.py),
[log](package-verification.log).

ZIP SHA-256: `a27e8a22f136c44ff36a686af74473494c7dad4f3810e803bf30bd1b8a26753b`.

## Native status and next step

**Native Allplan: not_run for these changed paths.** Portable tests use native
fakes; they do not prove setter persistence or Undo in Allplan. The full office
editing plan remains incomplete. The supplied transcript is retained as an
owner observation without exact installed build/payload binding. Existing
successful fire-classification/query/highlight observations and all frozen
packages remain preserved; do not repeat those trials.

Close Allplan and MCP, extract this complete ZIP, use Setup with the existing
Local folder, then restart the host and MCP from this package. In a disposable
copy, run only the two new trials in the linked guide: undefined numeric Wartość U
and the thin-Wall layer path. Preserve the exact Apply request before sending.
If its reply is lost, recover the same execution ID without another Apply.
Observe the UI, component readback, actual Undo scope and same-session health.

The frozen ZIP contains source documentation from before CI; this delivery
record adds later results without rebuilding the artifact.
