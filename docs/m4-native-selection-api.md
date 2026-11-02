# M4 — Allplan native selection API analysis

Analysis of 2026-10-27 for `develop/m4`, revision
`4315d177d27a4af70524dc4dd0fb64e95e8d2ac1`, product 0.39.0.
It covers the **selection** part of item 8 of the [development plan](development-plan.md).
It does not change the accepted delete scope or close the whole item.
External sources concern the PythonParts API **2026**; the owner-reported
runtime is Allplan **2026.1**, without the exact hotfix in the latest log.
Facts from code/documentation, the implementation design and the required
native observations are separated below. Allplan was not run and runtime was
not changed for this work.

## 1. Conclusion and recommendation

**The public API documents interactive user selection, but the checked
sources contain no complete programmatic contract for setting an arbitrary
adapter list as the current UI selection, clearing it, and independently
reading the whole selection.** This does not prove that such a capability is
absent from other interfaces or SDK versions.

The M4 requirement is the flow `query result → exact selection in Allplan`.
`StartElementSelect` implements a different flow: `user selection in Allplan
→ adapter list`. The latter can be designed and delivered as a separate
feature, but it does not replace the required `select` or close the item.

Recommended course:

1. Establish the **replace / clear / read-current** contract for the installed
   SDK; documentation first, then the narrow experiment in section 7. Send
   missing answers to the vendor instead of guessing setters.
2. After the contract is confirmed, connect a small native backend to the
   existing `model_selection`, keeping full query revalidation and the UI thread.
3. Separately consider `begin_pick` or importing preselection if a
   user-chosen scope is needed. Names and results must clearly distinguish this
   from programmatically setting the selection.

Until a backend is confirmed, the current `action=select` should keep
returning `unsupported` explicitly, without an automatic fallback to
highlight. This is the technical state of open work, not a decision to drop
the requirement.

## 2. What exists in M4

| Location | State and meaning for implementation |
| --- | --- |
| [MCP models](../src/allplan_mcp/property_models.py), `HighlightInput`, `SelectionRequest` | `highlight` and `select` take a `selection_id` and UUID exceptions; `clear_highlight` is separate. There is no `clear_selection` or native state read. |
| [MCP tool](../src/allplan_mcp/server.py), `model_selection` | Sends `m4-selection-1` to `/model-selection`; the description separates highlight and selection and grants no write right. |
| [Host validator](../python_host/PythonPartsScripts/PythonHost/property_contracts.py), `validate_selection` | A second, independent payload validation before the SDK. New actions must be added on both sides. |
| [Presentation](../python_host/PythonPartsScripts/PythonHost/model_selection.py), `present_selection` | `select` ends before the scan and UI calls. Highlight rescans the full query, checks fingerprint, TTL, adapters and budget, then clears highlights and highlights the result. |
| [Query](../python_host/PythonPartsScripts/PythonHost/model_query.py), `ModelQueryService` | JSON cache without durable adapters: TTL 300 s, max 8 entries, 5 s scan. `selection_id` identifies a query result in the host session, not a native selection set. |
| [Handler](../python_host/PythonPartsScripts/PythonHost/PythonHostHandler.py) | Shared service access point. Today `select` skips invalidation of plan presentations because it does nothing; this rule must be revisited when implemented. |
| [Interactor](../python_host/PythonPartsScripts/PythonHost/StartPythonHost.py) and [dispatcher](../python_host/PythonPartsScripts/PythonHost/transport.py) | A 50 ms `DispatcherTimer` runs native work on the UI. HTTP only queues requests. `process_mouse_msg` is empty; ESC stops the whole host. |
| [Presentation tests](../tests/test_model_properties.py) | Check the full query despite paging, stale/TTL before UI, `unsupported` without calls, `unknown` after a UI failure. These are mocks, not proof of selection in Allplan. |

The current highlight submits all recognized view representations of a model.
`requested_adapters` can exceed the number of models. The result leaves
`selected` and `highlighted` as `null`: the SDK call alone does not prove the
UI state. `clear_highlight` clears all highlights of the current document,
including those from other sources. These semantics must not be carried over
to native selection automatically.

## 3. What the 2026 API actually provides

### Interactive setting and choice

[`InputFunctionStarter`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/InputFunctionStarter/)
provides:

```python
StartElementSelect(text, selectSetting, postSel, markSelectedElements,
                   selectionMode=SelectionMode.eSelectGeometry)
RemoveFunction()
```

The first call starts an interactive choice; its arguments describe the
filter, the result receiver and the mode. There is no input
`BaseElementAdapterList` argument. `markSelectedElements=True` is not a
documented way to inject an existing list nor a guarantee of a persistent
selection after the function ends. `RemoveFunction` removes the input function;
it is not a documented `clear_selection`.

[`SelectionMode`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/SelectionMode/)
distinguishes `eSelectGeometry` (the chosen element), `eSelectObject` (also
related elements and children) and `eSelectSubObject` (part of the relations).
For M4 the risk is widening a wall to its axis, labels, attribute container or
children. Start with an explicit `eSelectGeometry` and check actual
identities; the mode name alone does not prove agreement with the semantic
query model.

[`MultiElementSelectInteractor`](https://pythonparts.allplan.com/2026/api_reference/ScriptObjectInteractors/MultiElementSelectInteractor/MultiElementSelectInteractor/)
is a higher layer for script objects. It still handles user choice; rewriting
the working host as a script object does not supply the missing setter.

### Reads — three different meanings of "selected"

| API | Documented result | Evidence limit |
| --- | --- | --- |
| [`PostElementSelection.GetSelectedElements(doc)`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/PostElementSelection/) | `BaseElementAdapterList` taken and removed from the interaction result container. | A consuming read. A second empty result does not prove the UI selection was cleared. |
| [`SelectElementsService.GetPreSelectedElements(doc, filter)`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/SelectElementsService/) | List of preselected elements matching a `SelectionQuery`. | Candidate for reading preselection. Timing relative to tool start, persistence, consumption and use as readback after set/clear are not established. |
| [`CoordinateInput.GetSelectedElements()`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/CoordinateInput/) | Elements at the same distance from the cursor, tied to input identification. | Not a documented read of the whole UI selection. `GetSelectedElement()` also concerns element identification during input. |

Preselection deserves its own experiment rather than early rejection. A
potential readback must never be filtered only to the requested set: that
would hide accidentally selected extra elements and give a false PASS.

### Search, highlight and adapter state

- [`SelectElementsService.SelectByPolygon` / `SelectByRect`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/SelectElementsService/)
  return adapters found by geometry, projection and filter. They do not take an
  adapter list to set. The official example
  [SlopedGeneralOpening.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ArchitectureExamples/Objects/SlopedGeneralOpening.py)
  highlights the result separately. There is no basis to treat a query result
  as a programmatic replacement of the selection.
- [`BaseElements.ElementsSelectService`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ElementsSelectService/)
  is a different class from `IFW_Input.SelectElementsService`. Its
  `SelectAllElements` and `SelectElementsByIfcGuid` return element lists. The
  M4 scanner already uses the former; it does not select the whole model in the UI.
- [`HighlightService`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_Input/HighlightService/)
  has `HighlightElements(eleList)` and `CancelAllHighlightedElements(documentID)`.
  [GetObjectByAttributeValue.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ObjectAccessExamples/GetObjectByAttributeValue.py)
  shows query, highlight and redraw. It does not document selection set/clear/readback.
- [`BaseElementAdapter`](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapter/)
  has `IsActive()` described as an activation check, without a contract strong
  enough to equate it with the current UI selection. Its method list has no
  `IsSelected`/`SetSelected`. Neither `IsActive` nor `SetVisibilityState`
  justifies implementing selection setters.

The example [SelectObjectsByAttributeID.py](https://github.com/NemetschekAllplan/PythonPartsExamples/blob/8e2c252477e20bc9afac8918f78a8eeabd473a81/PythonPartsExampleScripts/ModelObjectExamples/SelectionExamples/SelectObjectsByAttributeID.py)
confirms the path `StartElementSelect → callback → PostElementSelection`.
Examples are pinned to revision `8e2c252477e20bc9afac8918f78a8eeabd473a81`;
they are not M4 acceptance on the current build. Earlier findings are in the
[0.25 note](m4-editing-api.md#native-selection-remains-interactive)
and the [0.28 note](m4-editing-api.md#selecting-existing-query-results).

## 4. Design of programmatic set/clear/readback — after the API is confirmed

The names below are **a proposed M4 contract, not existing Allplan methods**.
A minimal backend should separate `replace_exact`, `clear` and `read_current`,
with declared scope, supported builds, identity and synchronicity. Missing any
part does not allow announcing full support of the item.

### MCP contract

| Proposed action | Contract |
| --- | --- |
| `select` | The full, freshly checked `selection_id` result minus explicit exceptions; replace semantics, no silent add/toggle. Result after an independent read. |
| `read_selection` | A new read of the backend's current state, without requiring a live query ID. Observation time, context, completeness and read scope reported separately. |
| `clear_selection` | An explicitly declared clearing scope and a fresh read of an empty set in the same scope. Independent of `clear_highlight`. |

The extension needs a consistent schema version on both sides (for example a
new `m4-selection-2`) and an explicit error/unsupported for an older host.
Do not silently change the meaning of `clear_highlight` or equate a query
identifier with a UI operation identifier.

### Identities and revalidation

First supported scope: one explicitly named active drawing, without file
activation or layer changes. The number of selected elements is not limited by
the 32-change model limit; it needs its own budget and performance acceptance.
200 is the query page limit, not the full set to select.

Before the UI, rebuild the whole query, check context, TTL, fingerprint,
completeness and absence of ambiguous representations. Do not select only the
first page or a sample. For exact selection reject an incomplete result or one
with unknown identity; disclosing omissions without blocking is not enough
for an "all" promise.

The model key is at least `(drawing_file, model_uuid)` within the bound
project/document/session. Keep the adapter `view_uuid` and parent/child
relations separately. The current `exclude_model_uuids` exceptions and
internal `target_model_uuids` do not qualify the file. When widening scope,
switch to full refs or reject ambiguity; do not assume UUIDs are globally
unique across drawings.

Do not copy all highlight view adapters to native selection automatically.
First establish whether setter/readback operate on the model, a
representation or an object with dependencies. Do not redirect Slab to
MultiSlab, an opening to its wall or a child to its parent. Every widening of
the set must be visible.

### Operation flow

```text
MCP → payload validation → UI queue
    → full query revalidation → resolution of exact adapters
    → read of the replaced scope → backend.replace_exact
    → backend.read_current → set comparison → JSON result
```

This is a design, not executable SDK pseudocode. All native calls stay on the
UI thread. Keep adapters and their owners alive through the call; store
JSON/refs, not SDK pointers, in the cache and response. If the setter
completes asynchronously, a callback/state machine is needed rather than an
assumption that the result is ready before the current tick ends.

Do not decide success by comparing counts. For a requested set `E` and an
independently read `A`, report `missing = E − A`, `unexpected = A − E`,
unrecognized adapters and completeness. `verified` needs both differences
empty, a complete read and a matching context. The comparison must also cover
objects outside query-known families if they could stay selected. A read
filtered only to `E` cannot detect `unexpected`.

After clear, `A` must be empty in the declared scope. A read error does not
mean an empty set. Before the UI call, `unsupported`/`blocked` may be returned
with `ui_calls_started=false`; after the call and loss of certainty —
`unknown`; with a complete read showing a difference — an explicit `mismatch`.
`submitted` is not `verified`.

Selection stays `model_data_changed=false`, `usable_for_write=false`. It runs
no Apply, delete, Undo or property setters. A presentation change requires a
review of the plan-presentation invalidation rule in the handler, but must not
weaken existing write locks, the journal or recovery.

After a lost reply do not repeat replace/clear automatically: the user may
already have changed the selection. An operation identifier and in-session
status allow accounting for the request; they need a new operation
registry/status. The current bridge `request_id` correlates logs and does not
by itself prove execution. Readback stays a fresh observation. After loss of
the registry an unresolved operation's result is unknown. Restart invalidates
the session and query IDs and does not prove native selection was cleared.
Without a read contract do not promise automatic restoration of an earlier
choice.

## 5. Separate feature: interactive choice by the user

This is a feasible direction based on the documented API, requiring
integration and a native trial. Proposed contract:
`begin_pick → status/result → cancel_pick`, with a separate `operation_id`.
HTTP should return `awaiting_user` quickly; do not block the UI or the HTTP
response until a human clicks.

The [selection manual](https://pythonparts.allplan.com/2026/manual/features/input/selection/)
describes taking over mouse handling until the choice ends, the user being able
to change the filter, and the risk of a crash when restarting an active
function or removing an inactive one. The host therefore needs a state machine
`idle → starting → awaiting_user → completed/cancelled/unknown`, a single owner
of the input function and separate ESC handling during the choice.

In the proposed integration the SDK pattern uses a resumed `process_mouse_msg`
to fetch the result after the interaction ends; the current host does not
implement this. The callback is not for polling the result during the choice.
Fetch `PostElementSelection` once, convert it into a bounded ref snapshot and
re-check scope/types/relations. Do not trust the filter alone. An empty result
is a valid completion, not a reason for an automatic restart. Call
`RemoveFunction` only for a still active function owned by the host; do not
remove it again after a normal completion.

While waiting, other UI mutations and Apply/delete/Undo should get
`selection_busy`. Allow status/cancel and only checked reads; the timer
behaviour in the native input loop must be confirmed. ESC, a project/drawing
change and host stop must end the operation without double cleanup and without
leaving an active function. A `starting/unknown` state does not authorize a
blind `RemoveFunction` or a second start.

Name the result `interactive_pick`, with `readback_kind=interaction_result`.
Do not present it as a persistent UI selection or as a `read_selection` result.
A separate snapshot of the input scope may be created; it is still no write
consent and must pass normal preview/revalidation before editing.

## 6. Variants and technical cost

| Variant | What it gives | Assessment |
| --- | --- | --- |
| Public replace/clear/read-current backend | Meets the target query → native UI direction if the contract is confirmed. | Preferred; currently BLOCKED by a missing complete contract. |
| `StartElementSelect` + callback result | The user chooses elements with native gestures. | A real separate feature; medium lifecycle complexity, does not close the current requirement. |
| `GetPreSelectedElements` | Potential import of a previously selected scope. | The smallest read experiment; semantics and scope need checking. |
| Another official SDK/vendor extension | Potentially the missing setter and readback. | To be clarified with the vendor; no concrete C++/.NET path is confirmed here. Adds installation, ABI/build and a bridge to the host. |
| Highlight, rectangle geometry or synthetic clicks | Presentation or an attempt to reproduce a gesture. | Do not provide a documented exact set/clear/readback; not a substitute for the requirement. |

The largest cost is not adding a new MCP action but establishing native
selection semantics and safely integrating the UI loop. Without the missing
contract there is no basis for a credible estimate of the full implementation.

## 7. Minimal experiment and deciding questions

This is the design of a future trial, **not an executed test and not a request
to repeat accepted model operations**. Work on a small test drawing; record
the Allplan build, SDK/stubs, package version and exact element refs. Do not
resume broad property discovery or historic trials that led to crashes.

1. Check local stubs of the listed classes only, and the vendor's official
   answer about a setter, clear and a global readback. A symbol's existence is
   not proof of its semantics. Do not call guessed methods.
2. For a manual choice `{A, B}`, then `{B}` and an empty set, check
   `GetPreSelectedElements` before/during/after entering the host and a
   repeated read. Distinguish it from the under-cursor result and from
   highlight. Establish whether the read consumes the state and whether the
   filter really covers the whole scope. Compare a narrowing filter with a
   non-narrowing variant after checking its construction in the 2026 bindings.
   An empty `SelectionQuery` alone does not prove a global or complete readback.
3. For a separate pick check one completion, an empty result and cancellation;
   record callback order, timer behaviour, the `markSelectedElements` scope and
   what remains afterwards. No deliberate double start/Remove.
4. Only after a setter is established run `{A, B} → {B} → ∅`, with a foreign
   earlier selection `C`, comparing full exact refs in API and UI. If the
   backend gives no such readback, record BLOCKED rather than accepting
   highlight as success. Check that model data and Undo history do not change.
5. Only for a working path extend the matrix to Wall with openings,
   Slab/MultiSlab, view representations, passive/hidden layers, context
   change, lost reply, ESC and restart. Do not extend acceptance from one family
   to others; mark a missing example `fixture_missing`.

Questions for the vendor: which public method takes exact existing adapters as
the selection, is replace atomic, how is the state cleared and which getter
reads it independently of cursor/callback? What is the scope
(drawing/document/view/application), lifetime and behaviour after the
interactor ends? Are there normalizations to parent/children? Does
`GetPreSelectedElements` consume the preselection and work after a
programmatic set/clear? What exactly does `IsActive()` mean? Are these calls
supported from a `DispatcherTimer` callback on the UI in 2026.1? Does
`markSelectedElements` leave a selection after the function ends, and can that
set differ from the `PostElementSelection` result?

## 8. Verification of a future implementation and closure condition

Unit tests should check MCP/host contracts, the full set across all pages,
stale/TTL/context before UI, `missing/unexpected` differences, duplicate
representations, unrecognized refs, clear scope and `unknown` after UI start.
For pick: a single start, the result consumed once, no double Remove,
busy/cancel/stop and no automatic restart after an empty result. An HTTP test
should confirm a fast start/status and no implicit retry; a mock backend does
not prove that the real API exists.

A product candidate needs the checks of the [testing policy](testing-policy.md),
the corresponding CI and delivery, and a separate native trial. Selection
acceptance needs agreement of **the whole exact set in API and UI after replace
and after clear**, a check that the model was not edited, and a record of the
build and evidence scope. Reading a pick result or a highlight count is not
enough. The full delete/selection item also needs the missing delete
evidence; the existing grouped Column delete/Undo PASS is retained.

The current result of this work is documentation and code analysis with a
diff and link review. There is no new native PASS, selection implementation,
runtime tests or builds; the 0.39.0 limits remain current.
