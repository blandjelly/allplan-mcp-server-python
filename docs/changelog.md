# Changelog

## 0.5.2 — 2026-10-08

Correct owner demo bindings to the actual layer **short** names
SZ_OGÓ01/SZ_OGÓ02 (full names Ogólne01/Ogólne02), profile revision 1.0.2.
Owner screenshots also show empty user attribute groups with demo names,
not definitions in the Attributes list; clarify group versus attribute creation
and ordinary text/input definitions before repeating the resource preflight.
No native writes; older profile revisions and evidence archives are preserved.
[Sanitized runtime findings and validation](test-results/m1-profile-correction-0.5.2.md).

## 0.5.1 — 2026-10-08

Use owner-supplied existing layer short names Ogólne01/Ogólne02 in demo
profile revision 1.0.1. Retain revision 1.0.0 contract compatibility. Failed read
bindings now retain the lookup stage and validated returned IDs/names/type
codes instead of only a generic exception class. No model/resource writes.
The owner created both demo text attributes, but the 0.5.0 preflight is
not_checked; their native lookup cause is still unproven. Repeat only the
resource preflight on 0.5.1 before building the fixture.
[Evidence](test-results/m1-profile-followup-0.5.1.md).

## 0.5.0 — 2026-10-07

Complete the bounded M1 read implementation: mm geometry/AABB summaries,
dimensional and spatial predicates with explicit frame/boundary/tolerance,
parent-resolved native component counts, geometry/hierarchy/profile-sensitive
stale checks and schema-versioned demo resource binding. ModelContext can return
configured levels with explicit provenance. Profile queries resolve real IDs
freshly and reject unbound/mismatched resources; mark/status use separate demo
text attributes, not Object_name 498. No write profile is activated.

Add M1 Profile.cmd / M1 Final.cmd and full diagnostic batch/page/summary capture,
keeping seven MCP tools. **56 targeted portable checks PASS**; distributions and
versioned evaluation ZIP build. [Evidence](test-results/m1-completion-portable-0.5.0.md),
[final UI recipe and owner gate](m1-final-batch.md). M1 code is ready for owner
test; UAT-02/UAT-03 geometry/display-unit/nonzero-offset/hierarchy and actual
demo binding are still pending. Preserve accepted 0.2.1/0.3.0/0.4.0 evidence and
archives; do not repeat their accepted owner batches.

## 0.4.0 — 2026-10-07

Add typed `model_query` action `inspect`: explicit scope, bounded raw element
sample, per-field attribute name/type/control/unit and layer name reads,
resource-sensitive probe fingerprints and read/size budgets. Missing passive
values remain API omissions without a native-absence or profile-binding claim.
Add **M1 Metadata.cmd** and diagnostics request/full-response capture, retaining
the seven-tool catalog. **12 targeted portable checks PASS**; distributions and
versioned evaluation ZIP build. [Portable evidence](test-results/m1-metadata-portable-0.4.0.md).
[Two-capture owner card](m1-metadata-batch.md) subsequently **PASS** on the two
columns: complete JSON, resource metadata and passive/active raw 498 comparison.
Owner confirms columns unchanged, passive state restored and unchanged build.
[Runtime evidence](test-results/m1-metadata-runtime-0.4.0.md) remains separate from
automated checks; archive and raw uploads are preserved unchanged. Accepted
0.3.0 query evidence and original ZIP are unchanged; previous batches need no
repeat. Geometry/offset/hierarchy and demo schema/binding remain pending.

## 0.3.0 — 2026-10-07

Add read-only `model_query` with explicit drawing-file/passive/visibility scope,
observed type/layer/raw-attribute predicates, all/any/not composition and distinct
missing/failed reads. Add bounded full selections, deterministic pages and
summaries, per-read source/context revalidation, five-minute expiration and
restart/eviction handling. No partial selection is created on budget failure.
24 relevant portable checks pass; wheel/sdist and evaluation ZIP are built.
[Contract](tool-reference.md), [portable evidence](test-results/m1-query-portable-0.3.0.md).

The three bounded owner query cases subsequently **PASS** on the two-column
scene: scope, metadata, pages/full summary and observed-value predicates.
[Runtime evidence](test-results/m1-query-runtime-0.3.0.md) is recorded after the
original archive was built; that archive and its hash are unchanged. Broader
query behaviors retain portable evidence only. The accepted 0.2.1 context reader is
reused; its correction batch need not be repeated. Geometry/spatial filtering,
offset conversion, top-level native component counting and demo binding remain
pending. M1 is not accepted. [New small owner batch](m1-query-batch.md).

## 0.2.1 — 2026-10-07

Preserve project name/host when project-path lookup fails and retain each
read-only lookup's result. The tested Allplan 2026-1-7 runtime resolves paths
with host/name argument order; the fallback handles this documented-signature
discrepancy without switching projects. The owner follow-up batch passes project
lookup/switch, file unload exclusion and model/view identity reads and confirms
the model is unchanged. 31 portable tests pass.

M1 remains in progress. Geometry unit/offset normalization, levels, durable
references, queries, reusable selections and profile binding remain pending.
[Evidence](test-results/m1-context-runtime-0.2.1.md).

## 0.2.0 — 2026-10-07

Start M1 with typed read-only context/identity probing: current project/document,
foreground and loaded file states, input unit codes, raw project offset and
optional bounded raw-adapter model/view GUID samples. Include context in
diagnostics. 29 portable tests pass. Owner runtime verifies file states and GUIDs
but exposes project lookup failure, corrected in 0.2.1.

## 0.1.2 — 2026-10-07

Correct private-library installation to `Local/Library/PythonHost`, migrate the
earlier library location with backups and preserve restore support. Owner UAT-00
and UAT-01 pass on Allplan 2026-1-7 / local Windows Codex. **M0 closed**.
[Acceptance](test-results/m0-acceptance-0.1.2.md).

## 0.1.1 — 2026-10-07

Deliver recursive integrity-checked bridge installation, rollback/restore,
versioned Windows evaluation packaging and Explorer setup/launch/connect/
diagnostic helpers. Add typed baseline tools, structured errors, per-request
document access, UI dispatch and cancellation/restart handling. Separate embedded
and external runtime diagnostics; disable development Python execution by default.
The private-library target defect is corrected by 0.1.2. Portable installer,
transport and real HTTP MCP checks are included; GitHub Actions results are not
claimed as previously executed evidence.
