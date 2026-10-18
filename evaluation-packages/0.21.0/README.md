# 0.21.0 — actionable writes and generic attribute support

[Complete Windows ZIP](allplan-mcp-0.21.0-windows-evaluation.zip) ·
[Short Polish trial](../../docs/m4-agent-fixes-0.21.0.pl.md) ·
[PR #15](https://github.com/blandjelly/allplan-mcp-server-python/pull/15).

The owner’s v2 agent transcript stopped at prepared plans citing a false generic
write flag and native acceptance pending. It has no raw payloads or setter
attempt, so it does not establish an API write rejection. This candidate exposes
model_edit's actual evaluation Apply consistently at top level and in capability
information, with a separate production flag, specific blockers, requirements
and exact next-action hints. All reviewed-copy, highlight, fingerprint, fresh
preflight, durable journal, strict readback and no-retry safeguards remain.

Existing project attribute IDs/names are generic targets, without a list of
special attribute IDs. Default auto typing binds actual SDK scalar members;
explicit enum labels bind targeted label→key→label→key checks and use the
label as setter/readback value. One-component attribute listing supports exact
model/view identity, name filtering, paging and incomplete-metadata reporting.
Opt-in computed-inclusive query supports computed fields with read-only
provenance and proven absence; stored mode keeps its old behavior.

This covers text, integer, real, runtime-supported boolean and validated enum
labels. Date/vector/opaque codecs, native material/property updates, whole-project
and multi-file/production writes remain unsupported. Computed-only attributes
are never writable. The isolated listing covers stored fields present on one
element, not all project definitions; broad discovery stays quarantined.
[Type/API evidence and limits](../../docs/m4-attribute-type-coverage.md).

## Automated evidence

Clean runtime source: **39405be16a2ba9916b05a564702e89e1ff12d1cf**.
[CI 39121935578](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39121935578)
passed **437 tests on each Windows/Ubuntu Python 3.12 job**, followed by a
successful package job. [Source CI record](source-ci.json).

The connector retrieved CI artifact 12134876088; its transfer into this workspace
was blocked by proxy tunnel HTTP 403. The permitted single local fallback build
used a clean detached checkout of that exact source and frozen dependencies.
These delivered files are that build; no byte equality to the CI archive is
claimed. [Checksums](artifact-hashes.json).

The exact delivered ZIP passed checksum/payload verification, fresh bridge
registration, frozen dependency sync/import from extracted contents, upgrade
from 0.20.1 and restore. **36 bridge hashes** verified; journal, native trace
and bridge log were preserved. Wheel/sdist contents were also checked.
[Verification](package-verification.json) · [script](verify_package.py) ·
[log](package-verification.log).

ZIP SHA-256: `201c7a7a4de6dfc2e62bf53adea855e8b6708cabdf4809ebdf2a00c0b6ff469b`.

## Install and scoped native trial

Close Allplan and MCP, extract the complete ZIP, run Setup using the existing
Local folder, then restart the host and MCP from this package. Use a disposable
project copy and the linked short guide: discovery, undefined numeric Wartość U,
explicit Materiał attribute and thin-Wall layer editing; an enum trial is optional
only when a suitable existing field is available. Persist the exact Apply request
before sending; on a lost reply recover the same execution ID without another
Apply. Observe UI, native readback, actual Undo scope and same-session health.

**Native Allplan: not_run for this candidate’s changed paths.** Portable tests
use native fakes and do not establish setter persistence or Undo in Allplan.
Preserve the earlier successful fire/query/highlight and accepted read trials;
do not repeat them. The full office editing plan remains incomplete.

The ZIP contains source documentation from before final CI. This later delivery
record adds results without rebuilding the frozen artifact.
