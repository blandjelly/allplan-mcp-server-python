# M4 single-Wall read — owner observation on 0.18.2

**PASS / accepted_on_build 0.18.2**, limited to the single native Wall property
read observed on **2026-10-17 Europe/Warsaw**. The owner confirmed that the
reported thickness and material match Allplan's UI. The runtime reports source
`47ec1ad5ccc494452d2bdcd5c7252f8969facbd5`, verified installed bridge integrity
and package version 0.18.2.

The file contains two Walls, described by the owner as 24 cm and 20 cm. M1
found **two Wall identities** (`matched_model_identities=2`), while the probe
intentionally read **one Wall** (`sampled_walls=1`, `is_full_wall_filter=false`).
Without an explicit model UUID it selects the first Wall in deterministic UUID
order; it does not select by thickness or read properties from every Wall.

The sampled Wall in foreground drawing **101** was:

| Field | Observed value |
| --- | --- |
| Model UUID | `06d71e4d-193b-483e-8a32-344ade3d612c` |
| Tier count | 1 |
| Native thickness | **240.0 mm**, matching the owner's 24 cm UI value |
| Raw native material | **`Beton`**, owner-confirmed |
| Strict `<240 mm` criterion | **false**; equality is excluded |
| Adapter representations of this root | **4**, resolved to one sample |

All seven recorded native read stages returned `observed`. Healthy
`health_before` and `health_after` replies share host session
`dcd2c952-59f8-49fe-954b-0c306f7d734d`. The request reports read-only behavior,
no model change and no requested setters or automatic retry.

The JSON remains unchanged: its `awaiting_owner_observation`,
`allplan_acceptance=not_run`, `runtime_verified=false` and
`units_runtime_verified=false` describe the automated report before owner
confirmation. The confirmation above supplies the scoped UI observation; it
does not establish general unit verification. The 20 cm Wall's properties were
not read. Full-Wall thickness filtering, Wall highlighting, material resource
binding, writes/readback, Undo and complete M4 acceptance remain unverified.
This completed single-sample check needs no repeat.

The earlier guide incorrectly expected the 200 mm fixture Wall to be chosen.
The corrected guide explains UUID ordering and both threshold outcomes. The
successful 240 mm sample is valid evidence, rather than a failed 200 mm test.
Frozen ZIP/wheel/sdist files and their original delivery records are unchanged;
this is a documentation/evidence update, without a new build.

Original owner uploads, preserved byte-for-byte:

- [JSON](../../evaluation-packages/0.18.2/native-acceptance/20261017-owner/wall-properties-20261017T112934953302Z.json)
- [TXT](../../evaluation-packages/0.18.2/native-acceptance/20261017-owner/wall-properties-20261017T112934953302Z.txt)

[delivery and portable verification](../../evaluation-packages/0.18.2/README.md).
