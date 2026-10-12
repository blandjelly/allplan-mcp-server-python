# M3 closure — retained test project

**Closed within the fixture scope, 2026-10-12 Europe/Warsaw.** The owner resumed
work and explicitly chose to close M3 within the retained test project. This
decision supersedes the previous pause and open-M3 statements in historical
gate reports. Package **0.15.0** remains unchanged.

**UAT-05/UAT-06 are accepted for the scope below using existing native evidence.**
This is a narrowed milestone acceptance, not a new native test or acceptance of
the original broader gate. In particular, native manual UI edits against an
active plan remain unaccepted. M0–M3 form a **fixture evaluation MVP**; typical
office-project use remains future work. Main integration and release are
separate from this milestone closure.

## Accepted scope

- The same original disposable **MCP_QA_DEMO** project/copy, installed Local
  journal and recorded Allplan **2026-1-7** setup with local Windows Codex.
- Foreground drawing file **101**, six native Column roots C01–C06, demo read
  profile **1.0.2**, audit profile **2.0.0** and retained named resources.
  The fixture's beams, wall, slab and files 102/103 have no accepted M3 writes.
- The recorded one- or two-change plans: C05 layer repair, C06 existing-string
  status repair, C03/C04 existing-string mark numbering, C03 conflict/recovery
  experiment and selected C04 mark replacement with C02 explicitly excluded.
  Acceptance does not cover every combination of these targets or fields.
- `fix_model_issues`, `apply_office_standard` and `rule_based_edit` through
  their explicit evaluation route, reviewed plan ID/hash, fresh source checks
  and execution identity saved before sending. Demo standards remain versioned.
- Preview/revalidation, audited-field readback and post-audit verification,
  saved-ID replay without setters, read-only recovery and the observed separate
  owner Undo steps. No grouped Undo, automatic rollback or resume is claimed.
- Healthy-journal inspection in the retained Local, with observed summaries
  **6 → 7 → 7**. The 128-record stop remains an operational limit.

The executor still implements eligibility for **1–32** changes in one foreground
file. That implementation limit is broader than native acceptance. Closure
does not change the runtime, enable a generic writable profile or turn
`evaluation_apply_available` into a supported-project registry.
`active_for_write=false`, general `apply_available=false` and durable-reference
limitations remain in force.

## UAT evidence mapping

| Bounded requirement | Existing evidence | Accepted result |
| --- | --- | --- |
| Preview leaves the model unchanged; exact changes and exclusions can be reviewed | [Validation history](validation-status.md#accepted-m3-slices), 0.7.0/0.9.0/0.10.0; [0.15.0](m3-selected-mark-acceptance-0.15.0.md) | Side-effect-free previews, deterministic numbering and retained full snapshots. |
| Reviewed layer/status repairs affect only authorized targets | [0.11.0 workflow gate](validation-status.md#accepted-m3-slices) | Two separately reviewed single-target workflows, exact readback, audited-field checks and complete audits **5 → 4 → 3**; owner confirms UI, peers, host survival and two-step Undo. |
| Marks/numbering use full-scope collision evidence and preserve exceptions | [0.12.0](m3-numbering-acceptance-0.12.0.md), [0.15.0](m3-selected-mark-acceptance-0.15.0.md) | Two numbered writes and subsequent no-op, audits **3 → 0 → 3**; selected C04 write preserves excluded C02, audits **3 → 1 → 3**. |
| Stale authorization cannot write; changed excluded-peer evidence is observable | [0.13.0](m3-conflict-acceptance-0.13.0.md), restart/stale gate in [validation history](validation-status.md#accepted-m3-slices) | Stale Apply rejects before setters, changed excluded C03 produces a source/report conflict during read-only invalidated-plan inspection; restart expires old plans. This is not active-plan manual-edit acceptance. |
| Repeating a saved execution does not repeat writes | [0.12.0](m3-numbering-acceptance-0.12.0.md), [0.14.1](m3-recovery-acceptance-0.14.1.md), [0.15.0](m3-selected-mark-acceptance-0.15.0.md) | Exact-ID replay is read-only after completion/restart/Undo; historical results remain distinct from current observations. |
| A controlled unknown result can be inspected without resuming skipped work | [0.14.1](m3-recovery-acceptance-0.14.1.md) | Actual C03 running/unknown record, skipped C04, new-ID rejection, restart/reconciliation and replay without resume; owner Undo, audits **3 → 2 → 3**. |
| Readback, audit, UI and Undo agree within the recorded scope | [0.14.1](m3-recovery-acceptance-0.14.1.md), [0.15.0](m3-selected-mark-acceptance-0.15.0.md) | Complete six-column snapshots restore the baseline; session continuity is claimed only where observed/owner-confirmed. |
| Installed healthy history is inspectable without model access or record changes | [0.15.0](m3-selected-mark-acceptance-0.15.0.md) | Complete verified summaries **6 → 7 → 7**, no blockers; no native capacity/corruption/migration claim. |

The original exit gate combined stale-plan rejection with manual-edit conflicts.
The owner-selected fixture closure retains the proved stale-plan behavior and
explicitly defers the unproved active-plan manual-edit case. It does not
retroactively label that original broader requirement PASS. Findings counts
are scenario-specific: three remaining mark findings after layer/status repair
are expected, not an unsuccessful repair or a universal completion rule.

## Retained delivery evidence

The [0.15.0 delivery](../evaluation-packages/0.15.0/README.md) records clean
source **7e3657bc33ecf913376d302da900af386b3b8a23**, **219 portable tests PASS**,
frozen sync, wheel/sdist builds, exact installation/restore with **23** bridge
hashes and preserved journal, and [source CI 38181795091](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38181795091)
**6/6 PASS** on Windows/Ubuntu Python 3.11–3.13. These results retain their tested
source and environment; they are not a fresh run on the closure commit.

Historical acceptance reports, raw uploads, delivery manifests, archives,
embedded instructions and source-CI observations remain unchanged. Their
as-recorded open/pause or ready_for_owner_test statements describe the delivery
at that point; this document and the current handoff define the current milestone.
Documentation closure runs link/diff checks only, no runtime tests/builds or
repeated native gate. Before actual main integration, follow the final-candidate
checks and full matrix required by [testing policy](testing-policy.md).

## Operational limits and handoff

Leave/save the original copy after the accepted Undo: C02/C04=S02, C03 missing
with its original raw value, C05 structure layer and C06 NEW. The owner confirmed
that the fixture is in its documented state. Preserve package logs, saved
execution identities and **Local/.allplan-mcp/repairs**. No Redo, repeated writing
gate or new owner batch is needed for this closure.

At 128 records, stop new execution. Do not delete records to regain slots;
valid saved replay/recovery remain available. Bridge backups are not journal
backups. Do not transfer replay/recovery identities to another project copy,
Local folder or machine. A changed host requires fresh preview authorization.
Do not repeat the UI-edit scenario known to cancel the host unchanged.

Remaining unaccepted work is tracked in the [office-project roadmap](office-project-roadmap.md):
wider plans/profiles/files, native active-plan manual conflicts, durable/cross-copy
identity, journal capacity/corruption/migration/rollover, crash/power-loss and
broader/grouped Undo. Those limits no longer block this explicitly narrowed
fixture milestone; they still constrain what may be promised to users.
Graphic labels, file moves and universal native-property setters remain
conditional extensions.
