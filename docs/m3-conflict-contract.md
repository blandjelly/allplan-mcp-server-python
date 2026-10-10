# M3 invalidated-plan inspection — 0.13.0

Status: **ready_for_owner_test**. Portable behavior and native acceptance are
separate. [New owner gate](m3-conflict-owner-test.md) changes one existing C03
mark through the shared executor without leaving the host session.

## Authorization remains invalidated

When an execution starts, all active repair plans become unavailable to Apply
and all cached selections are cleared, as before. Exact-ID journal replay is
unchanged. Invalidated plans retain their original immutable request/plan/hash
only for one read-only revalidate call. Apply requires an active plan and rejects
invalidated evidence with plan_expired before scanning/setters. It leaves that
evidence available for inspection; no execution record is created for this rejection.

The active and invalidated caches share **8 entries / 8 MiB total**, with the
existing 4 MiB per-entry limit. Both use the original **300-second creation TTL**;
invalidation never renews it. A preview evicts the oldest evidence across both
caches. Expiry, eviction or host restart makes inspection unavailable. No adapter
or native document is retained. This evidence cache is separate from the durable
128-record execution journal and changes none of its lifecycle guarantees.

## One fresh read-only comparison

The existing revalidate request accepts the exact retained plan ID/hash. It reruns
the original full audit, checks expiry again after the native read and compares
source/report fingerprints. An invalidated plan always returns state=conflict,
read_only=true and evaluation_apply_available=false. Additional fields are
plan_invalidated=true and invalidation_reason=execution_started.
source_unchanged reports the actual fingerprint comparison independently of
authorization: false for changed audited evidence; true if the model has returned
to its prior state. Neither value restores authorization. Successful inspection
consumes the invalidated evidence. A hash mismatch does not consume it or scan.
Failed reads do not establish validity or authorize Apply.

Active-plan revalidation retains its previous unchanged/conflict behavior and
adds plan_invalidated=false / invalidation_reason=null. No request schema, general
write eligibility, native setter or journal format changes.

## Supported-lifecycle native experiment

Two selected numbering previews use the same fresh full six-column source.
The older C04-only plan proposes S02 → S03; the C03-only plan proposes undefined
→ S03. Only C03's separately reviewed plan executes. Its write invalidates the
C04 plan. The stale Apply must reject before setters, then the retained C04
evidence must compare against the actual changed excluded peer C03 and return
different source/report hashes. The final audit must match C03's verified
post-write audit, C04 must retain S02 and health must retain the same host session.

The launcher saves exact write and stale-probe request identities before sending,
captures MCP text/data, stops on any mismatch/lost reply and provides read-only
recovery of C03. It never retries either write under a new ID. The stale probe's
separate ID is retained in its report if that reply is lost. Manual UI edits
known to cancel the host are excluded from this experiment. One owner Undo and
current-value Recover restore/observe the original C03 state.

This proves only the behaviors actually observed by the new gate. Invalidation
rejection is distinct from a fingerprint conflict detected on an active plan;
the latter still has portable coverage but lacks native manual-edit evidence.
Controlled partial/unknown native recovery remains separate next work.
