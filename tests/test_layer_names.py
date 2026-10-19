"""Layer name resolution stays exact and asks for confirmation on collisions."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import test_model_query as fixtures


class LayerNameTests(unittest.TestCase):
    def setUp(self):
        fixtures.QueryTests.setUp(self)
        from test_allplan_host.layer_names import (
            bounded_layer_id, exact_layer_name_matches, resolve_direct_layer_name, scan_layer_name_page,
        )
        self.bounded_layer_id = bounded_layer_id
        self.exact_layer_name_matches = exact_layer_name_matches
        self.resolve_direct_layer_name = resolve_direct_layer_name
        self.scan_layer_name_page = scan_layer_name_page
        service = Mock()
        self.base = SimpleNamespace(LayerService=service)
        self.doc = Mock()
        self.doc_id = 42
        names = {
            0: ("DEFAULT", "DEFAULT"),
            3702: ("SZ_OGÓ03", "SZ_OGÓ03 (Ogólne03)"),
            3703: ("OTHER", "OTHER (Ogólne03)"),
        }

        def short(ident, _doc_id):
            if ident not in names:
                raise ValueError("undefined ID")
            return names[ident][0]

        def display(ident, _doc_id):
            if ident not in names:
                raise ValueError("undefined ID")
            return names[ident][1]

        self.base.LayerService.GetShortNameByID.side_effect = short
        self.base.LayerService.GetNameByID.side_effect = display
        self.base.LayerService.GetIDByShortName.side_effect = lambda name, _doc: {
            "DEFAULT": 0, "SZ_OGÓ03": 3702, "OTHER": 3703}.get(name, -1)
        # Model the 2026 API: no GetIDByName method exists.
        del service.GetIDByName
        self.reader = lambda _api, callback: callback()

    def test_exact_short_lookup_preserves_short_name_and_long_name(self):
        result = self.resolve_direct_layer_name(self.base, self.doc, self.doc_id, "SZ_OGÓ03", self.reader)
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["candidates"][0]["short_name"], "SZ_OGÓ03")
        self.assertEqual(result["candidates"][0]["long_name"], "Ogólne03")

    def test_default_layer_id_zero_round_trips_and_negative_id_is_rejected(self):
        result = self.resolve_direct_layer_name(self.base, self.doc, self.doc_id, "DEFAULT", self.reader)
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(result["candidates"][0]["layer_id"], 0)
        self.assertEqual(self.bounded_layer_id(0), 0)
        with self.assertRaises(ValueError):
            self.bounded_layer_id(-1)

    def test_typed_model_edit_accepts_default_layer_id_zero(self):
        import importlib
        editor = importlib.import_module("test_allplan_host.model_edit")
        from unittest.mock import Mock
        self.doc.GetDocumentID.return_value = self.doc_id
        trace = Mock()
        trace.call.side_effect = lambda _api, callback: callback()
        result = editor.bind_changes(self.doc, self.base,
                                     {"changes": [{"target": {"kind": "layer", "short_name": "DEFAULT"}}]},
                                     lambda: None, trace)
        self.assertEqual(result[0]["resource"], {"layer_id": 0, "short_name": "DEFAULT"})
        named = editor.bind_changes(self.doc, self.base,
                                    {"changes": [{"target": {"kind": "layer", "name": "DEFAULT"}}]},
                                    lambda: None, trace)
        self.assertEqual(named[0]["new_value"], 0)
        self.base.LayerService.GetIDByShortName.side_effect = lambda _name, _doc: -1
        with self.assertRaises(ValueError):
            editor.bind_changes(self.doc, self.base,
                                {"changes": [{"target": {"kind": "layer", "short_name": "DEFAULT"}}]},
                                lambda: None, trace)

    def test_full_name_on_2026_requests_catalog_scan(self):
        result = self.resolve_direct_layer_name(self.base, self.doc, self.doc_id, "Ogólne03", self.reader)
        self.assertEqual(result["status"], "catalog_scan_required")

    def test_confirmed_layer_rejects_changed_id_or_name_before_planning(self):
        import importlib
        editor = importlib.import_module("test_allplan_host.model_edit")
        self.doc.GetDocumentID.return_value = self.doc_id
        trace = Mock()
        trace.call.side_effect = lambda _api, callback: callback()
        target = {"kind": "layer", "short_name": "SZ_OGÓ03", "expected_layer_id": 3702,
                  "expected_name": "SZ_OGÓ03 (Ogólne03)"}
        bound = editor.bind_changes(self.doc, self.base, {"changes": [{"target": target}]}, lambda: None, trace)
        self.assertEqual(bound[0]["resource"]["confirmed_name"], target["expected_name"])
        for field, value in (("expected_layer_id", 3703), ("expected_name", "SZ_OGÓ03 (Renamed)")):
            with self.subTest(field=field), self.assertRaises(editor.BridgeError) as error:
                editor.bind_changes(self.doc, self.base, {"changes": [{"target": {**target, field: value}}]},
                                    lambda: None, trace)
            self.assertEqual(error.exception.code, "layer_confirmation_stale")

    def test_catalog_scan_reports_all_exact_full_name_candidates_without_guessing(self):
        result = self.scan_layer_name_page(self.base, self.doc, self.doc_id, "Ogólne03", 3700, 4, self.reader)
        self.assertEqual(result["status"], "confirmation_required")
        self.assertEqual([item["layer_id"] for item in result["candidates"]], [3702, 3703])
        self.assertFalse(result["scan"]["complete"])
        self.assertEqual(result["scan"]["next_offset"], 3704)

    def test_candidate_on_first_page_preserves_search_for_later_duplicate_name(self):
        first = self.scan_layer_name_page(self.base, self.doc, self.doc_id, "Ogólne03", 3702, 1, self.reader)
        self.assertEqual(first["candidate_ids"], [3702])
        self.assertEqual(first["scan"]["next_offset"], 3703)
        second = self.scan_layer_name_page(self.base, self.doc, self.doc_id, "Ogólne03",
                                           first["scan"]["next_offset"], 1, self.reader,
                                           prior_candidate_ids=first["candidate_ids"])
        self.assertEqual(second["candidate_ids"], [3702, 3703])

    def test_catalog_scan_is_bounded_and_completes_at_documented_end(self):
        result = self.scan_layer_name_page(self.base, self.doc, self.doc_id, "unknown", 65535, 1, self.reader)
        self.assertTrue(result["scan"]["complete"])
        self.assertEqual(result["status"], "scan_exhausted_no_match")
        self.assertFalse(result["absence_proven"])
        self.assertIsNone(result["scan"]["next_offset"])
        with self.assertRaises(ValueError):
            self.scan_layer_name_page(self.base, self.doc, self.doc_id, "unknown", 0, 8193, self.reader)

    def test_match_is_casefolded_but_not_fuzzy(self):
        record = {"short_name": "SZ_OGÓ03", "long_name": "Ogólne03",
                  "name": "SZ_OGÓ03 (Ogólne03)"}
        self.assertEqual(self.exact_layer_name_matches(record, "ogólne03"), ["long_name"])
        self.assertEqual(self.exact_layer_name_matches(record, "ogolne03"), [])


if __name__ == "__main__":
    unittest.main()
