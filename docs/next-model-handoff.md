# Current M4 handoff

## Next task — finish the bounded Slab child getter probe

Continue on the M4 topic branch based on **develop/m4**; main integration is a
separate task. Candidate 0.41.0 adds optional
`parent_ref={model_uuid,view_uuid}` only to getter-only
`model_property_probe` `material_comparison`. It identifies an exact MultiSlab
wrapper from a complete foreground scan, then uses documented
`GetChildModelElements` for the exact drawing/model/view of its Slab child.
Retain exact child and parent refs, including differing views. Do not redirect
the child to the parent or a writable owner. Preserve current scan/query/write
guards, trace and budgets, and native container lifetime. Bound the probe to at
most 16 exact parent/target wrappers and 256 child visits total. The SDK double
reproduces a child absent from the direct scan; the native cause is unknown,
and supplied evidence does not show that SelectAll omits Slab.

After 0.41.0 CI and exact-ZIP verification/installation, ask the owner to run
only the retained Slab child probe with an explicit exact `parent_ref`,
`include_parent=true`, and attribute ID 508, using the
[exact request](tool-reference.md#model_property_probe--isolated-read-phases) and preserving trace.
Do not repeat the three successful 0.40.0 probes or any setter. Broad property
discovery stays suspended.

## Latest candidate and native evidence

Candidate **0.41.0**, branch `codex/m4-child-material-probe`, is based on
develop/m4 `7bb20d6e` (merged [PR #46](https://github.com/blandjelly/allplan-mcp-server-python/pull/46)).
**82 focused unit checks (including version consistency) + 8 MCP/HTTP checks
PASS** on Linux/Python 3.12.14. Full candidate CI, exact ZIP/upgrade/restore
and native acceptance remain pending. The 0.40.0 head `fca3da98` passed
Windows/Ubuntu Python 3.12 CI, package production and `ci-required`;
[health and delivery evidence](validation-status.md#delivery-and-ci-evidence)
bind its installed bridge to that source with verified file hashes, while exact
ZIP installation/upgrade/restore remains unverified.

**Read-only Allplan comparison, 2026-10-27 (0.40.0):** both SkeletonBeams
(`StructuralBeamElement`) and the MultiSlab (`SlabElement`) returned native
Material exactly `" "`; attribute 508 resolved live as `Materiał` / SDK
`String`, roundtrip ID 508, and returned `TEST1` in both `ReadAll` and
`ReadAllAndComputable`. Native Material and attribute 508 are separate observed
values; owner equivalence, shared storage and persistence are unknown. All three
successful probes were `usable_for_write=false`. The exact Slab child request
was blocked with `probe_scope_unavailable`; no child or separate parent read
completed. MultiSlab's observed child edge does not establish child values.
SkeletonBeam 1's target and parent-edge views still differ. Do not infer that
SelectAll omits Slab or assign a native cause. The complete 31-record journal
inspection showed `87a45065d5e14e3a9ac8c54756e273a0` as `stopped`,
`reconciled: 1`, integrity verified, `requires_recovery=false`; this does not
establish applied success or preservation. `4388b04e39a14fac811db4f58723d01f`
was absent from those 31 returned records, which does not establish its archive
state. Keep earlier Slab writes unassigned to an execution without direct
proof. Raw evidence and limits are in [validation status](validation-status.md#latest-owner-observations)
and [the preserved 0.40.0 files](test-results/evidence/0.40.0-2026-10-27/).

The owner-reported 0.39.0 intended-value PASS remains recorded for native
material on Wall, Wall with opening, and Column, and for attribute writes on two
SkeletonBeams and the MultiSlab/Slab representations of one assembly. Keep
those results separate from preservation, Undo, exact package attribution and
the 0.40 getter observations. Do not repeat completed writes. A native write
change requires a freshly reviewed exact-owner preview, Apply, readback and
preservation evidence. See the [API comparison](m4-editing-api-0.32.0.md#native-material-material-attribute-and-surface)
and [development plan](office-editing-development-plan.pl.md).

## Other active boundaries

Scalability analysis (2026-10-27) is in the [implementation plan, S0–S5](implementation-plan.md#analiza-skalowania-developm4-i-ergonomii-mcp).
The 200-result bound is per page; repeated scans and independent scan/cache
budgets limit larger reads. More than 32 changes should use a reviewed durable
manifest and sequential batches, initially in one drawing. Larger writes depend
on the relevant native gates above.

Native selection research for priority 5 is in the [API analysis](m4-native-selection-api.md).
The inspected public 2026 API documents interactive pick, but no complete
arbitrary replace/clear/current-state readback contract was found. Resolve the
installed SDK contract and scope/lifecycle of `GetPreSelectedElements` with
the bounded experiment in that note. `select` remains unsupported; interactive
pick would be a separate feature. This does not change the Beam/Slab material
scope or accepted delete evidence.

Preserve target/owner binding, fresh revalidation, journals/traces, replay
protection, write/Undo guards and unknown outcomes. Never remove records to
free a recovery lock or retry a setter to resolve unknown state. Earlier broad
property and native preview crashes have unproven causes; do not repeat them.
Read [AGENTS](../AGENTS.md), the [documentation policy](documentation-policy.md)
and [testing policy](testing-policy.md). Required-check configuration for
develop/m4 still needs confirmation.
