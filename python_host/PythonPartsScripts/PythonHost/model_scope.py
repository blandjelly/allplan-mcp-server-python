"""Resolve the read-only open-drawings default; never load or activate a file."""
from __future__ import annotations

import copy

from .transport import BridgeError


def resolve_scope(scope, context):
    if scope != "open_drawings":
        return copy.deepcopy(scope)
    inventory = context["loaded_drawing_files"]
    if inventory["status"] != "observed":
        raise BridgeError("context_unavailable", "Open drawing-file inventory is unavailable.", 409)
    files = [item["number"] for item in inventory["value"]]
    if not files or len(files) > 100 or len(set(files)) != len(files):
        raise BridgeError("context_unavailable", "Open drawing files must be a nonempty, unambiguous inventory of at most 100 files.", 409)
    return {"drawing_files": sorted(files), "include_passive": True, "visibility": "api_select_all"}
