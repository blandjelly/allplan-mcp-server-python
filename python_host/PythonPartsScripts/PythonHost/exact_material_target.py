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

    def by_type(values):
        counts = {}
        for value in values:
            counts[value.split("|", 1)[0]] = counts.get(value.split("|", 1)[0], 0) + 1
        return counts

    # Per-type counts are descriptive (0.43.0 trial: one AttributeContainer
    # child replaced by another UUID); they are not a verdict on benignness.
    removed_types, added_types = by_type(before - after), by_type(after - before)
    type_changes = {name: {"removed": removed_types.get(name, 0), "added": added_types.get(name, 0)}
                    for name in sorted(set(removed_types) | set(added_types))}
    return {"status": "observed", "scalar_changes": scalar, "child_type_changes": type_changes,
            "children_removed": listed(before - after), "children_added": listed(after - before),
            "edges_removed": listed(set(expected["edges"]) - set(current["edges"])),
            "edges_added": listed(set(current["edges"]) - set(expected["edges"])),
            "parents_expected": sorted(p["parent"] for p in expected["parents"]),
            "parents_current": sorted(p["parent"] for p in current["parents"])}


ATTRIBUTE_CONTAINER = "AttributeContainer_TypeUUID"


def attribute_containers_regenerated(expected, current):
    """True only for a one-for-one AttributeContainer replacement per parent.

    Every other child, every edge between non-container children and parents,
    every scalar and every parent stay identical; each parent keeps the same
    number of AttributeContainer children and container edges. Used only for
    the post-setter readback of an exact Slab tier attribute write (0.46.0).
    """
    if not valid_inventory_summary(expected) or not valid_inventory_summary(current):
        return False
    if any(expected[key] != current[key]
           for key in ("parent_representation_count", "child_visits", "target_in_direct_scan")):
        return False

    def container(key):
        return key.split("|", 1)[0] == ATTRIBUTE_CONTAINER

    def parents(summary):
        rows = {}
        for item in summary["parents"]:
            if item["parent"] in rows or container(item["parent"]):
                return None
            rows[item["parent"]] = item["children"]
        return rows

    def edges(summary):
        kept, containers = [], {}
        for edge in summary["edges"]:
            child, separator, parent = edge.partition(">")
            if not separator:
                return None, None
            if container(child):
                containers[parent] = containers.get(parent, 0) + 1
            else:
                kept.append(edge)
        return sorted(kept), containers

    before, after = parents(expected), parents(current)
    if before is None or after is None or set(before) != set(after):
        return False
    replaced = False
    for parent, children in before.items():
        old_other = sorted(child for child in children if not container(child))
        new_other = sorted(child for child in after[parent] if not container(child))
        old_containers = {child for child in children if container(child)}
        new_containers = {child for child in after[parent] if container(child)}
        if old_other != new_other or len(old_containers) != len(new_containers):
            return False
        replaced = replaced or old_containers != new_containers
    (old_edges, old_counts), (new_edges, new_counts) = edges(expected), edges(current)
    if old_edges is None or new_edges is None or old_edges != new_edges or old_counts != new_counts:
        return False
    return replaced


def _bounded(summary):
    return {**{key: summary[key] for key in ("parent_representation_count", "child_visits", "target_in_direct_scan")},
            "edges": summary["edges"][:MAX_DIFF_ITEMS],
            "children": sorted(c for p in summary["parents"] for c in p["children"])[:MAX_DIFF_ITEMS]}


def locate(doc, base, target, check, trace=None, expected=None, *, evidence=None, drift=None,
           expected_summary=None, accept_attribute_containers=False):
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
            if accept_attribute_containers and attribute_containers_regenerated(expected_summary, summary):
                # Read-only readback of an exact tier attribute write: the
                # outcome still requires the new value on every representation.
                drift["accepted"] = "attribute_containers_regenerated"
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
