# Implementation plan

M4 development uses **develop/m4**; main integration is separate.
Read the [current handoff](next-model-handoff.md) for the version and next task,
the [development plan](development-plan.md) for the
backlog, and the [testing policy](testing-policy.md) for checks and builds.

## Accepted fixture baseline

| Stage | Accepted scope |
| --- | --- |
| M0 | Installation, update/restore, health/version/box tools and host lifecycle. |
| M1 | Explicit model context, typed query, selection pages, summaries, resource binding and canonical geometry. |
| M2 | Read-only audit profile, coverage, evidence and locatable findings. |
| M3 | Bounded preview/apply/revalidate, layer/status/mark repairs, stale guards, journaling, replay/readback and controlled unknown-result recovery. |

Acceptance is limited to the retained fixture and recorded scopes in
[validation status](validation-status.md). It does not establish arbitrary
multi-file writes, universal project identity or whole-project coverage.
M4 remains partially accepted; its remaining gates are maintained only in
the development plan.

## Later scope

Model generation, layouts, issue exports and whole-project documentation are
future work. Specify their inputs, ownership, conflicts, recovery and native
acceptance independently; they do not expand the accepted M4 scope.

## Scaling analysis of develop/m4 and MCP ergonomics

Code analysis from **2026-10-27 (Europe/Warsaw)**, base `develop/m4`
[`6cab354c437c8d08c9b8370164733e6ef13eecd7`](https://github.com/blandjelly/allplan-mcp-server-python/commit/6cab354c437c8d08c9b8370164733e6ef13eecd7),
version 0.39.0. Implemented state is separated from proposals below. No native
measurements or new Allplan trials were made; cost conclusions follow from the
code flow, and any expected speed-up needs a benchmark. This is an
optimization design, not an extension of the accepted product scope. Product
priorities remain in the [development plan](development-plan.md).

### Conclusion and meaning of the limits

**Larger models can be supported, but raising 32 and 200 alone will not solve
the problem.** 200 is the read page size, not the maximum number of found
elements. 32 limits the expanded changes of one Apply. Scale separately: the
number of scanned adapters, the amount of data returned to the agent, and the
number of changes in a whole job. A large model with a single hit can also
exceed the enumeration budget.

| Layer | Current contract and source | Consequence |
| --- | --- | --- |
| Query page | Default 100, max 200; `QueryInput`, `PageInput` in [query_models.py](../src/allplan_mcp/query_models.py), validated in [query_contracts.py](../python_host/PythonPartsScripts/PythonHost/query_contracts.py). | `selection_id` and `page.next_cursor` already allow more than 200 results if the whole scan fits the other budgets. |
| Enumeration | Default 5000, max 10000 **raw adapters**, 5 s per scan; `ModelQueryService._scan` in [model_query.py](../python_host/PythonPartsScripts/PythonHost/model_query.py). | Adapters are not business elements. The counter grows before out-of-scope files are rejected; narrowing predicate/scope does not shrink the `SelectAllElements` enumeration. |
| Read memory | 4 MiB total of serialized `source` records during a scan; 8 selections, TTL 300 s (`ModelQueryService`). | Not a strict RAM limit or a 4 MiB response. `source`, groups, results, hashing and copies raise peak memory. The selection cache has no total byte limit. |
| Fields and scope | Max 32 attributes, explicit scope up to 100 files, `max_adapters` as above. | The attribute limit is independent of the change limit; unloaded files do not become available by widening scope. |
| M4 plan | Up to 16 `changes` declarations in [model_edit_models.py](../src/allplan_mcp/model_edit_models.py); `preview` expands them per element and field in [model_edit.py](../python_host/PythonPartsScripts/PythonHost/model_edit.py). | 20 elements × 2 changed fields = 40 changes, above 32. A no-op adds no change. Changes need not equal SDK calls (delete has a grouped setter). |
| Apply | `RepairExecutor.MAX_CHANGES = 32`; also enforced in plan eligibility and stored-record validation, [repair_execution.py](../python_host/PythonPartsScripts/PythonHost/repair_execution.py). One active foreground drawing. | Changing one constant needs a compatibility review of the journal, recovery and all M3/M4 routes, not just a longer request list. |
| Plan cache | TTL 300 s, up to 8 plans, 4 MiB/plan, 8 MiB total, [model_repair.py](../python_host/PythonPartsScripts/PythonHost/model_repair.py). | A large preview may not fit the cache. Apply invalidates other plans and clears selections. |
| Journal and trace | 512 active records, 1 MiB/record (`RepairExecutor`); trace 8 MiB and durable call boundaries in [property_probe.py](../python_host/PythonPartsScripts/PythonHost/property_probe.py). | Batches increase space use; a full journal/trace stops the workflow. Never delete unresolved data to free space. |
| Time and transport | Apply budget checks 20 s; material evidence 10 s, base scan 5 s. [transport.py](../python_host/PythonPartsScripts/PythonHost/transport.py): queue of 32 requests, 3 s UI start, 1 MiB request body. [allplan_client.py](../src/allplan_mcp/allplan_client.py): default 30 s timeout. | These are different limits. A time check does not interrupt a running native call. A lost Apply reply may mean the write happened. The queue of 32 is not a model-change limit. |

An exceeded read budget ends with an error and no complete selection. Such a
result must never be presented as "found 0". `page.complete` means the end of
paging, not full project coverage: `coverage`, `omissions`, representation
conflicts and `not_checked` apply separately. This matters especially for the
still-open Beam/SkeletonBeam discovery.

### Where the cost arises today

1. **Full rescan for every page and summary.** `ModelQueryService.handle`
   calls `_scan` again and compares `source_fingerprint` before reading the
   cached page. For N adapters and P pages that is P enumerations plus any
   summary. The scan includes native reads, grouping, sorting and hashing; its
   cost is not limited by the number of returned hits.
2. **Field reads before predicate evaluation.** `_scan` reads needed fields,
   geometry and hierarchy before the final group filter. Rejected records stay
   in the fingerprint to detect new hits. Keep that safeguard, but expensive
   presentation fields need not always be read for excluded candidates. The
   native-material path already narrows this in `model_edit.observe`; do not
   describe it as a new feature.
3. **Repeated observation during highlight.** `model_edit.highlight` runs
   revalidate, another observe, a separate `_scan`, and then
   [model_selection.present_selection](../python_host/PythonPartsScripts/PythonHost/model_selection.py)
   scans again: four scans per highlight in the typical M4 path. Each is
   justified by current service boundaries, but sharing them within one UI
   operation is a concrete refactoring candidate.
4. **Every target resolved from scratch.**
   [native_model_edit.resolve](../python_host/PythonPartsScripts/PythonHost/native_model_edit.py)
   runs `SelectAllElements` again. A normal Apply resolves each target in
   preflight, before the setter and at fresh readback, and also observes the
   whole scope before/after execution. Enumeration therefore grows as N × K for
   K changes. Delete has a separate grouped path; measure it separately, as
   well as the material preservation cost.
5. **Durable writes and serialization.** `RepairExecutor.save` serializes and
   hashes the whole record, writes a temp file, fsyncs and replaces. The full
   record is rewritten before each setter and after readback. A large
   monolithic plan multiplies this cost. The trace also persists call
   boundaries; optimization must not remove fsync.
6. **Agent interaction cost.** [server.py](../src/allplan_mcp/server.py) has
   long descriptions of multi-action tools, and results repeat metadata.
   `model_edit` already returns `write_blockers`, `required_steps` and
   `next_action`; unify this pattern rather than building a second workflow.
   The client classifies read-only by endpoint, so even a preview timeout on
   `/model-edit` is reported as `execution_unknown`.

There is no basis for promising a specific speed-up. In particular, parallel
MCP requests will not speed up the Allplan API: the dispatcher runs one
callback per UI tick, and excess requests consume the queue and start budget.

### Target read: large set, small responses

**First expose existing capabilities more clearly.** Add a ready `next_action`
for the next page, an explicit `matched_total` versus `returned`, and a
type/file summary from the existing snapshot. Do not require an extra summary
or fetching all pages when the user asks for a count or plans a
criterion-based edit. `model_edit.preview` already accepts a predicate and
needs no prior query.

**Separate two explicit read-consistency modes (API proposal):**

- Keep the current default `live_verified`: a page requires a fresh source
  comparison. A bounded `collect` could fetch a larger chunk after one
  revalidation, with a byte limit and cursor; do not pretend it removes the scan.
- Add opt-in `snapshot`: the immutable result of one completed scan; later
  pages come from JSON without a native full scan. Each page only checks the
  current session/project/document identity with a light context read, without
  element enumeration. Return the snapshot ID, observation time,
  session/project/document, `freshness=not_revalidated` and
  `usable_for_write=false`. Restart, context change or expiry invalidates the
  handle; reading an old snapshot must not suggest the model is current.
  Preview, highlight and Apply still perform their fresh checks. This is an
  explicit new semantic, not a silent removal of the stale guard.

In both modes introduce `summary|compact|full` projections, paged details and
`max_response_bytes`. Mark an unrequested field as omitted by projection, not
`null` or attribute absence. Always keep coverage, conflict/omission counts
and a path to full evidence. If even one record exceeds the budget, return a
detail ID or an explicit error; the cursor must advance without empty-page
loops. Byte size is enforceable; tokens depend on the client and are measured
separately.

**This still does not remove the 10000 adapters / 5 s / 4 MiB limits.** Next stage:

- Keep a JSON index by `(session, project, document, file, model, view)` and
  shared metadata instead of duplicating context in every element. Add an
  explicit byte budget for the whole cache, TTL and controlled eviction.
  Consider an on-disk snapshot after RAM measurements; keep separate limits and
  cleanup for the reproducible cache and the undeletable unresolved journal.
- Split the query into a cheap identity/condition read and expensive result
  fields. Pushdown must keep three-valued predicates, representation consensus
  and detection of elements entering the result. A geometry/metadata cache
  needs a context key and a proven invalidation signal; TTL does not prove the
  absence of manual changes in Allplan.
- Research per-file filtering/enumeration APIs and stable document change
  identifiers. The repository does not prove a sufficient revision token or a
  safe iterator continued across callbacks. Without such proof do not claim
  cheap, complete incremental revalidation.
- Chunk long read jobs on the UI only after establishing adapter lifetime and
  the semantics of changes during a scan. Only JSON enters the cache; live
  adapters must not reach worker threads or be used after a mutation. If a
  consistent scan cannot be proven, the result is incomplete/stale, not full.

### More than 32 changes: a durable job with small batches

The preferred direction is a **new job coordinator**, initially for one active
drawing and operations with suitable native evidence. Keep up to 32 expanded
changes per batch; the whole job may have more. Multi-file and whole-project
work are later, separate stages.

A loop over the existing Apply is not enough: the first write invalidates all
plans and selections, and re-evaluating the predicate may cover a different
set. Proposed lifecycle:

1. **Prepare/preview:** a complete read and a durable manifest with schema
   version, scope, criterion, exact targets/owner/view, old and new values,
   dependencies, exclusions, no-ops, blockers and a hash. Full details are
   paged; the summary must not hide any reviewed part of the scope. Resolve
   global rules first (for example numbering uniqueness and parent/child
   overlap). Without a complete read do not create an executable manifest.
2. **Review:** authorization covers the exact manifest and an explicit
   partial-execution model. Do not carry approval over from an arbitrary
   earlier selection. Keep the required highlight of exact targets; for large
   sets, page previews must not pretend to present the whole manifest.
3. **Partition:** deterministic units by file, element and dependency. Do not
   split one owner's changes or a delete subtree in a way that breaks their
   contract. The batch budget accounts for changes, bytes, expected time and
   journal space; 32 is a ceiling, not a required size.
4. **Execute:** only now create a fresh child plan for the next batch. Bind it
   to the manifest and its hash, re-check resources, scope, owners, values and
   global invariants. The coordinator recognizes its own confirmed changes; a
   foreign change or a new matching element stops the job for re-review
   instead of widening scope. For each batch persist the exact request and
   immutable execution ID before sending, run a serialized Apply and a fresh
   readback.
5. **Stop/recover/resume:** `unknown`, conflict, incomplete readback, full
   disk or a context change pause the next batches. After a lost reply only
   inspect/recover the same ID; a timeout never authorizes a new ID or a
   setter retry. Restart restores the journal/manifest, but old refs must be
   re-bound and validated; their durability is not proven today. An
   unconfirmed result stays unknown. Cancel stops future batches, does not
   interrupt a running native call and performs no implied rollback.
6. **Finish:** report `applied/failed/conflict/unknown/not_attempted/no_op`,
   element and change counts and the final validation scope. Check global rules
   again at the end. Do not promise atomicity, a single Undo or automatic
   rollback of the whole job without separate API/build evidence.

The manifest/job store must survive plan-cache invalidation. Its versioning,
execution lock, integrity validation, limits and replay form a new contract
alongside the existing journal; do not rewrite old records to fit a larger
limit. Reserve capacity before starting a batch, including readback growth.
Archival keeps the replay guard and unresolved records per the current
procedure.

**The key optimization inside a batch:** a shared resolver for many exact
targets during preflight and an identity index for later lookup. First remove
redundant scans within one non-mutating callback. Reusing adapters after a
setter is not allowed without proof of correctness; readback must come from a
new read and still cover all required representations. A targeted UUID lookup
is a separate API spike, not an assumed feature. Optimizing the final audit
must not skip new hits, neighbour drift or preservation.

### Faster and more intuitive MCP tools

| Proposed change | Concrete benefit and condition |
| --- | --- |
| Shared status/capabilities | One light source for scope, limits, session, available operations and journal blockers. Separate code support, experimental Apply and native acceptance; never present flags as acceptance evidence. |
| Uniform responses | `state`, `summary`, `counts`, `coverage`, `blockers`, `next_action`, a detail reference and identifiers. Reuse the current `write_availability`; stale/expired/limit errors should return concrete next requests or an explicit absence of a safe action. |
| Shorter descriptions and ready examples | Keep intent, a correct minimal request and critical write rules in the tool description; expose the long reference as an MCP resource from the existing [tool reference](tool-reference.md). Examples: walls below a thickness, a missing attribute, a layer change, native material versus attribute. Do not require type UUIDs to be memorized; consider explicit family aliases with a disclosed mapping and no automatic scope widening. |
| Simpler edit path | For a known intent use the existing `model_edit.preview(predicate, changes)` → highlight → Apply. Separate query/summary/revalidate only when needed for a decision; Apply already revalidates. An optional prepare+highlight could later combine non-mutating stages while keeping the exact hash, review and explicit UI highlight effect. |
| Separate tool effects | Add correct MCP annotations and optional thin read/write facades over shared services. Do not mark the whole multi-action `model_edit` read-only/idempotent. Clarify the choice between `model_edit`, `column_layer`, `rule_based_edit` and presets without parallel implementations. |
| Timeout per operation | Classify `(endpoint, action)` and phase: preview/query read the model, highlight changes presentation, Apply may change the model. Distinguish `not_started` from a lost result and include the execution ID/recovery request. Never add automatic write retries. |
| Prepared execution request | Return a complete Apply template and a field for a durable execution ID; eventually the coordinator persists the ID and payload before sending. The agent should not rebuild hashes by hand or generate a new ID after an error. |
| Bounded, directed discovery | Reuse a concrete name↔ID/type binding keyed by project, with a fresh verify before writing. Keep probe phases and the durable trace after earlier crashes; do not combine broad discovery or continue to the next phase without assessing the result. Native selection stays unsupported; highlight is not a substitute. |
| Long jobs | If measurements justify it: job ID, status/progress and bounded polling, with cancel between batches. HTTP/MCP can answer quickly, but native work still runs only on the UI. An async wrapper alone does not stop a long native call from freezing the UI. |

### Order of work and closure criteria

These identifiers are the technical breakdown of the scaling task in the main
backlog. Reads, measurements and ergonomics can progress independently of the
open Beam/Slab work. Enabling larger writes depends on evidence for each
operation; it does not inherit acceptance of unverified native material.

| Stage | Scope / main files | Criterion and dependency |
| --- | --- | --- |
| S0 — measurements and contract, first | `transport.py`, query/edit/repair services, existing diagnostics. | Stage baseline and limit matrix; separate UI/API/JSON/IO times. No timeout increase before profiling. |
| S1 — ergonomics, small scope | `server.py`, public schemas, host contracts, `tool-reference.md`. | Every important state has a parseable next step, counts distinguish total/page, no unnecessary query before preview; public/host contracts agree and older clients work. |
| S2 — snapshot read/projections | `model_query.py`, `query_models.py`, `query_contracts.py`, cache. | More than 200 results without loss/duplication; snapshot mode does zero full scans on later pages, live keeps the stale guard. Byte, RAM and TTL limits tested. Do not yet claim support for >10000 adapters. |
| S3 — fewer scans and large reads | `model_edit.py`, `model_selection.py`, `native_model_edit.py`, native readers. | The highlight/preflight scan count drops with identical results and guards. An enumeration/revision/lookup spike decides further architecture; a larger scan budget only with UI and memory measurements. |
| S4 — manifest and batched execution | New coordinator/store plus `model_repair.py`, `repair_execution.py`, M4 contracts. | A job of >32 changes in one drawing, accounted partial/unknown, durable IDs, crash/restart without repeated setters, global invariants and a full final report. Depends on S0/S3 and acceptance of the operations. |
| S5 — multiple drawings, later | Scope/context resolver, file coordinator and activation. | A per-file manifest, detection of active-file changes, controlled switching/restoration of context and explicit omissions. An unloaded whole project needs separate enumeration and acceptance. |

Raising the page size alone can be considered as a performance setting after
S0 but does not replace S2/S3. Leave raising a single Apply above 32 for later:
it needs time, readback/recovery, journal size and Undo evidence for a specific
family. There is currently no justification for a universal new limit.

### Verification plan for a future implementation

**Measurement scenarios:** separately 200/201 and 1000 results;
1000/5000/10000/50000 raw adapters (50000 is a research target, currently
outside the contract); 1/32/33/100/1000 expanded changes. Vary representation
count, hit ratio, number of fields, geometry, hierarchy, one/many open files.
Measure cold/warm reads, preview, highlight, Apply/recover and a full agent
session. Keep the same inputs before and after optimization.

Record p50/p95 time, the longest UI block, the number of enumerations and
native reads, MCP/HTTP requests, response bytes/tokens, peak RAM/cache,
journal bytes/time and fsync count. Model the direct cost of K changes and the
effect of N adapters separately. A fake-host/Linux result does not replace
Windows/Allplan. Structural goals: one enumeration for many preflight targets
instead of K (if the spike allows), no full scan for a snapshot page, and a
fixed response limit independent of job size. Set time goals after the
baseline; do not write an unmeasured "10× faster".

Minimum regression tests for future changes:

- Public/host schema boundaries; 200/201 results, 32/33 changes; zero hits,
  no-op and incomplete distinguished. 201 results should already work through
  paging, and 33 changes in one Apply should be rejected.
- Repeating a cursor returns the same page of the same snapshot; the current
  live replay still revalidates the source first. Other selection/session,
  expiry, eviction, byte budget and complete paging without duplicates. Live
  mode detects a manual change/addition of a matching element; snapshot
  explicitly does not claim revalidation.
- Scan reduction does not change consensus, owner/view, ordering or
  fingerprints required by the contract; it does not hide rejected peers,
  missing or unknown.
- Failure before the journal, after write-ahead, after the setter/before
  readback, lost reply, restart, full disk, corrupt record, full trace; all
  executions have a durable identity and recovery runs no setters.
- Batches: external change/new match between batches, active file change,
  parent/child overlap, two changes of one owner, global numbering/uniqueness,
  cancel and unknown in the middle. Do not skip unfinished targets or add new
  ones without manifest review.
- MCP/HTTP: minimal requests and next_action schemas, correct timeout
  classification of read/presentation/write, compatibility with older clients
  and no suggested Apply retry. For ergonomics compare call counts, invalid
  requests and bytes for the same user tasks.

A native trial covers only the new larger scope and changed path: UI
responsiveness, exact targets, fresh readback, preservation and the real Undo
scope on a disposable fixture. Do not repeat accepted small writes to recreate
history. CI/delivery details are in the [testing policy](testing-policy.md).

**Verification of this analysis:** source review, diff and links only. No
runtime changes, benchmarks, product tests, builds or new native acceptance;
the current version's limits are unchanged.
