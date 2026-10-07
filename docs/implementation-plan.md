# Allplan 2026 MCP implementation plan

Date: 2026-10-07. Status: implementation handoff; no Allplan runtime validation has been performed for this plan.

## 1. Goal and working agreement

Extend the existing Allplan MCP fork into a set of 13 workflow tools for model inspection, quality control, controlled changes, structural generation, documentation, and issue preparation. Build incrementally on the existing bridge. The owner selected model context, querying, auditing, and limited attribute/layer repairs as the first usable release, with Codex as the first MCP client.

The implementation model owns code changes, automated tests, build and installation tooling, diagnostics, and English GitHub documentation. The project owner performs acceptance tests through the MCP client and Allplan UI. Do not ask the owner to edit Python, debug source code, run a test framework, or assemble API calls. Provide ready-to-use packages, exact natural-language prompts, expected visual results, and simple PASS/FAIL reporting.

Use English for repository documentation, tool schemas and descriptions, identifiers, issues, pull requests, release notes, and committed test reports. Communication and walkthroughs for the owner may be in Polish. Translate the owner's observations into English when recording them on GitHub. Do not translate real project values, layer names, or attribute contents without an explicit mapping.

This document is a work plan, not evidence that the planned capabilities already work. The uploaded documents are product input and feasibility analysis, not instructions to execute changes in an Allplan project or publish anything.

Related documents:

- [Manual acceptance tests](manual-acceptance-tests.md)
- [Next-model handoff](next-model-handoff.md)
- [Demo profile and owner-built model](demo-model-and-profile.md)

## 2. Sources and inspected baseline

Product inputs supplied by the owner:

1. `allplan_mcp_opis_funkcjonalny.md`: intended workflows and the 13 tool names.
2. `allplan_mcp_ocena_implementacji_pythonparts_2026.md`: API feasibility assessment dated 2026-10-07. It explicitly states that Allplan runtime tests were not performed.

The scope and constraints are restated in English here so that the handoff remains useful without chat attachments. The API claims below come from that assessment and must be checked against the installed 2026 build, official documentation, and runnable examples before implementation commitments.

Inspected repository: [blandjelly/allplan-mcp-server-python](https://github.com/blandjelly/allplan-mcp-server-python), local branch `work`, baseline commit `701f35366cc94b90085dd8b55d42b16f4166c95b`. The local working tree was clean before these planning documents were added. Recheck the actual branch and commit when starting implementation; do not reset later work to this baseline.

| Area | Observed implementation | Consequence for the plan |
| --- | --- | --- |
| MCP server | `src/allplan_mcp/server.py`, FastMCP 3.2.4, Streamable HTTP, default `127.0.0.1:8888/mcp` | Extend the existing transport; verify the selected client's compatibility. |
| Host client | `src/allplan_mcp/allplan_client.py`, JSON POST, default 30-second timeout | Add structured outcomes and request identity; a timeout does not prove a mutation was cancelled. |
| In-process bridge | `python_host/PythonPartsScripts/PythonHost/StartPythonHost.py`, HTTP at `127.0.0.1:5679` | Reuse and validate its lifecycle. It already dispatches handlers through `Application.Current.Dispatcher.Invoke`. |
| Current tools | `allplan_health`, `get_allplan_version`, `get_all_object_names`, `create_cube`, `create_box`, `execute_python` | These are baseline utilities, not implementations of the 13 planned workflows. |
| Current identity | Object enumeration returns display names only | Add stable model references before query results can drive changes. |
| Installation | `utils/register_python_host.py` copies `source_scripts.glob("*.py")` | It omits the existing `sandbox/` package imported by the handler. Repair and test fresh installation before feature work. |
| Shutdown | Cancel calls `server_close()`; a daemon thread runs `serve_forever()` | Investigate clean shutdown/restart and in-flight requests, including dispatcher deadlocks. Do not assume a runtime failure has already been demonstrated. |
| Execution documentation | README exposes `execute_python`; `docs/post-execution-exploration.md` recommends a gated development endpoint | Reconcile actual behavior and docs. Product workflows should use typed handlers with the same scope and mutation checks. |
| Validation infrastructure | No tracked test suite or CI workflow found at this baseline | Add meaningful portable tests and CI; keep Allplan integration evidence separate. |
| Distribution provenance | No tracked LICENSE file found at this baseline | Check the upstream source and applicable license before packaging for redistribution; do not invent a license. |

The external server requires Python >=3.11. Allplan's embedded Python and available packages are a separate runtime to inspect. Do not install FastMCP or assume external-server dependencies are available inside Allplan.

## 3. Decisions and outstanding inputs

### Confirmed by the owner

- Target application: Allplan 2026.
- Use an existing MCP fork as the project foundation.
- Maintain GitHub documentation in English.
- Owner testing is practical testing in Allplan, not code work.
- Deliver a work plan for a subsequent implementation model.
- First useful workflow: search, audit, and cleanup of native Allplan elements.
- First client: Codex. A later Claude integration is desirable; preserve client-neutral MCP contracts and verify Claude compatibility separately.
- The existing MCP bridge has not yet been tested by the owner.
- No office standard exists yet. The model prepares a demo profile; the owner builds the test model from a concrete UI recipe.
- The implementation model should detect the installed Allplan version itself when the local session is reachable.

### Implementation decisions and remaining discovery

| Decision | Confirmed choice or planning default | When it matters |
| --- | --- | --- |
| First user value | Confirmed: context → query → audit → previewed repairs | Sets the first feature milestone. |
| Repository identity | Use the inspected `blandjelly` checkout | Reconfirm remote/provenance in M0; a different intended fork changes the baseline review. |
| Supported deployment | Local Windows machine running Allplan, bridge, and MCP server | M0 client connection and packaging. A cloud client needs an explicitly designed connection; its localhost is a different machine. |
| Allplan build / UI language | Not observable in this planning session; detect through the local bridge and installed metadata | Required for runtime evidence and a supported-version statement. |
| MCP client / existing bridge status | Confirmed: Codex first; bridge untested | M0 must establish the first working connection. |
| Initial elements | Confirmed: native elements first; start with ordinary columns, beams, walls, and slabs | IFC-specific support is a later extension. |
| Profiles and test project | Confirmed: model provides demo profile, owner builds test model | See the accompanying profile and UI recipe; the owner does not edit profile JSON. |
| Documentation target | One controlled foundation documentation profile, one layout template | Confirm before M5/M6; PDF and DWG are planned, subject to runtime probes. |
| Connectivity / multi-user scope | One local session; no shared service or simultaneous writers in the first release | Avoid promising multi-user project coordination without tests. |

The owner answered the initial clarification questions on 2026-10-07; those answers are incorporated above. There are no unanswered product questions blocking M0. Exact build, client connectivity and local paths are discovery tasks. This planning session had a Linux workspace and no connected Allplan tools, so it could not inspect the owner's Windows installation. Repository defaults naming 2026 are not evidence of the installed hotfix. Start with the existing `get_allplan_version`; if its output omits build details, extend the diagnostic using verified installed-version metadata. Only request a simple UI observation if automatic discovery is unavailable.

Keep Codex-specific connection instructions separate from shared MCP schemas. Add a later Claude smoke-test batch covering discovery, structured results, preview/apply and errors; do not assume identical client configuration or resource support. No second business-logic implementation should be needed solely for another conforming MCP client.

Later, request only the information needed for the next vertical slice: representative element types, business meanings and office rules, project size, layout/title-block sample, export settings, and model-update expectations. Discover API identifiers yourself and offer prepared mappings/defaults the owner can assess visually.

### Scope limits for the initial releases

- Operate on explicit, currently accessible drawing files. Report unloaded, omitted, and read-only files; do not label a current-document scan a whole-project scan.
- Use configured floor, level, grid, and drawing-file mappings until equivalent 2026 API behavior is demonstrated.
- Do not promise arbitrary element-property editing, native revision-table management, or complete interpretation of existing third-party documentation.
- Generate dimensions and foundations from explicit design parameters and rules. Structural and geotechnical sizing is outside this implementation scope.
- Prefer native supported components. Generic solids are a separately labeled fallback only where the agreed workflow permits them.
- Do not introduce 2027-only APIs, including unverified BuildingStructure services or ReportService, into the 2026 support claim.

## 4. Architecture and shared contracts

Keep this boundary:

```text
MCP client
  -> existing FastMCP server: typed public workflow tools
  -> portable services: queries, rules, change planning, profiles, reports
  -> versioned JSON bridge requests
  -> existing Allplan host: lifecycle + dispatch in a valid UI/API context
  -> adapters for confirmed Allplan 2026 operations
  -> JSON snapshots and observed outcomes
```

All `NemAll_*` imports, live documents, element adapters, and Allplan writes stay inside the host. Pure rule/planning code must be testable without Allplan. Exchange JSON data, not adapter objects or `repr()` strings pretending to be stable references.

Suggested organization, to be introduced only as needed:

- `src/allplan_mcp/server.py`: tool registration; avoid accumulating business logic here.
- `src/allplan_mcp/contracts/`, `services/`, `profiles/`: versioned schemas, deterministic logic, profile validation.
- `python_host/PythonPartsScripts/PythonHost/handlers/`, `adapters/`: narrow host routes and Allplan-specific code.
- `profiles/`: versioned example office, structure, documentation, and export profiles, packaged for end users.
- `tests/`: portable contracts, rules, transport behavior, installation, and release packaging.
- `docs/`: user setup, tool contracts, support matrix, decisions, acceptance evidence, release notes.

Choose a simple versioned JSON profile format initially unless the fork provides a better established convention. Validate dependencies and installation on both runtimes before sharing code between them. Use portable JSON schemas or small shared dependency-free definitions if necessary.

### Required common data

| Contract | Required meaning |
| --- | --- |
| `ModelContext` | Session/project identity, installed build, active file, explicit file states, units, offset, available levels, capabilities, omissions and unresolved data. |
| `Scope` | Explicit file IDs and/or model references, filters, read/write eligibility, visibility policy, and completeness. No implicit whole-project writes. |
| `ElementRef` | Project/session binding, drawing-file identity, `GetModelElementUUID()` where supported, element type. View UUIDs are separate. Re-resolve before writes. |
| `ElementSnapshot` | Typed attribute IDs and values, layer ID, available native properties, normalized geometry summaries, and the fields used for stale-state checks. |
| `SelectionResult` | Reusable selection ID, scope, snapshot identity, counts, paginated elements, and omissions. A limited page must not silently become the full edit target. |
| `AuditReport` | Rule ID, severity, element references, evidence, proposed remedy, coverage, and distinct `pass`, `fail`, `not_checked`, and `not_applicable` states. |
| `ChangePlan` | Exact targets, old/new values, operation types, exclusions, source fingerprints, profile version, expiration/session binding, and plan hash. |
| `ExecutionResult` | Request ID, per-target applied/skipped/conflict/failed/unknown outcomes, readback, changed references, and actual undo/recovery limits. |
| `PackageRegistry` | Package and generation keys, owned element roles, source fingerprints, allocated files/layouts, issue metadata, output paths and hashes. |

Normalize geometry to explicit canonical units (proposed millimetres and degrees) at the boundary and document conversions. Preserve user-facing input units. Apply the project offset exactly once. Distinguish logical visibility from screen inclusion and occlusion.

For a negative drawing-file number returned for a passive file, preserve its state separately from normalized file identity. Do not use names as unique IDs. Do not treat `GetTimeStamp()` as a universal modification counter; fingerprint the source fields relevant to a query, edit, or generated package.

### Mutation lifecycle

Implement one shared lifecycle for repairs, standards, rule-based edits, generators, and documentation changes:

1. Resolve an explicit scope and supported operations.
2. Produce a side-effect-free `preview` showing targets, changes, exclusions, and expected counts. A visual preview must not persist model changes.
3. Bind an `apply` request to the reviewed plan ID/hash and the user's current authorization. Existing explicit authorization can cover the concrete operation; avoid repeated generic confirmation prompts.
4. Re-read identity, file writability, and relevant source fields immediately before writing. Reject stale plans or report conflicts according to a documented policy.
5. Execute in the valid Allplan context, serializing mutations. Group operations only where runtime-tested undo behavior permits it.
6. Read back the actual result. A successful API return is not sufficient evidence of a property change.
7. Record per-target outcomes and invalidate affected cached selections/plans.

Use the existing 13 tool names with shared preview/apply conventions; common infrastructure need not inflate the public catalog. Define request status/recovery behavior before releasing mutating tools. A repeated request ID must not repeat an already applied operation. A network timeout may leave the execution status unknown: reconcile before retrying, including after host restart. Test durable records or provide a clearly documented recovery path where exactly-once behavior cannot be guaranteed.

Do not promise an atomic transaction spanning multiple drawing files, Allplan undo, the local registry, and exported files. On partial failure, report completed work and a recovery path. Store the registry outside Allplan's undocumented internal files, keyed to a verified project identity; specify backup, persistence, migration, project-copy, and undo reconciliation behavior. Registry presence alone is not proof that an element still exists.

Retain the local connection model. Treat the existing `execute_python` path as a separate development capability; it must not bypass the scope and plan checks advertised for production workflows. Audit its actual behavior rather than assuming AST filtering establishes an isolation boundary.

## 5. Coverage of all 13 tools

The first implementation of each tool is intentionally bounded. Extending its scope requires additional evidence in the capability matrix.

| Tool | First deliverable | Dependencies / milestone | Deferred or conditional scope |
| --- | --- | --- | --- |
| `get_model_context` | Current project/session, file states, units, offset, available levels, capabilities and missing data | M0 → M1 | Complete BWS, closed project data, automatic floor names. |
| `model_query` | Type, drawing file, layer, attribute predicates, supported dimensions and explicit spatial box; reusable paginated result | M1 | Arbitrary native grids and complex spatial relationships; define containment/intersection semantics first. |
| `model_audit` | Required fields, allowed values, layer checks, scoped duplicate marks and simple dimensional rules | M1 → M2 | Rules whose inputs are unavailable remain `not_checked`. |
| `fix_model_issues` | Selected audit findings → preview → supported attribute/layer changes → readback and re-audit | M2 → M3 | Native material semantics, graphical labels and component-property repairs need separate adapters. |
| `apply_office_standard` | Versioned profile reusing audit and repair services for attributes, marks, layers and defined numbering | M3 | Moving/copying between files only after relation/undo probes; full BWS restructuring deferred. |
| `generate_structural_frame` | Rectangular explicit grid, elevations, profile sections/materials, omissions; native columns/beams first | M3 infrastructure → M4 | Arbitrary native grid extraction, complex bracing and destructive regeneration. Choose component family according to editing needs. |
| `generate_foundations_from_structure` | Rule-sized native pads below selected base columns; later strips below selected straight walls | M1 + M3 infrastructure → M4 | General support inference, stepped/combined foundations, design calculations. |
| `generate_coordination_openings` | Supported straight pipe/duct crossings of native vertical walls and horizontal slabs, clearance, host link and repeat detection | Early spike; delivery M7 | Arbitrary imports, oblique crossings, layered walls and merging require explicit follow-up evidence. |
| `rule_based_edit` | Query result → attribute/layer edits; later proven native column/beam/wall properties with exceptions | M1 + M3; native properties M4 | No universal setters or implicit conversion from Structural Framing to ordinary components. |
| `create_documentation_package` | One controlled foundation profile: plan, two sections, role-based labels/dimensions and own schedule | M1 + M3 infrastructure + M5 probes → M6 | Arbitrary complete drawing sets, standard report automation, automatic preservation of every manual adjustment. |
| `documentation_audit` | Registry/profile coverage, required views/scales/dimension roles, source freshness and known title-block fields | Limited M5; managed-package scope M6 | Semantic completeness of arbitrary existing drawings; report coverage instead. |
| `populate_layouts` | Prepared drawing files/crops on specified layouts using one template, margins, scales and deterministic overflow | M3 infrastructure → M5 | Safe rearrangement of arbitrary existing layouts and automatic discovery of all sheet metadata. |
| `prepare_issue_package` | Explicit layouts, profile audit, plugin revision/date/description, PDF/DWG export and manifest | M5 | Native revision history and arbitrary title-block updates remain conditional. Files are prepared locally; sending them is outside the tool. |

A limited existing-layout export path can provide value before the full documentation generator. Its audit must explicitly distinguish manually supplied sheet metadata, verified metadata, and uncheckable criteria. Do not market it as complete automatic drawing approval.

## 6. Milestones, tasks and exit gates

Each milestone should be delivered in small reviewable PRs. Use task IDs below in issues, PRs, acceptance cards, and progress records. Dependency gates represent required evidence, not a claim about fixed development dates.

### M0 — Reproducible installation and bridge baseline

**Completed 2026-10-07:** M0.1–M0.5; UAT-00/UAT-01 PASS on Allplan 2026-1-7,
package 0.1.2. [Acceptance record](test-results/m0-acceptance-0.1.2.md).

**Tasks**

- **M0.1** Recheck fork/upstream provenance, exact baseline, applicable license, existing edits, and client/Windows/Allplan environment. Record external and embedded Python versions separately.
- **M0.2** Fix recursive bridge registration, preserving subpackages and excluding caches. Support the actual Allplan user path, clean install, repeat install, version identification, and restoration of the previous package. Add a temporary-directory installation test that detects the missing `sandbox/` case.
- **M0.3** Verify health, version, names and one existing box operation through the selected MCP client. Improve error categories for host absent, incompatible build, invalid payload, and unavailable session. Reconcile setup/execution docs with actual behavior.
- **M0.4** Investigate start, ESC/cancel, restart, minimize/restore, project switching and in-flight request lifecycle. Preserve UI-thread dispatch; shutdown must not block the UI waiting on a worker that is itself waiting on the dispatcher.
- **M0.5** Add a reproducible end-user package and launcher; run portable CI for changed behavior. Prepare a no-code installation walkthrough and diagnostic bundle containing versions and request IDs.

**Owner delivery:** versioned package, illustrated or precise UI setup steps, selected-client configuration supplied by the model, tests UAT-00 and UAT-01.

**Exit gate:** a clean Windows installation starts the bridge, the selected MCP client reaches the correct Allplan session, a known-sized box appears, and cancellation/restart has a recorded result. Failure to establish this blocks claims of integrated tool readiness, not portable development.

### M1 — Context, identity, selection and query

**Current 0.3.0 slice:** explicit scopes, typed type/layer/raw-attribute queries,
bounded session selections, paging/summary and staleness are implemented with
targeted portable checks. Allplan query verification remains pending; geometry,
offset, native hierarchy and demo binding are not complete. See
[current status](project-status.md) and [contracts](tool-reference.md).

- **M1.1** Implement `ModelContext`, `Scope`, model references, capability reporting, units and offset conversion. Probe loaded editable/passive files and model versus view identity.
- **M1.2** Implement `get_model_context` and basic `model_query`; define predicate composition, null/missing behavior, case rules, numeric tolerances, and spatial selection semantics.
- **M1.3** Add pagination, reusable selections, explicit completeness and stale-selection behavior; restrict scans to the requested fields and scope.
- **M1.4** Bind and validate the provided demo profile, then give the owner a finalized UI recipe with known counts. The owner creates the model. Any diagnostic/setup code is prepared by the model and packaged; the owner does not edit it.

**Exit gate:** UAT-02 and UAT-03 return the expected elements/counts, units, file states and omissions without changing the model. Portable tests cover conversions, filters, pagination and identity handling.

### M2 — Model audit and profile foundations

- **M2.1** Define a schema-versioned office profile with attribute IDs/types, expected values, layers, mark uniqueness scope and numeric tolerances. Validate that referenced resources exist.
- **M2.2** Implement `model_audit`, severity, evidence, `not_checked`, and machine-readable plus readable reports.
- **M2.3** Link findings to identifiable elements; provide a supported selection/highlight action when feasible, otherwise stable marks/file references for visual inspection. Do not make preview highlighting a hidden model edit.

**Exit gate:** UAT-04 finds deliberately introduced defects, avoids false duplicate errors outside the configured scope, and reports unavailable data without calling it a pass. The owner can locate the affected elements.

### M3 — Controlled repairs and standardization: selected MVP

- **M3.1** Implement common preview/apply plans, stale-state checks, serialized writes, request IDs, readback, partial outcomes and tested undo boundaries.
- **M3.2** Implement `fix_model_issues` for writable attributes and layers. A design mark stored as data and a visible graphical label are different operations.
- **M3.3** Implement `apply_office_standard` and attribute/layer `rule_based_edit` through the same services. Avoid independent, inconsistent mutation paths.
- **M3.4** Add managed-registry persistence and reconciliation where required. Prove duplicate prevention for retried writes and record unknown outcomes after connection loss.

**Exit gate:** UAT-05 and UAT-06 pass; preview is unchanged, only authorized in-scope targets change, manual edits invalidate stale plans, read-only files stay untouched, repeated apply does not repeat changes, and re-audit reflects the actual model. Document what Undo does for this exact release.

**MVP release:** M0–M3 plus installation/update instructions, portable CI, documented support matrix and owner acceptance evidence. Tools awaiting runtime testing remain labeled accordingly.

### M4 — Proven native edits, frames and foundations

- **M4.1** Probe ordinary columns/beams, Structural Framing and single-/multi-layer wall material behavior. Record `type × property × read/create/update` support by Allplan build. A setter or text attribute change is insufficient proof of geometric/native-property editing.
- **M4.2** Extend `rule_based_edit` only for confirmed combinations, including preservation of dependent data and exception targets.
- **M4.3** Implement explicit-grid `generate_structural_frame` with native ordinary columns/beams initially if editing is required and runtime-supported. Add Structural Framing/bracing only through documented capability choices. Persist generation keys; never silently delete/recreate hand-edited elements.
- **M4.4** Implement `generate_foundations_from_structure` for selected base columns, then straight-wall strips. Dimensions and bearing elevations come from a profile. Handle an existing generated foundation as an update/no-op/conflict, not a duplicate.

**Exit gate:** UAT-07–UAT-09 confirm native element types, counts, locations, cross-sections, levels, exceptions, repeat behavior and source links. Unsupported operations fail clearly with no misleading success.

### M5 — Prepared layouts, export and limited issue audit

- **M5.1** Probe layout insertion, paper scale/crop/margins, title block, PDF and DWG on one controlled sheet. Investigate native revisions separately; own metadata is the initial supported route.
- **M5.2** Implement `populate_layouts` for prepared files with template-reserved areas, layout-number allocation, explicit occupied-sheet policy and deterministic overflow. Model-space dimensions must be converted to paper dimensions.
- **M5.3** Implement limited `documentation_audit` for known layout/profile requirements. Uncheckable critical requirements block an automated readiness claim; allow documented manual review evidence where the agreed profile requires it.
- **M5.4** Implement `prepare_issue_package`: explicit sheet set, supplied revision/date/description, preflight, controlled metadata update, export to a new issue directory, file verification and manifest with hashes. Preserve existing issues by default; mark partial export failure, never claim a complete issue from a subset of files.

**Exit gate:** UAT-10 and UAT-12 confirm sheet contents, scale, template fields, exact output list and manifest. A PDF/DWG opens and matches the intended layout. A known critical audit failure blocks issuance. Exported files have an explicit recovery policy separate from model Undo.

This milestone can be prioritized after M3 if the owner values existing-sheet export more than generation; it does not require all M4 functionality.

### M6 — One managed documentation workflow

- **M6.1** Probe UVS creation/update with labels/dimensions and a controlled source change. Use `ViewSectionElement` / `CreateSectionsAndViews()` rather than building on legacy Associative View classes.
- **M6.2** Implement a foundation profile with one plan, two specified sections, dimension chains, marks and an own schedule. Document exactly which dimensions and quantities are checked.
- **M6.3** Store generated roles and source dependencies; extend `documentation_audit` to detect missing/stale content. Define preservation rules for manual label/layout changes. Where preservation is unsupported, report a conflict before regeneration.
- **M6.4** Compose the package with M5 layout and export services, avoiding duplicate numbering and duplicate generated content.

**Exit gate:** UAT-11 passes for initial generation, re-run and a source change; specified missing dimension roles are detected. Manual adjustments are preserved or explicitly surfaced for a decision. The result is ready for designer review within the declared profile.

### M7 — Coordination openings and later extensions

- **M7.1** Run an early feasibility spike once M1 provides reliable references: one pipe through a wall, one through a slab, host relationship and repeat prevention. Keep the spike separate from production availability.
- **M7.2** Implement `generate_coordination_openings` for the proven types with broad-phase candidates followed by actual geometric intersection, size/clearance rules, host references, source links and edge/support exceptions.
- **M7.3** Extend only from observed demand: imported geometry, oblique crossings, merged openings, broader native edits, additional documentation profiles and existing-document audit.
- **M7.4** Revisit native revision history, building structure access, and drawing-file moves only with 2026 evidence and dedicated acceptance cases.

**Exit gate:** UAT-13 confirms actual openings in the correct hosts, intended clearances, no duplicate on re-run, and clear reporting of unsupported/ambiguous cases. DN is not used as a substitute for actual outer geometry or insulation dimensions.

## 7. Feasibility probes and decision rules

Run the cheap, high-impact probes early enough to avoid choosing an unusable design. Each produces a small adapter experiment prepared by the model and an owner-facing test card; the owner does not write probe code.

| Probe | Earliest gate | Evidence and decision |
| --- | --- | --- |
| Installation and bridge lifecycle | M0 | Fresh install, active session, cancellation/restart, dispatcher context. Failure prevents integrated release. |
| File states, identity, offset and units | M1 | Same model element in several representations; passive-file behavior; known geometry under offset. Constrains all later scopes. |
| Ordinary vs Structural Framing edits | Before M4 design choice | Actual property/geometry readback, dependencies and undo. Choose supported native family or report unsupported update. |
| Native wall materials | Before native material repairs | Single-/multi-layer property agreement, not just text. Restrict unsupported cases. |
| Layout and PDF/DWG | After M1, before committing M5 scope | Two prepared files on one template, scale/crop/output and title-block behavior. Existing sheets may be the first export route. |
| UVS update and manual adjustment | Before M6 commitment | Source change propagation, dependency validity, moved labels and dimensions. Creation-only scope if update is unproven. |
| Host-linked openings | After M1 | Actual wall/slab modification, geometry and stable repeat detection. Stop at a feasibility result if host support fails. |
| Multi-file changes and undo | Before widening mutation scope | Partial failure, references and rollback boundaries. Keep single-file writes if necessary. |
| Native revisions and third-party title blocks | Before promising those features | Exact readable/writable fields on actual templates. Own issue registry remains a distinct capability. |

Capability evidence states: `proposed`, `documented_2026`, `prototype_verified`, `implemented`, `runtime_verified`, `unsupported`. Record support per operation and build; a broad tool name must not hide unsupported sub-operations. An implemented feature can still be awaiting runtime verification.

## 8. Testing and release responsibilities

### Model-owned automated checks

- Pure logic: query semantics, unit/offset conversion, tolerances, rule outcomes, numbering, geometric placement arithmetic, layout packing and manifests.
- Contract/transport: schema compatibility, malformed responses, timeouts, error mapping, plan validity, request deduplication, partial failures and unknown outcomes.
- Installation/distribution: recursive file inclusion, profiles/resources present, repeat install, upgrade/restore and launch configuration. Keep installed Allplan paths configurable.
- Fake-adapter integration: orchestration and readback decisions without importing `NemAll_*` in ordinary CI.
- Host integration: prepared scripts or self-check commands running inside a real Allplan session. Record the actual build and capability tested.

Mock tests and successful imports on Linux do not validate Allplan behavior. Do not claim to have tested Allplan if only portable CI ran. Make integration checks available through a diagnostic action or prepared package so the owner's task remains UI-based observation.

### Owner-owned acceptance

For every test batch, provide: package/release ID, full Allplan build, test model/reset procedure, a small number of concrete prompts, expected counts/values/visible outcomes, recovery steps, and a copyable result form. Use [manual-acceptance-tests.md](manual-acceptance-tests.md) as the catalog. Run only relevant cards; do not burden the owner with the full catalog after every small change.

The owner reports PASS, FAIL or BLOCKED and a short observation, optionally with a screenshot. The model collects available diagnostics, reproduces or narrows the cause, adds a meaningful regression test where appropriate, and returns a fixed package plus the smallest useful retest batch.

### Definition of done for a released capability

1. The bounded tool contract, supported types and omissions are documented in English.
2. Applicable portable checks pass, including observed regression paths.
3. A versioned package can be installed without code editing and includes an update/restore path.
4. Required Allplan integration and owner acceptance evidence is linked to the tested build and package.
5. Preview, scope, readback, retry behavior and recovery are verified for mutating capabilities.
6. Support matrix, known limitations, changelog and current handoff are updated.

Use `ready_for_owner_test` before runtime acceptance and `accepted_on_build` only with evidence. If the owner is unavailable, continue independent work and mark the affected gate pending; never fabricate acceptance.

## 9. English GitHub documentation and issue workflow

Create the following as implementation produces real content; avoid empty documentation scaffolding:

| File / area | Purpose |
| --- | --- |
| `README.md` | Product scope, verified support, setup entry point, first successful workflow. |
| `docs/installation.md` | Windows/client setup, install/update/restore, start/stop, diagnostic bundle. |
| `docs/architecture.md` | Runtime boundary, dispatch, transport/schema versioning, persistence. |
| `docs/tool-reference.md` | Inputs, outputs, scope, preview/apply, errors and examples for implemented tools. |
| `docs/capability-matrix.md` | Tool/type/property/build support and evidence links. |
| `docs/testing.md` | Model-owned CI and in-Allplan checks; owner acceptance process. |
| `docs/test-results/` | Sanitized English acceptance records with package and Allplan build. |
| `docs/decisions/` | Component-family choice, units/identity, lifecycle, registry, scope and layout decisions. |
| `docs/project-status.md` | Completed IDs, evidence, open blockers, owner decisions, next concrete task. |
| `CHANGELOG.md` | User-visible changes, compatibility, migrations and known limits. |
| `.github/ISSUE_TEMPLATE/` | Feature tasks and no-code bug/acceptance reporting. |

Issue template: user outcome, task ID, in/out scope, dependencies, implementation deliverables, portable checks, Allplan acceptance card, unresolved evidence and completion conditions. PR descriptions should explain the user-visible change, applicable automated validation, runtime evidence or pending tests, and installation implications.

Use small PRs that deliver one reviewable behavior. Suggested initial PR sequence:

1. M0.2: recursive installation and packaging regression test.
2. M0.3–M0.4: bridge diagnostics and lifecycle fixes supported by probes.
3. M1.1: contracts, context and capability reporting.
4. M1.2–M1.4: query, selections and demo fixture.
5. M2: audit profiles and report.
6. M3.1–M3.2: common change plans and first repair.
7. M3.3–M3.4: standards, attribute/layer rule edits and recovery.

Break these down further when the diff is too large. Repository collaboration, pushing and PR publication should follow the owner's working arrangement. This planning deliverable itself does not create remote issues or change the deployed bridge.

## 10. Risk handling and planning horizon

| Uncertainty | Practical response |
| --- | --- |
| Documentation support differs from installed behavior | Probe, read back, record build-specific evidence and narrow the contract. |
| Bridge installation/lifecycle fails | Resolve M0 before asking the owner to validate feature behavior. |
| Lost response after a write | Reconcile request and model state; prevent blind replay. |
| Large model blocks UI or exhausts response size | Explicit scopes, paging, bounded work, measured batch limits and cancellation at supported safe points. |
| Imported objects lack native properties | Return capability limits; do not pretend attribute edits change native geometry. |
| Regeneration overwrites manual work | Ownership/source fingerprints and explicit conflict handling. |
| Exports or registry diverge from model after Undo | Reconciliation and separate recovery records; no cross-system atomicity claim. |
| No established office standard | A versioned demo profile with clear labels, then owner-reviewed mappings. |

Plan by accepted vertical slices, not by an unverified promise to finish all 13 tools on a calendar date. M0 and the first runtime batch determine installation/lifecycle effort. M1–M3 define the first release. Estimate M4–M7 after their probes, documenting assumptions about test turnaround and model size. Documentation generation and arbitrary existing-document handling carry the largest uncertainty.

## 11. Reference starting points

These are source-assessment references, not claims of independent runtime validation:

- [Allplan 2026 supported elements](https://pythonparts.allplan.com/2026/manual/features/allplan_elements/)
- [Read access](https://pythonparts.allplan.com/2026/manual/features/model_access/read_access/)
- [Element modification](https://pythonparts.allplan.com/2026/manual/features/model_access/element_modification/)
- [Element attributes](https://pythonparts.allplan.com/2026/manual/features/attributes/element_attributes/)
- [Interactor PythonPart](https://pythonparts.allplan.com/2026/manual/key_components/script/interactor_pythonpart/)
- [LayoutFileService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/LayoutFileService/)
- [ViewSectionElement](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BasisElements/ViewSectionElement/)
- [UndoRedoService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/UndoRedoService/)
- [2026 release notes](https://pythonparts.allplan.com/2026/release_notes/)

Verify exact signatures and samples in the 2026 documentation and installed SDK. Keep documentation research separate from proof that a workflow succeeds on the owner's model.
