"""2026 evaluation adapter: fresh root resolution, fail-closed checks, no Undo."""
from .model_context import boolean, guid
from .native_readers import adapter_ref, root_adapter
from .transport import BridgeError


def resolve(doc, base, queries, change, writable=False):
    ref = change["ref"]
    matches = {}
    started = queries.clock()
    def budget():
        if queries.clock() - started >= queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Repair resolution time budget exceeded.", 409)
    for index, candidate in enumerate(base.ElementsSelectService.SelectAllElements(doc)):
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
        for method, expected in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                                 ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                                 ("IsInMacro", False), ("IsLabelElement", False)):
            if boolean(getattr(element, method)()) != expected:
                raise BridgeError("target_not_writable", f"Target fails {method}; no write requested.", 409)
        if element.GetDrawingfileNumber() != ref["drawing_file"]:
            raise BridgeError("target_not_writable", "Passive target cannot be changed.", 409)
    return element


def read(base, queries, element, change):
    return queries._fields(element, base, {change["field"]}, change["ref"]["drawing_file"],
                           "active_foreground")[change["field"]]


def write(base, element, change):
    import NemAll_Python_IFW_ElementAdapter as adapters
    targets = adapters.BaseElementAdapterList()
    targets.append(element)
    if change["operation"] == "set_layer":
        # ChangeLayer expects a short name, not a numeric ID or long name.
        return base.ElementsLayerService.ChangeLayer(targets, change["resource"]["short_name"])
    return base.ElementsAttributeService.ChangeAttributes(
        [(change["resource"]["attribute_id"], change["new_value"])], targets, False, False)
