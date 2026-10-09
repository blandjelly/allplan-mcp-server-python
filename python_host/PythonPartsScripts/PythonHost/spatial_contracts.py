"""Finite millimetre boxes and explicit coordinate transforms, without Allplan."""
from __future__ import annotations

import math

from .query_contracts import invalid, keys


def vector(value):
    if (not isinstance(value, (list, tuple)) or len(value) != 3
            or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in value)):
        raise ValueError("Expected three finite numeric coordinates")
    try:
        result = [float(v) for v in value]
    except (ValueError, OverflowError) as exc:
        raise ValueError("Coordinate exceeds finite floating-point range") from exc
    if not all(math.isfinite(v) for v in result):
        raise ValueError("Expected finite coordinates")
    return result


def box(minimum, maximum):
    minimum, maximum = vector(minimum), vector(maximum)
    if any(a > b for a, b in zip(minimum, maximum)):
        raise ValueError("Box minimum exceeds maximum")
    return {"min": minimum, "max": maximum}


def convert_point(point, source_unit, source_frame, target_frame, offset_mm):
    scales = {"mm": 1, "cm": 10, "m": 1000}
    if source_unit not in scales or source_frame not in {"model_local", "project_global"} or target_frame not in {"model_local", "project_global"}:
        raise ValueError("Unsupported unit/frame")
    point, offset = vector(point), vector(offset_mm)
    sign = 0 if source_frame == target_frame else 1 if target_frame == "project_global" else -1
    return vector([p * scales[source_unit] + sign * delta for p, delta in zip(point, offset)])


def validate_spatial(value):
    keys(value, {"min", "max", "relation", "boundary", "frame", "tolerance_mm"},
         {"min", "max", "relation", "boundary", "frame"})
    try:
        box(value["min"], value["max"])
    except ValueError:
        invalid("Spatial box must have finite min/max triples with min <= max.")
    if value["relation"] not in ("intersects", "contained") or value["boundary"] not in ("inclusive", "exclusive") or value["frame"] not in ("model_local", "project_global"):
        invalid("Spatial relation, boundary and frame must be explicit supported values.")
    tolerance = value.get("tolerance_mm", 0)
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or not math.isfinite(tolerance) or tolerance < 0:
        invalid("Spatial tolerance_mm must be finite and nonnegative.")


def matches_box(actual, requested):
    """Axis-aligned broad-phase test, never exact solid intersection."""
    tolerance = requested.get("tolerance_mm", 0)
    inclusive = requested["boundary"] == "inclusive"
    if requested["relation"] == "contained":
        pairs = [(a, b - tolerance) for a, b in zip(actual["min"], requested["min"])]
        pairs += [(b + tolerance, a) for a, b in zip(actual["max"], requested["max"])]
        return all(a >= b if inclusive else a > b for a, b in pairs)
    pairs = [(a, b + tolerance) for a, b in zip(actual["min"], requested["max"])]
    pairs += [(b - tolerance, a) for a, b in zip(actual["max"], requested["min"])]
    return all(a <= b if inclusive else a < b for a, b in pairs)
