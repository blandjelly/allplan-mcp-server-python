# Manual acceptance tests in Allplan

Status: test catalog; no cases were executed while initially preparing the plan.
Subsequent M0 UAT-00/UAT-01 and bounded M1 UAT-02/UAT-03 are accepted on the
owner setup. [M1 acceptance and limits](test-results/m1-acceptance-0.5.3.md).
UAT-04 onward remain NOT_RUN. Do not repeat accepted batches without a relevant
change/defect; run new cards only when a working release is supplied.

The owner interacts with Codex and the Allplan UI. The model supplies installation packages, actual MCP commands behind the prompts, diagnostics and fixes. No source editing, API research, terminal debugging or test-framework operation is assigned to the owner.

Use [the demo model and profile](demo-model-and-profile.md) for the first batch. English is the repository record language; the model can provide a Polish walkthrough and translate results back into English.

## Before every batch

The model fills in the package version, detected Allplan build, Codex configuration, bound profile version, model backup/reset procedure and exact prompts. Include only the relevant cards, usually a small batch. Keep actual request IDs and diagnostic details automatically where possible.

Run mutating tests in the disposable project or its copy. Restore the stated baseline between cases that depend on initial defects. A changed fixture is not a tool regression; confirm the precondition first.

## UAT-00 — First installation and Codex connection

**Milestone:** M0.

**Setup:** Allplan 2026 installed on the owner's Windows machine; a test project is open. The model supplies a versioned package and Codex connection setup. The owner has not previously validated this bridge.

**Actions:** Follow the prepared installer/launcher steps, start `StartPythonHost` in the Library palette, and ask Codex to check the connection and read the Allplan version.

**Expected:** The package installs all bridge subpackages, Codex discovers the intended tools, and health/version results identify the running application. Record the full build/hotfix and both runtime versions automatically where accessible. A major-version-only string must not be described as a full build. A deliberately stopped host gives a readable connection error and restart instruction.

**Evidence:** Package/build values, observed connection result, optional screenshot. The model records diagnostics; the owner does not inspect import stack traces.

## UAT-01 — Existing geometry operation and host lifecycle

**Milestone:** M0.

**Actions:** In an empty test area, use the existing box tool to create one 1000 × 1000 × 1000 mm box. Inspect its dimensions in Allplan. Cancel the host with ESC, restart it, then repeat a read-only request. Test minimize/restore and a project switch using the prepared instructions.

**Expected:** Exactly one correctly sized box appears. Cancel/restart releases and reopens the connection cleanly. The tools report the current session rather than using a stale document. If a normal Allplan command ends the interactor, the package explains the actual restart procedure. No UI freeze or duplicate box occurs.

**Reset:** Delete the test box through ordinary Allplan UI or restore the test copy. In-flight cancellation edge cases are exercised by model-prepared diagnostics, not by asking the owner to engineer a race condition.

## UAT-02 — Context, drawing-file states, units and offset

**Milestone:** M1.

**Setup:** Files 101 active/editable, 102 passive, 103 unloaded, using the fixture recipe.

**Actions:** Ask for project, files/states, levels, units and offset. Change display units through the UI and repeat. In a separate copy, use a known non-zero offset and repeat a prepared position query.

**Expected:** File states and omissions match Allplan. The tool does not claim full-project coverage or invent floor names. File 102 retains one identity even if its API number is negative. Known geometry keeps the same physical dimensions; displayed-unit conversion and offset handling are correct. Unresolved floor/structure information is explicit.

## UAT-03 — Reusable selection and query

**Milestone:** M1.

**Actions:** Ask for ordinary native columns in file 101, then narrow to mark `S02`. Pass the first selection to a read-only summary. The model also prepares a small-page query to exercise complete result traversal.

**Expected:** Six columns in file 101; two of those have mark `S02`. The reference column in 102 is excluded. A model-component summary identifies 10 top-level components in file 101. Repeated representations do not create extra model elements. Paging does not omit or repeat targets, and downstream tools use the intended full selection. No model change occurs.

**Additional check:** A dimension filter and spatial box return a subset with expected boundaries specified by the model; the containment/intersection policy is visible.

## UAT-04 — Audit with known defects

**Milestone:** M2.

**Actions:** Audit the six columns with the bound demo profile. Locate each finding by its mark/file/location or a supported highlight action.

**Expected:** Five findings affecting five columns: missing C03 mark, duplicate group C02/C04 reported as two findings, wrong layer C05, invalid status C06. C01 passes. No mark from file 102 or 103 becomes a duplicate in the file-101 scope. Nothing changes in the model.

**Negative check:** In a separate model-prepared variant, an unavailable attribute/resource produces an explicit profile error or `not_checked`, never a false clean audit.

## UAT-05 — Preview, repairs, office standard and attribute rule edits

**Milestone:** M3.

**Actions:** Request a preview of deterministic repairs, inspect the model before applying, then apply the reviewed plan. Re-run the audit. On reset copies, exercise `apply_office_standard` and an explicit attribute/layer `rule_based_edit` using the same bounded targets.

**Expected:** Preview proposes exactly C05 layer → `MCP_QA_STRUCTURE` and C06 status `NWE` → `NEW` and changes nothing. Apply changes those two values only; geometry and marks remain unchanged. The new audit contains three remaining mark findings. Every entry has an observed result, including skipped/failed targets. Shared operations have consistent behavior across the three public tools.

**Optional continuation:** Preview and authorize C03 mark = `S03`, C04 mark = `S04`. The next audit has zero findings for the four known rules. Missing or duplicate marks are not silently assigned by the initial repair batch.

## UAT-06 — Stale plans, read-only scope, repeat requests and recovery

**Milestone:** M3, extended whenever mutation scope changes.

**Actions:** Preview the initial repairs. Before apply, change C06 status to `EXISTING` manually in Allplan. Attempt to apply the old plan. In separate reset cases, include the passive file in a write request, repeat an already applied request, and use the documented Undo action.

**Expected:** The stale C06 value is not overwritten. Conflicts and any permitted partial application are reported according to the release policy. Passive objects are not written. Replaying the same request has no second effect. Undo behaves as documented for the tested operation, and subsequent read/audit/registry results match the restored model.

**Model-owned extensions:** Simulate lost responses, partial adapter failure and host restart. Reconcile unknown execution before retrying. Supply a short UI observation case if a real runtime failure path needs owner verification; do not ask the owner to edit network code.

## UAT-07 — Native geometry edit with exceptions

**Milestone:** M4.

**Setup:** Six 400 × 400 ordinary columns; preserve stable fixture identities.

**Actions:** Preview changing the section of those columns to 450 × 450 mm, excluding C01. Apply and inspect dimensions and properties. Test a separately provided Structural Framing sample only for advertised capabilities.

**Expected:** Exactly five ordinary columns change, C01 remains 400 × 400, and agreed elevations, materials and related data remain consistent. Native properties and visible geometry agree. Unsupported Structural Framing updates are rejected explicitly; a change to text alone is not a section edit.

## UAT-08 — Repeatable structural frame

**Milestone:** M4.

**Setup:** Empty designated file; grid X = [0, 6000], Y = [0, 6000] mm; levels 0 and 3000 mm; four perimeter beams at the upper level; no bracing or interior beams. Profile supplies sections/materials and insertion conventions.

**Actions:** Preview, apply, inspect native component types and positions, then repeat the same generation intent.

**Expected:** Four columns and four beams, with the agreed top/bottom elevations and insertion rules. Preview counts equal actual counts. Repeating unchanged input adds no duplicate elements. A manual modification followed by regeneration is preserved or reported as a conflict according to the ownership policy.

## UAT-09 — Foundations from explicitly selected supports

**Milestone:** M4.

**Setup:** Four selected base columns from UAT-08. Example test rule: pad size 1500 × 1500 × 500 mm, top elevation 0, centered under each selected column. These are fixture values, not design calculations.

**Actions:** Preview, apply, inspect in plan/section, and repeat.

**Expected:** Four native pad foundations at the specified positions/elevations; no foundations under unselected or upper-level columns. The second run creates no duplicates. Source-to-foundation links remain resolvable. Straight-wall strips get a separate card before they are advertised.

## UAT-10 — Prepared contents on a layout

**Milestone:** M5.

**Setup:** Two prepared drawing files and an agreed A1 or A3 template with defined margins, reserved title-block area and scale. The model supplies exact expected placement values.

**Actions:** Populate a designated empty layout, inspect print preview, and test a prepared overflow case.

**Expected:** Correct paper scale, crops, layers, margins and readable placement; no overlap with the reserved template area. Overflow follows the profile and uses available layout numbers. Existing occupied layouts are not silently replaced. Source drawing files and intended views are distinguished.

## UAT-11 — Managed documentation and freshness audit

**Milestone:** M6.

**Actions:** Generate the foundation profile: one plan, two sections, specified labels/dimension chains and schedule. Audit it, remove one required dimension in a test copy, and audit again. Change a source foundation and test refresh. Move a generated label manually before a subsequent update.

**Expected:** Content matches the profile and references the correct model. The missing dimension role is found. A relevant source change produces stale status until successful update. Regeneration avoids duplicates. Manual label changes are preserved or explicitly identified as conflicts. Unsupported checks are shown; the report does not grant formal design approval.

## UAT-12 — Issue package and blocked/partial exports

**Milestone:** M5; repeat with M6-generated contents.

**Actions:** Select exact layouts and provide revision `P01`, a fixed test date and description. Prepare PDF and DWG to a new output directory. Open the results in an available viewer/application. Repeat with a known critical audit failure and a model-prepared output failure case.

**Expected:** Correct filenames, exact sheet coverage, matching scales/content and a manifest recording source/profile/build/revision plus file hashes. The declared revision mechanism is visible: plugin-managed metadata is not mislabeled as native revision history. A critical audit failure blocks preparation; a failed export produces an incomplete result, not a complete issue. Existing issue files are preserved under the stated policy. Model Undo is not represented as deleting exported files.

**Recovery:** The model supplies a supported cleanup/retry workflow. The owner is not asked to modify manifests or calculate hashes.

## UAT-13 — Host-linked coordination openings

**Milestone:** M7.

**Setup:** A supported straight pipe through a native wall and a supported duct through a native slab, with known external dimensions/insulation, clearance and host properties. Add one deliberately ambiguous or unsupported case.

**Actions:** Preview and create openings, inspect actual hosts in plan/section, and repeat.

**Expected:** Openings affect the correct native hosts and have dimensions calculated from the agreed geometry and clearance convention. DN is not substituted for external geometry. Source/host links are retained and re-running adds no duplicate openings. Ambiguous cases and violated edge/support rules are reported for review, not guessed.

## Result form

The model pre-fills technical metadata and creates an English repository record from the owner's response.

```text
Test ID:
Package / commit:
Allplan full build:
MCP client / version:
Profile version:
Fixture / reset state:
Result: PASS | FAIL | BLOCKED
Expected:
Observed:
Screenshot or output file (optional):
Request / diagnostic reference (model supplies):
Retest required:
```

An unrun test stays `NOT_RUN`; `BLOCKED` means it was attempted but a prerequisite prevented a result. Screenshots support visual findings, while tool outputs and model-owned diagnostics support identity/count/readback claims. Both are tied to the actual package and Allplan build.
