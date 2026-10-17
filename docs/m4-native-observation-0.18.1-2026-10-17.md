# M4 native observations on 0.18.1 — 17 October 2026

Both observations used the verified 0.18.1 bridge from source
`f477f138231f2a8f45690c03bd761364c7e94ab6`. They show that the host responded
through the bounded observations. This does not change the frozen package or
accept the full M4/write workflow.

## Columns → W1 highlight

The preview inspected six Columns in drawing file 101: three F120 Columns were
nonmatching, and three undefined fire-resistance values on W1 were the targets.
The plan was `no_op`: zero changes and no Apply or setters. The highlight request
submitted three model identities/adapters. The owner confirmed that the Columns
were visible as highlighted in the UI. The JSON itself records
`highlighted: null` and `allplan_acceptance: not_run`; it does not verify UI
visibility. Healthy `health_before` and `health_after` replies share one host
session. The owner also reported that this 0.17.2 highlight test worked; the
captured run was on 0.18.1, which carries the same Column handler.

This is scoped owner evidence for highlight visibility and same-session health
delivery. It does not accept Column writes, Apply, readback, Undo, recovery, or
the complete M4 workflow.

## Wall sample

The `model_property_probe` request for `wall_sample`, drawing file 101, stopped
with `probe_scope_unavailable`: “Wall sample has ambiguous adapter
representations.” The saved report is `blocked`, with the sample request still
pending. It contains a healthy `health_before`, but no wall sample or
`health_after`. The observation therefore stopped before the native wall read
and before any wall highlight. No setters were requested. The report does not
establish a crash or the underlying reason for the ambiguous representations.

This is a blocked wall sample, not a failed highlight observation. Wall native
read acceptance and material writes remain pending.

## Original uploads

The files below are preserved byte-for-byte from the owner uploads:

- [Columns JSON](../evaluation-packages/0.18.1/native-acceptance/20261017-owner/m4-column-layer-check-20261017T110217587832Z.json) and [TXT](../evaluation-packages/0.18.1/native-acceptance/20261017-owner/m4-column-layer-check-20261017T110217587832Z.txt)
- [Wall JSON](../evaluation-packages/0.18.1/native-acceptance/20261017-owner/wall-properties-20261017T110348628132Z.json) and [TXT](../evaluation-packages/0.18.1/native-acceptance/20261017-owner/wall-properties-20261017T110348628132Z.txt)
