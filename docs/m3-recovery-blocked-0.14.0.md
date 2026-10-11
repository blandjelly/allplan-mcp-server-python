# 0.14.0 native recovery preflight blocked

Observed report: m3-recovery-check-20261011T215726520709Z.json/.txt,
supplied by the owner. Recorded on 2026-10-12 Europe/Warsaw; report timestamp
2026-10-11T21:57:26Z. This is diagnostic evidence, not native recovery acceptance.

The gate passed health_preflight (matching 0.14.0 MCP/bridge, verified integrity),
audit_before (six columns, exactly QA-001/QA-002/QA-002, complete coverage) and
snapshot_before (complete full six-column field read). It blocked at
numbering_preview; no revalidation, confirmation, Apply, execution ID or native
setter was reached. The project remains at the retained pre-test state; this
attempt requires no Undo. Preserve the original owner reports and Local journal.

The plan correctly proposed C03 undefined → S03 and C04 S02 → S04 with validated
numbering/marks and evaluation_apply_available=true. The planner sorted writes
by UUID, returning C04 first (4f3cc27e-5224-403d-939d-7b4e0cedf9a2), then C03
(65ab07fe-d37a-4adf-b1b6-3040fdde84a2). The canonical spatial assignments themselves
already listed C03 then C04. The recovery CLI and host intentionally require C03
first to interrupt after exactly that setter. Existing sequential fake UUIDs
coincidentally produced the expected order and missed this mismatch.

0.14.1 keeps generated changes in their canonical numbering assignment order
before the report and immutable plan hash are created. Explicit non-numbering
changes retain their relative file/UUID/field order. Number allocation, duplicate
keepers, resource/old-value checks, reviewed hashes and exact diagnostic scope
remain enforced. No uploaded plan is edited or reused as write authorization.
The fresh owner gate must build and review its own plan.

Regression fixtures use the owner's reversed UUID order. Host tests cover
stable previews under reversed adapter enumeration, ordinary two-target
numbering, controlled C03-only interruption, recovery and exact-ID read-only
replay. Real MCP HTTP checks cover the complete restart/Undo walkthrough and
preflight rejection with no Apply/ID, followed by a corrected preflight.
Pre-Apply failure messages now say No Apply sent/native_setters_started=false;
once an identity has been saved, uncertain-result protections remain in effect.

Next owner action: install the new [0.14.1 package](../evaluation-packages/0.14.1/README.md)
and repeat only the still-uncompleted [recovery gate](m3-recovery-owner-test.md)
on the same unchanged disposable copy. Earlier conflict/numbering acceptance
remains scoped to its delivered versions. PR #2 stays draft into main;
M3/UAT-05/UAT-06 remain open.
