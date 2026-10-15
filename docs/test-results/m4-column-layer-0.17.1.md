# M4 Column → W1: 0.17.1 native observation

**15 October 2026, 20:06 Europe/Warsaw.** The owner tested package **0.17.1**
from source commit `4287e472661dba9e21e60b9eb0e65ffe05d153df`. The installed
bridge hash verification passed. Allplan was healthy before and after the
workflow, both health replies report the same host session, and the owner
reported no crash.

## Observed result

The active drawing file was **101** and the scan covered **six Columns**. The
binding roundtripped to attribute ID **935**, exact name **Klasa odporności
ogniowej**. Three Columns had `F120` and were nonmatching. Three had
`<niezdefiniowany>`; two were planned changes and one was already on W1. The
owner identified Column 1 as already on W1; the preview record uniquely
identifies that no-op with UUID `eb88c850-0cac-408a-8091-f118872d74c2`.

The preview contained **2 changes**, **1 no-op**, and **3 nonmatching** Columns.
The exact-highlight call submitted only the two changes: the result reports
`requested_model_identities: 2` and `submitted_model_identities: 2`. It excluded
the no-op and the three nonmatching Columns. The owner reported that Columns 5
and 6 were highlighted and moved to W1. Apply returned **2 applied** outcomes;
both readbacks were layer ID **65535** (W1), and
`audited_fields_match_plan` was `true`. The follow-up criteria reported **3
no-op** and **3 nonmatching** Columns.

## Finding and acceptance limit

There is a semantic mismatch in highlighting: the requested criterion is
“Columns without fire resistance classification,” so every matching Column
should be highlighted, including the one already on W1. Highlighting currently
uses only planned changes, leaving that matching no-op out. Setters should
continue to apply only to actual changes. The 0.17.2 follow-up will make
highlighting cover matching changes and no-ops, including an all-no-op result,
while leaving setters change-only.

This observation confirms the correct field binding, the two reported W1
updates, readback and audited-field agreement, and healthy same-session replies.
It does **not** establish complete highlighting semantics or blanket
`accepted_on_build`: the no-op was omitted from highlighting, and the owner did
not report Undo, rerun/no-op verification, or geometry confirmation. The
owner's visual report is retained as reported; the uploaded record does not
prove geometry preservation or native UI Undo behavior.

## Original evidence

- [Original JSON](../../evaluation-packages/0.17.1/native-acceptance/20261015-owner/m4-column-layer-check-20261015T180606761353Z.json)
  (SHA-256 `83048187210f4ea3e765c02718c8ea692ee81cf6648a57fe244411c56e78bb56`)
- [Original TXT](../../evaluation-packages/0.17.1/native-acceptance/20261015-owner/m4-column-layer-check-20261015T180606761353Z.txt)
  (SHA-256 `ded0aaa0f65fb59f005bcb99fa7cc9507c3cce6ee37755ab0d6b0bd66d6ba579`)

Both uploaded files were copied unchanged. Package source/build/CI evidence is
recorded in the [0.17.1 delivery README](../../evaluation-packages/0.17.1/README.md);
it does not expand the native scope of this observation.
