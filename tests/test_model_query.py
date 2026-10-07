"""Portable query contracts and fake-adapter checks; no Allplan runtime evidence."""
import copy
import importlib
import json
import types
import unittest
from unittest.mock import MagicMock

import test_host_handler as host_fixtures


class QueryTests(unittest.TestCase):
    setUp = host_fixtures.HostHandlerTests.setUp
    prepare_context = host_fixtures.HostHandlerTests.prepare_context

    def prepare(self, adapters=None):
        self.prepare_context()
        self.base.ElementsSelectService.SelectAllElements.return_value = adapters or []
        self.base.eAttibuteReadState.ReadAll = 1
        self.contracts = importlib.import_module("test_allplan_host.query_contracts")

    def adapter(self, number=101, ident=1, view=None, layer=7, attrs=None):
        adapter = MagicMock()
        adapter.GetDrawingfileNumber.return_value = number
        adapter.GetModelElementUUID.return_value = f"00000000-0000-4000-8000-{ident:012d}"
        adapter.GetElementUUID.return_value = f"10000000-0000-4000-8000-{(ident if view is None else view):012d}"
        adapter.GetElementAdapterType.return_value.GetTypeName.return_value = "Column_TypeUUID"
        adapter.GetElementAdapterType.return_value.GetGuid.return_value = "20000000-0000-4000-8000-000000000001"
        adapter.GetDisplayName.return_value = "Column"
        adapter.GetCommonProperties.return_value = types.SimpleNamespace(Layer=layer)
        adapter.GetAttributes.return_value = [] if attrs is None else attrs
        return adapter

    def request(self, **changes):
        request = {"schema_version": "m1-query-1", "action": "query",
                   "scope": {"drawing_files": [101], "include_passive": False, "visibility": "api_select_all"}}
        request.update(changes)
        return request

    def query(self, **changes):
        result = self.handler.handle("/model-query", self.request(**changes))
        self.base.CreateElements.assert_not_called()
        json.dumps(result, allow_nan=False)
        return result

    def follow(self, result, action="page", **changes):
        return self.handler.handle("/model-query", {"schema_version": "m1-query-1", "action": action,
                                                   "selection_id": result["selection_id"], **changes})

    def assert_code(self, code, callback):
        with self.assertRaises(self.module.BridgeError) as error:
            callback()
        self.assertEqual(error.exception.code, code)

    def test_invalid_requests_never_enumerate_and_unknown_geometry_is_rejected(self):
        self.prepare()
        invalid = [self.request(scope={"drawing_files": [-101], "include_passive": False, "visibility": "api_select_all"}),
                   self.request(scope={"drawing_files": [101, 101], "include_passive": False, "visibility": "api_select_all"}),
                   self.request(scope={"drawing_files": [101]}), self.request(page_size=True),
                   self.request(max_adapters=10001), self.request(fields=["geometry"]),
                   self.request(predicate={"any": [{"field": "layer_id", "op": "eq", "value": 7}, {"bad": 1}]}),
                   self.request(predicate={"field": "attribute:2147483648", "op": "exists"}),
                   self.request(predicate={"field": "layer_id", "op": "eq", "value": float("nan")}),
                   self.request(predicate={"field": "layer_id", "op": "eq", "value": 7, "tolerance": True}),
                   self.request(predicate={"field": "layer_id", "op": "contains", "value": 7}),
                   self.request(spatial_box={"min": [0, 0, 0]})]
        for request in invalid:
            with self.subTest(request=request):
                self.assert_code("invalid_payload", lambda: self.handler.handle("/model-query", request))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.CreateElements.assert_not_called()

    def test_predicate_structure_and_depth_are_bounded(self):
        self.prepare()
        tree = {"field": "layer_id", "op": "exists"}
        for _ in range(10):
            tree = {"not": tree}
        for node in (tree, {"all": []}, {"any": None}, {"not": None},
                     {"all": [{"field": "layer_id", "op": "exists"}] * 64},
                     {"field": "layer_id", "op": "exists", "value": 0}):
            self.assert_code("invalid_payload", lambda: self.query(predicate=node))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_scope_reports_unloaded_and_passive_omissions_and_normalizes_signed_identity(self):
        active, passive, outside = self.adapter(), self.adapter(-102, 2), self.adapter(104, 3)
        self.prepare([outside, passive, active])
        scope = {"drawing_files": [101, 102, 103], "include_passive": False, "visibility": "api_select_all"}
        result = self.query(scope=scope)
        self.assertEqual(result["counts"]["matched_model_identities"], 1)
        self.assertEqual(result["omissions"], [{"drawing_file": 102, "reason": "passive_excluded"},
                                               {"drawing_file": 103, "reason": "unloaded_or_unavailable"}])
        self.assertFalse(result["coverage"]["requested_scope_complete"])
        passive.GetAttributes.assert_not_called()
        passive.GetCommonProperties.assert_not_called()
        scope["include_passive"] = True
        result = self.query(scope=scope)
        self.assertEqual(result["counts"]["matched_model_identities"], 2)
        item = next(e for e in result["elements"] if e["ref"]["drawing_file"] == 102)
        self.assertEqual(item["signed_drawing_file_numbers"], [-102])
        self.assertEqual(item["ref"]["drawing_file"], 102)
        self.assertFalse(item["usable_for_write"])

    def test_loaded_empty_scope_has_zero_observed_identities_without_whole_project_claim(self):
        self.prepare()
        result = self.query(scope={"drawing_files": [102], "include_passive": True, "visibility": "api_select_all"})
        self.assertEqual(result["counts"]["matched_model_identities"], 0)
        self.assertTrue(result["coverage"]["requested_scope_complete"])
        self.assertFalse(result["coverage"]["whole_project"])
        self.assertEqual(result["coverage"]["native_component_counts"], "not_checked")

    def test_unreadable_context_fails_before_enumeration(self):
        self.prepare()
        self.base.ProjectService.GetProjectPath.return_value = (1, "")
        self.assert_code("context_unavailable", self.query)
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_missing_null_empty_zero_and_failed_reads_are_distinct(self):
        missing, null, empty, zero, failed = [self.adapter(ident=n) for n in range(1, 6)]
        null.GetAttributes.return_value = [(83, None)]
        empty.GetAttributes.return_value = [(83, "")]
        zero.GetAttributes.return_value = [(83, 0)]
        failed.GetAttributes.side_effect = RuntimeError("not readable")
        self.prepare([missing, null, empty, zero, failed])
        result = self.query(attribute_ids=[83])
        self.assertEqual([e["fields"]["attribute:83"]["status"] for e in result["elements"]],
                         ["missing", "observed", "observed", "observed", "not_checked"])
        self.assertFalse(result["coverage"]["returned_fields_complete"])
        predicate = {"field": "attribute:83", "op": "is_null"}
        result = self.query(predicate=predicate)
        self.assertEqual(result["counts"]["matched_model_identities"], 1)
        self.assertEqual(result["counts"]["predicate_not_checked"], 2)
        result = self.query(predicate={"not": {"field": "attribute:83", "op": "exists"}})
        self.assertEqual(result["counts"]["matched_model_identities"], 1)
        self.assertEqual(result["counts"]["predicate_not_checked"], 1)

    def test_composition_numeric_tolerance_and_string_normalization(self):
        first = self.adapter(attrs=[(83, " S02 "), (220, 400.5)])
        second = self.adapter(ident=2, attrs=[(83, "s02"), (220, 402)])
        self.prepare([first, second])
        node = {"all": [{"field": "attribute:83", "op": "eq", "value": "S02", "case_sensitive": False, "trim": True},
                        {"field": "attribute:220", "op": "eq", "value": 400, "tolerance": 1}]}
        self.assertEqual(self.query(predicate=node)["counts"]["matched_model_identities"], 1)
        self.assertEqual(self.query(predicate={"field": "attribute:83", "op": "eq", "value": "S02"})["counts"]["matched_model_identities"], 0)
        fields = {"attribute:83": {"status": "not_checked", "value": None}, "layer_id": {"status": "observed", "value": 7}}
        unknown = {"field": "attribute:83", "op": "eq", "value": "S02"}
        true = {"field": "layer_id", "op": "eq", "value": 7}
        false = {"field": "layer_id", "op": "eq", "value": 9}
        self.assertIsNone(self.contracts.evaluate({"not": unknown}, fields))
        self.assertTrue(self.contracts.evaluate({"any": [unknown, true]}, fields))
        self.assertFalse(self.contracts.evaluate({"all": [unknown, false]}, fields))
        self.assertIsNone(self.contracts.evaluate({"all": [unknown, true]}, fields))

    def test_scalar_types_are_not_coerced_and_ordered_type_mismatch_is_unknown(self):
        self.prepare()
        field = "attribute:83"
        for actual, expected, match in [(True, 1, False), ("400", 400, False), (400, 400.0, True), ("S02", "s02", False)]:
            node = {"field": field, "op": "eq", "value": expected}
            self.assertEqual(self.contracts.evaluate(node, {field: {"status": "observed", "value": actual}}), match)
        self.assertIsNone(self.contracts.evaluate({"field": field, "op": "gt", "value": 400}, {field: {"status": "observed", "value": "401"}}))
        for op, number, expected in [("gt", 402, True), ("gt", 401, False), ("gte", 399, True), ("lt", 399, False), ("lte", 401, True), ("ne", 401, False)]:
            self.assertEqual(self.contracts.evaluate({"field": field, "op": op, "value": 400, "tolerance": 1},
                                                    {field: {"status": "observed", "value": number}}), expected)

    def test_duplicate_views_collapse_but_differing_values_do_not_pick_an_arbitrary_representation(self):
        first, second, conflict = self.adapter(), self.adapter(view=2), self.adapter(view=3, layer=9)
        self.prepare([first, second])
        result = self.query()
        self.assertEqual(result["counts"]["matched_model_identities"], 1)
        self.assertEqual(len(result["elements"][0]["view_uuids"]), 2)
        self.base.ElementsSelectService.SelectAllElements.return_value = [first, conflict]
        result = self.query()
        self.assertEqual(result["counts"]["conflicting_model_identities"], 1)
        self.assertEqual(result["counts"]["matched_model_identities"], 0)
        self.assertFalse(result["coverage"]["requested_scope_complete"])

    def test_unknown_identity_is_omitted_and_invalid_file_identity_is_reported(self):
        bad_model, bad_type, bad_file = self.adapter(), self.adapter(ident=2), self.adapter(ident=3)
        bad_model.GetModelElementUUID.return_value = "<repr>"
        bad_type.GetElementAdapterType.return_value.GetGuid.return_value = "00000000-0000-0000-0000-000000000000"
        bad_file.GetDrawingfileNumber.side_effect = RuntimeError()
        self.prepare([bad_model, bad_type, bad_file])
        result = self.query()
        self.assertEqual(result["counts"]["identity_not_checked"], 2)
        self.assertEqual(result["counts"]["file_identity_not_checked"], 1)
        self.assertEqual(result["elements"], [])
        self.assertFalse(result["coverage"]["requested_scope_complete"])

    def test_fields_are_read_only_when_requested_or_used_by_predicate(self):
        adapter = self.adapter(attrs=[(83, "S02"), (99, "private")])
        self.prepare([adapter])
        result = self.query(fields=[])
        self.assertEqual(set(result["elements"][0]["fields"]), {"type_name", "type_uuid"})
        adapter.GetAttributes.assert_not_called()
        adapter.GetCommonProperties.assert_not_called()
        adapter.GetDisplayName.assert_not_called()
        adapter.GetModelGeometry.assert_not_called()
        result = self.query(fields=[], predicate={"field": "attribute:83", "op": "contains", "value": "S"})
        self.assertEqual(result["elements"][0]["fields"]["attribute:83"]["value"], "S02")
        self.assertNotIn("attribute:99", result["elements"][0]["fields"])
        adapter.GetAttributes.assert_called_once_with(self.base.eAttibuteReadState.ReadAll)

    def test_pages_are_stable_and_summary_uses_all_targets_not_just_the_first_page(self):
        adapters = [self.adapter(ident=i) for i in [3, 1, 2]]
        self.prepare(adapters)
        result = self.query(page_size=1)
        ids = [result["elements"][0]["ref"]["model_uuid"]]
        self.assertFalse(result["page"]["is_full_selection"])
        self.base.ElementsSelectService.SelectAllElements.return_value = list(reversed(adapters))
        current = result
        while current["page"]["next_cursor"]:
            current = self.follow(result, cursor=current["page"]["next_cursor"], page_size=1)
            ids.extend(e["ref"]["model_uuid"] for e in current["elements"])
        self.assertEqual(len(set(ids)), 3)
        self.assertEqual(ids, sorted(ids))
        summary = self.follow(result, action="summary")
        self.assertEqual(summary["summary"]["type_names"], {"Column_TypeUUID": 3})
        self.assertTrue(summary["summary_uses_full_selection"])
        self.assertEqual(summary["source_fingerprint"], result["source_fingerprint"])

    def test_change_to_rejected_candidate_new_identity_and_deletion_invalidate_selection(self):
        first, second = self.adapter(), self.adapter(ident=2, layer=9)
        self.prepare([first, second])
        changes = [lambda: setattr(second.GetCommonProperties.return_value, "Layer", 7),
                   lambda: setattr(self.base.ElementsSelectService.SelectAllElements, "return_value", [first]),
                   lambda: setattr(self.base.ElementsSelectService.SelectAllElements, "return_value", [first, second, self.adapter(ident=3)])]
        for change in changes:
            second.GetCommonProperties.return_value.Layer = 9
            self.base.ElementsSelectService.SelectAllElements.return_value = [first, second]
            result = self.query(predicate={"field": "layer_id", "op": "eq", "value": 7})
            change()
            self.assert_code("selection_stale", lambda: self.follow(result))
            self.assert_code("selection_unavailable", lambda: self.follow(result))

    def test_project_document_and_scoped_file_state_changes_invalidate(self):
        self.prepare([self.adapter()])
        result = self.query()
        self.coord.GetInputViewDocument.return_value.GetDocumentID.return_value = 99
        self.assert_code("selection_stale", lambda: self.follow(result))
        result = self.query()
        self.base.ProjectService.GetCurrentProjectNameAndHost.return_value = ("Other", "local")
        self.assert_code("selection_stale", lambda: self.follow(result))
        result = self.query()
        self.base.DrawingFileService.return_value.GetFileState.return_value = [(101, 1)]
        self.assert_code("selection_stale", lambda: self.follow(result))

    def test_unrequested_attributes_and_outside_scope_changes_do_not_invalidate(self):
        first, outside = self.adapter(attrs=[(83, "S02")]), self.adapter(104, 2)
        self.prepare([first, outside])
        result = self.query()
        first.GetAttributes.return_value = [(83, "S03")]
        outside.GetCommonProperties.return_value.Layer = 55
        self.assertEqual(self.follow(result)["source_fingerprint"], result["source_fingerprint"])

    def test_expiry_eviction_restart_and_cross_selection_cursors(self):
        self.prepare([self.adapter(), self.adapter(ident=2)])
        service = self.handler.model_queries
        now = [100]
        service.clock = lambda: now[0]
        first, second = self.query(page_size=1), self.query(page_size=1)
        self.assert_code("invalid_cursor", lambda: self.follow(second, cursor=first["page"]["next_cursor"]))
        now[0] += 300
        self.assert_code("selection_unavailable", lambda: self.follow(first))
        first = self.query()
        for _ in range(8):
            self.query()
        self.assert_code("selection_unavailable", lambda: self.follow(first))
        result = self.query()
        self.handler = self.module.RequestHandler(self.coord)
        self.assert_code("selection_unavailable", lambda: self.follow(result))

    def test_scan_budget_and_read_failures_do_not_create_partial_selections(self):
        self.prepare([self.adapter(), self.adapter(ident=2)])
        self.assert_code("scan_limit_exceeded", lambda: self.query(max_adapters=1))
        self.assertEqual(len(self.handler.model_queries.selections), 0)
        self.base.ElementsSelectService.SelectAllElements.side_effect = RuntimeError()
        self.assert_code("query_read_failed", self.query)
        self.assertEqual(len(self.handler.model_queries.selections), 0)

    def test_selection_is_unverifiable_when_context_or_enumeration_fails(self):
        self.prepare([self.adapter()])
        result = self.query()
        self.base.ElementsSelectService.SelectAllElements.side_effect = RuntimeError()
        self.assert_code("selection_unverifiable", lambda: self.follow(result))
        self.assert_code("selection_unavailable", lambda: self.follow(result))

    def test_selection_responses_cannot_mutate_cached_state(self):
        self.prepare([self.adapter(attrs=[(83, "S02")])])
        result = self.query(attribute_ids=[83])
        original = copy.deepcopy(result)
        result["elements"][0]["fields"]["attribute:83"]["value"] = "CHANGED"
        result["scope"]["requested"]["drawing_files"].append(999)
        self.assertEqual(self.follow(original)["elements"], original["elements"])

    def test_snapshot_and_time_budgets_do_not_leave_partial_selections(self):
        adapter = self.adapter()
        self.prepare([adapter])
        service = self.handler.model_queries
        service.MAX_SNAPSHOT_BYTES = 1
        self.assert_code("scan_limit_exceeded", self.query)
        self.assertEqual(len(service.selections), 0)
        service.MAX_SNAPSHOT_BYTES = 4 * 1024 * 1024
        now = [100]
        service.clock = lambda: now[0]
        def slow_read():
            now[0] += 6
            return "Column"
        adapter.GetDisplayName.side_effect = slow_read
        self.assert_code("scan_limit_exceeded", self.query)
        self.assertEqual(len(service.selections), 0)

    def test_passive_sign_conflicts_and_duplicate_attribute_ids_are_not_silently_resolved(self):
        signed_conflict = self.adapter(-101)
        duplicate_attrs = self.adapter(ident=2, attrs=[(83, "S01"), (83, "S02")])
        self.prepare([signed_conflict, duplicate_attrs])
        result = self.query(attribute_ids=[83])
        self.assertEqual(result["counts"]["file_state_conflicts"], 1)
        self.assertFalse(result["coverage"]["requested_scope_complete"])
        self.assertEqual(result["elements"][0]["fields"]["attribute:83"]["status"], "not_checked")
        self.assertEqual(result["not_checked_samples"][0]["reason"], "file_state_conflict")
