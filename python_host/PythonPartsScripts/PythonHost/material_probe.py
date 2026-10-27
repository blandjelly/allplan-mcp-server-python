"""Exact getter-only Beam/Slab evidence, independent of edit eligibility."""
from __future__ import annotations

import importlib


_CLASSES = {
    "Beam_TypeUUID": ("BeamElement", "StructuralBeamElement"),
    "SkeletonBeam_TypeUUID": ("BeamElement", "StructuralBeamElement"),
    "Slab_TypeUUID": ("SlabElement",),
    "MultiSlab_TypeUUID": ("SlabElement",),
}


def native_material_evidence(base, adapter, ref, read):
    """Return JSON evidence while retaining native/props through Material read.

    Read access through a represented object is evidence about that accessor,
    not proof that submitting that object can persist a property edit.
    """
    def representation():
        native = base.GetElement(adapter)
        if native is None:
            raise ValueError("Native representation unavailable")
        return native

    native_result = read("BaseElements.GetElement.material_comparison", representation)
    if native_result["status"] != "observed":
        return native_result, {"status": "not_checked", "value": None,
                               "reason": "native_representation_unavailable"}
    native = native_result["value"]
    represented = {"status": "observed", "value": {
        "module": type(native).__module__, "name": type(native).__name__}}
    unavailable = {"status": "not_checked", "value": None,
                   "reason": "native_material_read_route_unsupported"}
    names = _CLASSES.get(ref["type_name"])
    if names is None:
        return represented, unavailable
    arch_result = read("Python.import.NemAll_Python_ArchElements.material_comparison",
                       lambda: importlib.import_module("NemAll_Python_ArchElements"))
    if arch_result["status"] != "observed":
        return represented, {"status": "not_checked", "value": None,
                             "reason": "native_material_module_unavailable"}
    arch = arch_result["value"]
    matches = [name for name in names if isinstance(getattr(arch, name, None), type)
               and isinstance(native, getattr(arch, name))]
    if len(matches) != 1:
        return represented, unavailable
    class_name = matches[0]
    accessor = "StructuralBeamProperties" if class_name == "StructuralBeamElement" else "Properties"
    path = class_name + "." + accessor
    props_result = read(path, lambda: getattr(native, accessor))
    binding = {"access_path": path + ".Material", "owner_ref": ref,
               "writable_owner": "not_established"}
    if props_result["status"] != "observed":
        return represented, {**props_result, **binding}
    props = props_result["value"]

    def material():
        value = props.Material
        if type(value) is not str or len(value) > 255:
            raise ValueError("Native Material must be a bounded string")
        return value

    value = read(class_name.replace("Element", "Properties") + ".Material", material)
    return represented, {**value, **binding}
