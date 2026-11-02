"""Opt-in exact Slab enumeration; locating a wrapper never authorizes mutation."""
from types import SimpleNamespace

from .component_ownership import identity
from .material_probe import resolve_slab_child
from .query_contracts import fingerprint
from .transport import BridgeError

INVENTORY_SUMMARY_SCHEMA = "m4-exact-inventory-summary-1"
MAX_DIFF_ITEMS = 32


class ScopedBase:
    def __init__(self, base, wrappers, owners):
        self._base = base
        self._owners = owners
        self.ElementsSelectService = SimpleNamespace(SelectAllElements=lambda doc: wrappers)

    def __getattr__(self, name):
        return getattr(self._base, name)


def _key(ref):
    return "|".join(str(ref[key]) for key in ("type_name", "model_uuid", "view_uuid"))


def inventory_summary(resolution, inventory):
    """Bounded JSON evidence of what the inventory fingerprint covered."""
    return {"schema_version": INVENTORY_SUMMARY_SCHEMA,
            "parent_representation_count": resolution["parent_representation_count"],
            "child_visits": resolution["child_visits"],
            "target_in_direct_scan": resolution["target_in_direct_scan"],
            "edges": sorted(_key(edge["child"]) + ">" + _key(edge["parent"])
                            for edge in resolution["child_parent_edges"]),
            "parents": [{"parent": _key(item["parent"]),
                         "children": sorted(_key(child) for child in item["children"])}
                        for item in inventory]}


def valid_inventory_summary(value):
    if not isinstance(value, dict) or value.get("schema_version") != INVENTORY_SUMMARY_SCHEMA:
        return False
    if set(value) != {"schema_version", "parent_representation_count", "child_visits",
                      "target_in_direct_scan", "edges", "parents"}:
        return False
    return (type(value["parent_representation_count"]) is int and type(value["child_visits"]) is int
            and type(value["target_in_direct_scan"]) is bool
            and isinstance(value["edges"], list) and all(isinstance(e, str) for e in value["edges"])
            and isinstance(value["parents"], list)
            and all(isinstance(p, dict) and isinstance(p.get("parent"), str)
                    and isinstance(p.get("children"), list) for p in value["parents"]))


def inventory_diff(expected, current):
    """Name what differs; never decide whether the difference is benign."""
    if not valid_inventory_summary(expected):
        return {"status": "expected_summary_unavailable", "current": _bounded(current)}

    def children(summary):
        return {child for parent in summary["parents"] for child in parent["children"]}

    def listed(values):
        values = sorted(values)
        return {"count": len(values), "items": values[:MAX_DIFF_ITEMS], "truncated": len(values) > MAX_DIFF_ITEMS}

    scalar = {key: {"expected": expected[key], "current": current[key]}
              for key in ("parent_representation_count", "child_visits", "target_in_direct_scan")
              if expected[key] != current[key]}
    before, after = children(expected), children(current)
    return {"status": "observed", "scalar_changes": scalar,
            "children_removed": listed(before - after), "children_added": listed(after - before),
            "edges_removed": listed(set(expected["edges"]) - set(current["edges"])),
            "edges_added": listed(set(current["edges"]) - set(expected["edges"])),
            "parents_expected": sorted(p["parent"] for p in expected["parents"]),
            "parents_current": sorted(p["parent"] for p in current["parents"])}


def _bounded(summary):
    return {**{key: summary[key] for key in ("parent_representation_count", "child_visits", "target_in_direct_scan")},
            "edges": summary["edges"][:MAX_DIFF_ITEMS],
            "children": sorted(c for p in summary["parents"] for c in p["children"])[:MAX_DIFF_ITEMS]}


def locate(doc, base, target, check, trace=None, expected=None, *, evidence=None, drift=None,
           expected_summary=None):
    """Retain a complete direct inventory plus one explicitly enumerated child.

    This facade lives only for the enclosing operation. Ordinary query and edit
    callers keep their original enumeration and all downstream write guards.

    ``drift`` is only for read-only post-setter observation. A changed
    inventory fingerprint is then reported into that dict instead of raising:
    ModifyElements can regenerate MultiSlab child representations, so the
    pre-setter fingerprint cannot identify a fresh readback. The target view,
    child type and parent edge remain strict in every mode. Pre-setter
    callers never pass ``drift`` and keep the exact fingerprint guard.
    """
    def call(api, callback, **details):
        check()
        value = trace.call(api, callback, **details) if trace else callback()
        check()
        return value
    try:
        owner = call("ExactMaterial.SelectAllElements", lambda: base.ElementsSelectService.SelectAllElements(doc))
        owners, wrappers, live, models = [owner], [], {}, {}
        for index, adapter in enumerate(owner):
            check()
            if index >= 10000:
                raise BridgeError("scan_limit_exceeded", "Exact material inventory exceeds 10000 wrappers.", 409)
            wrappers.append(adapter)
            ref = call("ExactMaterial.identity", lambda: identity(adapter, trace=call))
            if ref["drawing_file"] != target["drawing_file"]:
                continue
            row = models.setdefault(ref["model_uuid"], {"ref": {"type_uuid": ref["type_uuid"]},
                "view_identity_not_checked": False, "view_uuids": [],
                "fields": {"type_name": {"value": ref["type_name"]}}})
            if (row["ref"]["type_uuid"] != ref["type_uuid"]
                    or row["fields"]["type_name"]["value"] != ref["type_name"]):
                row["view_identity_not_checked"] = True
            row["ref"]["model_uuid"] = ref["model_uuid"]
            row["view_uuids"].append(ref["view_uuid"])
            live.setdefault((ref["drawing_file"], ref["model_uuid"]), {}).setdefault(ref["view_uuid"], []).append(adapter)
        details = {}
        _, found, resolution = resolve_slab_child(target, {"elements": list(models.values())}, live, owners,
                                                  SimpleNamespace(call=call), check, details)
        if any(edge["parent"][k] != target["parent_ref"][k]
               for edge in resolution["child_parent_edges"] for k in ("model_uuid", "view_uuid")):
            raise BridgeError("repair_conflict", "Exact child parent view changed.", 409)
        digest = fingerprint(resolution)
        summary = inventory_summary(resolution, details["inventory"])
        if evidence is not None:
            evidence["inventory_summary"] = summary
        if expected is not None and digest != expected:
            if drift is None:
                raise BridgeError("repair_conflict", "Exact child inventory or parent edge changed.", 409)
            drift.update({"status": "changed", "expected_fingerprint": expected, "current_fingerprint": digest,
                          "diff": inventory_diff(expected_summary, summary),
                          "meaning": "Post-setter inventory differs from the reviewed plan; target view and "
                                     "parent edge were re-verified. This is evidence, not write authorization."})
        elif expected is not None and drift is not None:
            drift.update({"status": "unchanged", "current_fingerprint": digest})
        for adapter in found.values():
            if all(adapter is not existing for existing in wrappers):
                wrappers.append(adapter)
        return ScopedBase(base, wrappers, owners), digest
    except BridgeError:
        raise
    except Exception as exc:
        raise BridgeError("repair_conflict", "Exact material target could not be resolved.", 409) from exc
