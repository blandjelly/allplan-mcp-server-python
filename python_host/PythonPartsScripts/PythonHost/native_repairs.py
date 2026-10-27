"""2026 evaluation adapter: fresh root resolution, fail-closed checks, no Undo."""
from .model_context import boolean, guid, observation
from .native_readers import adapter_ref, root_adapter
from .transport import BridgeError


def resolve(doc, base, queries, change, writable=False, diagnostics=None, adapter_owners=None,
            all_representations=False):
    if change.get("adapter_version") == "m4-model-edit-1":
        from . import native_model_edit
        return native_model_edit.resolve(doc, base, queries, change, writable, diagnostics, adapter_owners,
                                         all_representations=all_representations)
    ref = change["ref"]
    matches = {}
    started = queries.clock()
    def budget():
        if queries.clock() - started >= queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Repair resolution time budget exceeded.", 409)
    # Native container ownership must extend through the caller's read/setter,
    # not just through iteration in this resolver.
    owner = base.ElementsSelectService.SelectAllElements(doc)
    if adapter_owners is not None:
        adapter_owners.append(owner)
    for index, candidate in enumerate(owner):
        budget()
        if index >= 10000:
            raise BridgeError("scan_limit_exceeded", "Repair resolution adapter budget exceeded.", 409)
        if abs(candidate.GetDrawingfileNumber()) != ref["drawing_file"]:
            continue
        root, _ = root_adapter(candidate, budget)
        current = adapter_ref(root)
        if current["model_uuid"] != ref["model_uuid"]:
            continue
        if (current["type_name"] != "Column_TypeUUID"
                or guid(root.GetElementAdapterType().GetGuid()) != ref["type_uuid"]):
            raise BridgeError("repair_conflict", "Resolved target type changed.", 409)
        matches[current["view_uuid"]] = root
    if len(matches) != 1:
        raise BridgeError("repair_conflict", "Repair target missing or ambiguous; no arbitrary representation selected.", 409)
    element = next(iter(matches.values()))
    if writable:
        flags = {}
        if diagnostics is not None:
            diagnostics.update(resolved_root=adapter_ref(element), native_flags=flags,
                               hierarchy_check="terminal_Column_root_matches_reviewed_model_and_type")
        # 2026 documents IsInMacro as "element has parent object", not a
        # macro-only classifier. A native Column can return True. The required
        # parent walk above resolves to the terminal reviewed Column root;
        # macro/container ancestors cannot resolve as that root and are rejected.
        flags["IsInMacro"] = observation(lambda: boolean(element.IsInMacro()))
        for method, expected in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                                 ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                                 ("IsLabelElement", False)):
            flags[method] = observation(lambda: boolean(getattr(element, method)()))
            if flags[method].get("status") != "observed" or flags[method].get("value") != expected:
                raise BridgeError("target_not_writable", f"Target file {ref['drawing_file']} model {ref['model_uuid']} fails {method} ({flags[method]}); no write requested.", 409)
        if element.GetDrawingfileNumber() != ref["drawing_file"]:
            raise BridgeError("target_not_writable", "Passive target cannot be changed.", 409)
    return element


def observe(doc, base, queries, change, diagnostics=None):
    owners = []
    if change.get("adapter_version") == "m4-model-edit-1" and change.get("operation") == "delete_element":
        from .model_delete import observe_deleted
        return observe_deleted(doc, base, queries, change, diagnostics)
    if change.get("adapter_version") == "m4-model-edit-1":
        from .native_model_edit import read_consensus
        roots = resolve(doc, base, queries, change, adapter_owners=owners, all_representations=True)
        return read_consensus(base, queries, roots, change, diagnostics)
    element = resolve(doc, base, queries, change, adapter_owners=owners)
    return read(base, queries, element, change)


def read(base, queries, element, change):
    if change.get("adapter_version") == "m4-model-edit-1":
        from . import native_model_edit
        return native_model_edit.read(base, queries, element, change)
    return queries._fields(element, base, {change["field"]}, change["ref"]["drawing_file"],
                           "active_foreground")[change["field"]]


def write(base, element, change, doc=None, check=lambda: None, *, trace=None):
    if change.get("adapter_version") == "m4-model-edit-1":
        from . import native_model_edit
        return native_model_edit.write(base, element, change, doc, check, trace=trace)
    import NemAll_Python_IFW_ElementAdapter as adapters
    targets = adapters.BaseElementAdapterList()
    targets.append(element)
    if change["operation"] == "set_layer":
        # ChangeLayer expects a short name, not a numeric ID or long name.
        return base.ElementsLayerService.ChangeLayer(targets, change["resource"]["short_name"])
    return base.ElementsAttributeService.ChangeAttributes(
        [(change["resource"]["attribute_id"], change["new_value"])], targets, False, False)
