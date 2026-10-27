# Allplan bounded read-only comparison log

I archived the M4 trace and captured the read-only comparison in drawing file **101** (active foreground, document **0**). The query covered all **26** model identities; it reported **0 conflicting model identities** and **0 duplicate representations**. Unloaded files and screen occlusion were not checked.

| Target | Exact identity and lineage | Native representation | Material evidence |
|---|---|---|---|
| SkeletonBeam 1 | Model `2dfa6117-d481-4588-8647-d24049d61d29`, view `d9f3d9b1-a005-4789-b929-c39b291d1cd0`; query classifies it as top-level. | `StructuralBeamElement`; property owner not established. | Attribute read blocked because root adapter representations are ambiguous. |
| SkeletonBeam 2 | Model `8f13565b-abfc-4ce2-8b1d-7d133fe1a10d`, view `5f6e4603-6282-4ae0-9d02-ad089e73b859`; query classifies it as top-level. | `StructuralBeamElement`; lineage is complete, with a `SkeletonAxis` child. Property owner not established. | Complete name search returned 0 `material` matches. No attribute ID, type, or value was resolved. |
| MultiSlab | Model `bf097d95-8275-4229-ac74-27bbea26c211`, view `b4a59b5b-c0ae-4c1e-9d59-df5761390eb9`; query classifies it as top-level. | `SlabElement`; lineage is complete and includes the Slab child. Property owner not established. | Complete name search returned 0 `material` matches. No attribute ID, type, or value was resolved. |
| Slab child | Query reports model `8a693925-ae20-4dda-91d1-3951af3c0a52`, view `a0fcd7b3-85c8-4f83-99b7-59e8a3463c94`, under that MultiSlab. | Could not confirm separately. | Exact component probe did not resolve to one complete semantic component; no attribute read occurred. |

The first SkeletonBeam also has an identity discrepancy: its query view is `d9f3…`, while the native ownership child-parent edges name the parent view as `efb18c61-fab3-42f4-b79b-9f41d05da940`. The query still reports zero conflicting **model** identities, but this view mismatch prevents a clean exact lineage comparison for that target.

**Native Material and property owner remain unestablished for all targets.** The available isolated probe reports runtime classes and ownership lineage, but does not read native Material. The project-attribute probe found no `material`-named stored attributes on the second SkeletonBeam or MultiSlab; that is not proof that no such attribute exists because ReadAll omissions remain unknown. The ambiguous first beam and unresolved Slab child have no attribute evidence. No attribute ID, name, type, and value could be resolved as a complete set.
