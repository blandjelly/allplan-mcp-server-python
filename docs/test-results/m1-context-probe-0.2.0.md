# M1.1 context/identity slice — 0.2.0

Prepared 2026-10-07. **Portable checks PASS**. Subsequent owner runtime logs
show partial success and failed project lookup; see
[runtime findings and 0.2.1 correction](m1-context-runtime-0.2.0.md).
M0 remains closed on its preserved 0.1.2 artifact. This is not M1 acceptance.

- Added typed `/get-model-context` and `get_model_context` MCP tool. Session ID
  and request ID are supplied by the existing bridge transport; installed build
  metadata is supplied by the existing runtime reader.
- Reads current project name/host/path-derived key, document ID, foreground
  drawing file, all loaded file states/names (including empty files), input
  length/angle enum codes and raw offset. No load/unload/switch/write API is called.
- Optional raw-adapter identity sample is bounded to 20 returned items. Keeps
  signed file number, model UUID and view UUID separate. Invalid GUID strings
  remain `not_checked`; no native repr is used as an identity. These observations
  are not production ElementRefs or reusable selections.
- Project key is a name/host/path fingerprint, not a verified durable project
  GUID. Levels, geometry conversion, offset semantics, unloaded inventory,
  component counts and write eligibility remain explicitly unresolved.
- Diagnostics now calls the new read tool when discovered, retaining backward
  compatibility with servers that expose only the M0 tools.

## Validation

Linux CPython 3.12.14, FastMCP 3.2.4. **29 unittest tests passed**. New fake-adapter
tests cover loaded empty/passive/background files, per-request project reads,
missing/error/non-finite values, bounded sampling, UUID validation, model/view
separation, parameter rejection and absence of geometry/attribute/write calls.
Real HTTP MCP smoke checks cover six-tool discovery, context calls, invalid
sample size and diagnostic capture, against a fake bridge. Existing installation,
rollback, deterministic ZIP and cancellation checks also pass.

Fake adapters are not Allplan runtime evidence. The next owner batch is
[M1.1 context probe](../m1-context-probe-batch.md), with no developer commands.
M1.1 remains in progress; M1.2–M1.4 follow this runtime probe.

## Documented 2026 APIs used

- [ProjectService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/ProjectService/): project name/host and path.
- [DrawingFileService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/DrawingFileService/) and [load states](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/DrawingFileLoadState/): foreground file, loaded-file inventory and names.
- [DocumentAdapter](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/DocumentAdapter/) and [BaseElementAdapter](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_IFW_ElementAdapter/BaseElementAdapter/): document ID, signed file number, model/view UUID and active-document state.
- [AllplanSettings](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_AllplanSettings/) and [global settings](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_AllplanSettings/AllplanGlobalSettings/): input unit enums and offset point.

Documentation establishes API feasibility only. No 2027 API or inferred native
attribute/type/layer ID is used; the demonstration profile stays unbound.
