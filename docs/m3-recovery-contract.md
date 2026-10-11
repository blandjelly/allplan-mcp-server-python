# Controlled unknown-result inspection — 0.14.1

Status **ready_for_owner_test**. Native partial/unknown-result recovery has no
acceptance yet. Previous [0.13.0 conflict acceptance](m3-conflict-acceptance-0.13.0.md)
and [0.12.0 numbering acceptance](m3-numbering-acceptance-0.12.0.md) remain scoped
and need no repeat. [Owner walkthrough](m3-recovery-owner-test.md).

## Correction after the 0.14.0 owner preflight

The owner report at 2026-10-11T21:57:26Z passed health, three-finding audit
and full six-column snapshot, then blocked at numbering_preview. No Apply or
execution ID was created. Correct proposals were ordered C04/C03 by model UUID,
while the diagnostic requires C03/C04. Package 0.14.1 preserves generated
numbering assignment order in the immutable preview before its hash is computed.
The ordinary numbering values/keepers are unchanged; generated writes now follow
the reviewed canonical spatial order. Non-numbering plans retain their order.
The CLI and host still require the exact C03-first fixture; no guard was relaxed.
Pre-Apply failures report native_setters_started=false / No Apply sent and allow
a corrected preflight retry without deleting journals. Once an ID is saved,
unknown/rejected/replay protections retain their existing behavior.

## Explicit diagnostic control

The optional Apply field `evaluation_stop=after_first_setter_before_readback`
requires the separate acknowledgement `disposable_copy_reviewed_recovery_test`.
Both public MCP and dependency-free host validators require the exact pair;
unknown controls, nulls and pairing with an ordinary acknowledgement reject
before native document access. Normal Apply requests have no control and retain
their existing behavior. The control participates in the durable request hash;
removing it while reusing an execution ID conflicts.

The executor additionally restricts the control to the unselected versioned demo
numbering plan in foreground file 101: two Column existing-string mark changes,
C03 undefined → S03 at center (12000,0,1500) mm, then C04 S02 → S04 at
(0,6000,1500) mm, exactly three initial audit findings. Both changes must share
the same freshly bound string resource. Normal full-source/hash/TTL, collision,
all-target native preflight, old-value and serialization checks still run.

After the first native setter returns, this diagnostic returns immediately,
before readback, second setter, post-audit or final record save. The existing
write-ahead record remains **running**, with **unknown / skipped** outcomes and
no claimed successful readback. Its diagnostic metadata explicitly identifies
controlled interruption, not a native crash. No record is manually forged or
edited to manufacture unknown state. An actual native exception still follows
the ordinary stopped/unknown error path and fails the walkthrough expectations.

This is a controlled interruption after a setter, not proof of native exceptions,
process crash/power-loss durability or cancellation during an executing setter.
Only C03 is requested to be written in this experiment; C04 stays skipped.
The reviewed full plan permits the existing preflight to check both targets,
but the diagnostic control stops before the second write.

## One-off gate and recovery

The first launcher durably saves the exact execution/request identity before
sending Apply. It verifies the actual running marker, read-only exact-ID replay,
and rejection of a separate new execution identity with `repair_recovery_required`
before setters. The guard probe uses the invalidated original plan: even if the
journal guard regressed, this plan still cannot authorize a second write.
The probe has its own saved identity and unresolved-response flag.
Fresh full six-column audits and field snapshots must show only C03 changed,
including unchanged status/layer/geometry and C04/C02=S02; audit findings **3 → 2**.

The owner restarts StartPythonHost in the original project before the separate
inspection launcher. Health must report a changed host session and matching
package/integrity. Recover uses the original execution ID and normal journal
code: unknown C03 becomes **reconciled / new_value_observed**, C04 remains
**skipped** with **old_value_observed**; record state becomes **stopped**.
Saved-request replay remains read-only and cannot resume C04. Fresh full snapshots,
audit and health confirm unchanged partial state after inspection.

After the owner observes UI and performs one Undo, the third launcher observes
both old values and **3** findings. It checks the original full field snapshot
with only the fresh query-session ref omitted. Reconciled history remains
historical; exact-ID replay still cannot write. All inspection operations can
update journal observations but invoke no native setter, retry, resume or Undo.

A saved test pointer blocks rerunning the writing launcher even after resolution.
Categorized pre-setter rejection retains explicit rejected/native_setters_started=false
evidence; inspection sends no recovery request for it. Lost write replies retain the original identity; after host restart use inspection,
never a new Apply. A lost guard-probe reply retains both identities and blocks
ordinary inspection until local Codex inspects the separate probe and fresh
model/journal evidence. No deletion or automatic journal pruning is introduced.
Copy identity and mutation causality remain unproven; use only the original copy.

M3/UAT-05/UAT-06 remain open. Any native acceptance must be recorded separately
from portable fake/HTTP checks and bounded to the observations actually supplied.
