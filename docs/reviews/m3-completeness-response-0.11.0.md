# Response to the M3 completeness review — 0.11.0

The [owner-supplied audit](m3-completeness-review-2026-10-10.md) is preserved
byte-for-byte as a historical review of ad146f6. Its old environment attempts,
temporary file links and CI observations are not results for this new version.
The owner requested implementation through the next necessary native test.

| Review priority | Implemented now | Remaining work |
| --- | --- | --- |
| Generalize supported executor and connect standard/selection | 1–32 existing string-status/layer changes, any validated foreground file, Column roots; shared typed workflow Apply/Revalidate/Recover, hash/source/exceptions/dedup/readback retained | Expanded native observation using two separately reviewed single-target workflows |
| Mark assignment and numbering | Existing accepted collision-aware previews retained; all mark plans still refuse Apply | Implement native mark write and deterministic versioned-standard numbering after the new execution gate; baseline scope has not been reduced |
| Same-session conflicts and partial/unknown recovery | Existing executor guards retained; added actual HTTP lost-reply test and read-only recovery without Apply replay | Design controlled native tests in a supported lifecycle after this gate; do not repeat UI editing known to cancel the host |
| Current documentation/journal/integration | Corrected current mark/execution statuses and links, added journal capacity/update/copy/restore policy and current handoff | No pruning/rollover implemented; broader identity/power-loss acceptance, final UAT and main integration remain open |

[178 portable tests PASS](../test-results/m3-workflow-portable-0.11.0.md), frozen
sync and wheel/sdist build pass. Native acceptance for expanded execution is
not_run. [Next concrete owner action](../m3-workflow-apply-batch.md).
M3 remains partially implemented. Two-step Undo is still the accepted earlier
limit; graphic labels, file moves and universal native setters do not become
mandatory M3 closure requirements.
