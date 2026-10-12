# Office-project roadmap

Goal: edit a typical complex office project. The [accepted M3 fixture MVP](validation-status.md)
provides controlled execution; it does not yet support whole-project edits.
Prioritize **M4.1–M4.2** before frame/foundation generation.

## First property-edit slices

| Requested workflow | Required probe | First acceptance |
| --- | --- | --- |
| Select walls without fire resistance and assign it | Identify the real attribute/type, absent versus empty/undefined/unreadable values, and root/tier ownership for ordinary/multilayer walls. | One intended test wall changes through a proven replace/add adapter; exact readback, audited-field comparison, read-only replay and observed Undo. Unknown data never silently counts as missing. |
| Change concrete class of columns on a storey | Establish whether the intended class is an attribute or native material property and prove its read/write API; configure storey-to-file/elevation mapping. | One test column changes the intended property, excluded elements stay unchanged, related geometry/material fields are checked, and readback/replay/Undo pass. |

Current M3 replaces existing string marks/statuses or layers on Column roots.
It does not add absent attributes, write walls/native concrete properties or
infer storeys. Do not substitute custom text for the intended native property.
The model discovers API IDs/signatures and prepares typed diagnostics/packages;
the owner supplies intended property/value and observes through Allplan/local Codex.

## Expand after the small slices pass

1. **Write profiles/identity:** validated resources and supported build/type/property
   registry; fresh resolution, reopen/copy/move identity and recovery boundaries.
   Project names or copied UUIDs alone do not prove cross-copy uniqueness.
2. **Storey/multi-file scope:** preview explicit files/elevations and account for
   locked/passive/unloaded data and shared references. Report incomplete coverage;
   never silently activate files or claim native BWS support.
3. **Project operations:** reviewed manifest, complete inventory/exceptions,
   deterministic bounded batches and pre-send identities. Revalidate batches while
   distinguishing earlier operation writes from outside edits; report partial
   outcomes. Raising the 32-change limit alone does not solve scan/cache/time/
   transport budgets, journal consumption or performance acceptance.
4. **Journal lifecycle:** backup/import/migration and capacity handling preserving
   deduplication, unresolved outcomes and recovery across batches. Validate
   full/corrupt history and storage rollback; deleting IDs is not maintenance.
5. **Native conflicts/recovery:** a safe active-plan manual-edit experiment,
   broader interrupted/partial outcomes, promised crash/persistence behavior and
   observed Undo. Controlled stops are not power-loss proof; model/journal/multi-file
   changes are not one atomic transaction.
6. **Office-project acceptance:** on a disposable representative project copy,
   verify full selection, values/exceptions, audits, repeat/no-op, partial recovery,
   Undo and performance before normal use.

Use [testing policy](testing-policy.md); no completed fixture gate needs automatic
repetition. Labels, file moves and geometry generation have separate probes and
do not block the first two requested property edits. No new owner batch is
requested by this roadmap.
