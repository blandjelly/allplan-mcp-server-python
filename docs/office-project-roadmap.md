# From the fixture MVP to office-project edits

The owner wants the tool to operate on a typical, more complex office project.
The [bounded M3 closure](m3-closure.md) is the foundation for that goal; it does
not accept production-project writes. The first requested use cases are:

1. Select all walls without a fire-resistance value and assign the intended
   attribute/value.
2. Change the concrete class of all columns on a specified storey.

These are planned workflows, not current capabilities. Prioritize the native
read/edit probes in **M4.1–M4.2** before frame/foundation generation. No new owner
test is dispatched by this roadmap.

## First deliverable: one wall and one column

| Workflow | Required discovery | Acceptance for the first small slice |
| --- | --- | --- |
| Wall fire-resistance assignment | Identify the actual Allplan 2026 attribute and type; distinguish absent, empty, undefined and unreadable values; establish ordinary/multilayer wall root-versus-tier ownership. | Query identifies the intended test wall, preview shows exact owner/old state/value, the proven setter replaces or adds only the intended attribute, readback and whole audited-field verification pass, replay is read-only and Undo is observed. Unknown data cannot silently count as a missing value. |
| Column concrete-class change | Identify whether the project stores the intended class as an ordinary attribute or a native material property; prove the matching read/write API and configured storey-to-file/elevation mapping. | A specified test column changes the intended property, excluded storeys/elements remain unchanged, related geometry/material fields are checked, and readback/replay/Undo pass. Do not substitute a custom text attribute for the native property without an explicit product decision. |

The current M3 adapter replaces **existing strings** on **Column roots** or
changes their layer. It does not append absent attributes, write walls, write
native concrete properties or infer storeys from a generic model. An observed
undefined string such as C03's mark is different from an absent attribute.

The implementation model researches identifiers and signatures and prepares
typed requests, diagnostics and a ready package. The owner supplies the intended
property/value and observes the prepared slice through Allplan/local Codex;
they do not edit Python/JSON or discover API IDs. Confirm the actual attribute,
concrete-class representation and intended target values when preparing each
workflow, rather than requesting them as a prerequisite for closing M3.

## Expand only after the per-property slice passes

1. **Write profiles and target identity.** Introduce an explicit supported
   build/type/property registry and validated project resources. Prove fresh
   resolution and handling of reopen/copy/move/duplicate identities before
   allowing recovery or replay outside the original copy. A project name or
   copied element UUID alone is not a demonstrated cross-copy boundary.
2. **Storey and multi-file scope.** Configure and preview exactly which files
   and elevations define the requested storey. Account for loaded/unloaded,
   foreground/passive and locked files and shared references. Report unchecked
   or inaccessible members instead of claiming all walls/columns were covered.
   Do not silently change active files or claim native BWS support.
3. **Plans for a whole project.** Design a reviewed operation manifest with
   complete inventory, exceptions and deterministic bounded batches. Revalidate
   each batch against its reviewed inputs while distinguishing earlier changes
   made by the same operation from outside edits. Preserve stable batch/execution
   identities before sending and report partial results honestly. Raising the
   32-change constant alone does not solve scan/cache/time/transport limits or
   journal consumption. Define performance acceptance on representative data.
4. **Journal lifecycle.** Design backup/import/migration and capacity handling
   that retain deduplication across batches and recovery. Validate full,
   invalid/unresolved history and storage rollback. Automatic eviction or deleting
   old IDs cannot serve as the maintenance design.
5. **Native conflicts and recovery.** Prove a safe active-plan manual-edit
   conflict experiment, broader partial outcomes, interrupted setters/processes
   and the promised persistence behavior. Separate controlled diagnostic stops
   from crash/power-loss tests. Define and observe Undo behavior; multi-file writes
   and journal records are not one atomic transaction.
6. **Representative office-project acceptance.** On a disposable copy of a
   typical project, prove the complete requested selection, values, exclusions,
   before/after audits, repeat/no-op, partial recovery and Undo contract. Record
   supported combinations and limits before allowing normal office use.

Keep M0–M3 evidence as regression references. New tests cover new or materially
affected behavior under the [testing policy](testing-policy.md); there is no
automatic repeat of completed fixture gates. Graphical labels, file moves,
Structural Framing and general geometry generation have their own probes and
do not block the first two requested property-edit workflows.
