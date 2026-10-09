"""Narrow Allplan 2026 readers; native adapters never leave the UI handler."""
from __future__ import annotations

from .model_context import boolean, guid, integer, observation, text
from .spatial_contracts import box, convert_point, vector

# Root families observed/read through native adapters. Child axes/tiers resolve
# to these roots; unrelated Structural Framing families remain unsupported.
COMPONENT_TYPES = {"Column_TypeUUID", "Beam_TypeUUID", "SkeletonBeam_TypeUUID",
                   "Wall_TypeUUID", "Slab_TypeUUID", "MultiSlab_TypeUUID"}


def adapter_ref(adapter):
    return {"drawing_file": abs(integer(adapter.GetDrawingfileNumber())),
            "model_uuid": guid(adapter.GetModelElementUUID()),
            "view_uuid": guid(adapter.GetElementUUID()),
            "type_name": text(adapter.GetElementAdapterType().GetTypeName())}


def root_adapter(adapter, check_budget):
    import NemAll_Python_IFW_ElementAdapter as adapters
    visited, chain = set(), []
    current = adapter
    for _ in range(16):
        check_budget()
        ref = adapter_ref(current)
        key = (ref["drawing_file"], ref["model_uuid"], ref["view_uuid"], ref["type_name"])
        if key in visited:
            raise ValueError("Hierarchy cycle")
        visited.add(key)
        chain.append(ref)
        parent = adapters.BaseElementAdapterParentElementService.GetParentElement(current)
        if boolean(parent.IsNull()):
            return current, chain
        if abs(integer(parent.GetDrawingfileNumber())) != ref["drawing_file"]:
            raise ValueError("Parent crosses drawing-file scope")
        current = parent
    raise ValueError("Hierarchy exceeds 16 levels")


def geometry_box(adapter, check_budget):
    import NemAll_Python_Geometry as geo
    import NemAll_Python_IFW_ElementAdapter as adapters

    def direct(element):
        check_budget()
        geometry = element.GetModelGeometry()
        if not isinstance(geometry, (geo.Polyhedron3D, geo.BRep3D)):
            raise ValueError("Unsupported model geometry; require Polyhedron3D or BRep3D")
        bounds, code = geo.CalcMinMax(geometry)
        if code != geo.eServiceResult.NO_ERR or not boolean(bounds.IsValid()):
            raise ValueError("Invalid CalcMinMax result")
        lo, hi = bounds.GetMin(), bounds.GetMax()
        return box([lo.X, lo.Y, lo.Z], [hi.X, hi.Y, hi.Z])

    root_type = adapter.GetElementAdapterType().GetTypeName()
    part_types = {"Wall_TypeUUID": "WallTier_TypeUUID", "MultiSlab_TypeUUID": "Slab_TypeUUID"}
    if root_type not in part_types:
        # Includes the two observed SkeletonBeam roots. Their axes are not
        # geometry substitutes; unavailable solid geometry remains not_checked.
        return direct(adapter)
    # Wall/aggregate slab roots carry geometry on their direct tiers. Include
    # hidden tiers without using axes, openings or labels as solid geometry.
    parts = []
    for index, child in enumerate(adapters.BaseElementAdapterChildElementsService.GetChildModelElements(adapter, True)):
        if index >= 256:
            raise ValueError("Component child budget exceeded")
        check_budget()
        if child.GetElementAdapterType().GetTypeName() == part_types[root_type]:
            if abs(integer(child.GetDrawingfileNumber())) != abs(integer(adapter.GetDrawingfileNumber())):
                raise ValueError("Component tier crosses drawing file")
            parts.append(direct(child))
    if not parts:
        raise ValueError("No readable component tiers")
    return box([min(p["min"][i] for p in parts) for i in range(3)],
               [max(p["max"][i] for p in parts) for i in range(3)])


def geometry_fields(adapter, settings, frame, needed, check_budget):
    def read():
        raw = geometry_box(adapter, check_budget)
        # GetModelGeometry coordinates use API millimetres. The model-local
        # source-frame convention is explicit and requires the offset owner gate.
        point = settings.AllplanGlobalSettings.GetOffsetPoint()
        offset = vector([point.X, point.Y, point.Z])
        canonical = box(convert_point(raw["min"], "mm", "model_local", frame, offset),
                        convert_point(raw["max"], "mm", "model_local", frame, offset))
        return {**canonical, "unit": "mm", "frame": frame,
                "source_api": "GetModelGeometry/CalcMinMax", "source_frame": "model_local",
                "offset_mm": offset, "offset_applied": frame == "project_global",
                "runtime_verified": False}
    bounds = observation(read)
    result = {}
    for field in needed:
        if bounds["status"] != "observed" or field == "bounding_box_mm":
            result[field] = dict(bounds)
            continue
        lo, hi = bounds["value"]["min"], bounds["value"]["max"]
        if field.startswith("size_"):
            value = hi["xyz".index(field[5])] - lo["xyz".index(field[5])]
        elif field.startswith("center_"):
            value = (hi["xyz".index(field[7])] + lo["xyz".index(field[7])]) / 2
        else:
            value = lo[2] if field == "min_z_mm" else hi[2]
        result[field] = observation(lambda: vector([value, 0, 0])[0])
    return result
