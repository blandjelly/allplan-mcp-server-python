"""Exact layer-name lookup using only document-bound LayerService reads.

Allplan 2026 lacks the name-catalog and full-name lookup methods introduced in
later SDKs. Its documented ID range, including DEFAULT at ID 0, is therefore
exposed as a bounded scan so callers can paginate and collect exact candidates
before asking for a choice. No fuzzy matching or implicit short-name
substitution is performed.
"""
from __future__ import annotations

import unicodedata

from .model_context import integer
from .model_metadata import bounded_text
from .transport import BridgeError

LAYER_ID_MIN = 0
LAYER_ID_MAX = 65535
LAYER_SCAN_PAGE_MAX = 8192


def _key(value):
    return unicodedata.normalize("NFC", value.strip()).casefold()


def bounded_layer_id(value):
    """Validate Allplan's DEFAULT layer ID 0 and regular 16-bit layer IDs."""
    ident = integer(value)
    if not LAYER_ID_MIN <= ident <= LAYER_ID_MAX:
        raise ValueError("Layer ID is outside the documented Allplan range")
    return ident


def _long_name(display_name, short_name):
    """Read the long part of the documented `short (long)` display, if present."""
    if " (" in display_name and display_name.endswith(")"):
        prefix, long_name = display_name.split(" (", 1)
        if prefix == short_name:
            return long_name[:-1]
    return display_name


def layer_record(base, layer_id, document_id, read, doc=None):
    """Return fresh names for an ID; `read(api, callback)` owns trace/budget."""
    ident = bounded_layer_id(layer_id)
    short = bounded_text(read("LayerService.GetShortNameByID",
                              lambda: base.LayerService.GetShortNameByID(ident, document_id)))
    display = bounded_text(read("LayerService.GetNameByID",
                                lambda: base.LayerService.GetNameByID(ident, document_id)))
    if doc is not None:
        roundtrip = integer(read("LayerService.GetIDByShortName",
                                 lambda: base.LayerService.GetIDByShortName(short, doc)))
        if roundtrip != ident:
            raise ValueError("Layer ID/short-name round trip differs")
    return {"layer_id": ident, "short_name": short, "name": display,
            "long_name": _long_name(display, short)}


def exact_layer_name_matches(record, requested_name):
    """Match only complete short, long, or API display names."""
    requested = _key(requested_name)
    return [key for key in ("short_name", "long_name", "name")
            if _key(record[key]) == requested]


def scan_layer_name_page(base, doc, document_id, requested_name, offset, limit, read,
                         prior_candidate_ids=(), should_continue=None):
    """Scan one bounded ID page and return matching candidates plus continuation."""
    if isinstance(offset, bool) or not isinstance(offset, int) or not LAYER_ID_MIN <= offset <= LAYER_ID_MAX + 1:
        raise ValueError("Invalid layer scan offset")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= LAYER_SCAN_PAGE_MAX:
        raise ValueError("Invalid layer scan page size")
    stop = min(offset + limit, LAYER_ID_MAX + 1)
    candidates = []
    seen = set()
    api_errors = 0
    api_calls = 0
    for ident in prior_candidate_ids:
        ident = bounded_layer_id(ident)
        if ident in seen:
            raise ValueError("Invalid or duplicate prior layer candidate ID")
        seen.add(ident)
        record = layer_record(base, ident, document_id, read, doc)
        matches = exact_layer_name_matches(record, requested_name)
        if not matches:
            raise ValueError("A previous layer candidate no longer matches the requested name")
        candidates.append({**record, "matched_names": matches})
    scanned_to = offset
    for ident in range(offset, stop):
        if should_continue is not None and not should_continue():
            break
        if ident in seen:
            scanned_to = ident + 1
            continue
        try:
            # GetNameByID exists in 2026 and may return the combined
            # `short (long)` display. Avoid a second native call for every ID.
            display = bounded_text(read("LayerService.GetNameByID",
                                        lambda: base.LayerService.GetNameByID(ident, document_id)))
            api_calls += 1
            match_by_display = _key(display) == _key(requested_name)
            short_hint = None
            long_hint = None
            if display.endswith(")") and " (" in display:
                short_hint, long_hint = display.split(" (", 1)
                long_hint = long_hint[:-1]
            name_match = (match_by_display or (short_hint is not None and
                                               _key(requested_name) in {_key(short_hint), _key(long_hint)}))
            if not name_match:
                scanned_to = ident + 1
                continue
            short = bounded_text(read("LayerService.GetShortNameByID",
                                      lambda: base.LayerService.GetShortNameByID(ident, document_id)))
            api_calls += 1
            reverse = integer(read("LayerService.GetIDByShortName",
                                   lambda: base.LayerService.GetIDByShortName(short, doc)))
            api_calls += 1
            if reverse != ident:
                api_errors += 1
                scanned_to = ident + 1
                continue
            if short_hint is not None and short_hint != short:
                api_errors += 1
                scanned_to = ident + 1
                continue
            record = {"layer_id": ident, "short_name": short, "name": display,
                      "long_name": long_hint if short_hint == short and long_hint is not None else display}
        except BridgeError:
            raise
        except Exception:
            # The API reference does not specify how undefined IDs are reported.
            # Preserve these as incomplete evidence; never claim authoritative absence.
            api_calls += 1
            api_errors += 1
            scanned_to = ident + 1
            continue
        matches = exact_layer_name_matches(record, requested_name)
        if matches:
            candidates.append({**record, "matched_names": matches})
            seen.add(ident)
        scanned_to = ident + 1
    complete = scanned_to == LAYER_ID_MAX + 1
    return {"requested_name": requested_name, "candidates": candidates,
            "candidate_ids": sorted(seen),
            "status": "confirmation_required" if seen else "scan_exhausted_no_match" if complete else "no_match_in_page",
            "absence_proven": False,
            "scan": {"start": offset, "end_exclusive": scanned_to, "complete": complete,
                     "time_budget_reached": scanned_to < stop,
                     "range_scanned_complete": complete,
                     "page_read_errors": api_errors, "page_read_calls": api_calls,
                     "next_offset": None if complete else scanned_to,
                     "id_range": [LAYER_ID_MIN, LAYER_ID_MAX],
                     "page_size": limit}}


def resolve_direct_layer_name(base, doc, document_id, requested_name, read):
    """Use exact documented lookups available in the loaded SDK.

    2026 exposes only the short-name lookup. Newer SDKs may expose exact
    GetIDByName; every ID is verified through fresh reverse lookups. An empty
    result means a paginated 2026 catalog scan is required before declaring
    absence.
    """
    service = base.LayerService
    ids = {}
    short_lookup = getattr(service, "GetIDByShortName", None)
    if callable(short_lookup):
        try:
            ident = bounded_layer_id(read("LayerService.GetIDByShortName",
                                          lambda: short_lookup(requested_name, doc)))
            ids[ident] = "short_name_lookup"
        except BridgeError:
            raise
        except Exception:
            pass
    full_lookup = getattr(service, "GetIDByName", None)
    if callable(full_lookup):
        try:
            ident = bounded_layer_id(read("LayerService.GetIDByName",
                                          lambda: full_lookup(requested_name, doc)))
            ids[ident] = "name_lookup"
        except BridgeError:
            raise
        except Exception:
            pass
    matches = []
    for ident in sorted(ids):
        record = layer_record(base, ident, document_id, read, doc)
        names = exact_layer_name_matches(record, requested_name)
        if names:
            matches.append({**record, "matched_names": names,
                            "lookup_methods": [ids[ident]]})
    return {"requested_name": requested_name, "candidates": matches,
            "status": "resolved" if len(matches) == 1 else "ambiguous" if len(matches) > 1 else "catalog_scan_required"}
