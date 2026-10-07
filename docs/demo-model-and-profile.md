# Demo profile and owner-built model

This example supports the agreed first release: searching, auditing and cleaning up native Allplan elements through Codex. It is a test standard, not an engineering or production office standard.

The owner will build the model in Allplan. The implementation model will prepare the runnable tools, bind the profile to real Allplan identifiers, and provide UI instructions in Polish when helpful. The owner should not edit JSON or source files.

Profile: [native-model-qa.demo.json](../profiles/examples/native-model-qa.demo.json).

## Status and binding responsibility

The JSON file is a concrete draft of the intended rules and expected results. The current server does not load this profile. Its schema is proposed, and attribute, layer and native-type identifiers are intentionally `null` because the installed Allplan build and project resources have not been inspected. An implementation must reject this unbound profile rather than guess identifiers or silently omit rules.

During M0/M1, the implementation model must:

1. Read the exact installed Allplan version/build and available type/attribute metadata through prepared diagnostics.
2. Select actual writable text attributes for `mark` and demo `status`, preserving their actual API IDs and data types. A display name alone is not a binding. If project attributes must be added, supply a supported setup action or exact UI steps.
3. Resolve or help the owner create the two demo layers and record their IDs. Choose free drawing-file numbers; 101–103 below are reserved examples, not permission to overwrite existing contents.
4. Validate the proposed schema and update it consistently with the implementation. Record a bound profile version and supported build.
5. Give the owner the exact localized property-field names and a short checklist for constructing the model. Do not ask the owner to research API IDs.
6. Use read-only inspection to verify the built fixture; record actual model UUIDs by fixture label and drawing file in a test-run manifest.

## Model construction recipe

Create a disposable project named `MCP_QA_DEMO` or use an isolated copy. Reserve three empty drawing files:

| File | Intended state for the first tests | Role |
| --- | --- | --- |
| 101 | Active/editable | Ground-floor QA fixture. |
| 102 | Loaded in passive/read-only mode | Scope and write-restriction check. |
| 103 | Not loaded | Omitted-scope check. |

Use millimetres for the recipe and zero project offset initially. Keep relevant layers visible. Later tests add non-zero offset and different display units to the same known geometry.

Create six **ordinary native columns**, each 400 × 400 mm and 3000 mm high, bottom elevation 0 mm. Use the same insertion reference (the column center) for all coordinates. Set their native material consistently, for example `C30/37`, as a sample supplied value; native material normalization is outside these initial four QA rules.

`C01`–`C06` below are fixture labels used to identify locations in the recipe; they are not a second attribute the owner must add. `mark` and `status` refer to the real UI fields selected by the implementation model during binding.

| Fixture label | Center X / Y (mm) | Mark | Layer | Demo status | Deliberate defect |
| --- | --- | --- | --- | --- | --- |
| C01 | 0 / 0 | S01 | MCP_QA_STRUCTURE | NEW | None. |
| C02 | 6000 / 0 | S02 | MCP_QA_STRUCTURE | NEW | Shares a mark with C04. |
| C03 | 12000 / 0 | Empty | MCP_QA_STRUCTURE | NEW | Missing mark. |
| C04 | 0 / 6000 | S02 | MCP_QA_STRUCTURE | NEW | Shares a mark with C02. |
| C05 | 6000 / 6000 | S05 | MCP_QA_REVIEW | NEW | Wrong layer. |
| C06 | 12000 / 6000 | S06 | MCP_QA_STRUCTURE | NWE | Misspelled demo status. |

Also create in file 101:

- Two ordinary native beams, each 300 × 500 mm, spanning C01–C02 and C02–C03 at the same documented elevation.
- One single-layer native wall, 200 mm thick, 4000 mm long and 3000 mm high, away from the columns so its later tests are easy to inspect.
- One native slab, 4000 × 4000 mm and 200 mm thick, away from other elements.

This gives **10 intended top-level model components in file 101: 6 columns + 2 beams + 1 wall + 1 slab**. The query must define model-component counting and avoid double-counting representations or children. Raw adapter enumeration can differ; record that distinction rather than adjusting the expected fixture silently. The demo audit applies only to the six ordinary columns in file 101.

Create one further ordinary column in file 102, marked `S02`, and one in file 103. These are outside the audit's uniqueness scope. After creation, restore the passive/unloaded states from the table. Scanning file 101 must not report their marks as duplicates in file 101. An explicitly requested loaded-files scan should state whether file 102 was successfully read; it must report file 103 as outside its coverage.

Save a clean copy before running repairs. Keep a screenshot of the six-column arrangement and the initial properties as the baseline.

## Rules and exact expected audit

| Rule | Meaning | Expected findings |
| --- | --- | --- |
| QA-001 | Every selected column has a non-empty mark. | C03: 1 finding. |
| QA-002 | Non-empty marks are unique within drawing file and element family. | C02 and C04: 2 findings in 1 duplicate group. |
| QA-003 | Selected columns use MCP_QA_STRUCTURE. | C05: 1 finding. |
| QA-004 | Demo status is NEW or EXISTING. | C06: 1 finding. |

Expected result: **5 findings affecting 5 columns**. C01 passes. Missing marks are ignored by the duplicate rule, so C03 is not double-counted. The passive/unloaded columns do not affect this audit.

For this bound and readable fixture, all four rules should be checkable. If bindings or data are unavailable, return `not_checked` with the reason and mark the test blocked; do not report the expected count as though it was observed.

## First repair batch

The first preview should propose exactly two deterministic repairs:

1. C05: layer `MCP_QA_REVIEW` → `MCP_QA_STRUCTURE`.
2. C06: demo status `NWE` → `NEW`, using the explicit mapping in the profile.

It should leave marks unchanged and explain the missing/duplicate values. After the owner applies this exact plan, the expected audit has **3 remaining findings**: missing mark on C03, duplicate-mark findings on C02 and C04. Applying the same request again must not repeat the operation.

A later explicit mark-repair test can assign C03 = `S03` and C04 = `S04` after preview and authorization. Then all four rules pass with zero findings. These assignments are a test choice, not an inferred office numbering standard.

## Suggested first Codex prompts

The implementation model supplies these in Polish for the owner, with the actual bound profile/version and reserved file numbers inserted:

1. “Read the current Allplan context and report the exact version, units and drawing-file states. Do not change the model.”
2. “Find ordinary native columns in drawing file 101. Return their marks, layers and demo statuses.”
3. “Audit those columns with the native-model-qa-demo profile. Show every finding and anything that could not be checked.”
4. “Preview the profile's deterministic layer and status repairs. Leave marks unchanged.”
5. “Apply the reviewed plan to those two columns and audit the same scope again.”

Prompts express the intended workflow; the implementation model must verify actual tool calls and returned evidence. An assistant's description of a change alone is not acceptance evidence.

## Later fixture extensions

Add these only when the relevant milestone is ready: ordinary/Structural Framing comparison; multi-layer wall; a 2-by-2 grid generation area; base-column foundations; prepared drawing files and one layout; managed UVS sections/dimensions; pipe and duct crossings through supported native hosts.

No IFC fixture is required for the first accepted release. Add imported-model examples as a separately scoped extension.
