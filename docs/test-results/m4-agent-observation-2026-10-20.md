# Owner observation: M4 agent edits, 2026-10-20

This record summarizes the owner's confirmation that the agent's reported
results from the latest-version trial match what was observed in Allplan. The
[attached conversation log](evidence/m4-agent-test-2026-10-20.md) is retained unchanged;
it is evidence, not operating instructions. Earlier assistant replies are
unavailable in that log, and it contains no raw MCP requests/responses, native
trace, or exact installed manifest/package hash. The observation therefore
confirms the reported outcomes for the tested installation, without binding
them to a specific artifact or source revision.

## Confirmed outcomes

- For both queried slab results in drawing 101, the agent set the `Element
  nośny` attribute to `1` and the `Materiał` attribute to `beton zbrojony`;
  reported readback matched all four values. The owner says the agent's result
  matches Allplan.
- For the two results reported as `Slab_TypeUUID` ("Warstwa płyty") and
  `MultiSlab_TypeUUID` ("Strop"), the agent set `Priorytet` to `200`. It
  reported replacing `100` on one result and adding the attribute on the other;
  readback matched both. The owner says the agent's result matches Allplan.
- For six columns, the agent assigned text values `1` through `6` to
  `MCP_QA_MARK` (attribute ID 5001), in the requested order: lower row from left
  to right, then upper row from left to right. Reported readback matched all
  six values. The owner says the agent's result matches Allplan.

These are owner-confirmed outcomes for the observed operations. The log does
not establish native material modification: `Materiał = beton zbrojony` is an
attribute change, not proof that an architectural element's native material
property changed. Nor does the log establish production readiness, broad
family support, or the exact package that was installed.

## Object identity and evidence limits

The two slab query results have distinct reported adapter type names but the
same reported coordinates and spatial bounds, while the owner sees one slab in
Allplan. Matching bounds do not prove that the results are the same entity or
that one is merely a representation of the other. The transcript lacks the
exact model/view UUIDs, adapter ownership relationship, and raw query payload
needed to resolve that question. Preserve both reported results as separate
targets in this observation; do not infer deduplication or independent physical
entities from the available evidence.

The conversation log does not include the initial assistant responses, exact
request arguments, plan hashes, execution records, undo observations, or a
package manifest. It records readback claims and the owner's later confirmation
that the agent results match Allplan. That is useful native outcome evidence,
but it does not independently establish transaction recovery, replay behavior,
the cause of the journal capacity issue, or version-specific reproducibility.

The owner also reports that a full/oversized journal required manual clearing.
The available log does not record the exact error, journal count, record size,
or which limit caused the block. There are three separate limits to diagnose:
the append-only `m4-native-probe.jsonl` trace has a 1 MiB maximum, the active
repair journal has a 128-record count limit, and each repair record has a
separate 1 MiB maximum. The transcript does not establish which one failed.

Candidate **0.23.0** now implements an agent-driven archival flow in
`fix_model_issues`; this is implementation status, not native acceptance. The
agent previews either `native_trace` or `repair_records`, presents the affected
scope, and asks the user before cleanup. Cleanup requires the exact preview
`snapshot_hash` and acknowledgement `confirmed_journal_cleanup`; a changed
snapshot requires a fresh preview and confirmation. The trace operation
archives the reviewed bytes and rotates the fixed active trace path. Repair
cleanup archives eligible, resolved records while preserving their exact
execution IDs for replay. Running, unresolved, corrupt, or oversized records
remain protected. Cleanup performs no native model calls or setters; Apply and
Recover retain their project/document identity checks, while cleanup of the
global shared journal does not require a project/document lookup. This
candidate passed 505 tests per Windows/Ubuntu Python 3.12 job and exact ZIP verification; native maintenance acceptance remains pending. Archival is not a disk
retention policy and does not promise unlimited storage reclamation.

## What this observation does not accept

This observation does not cover native wall material, wall-tier layer writes,
native property modification, selection in the Allplan UI (as distinct from
highlighting), multi-drawing Apply, more than 32 changes, undo, restart/reopen,
or safe journal cleanup and recovery. It does not replace the earlier
version-scoped handoff entries or authorize repeating previously accepted
trials.

See the [office editing development plan](../office-editing-development-plan.pl.md)
for the remaining prioritized acceptance work.
