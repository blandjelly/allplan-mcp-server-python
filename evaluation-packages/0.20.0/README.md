# 0.20.0 — typed model attribute and layer edits

[Complete Windows ZIP](allplan-mcp-0.20.0-windows-evaluation.zip) ·
[Polish workflow and native trial](../../docs/m4-model-edit.pl.md) ·
[PR #13](https://github.com/blandjelly/allplan-mcp-server-python/pull/13).

`model_edit` plans edits directly from model criteria, without audit findings.
Exact project attribute names/IDs and loaded SDK type members bind text,
integer, real and available boolean values. A plan can assign F120 and an
existing W1 layer to the same matched Column, or assign an explicitly named
material attribute to a Wall. The latter does not update native Wall material.
Replace/add/upsert are separate modes. Stored-read omissions stay unknown;
opt-in dual stored/computed reads establish absence and block computed-only
destinations. No attribute definition or layer is created.

Query supports semantic owners and optional class-based door/window opening
recognition, retaining unrecognized representations as not_checked. Highlights
include matched no-ops and preserve exclusions. Native selection, general
native-property writes, enum/date codecs and multi-file batching remain outside
this candidate. Apply is experimental and limited to 32 setters in one active
foreground drawing, with the existing reviewed-copy acknowledgement, exact
highlighted plan, full-source revalidation, durable journal, strict readback,
same-ID replay and read-only recovery. Partial native failures are reported;
there is no automatic rollback or claim of one combined Undo.

## Automated evidence and delivery

Clean runtime source: **ec2aeae832c2ac017c07c4af71b7c7a6ff47f9d9**.
[CI 39049036363](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/39049036363)
passed **Windows and Ubuntu, Python 3.12, 387 tests per platform**, followed by
one successful package job. [Source CI record](source-ci.json).

CI artifact 12107341025 was retrieved by the connector, but workspace transfer
returned HTTP 403. The permitted single local fallback build used a clean
detached checkout of that same source, with frozen dependencies. These delivered
files are that fallback build, without a claim of byte equality to CI artifacts.
[Artifact checksums](artifact-hashes.json).

The exact delivered ZIP passed payload/checksum verification, fresh registration,
frozen sync/import from its extracted contents, upgrade from 0.19.0, and restore.
**34 bridge hashes** verified; journal, native trace and bridge log were preserved.
Wheel and sdist contents were also checked for the new tool/modules.
[Verification](package-verification.json), [script](verify_package.py),
[log](package-verification.log).

ZIP SHA-256:
`8d78fb8d872dccb5f9404ff62ac97b04b26552a1a837feef1d4d3e9bdbe6c054`.

## Native status and next step

**Native Allplan: not_run for this new path.** Portable tests use native fakes
and do not establish new setter, opening-owner, readback or Undo acceptance.
The complete office-editing plan remains incomplete. Existing accepted
0.19.0/0.18.2/Column/M3 observations and frozen artifacts remain unchanged.

Close Allplan and MCP, extract this complete ZIP, use Setup with the existing
Local folder, then restart the host and MCP from this package. In a disposable
copy, use local Codex/MCP to perform only the new short attribute add/replace
and F120 + W1 trial in the linked Polish guide. Save the exact Apply request
before sending. If its response is lost, recover its execution ID; do not
create another ID or retry setters. Observe UI values, the actual Undo scope,
and same-session health. Do not repeat already accepted native read trials.

The frozen ZIP contains the source documentation as it stood before CI;
this delivery record adds subsequent results without rebuilding that artifact.
