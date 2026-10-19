"""Bounded native Wall filtering and highlight boundaries with fakes only."""
import json
import importlib
import types
import unittest
import weakref
from unittest.mock import MagicMock, patch

import test_wall_probe as fixtures


class WallFilterTests(unittest.TestCase):
    setUp = fixtures.WallProbeTests.setUp
    prepare_context = fixtures.WallProbeTests.prepare_context
    prepare = fixtures.WallProbeTests.prepare
    adapter = fixtures.WallProbeTests.adapter
    native = fixtures.WallProbeTests.native
    element = fixtures.WallProbeTests.element
    assert_code = fixtures.WallProbeTests.assert_code
    fixture = fixtures.WallProbeTests.fixture
    records = fixtures.WallProbeTests.records

    def setUp_filter(self):
        fixtures.WallProbeTests.wall_fixture(self)
        service_type = importlib.import_module("test_allplan_host.wall_filter").WallFilterService
        self.service = service_type(self.handler.model_queries, self.path)
        self.ifw = self.module.AllplanIFW

    def request(self, **changes):
        return {"schema_version": "m4-wall-filter-1", "action": "query", "drawing_file": 101,
                "threshold": {"value": 24, "unit": "cm"}, **changes}

    def run_filter(self, **changes):
        result = self.service.handle(self.coord.GetInputViewDocument, self.base, self.settings,
                                     self.ifw, self.request(**changes))
        json.dumps(result, allow_nan=False)
        self.base.ModifyElements.assert_not_called()
        self.base.DeleteElements.assert_not_called()
        self.base.CreateElements.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        return result

    def add_walls(self, thicknesses):
        original = list(self.base.ElementsSelectService.SelectAllElements.return_value)
        first = original[1]
        others = [self.element(index + 3, name="Wall_TypeUUID") for index in range(len(thicknesses) - 1)]
        self.base.ElementsSelectService.SelectAllElements.return_value[:] = [*original, *others]
        wall_elements = [first, *others]
        native_walls = []
        for thickness in thicknesses:
            tier = types.SimpleNamespace(Thickness=thickness)
            props = types.SimpleNamespace(TierCount=1, GetWallTierProperties=MagicMock(return_value=tier))
            native_walls.append(fixtures.WallElement(props))
        self.base.GetElement.side_effect = lambda adapter: native_walls[wall_elements.index(adapter)]
        return wall_elements, native_walls

    def test_strict_threshold_and_unit_conversion_read_thickness_only(self):
        self.setUp_filter()
        _, native_walls = self.add_walls([180, 239.9, 240, 250])
        result = self.run_filter()
        self.assertEqual(result["state"], "observed")
        self.assertEqual(result["threshold"], {"property": "wall.total_thickness", "operator": "lt", "value": 240.0, "unit": "mm"})
        self.assertEqual([item["match"] for item in result["walls"]], [True, True, False, False])
        self.assertEqual([item["thickness_mm"] for item in result["walls"]], [180.0, 239.9, 240.0, 250.0])
        self.assertFalse(result["units_runtime_verified"])
        for adapter in self.base.ElementsSelectService.SelectAllElements.return_value:
            adapter.GetModelGeometry.assert_not_called()
            adapter.GetAttributes.assert_not_called()
        self.assertEqual(len([r for r in self.records() if r["api"] == "WallTierProperties.Thickness" and r["state"] == "started"]), 4)

    def test_mm_m_and_max_wall_count_guard_precedes_native_reads(self):
        self.setUp_filter()
        self.add_walls([200, 240])
        result = self.run_filter(threshold={"value": 239.9, "unit": "mm"})
        self.assertEqual(result["walls"][0]["match"], True)
        self.assertEqual(result["walls"][1]["match"], False)
        result = self.run_filter(threshold={"value": .24, "unit": "m"})
        self.assertEqual(result["threshold"]["value"], 240.0)
        self.base.GetElement.reset_mock()
        result = self.run_filter(max_walls=1)
        self.assertEqual(result["state"], "blocked")
        self.assertFalse(result["coverage"]["criteria_complete"])
        self.base.GetElement.assert_not_called()

    def test_exclusions_are_members_of_full_scope_and_skip_native_read(self):
        self.setUp_filter()
        adapters, native_walls = self.add_walls([200, 220])
        excluded = adapters[0].GetModelElementUUID()
        result = self.run_filter(exclude_model_uuids=[excluded])
        self.assertEqual(result["coverage"]["criteria_complete"], True)
        self.assertEqual(result["counts"]["excluded"], 1)
        self.assertEqual(result["walls"][0]["status"], "excluded")
        self.assertEqual(result["counts"]["matched"], 1)
        self.base.GetElement.assert_called_once_with(adapters[1])
        self.base.GetElement.reset_mock()
        stale = self.run_filter(exclude_model_uuids=["00000000-0000-4000-8000-000000000099"])
        self.assertEqual(stale["state"], "blocked")
        self.base.GetElement.assert_not_called()

    def test_highlight_clears_when_no_match_and_submits_only_matched_roots(self):
        self.setUp_filter()
        adapters, _ = self.add_walls([240, 250, 200])
        result = self.run_filter(action="highlight")
        self.assertEqual(result["state"], "submitted")
        self.ifw.HighlightService.CancelAllHighlightedElements.assert_called_once_with(42)
        submitted = self.ifw.HighlightService.HighlightElements.call_args.args[0]
        self.assertEqual(submitted, [adapters[2]])
        self.assertEqual(result["counts"]["submitted_model_identities"], 1)
        self.assertIsNone(result["counts"]["highlighted"])
        self.assertIsNone(result["counts"]["selected"])
        self.ifw.HighlightService.HighlightElements.reset_mock()
        result = self.run_filter(action="highlight", threshold={"value": 1, "unit": "mm"})
        self.assertEqual(result["state"], "submitted")
        self.ifw.HighlightService.CancelAllHighlightedElements.assert_called_with(42)
        self.ifw.HighlightService.HighlightElements.assert_not_called()

    def test_empty_wall_scope_is_complete_and_highlight_still_clears(self):
        self.setUp_filter()
        elements = self.base.ElementsSelectService.SelectAllElements.return_value
        elements[:] = [elements[0]]  # Keep the active file, but no Wall roots.
        result = self.run_filter(action="highlight")
        self.assertEqual(result["state"], "submitted")
        self.assertTrue(result["criterion_complete"])
        self.assertEqual(result["walls"], [])
        self.ifw.HighlightService.CancelAllHighlightedElements.assert_called_once_with(42)
        self.ifw.HighlightService.HighlightElements.assert_not_called()
        self.base.GetElement.assert_not_called()

    def test_same_root_wrappers_share_one_single_view_and_one_native_thickness_read(self):
        self.setUp_filter()
        root = self.base.ElementsSelectService.SelectAllElements.return_value[1]
        wrapper = self.element(2, name="Wall_TypeUUID")
        tier = self.element(3, name="WallTier_TypeUUID")
        axis = self.element(4, name="WallAxis_TypeUUID")
        self.parents[id(tier)] = wrapper
        self.parents[id(axis)] = root
        self.base.ElementsSelectService.SelectAllElements.return_value[:] = [tier, axis, root, wrapper]
        result = self.run_filter()
        self.assertEqual(result["counts"]["walls"], 1)
        self.assertEqual(result["state"], "observed")
        self.base.GetElement.assert_called_once()
        self.props.GetWallTierProperties.assert_called_once_with(1)

    def test_incomplete_foreground_scope_blocks_before_native_properties(self):
        self.setUp_filter()
        result = self.run_filter(drawing_file=102)
        self.assertEqual(result["state"], "blocked")
        self.assertFalse(result["coverage"]["m1_complete"])
        self.base.GetElement.assert_not_called()
        self.ifw.HighlightService.CancelAllHighlightedElements.assert_not_called()

    def test_multitier_or_failed_thickness_stops_before_later_wall_and_ui(self):
        self.setUp_filter()
        adapters, native_walls = self.add_walls([200, 210, 220])
        native_walls[1].Properties.TierCount = 2
        result = self.run_filter(action="highlight")
        self.assertEqual(result["state"], "blocked")
        self.assertEqual([w["status"] for w in result["walls"]], ["observed", "unsupported"])
        self.assertEqual(result["counts"]["unprocessed"], 1)
        self.ifw.HighlightService.CancelAllHighlightedElements.assert_not_called()
        self.ifw.HighlightService.HighlightElements.assert_not_called()
        self.assertEqual(native_walls[2].Properties.GetWallTierProperties.call_count, 0)

    def test_unreadable_thickness_stops_and_reports_completed_unprocessed(self):
        self.setUp_filter()
        adapters, native_walls = self.add_walls([200, 210, 220])
        native_walls[1].Properties.GetWallTierProperties.return_value.Thickness = float("nan")
        result = self.run_filter()
        self.assertEqual(result["state"], "blocked")
        self.assertEqual([w["status"] for w in result["walls"]], ["observed", "unreadable"])
        self.assertEqual(result["counts"]["unreadable"], 1)
        self.assertEqual(result["counts"]["unprocessed"], 1)
        self.assertEqual(native_walls[2].Properties.GetWallTierProperties.call_count, 0)

    def test_native_enumeration_owner_lives_through_all_thickness_reads(self):
        self.setUp_filter()
        adapters, native_walls = self.add_walls([200, 220])
        selected = self.base.ElementsSelectService.SelectAllElements.return_value
        class Owner(list):
            pass
        refs = []
        def enumerate_roots(_doc):
            owner = Owner(selected)
            refs.append(weakref.ref(owner))
            return owner
        self.base.ElementsSelectService.SelectAllElements.side_effect = enumerate_roots
        original_get = self.base.GetElement.side_effect
        def get(adapter):
            self.assertIsNotNone(refs[-1](), "M1 native owner released before Wall properties were read")
            return original_get(adapter)
        self.base.GetElement.side_effect = get
        result = self.run_filter()
        self.assertTrue(result["coverage"]["criteria_complete"])
        self.assertTrue(all(ref() is None for ref in refs))

    def test_budget_expiry_stops_before_following_wall_native_calls(self):
        self.setUp_filter()
        _, native_walls = self.add_walls([200, 220])
        clock = [0.0]
        self.service.queries.clock = lambda: clock[0]
        original_get = self.base.GetElement.side_effect
        def slow_get(adapter):
            result = original_get(adapter)
            clock[0] = 6.0
            return result
        self.base.GetElement.side_effect = slow_get
        result = self.run_filter(action="highlight")
        self.assertEqual(result["state"], "blocked")
        self.assertFalse(result["criterion_complete"])
        self.assertEqual(result["counts"]["unprocessed"], 1)
        self.assertEqual(self.base.GetElement.call_count, 1)
        self.assertEqual(native_walls[0].Properties.GetWallTierProperties.call_count, 0)
        self.ifw.HighlightService.CancelAllHighlightedElements.assert_not_called()

    def test_ambiguous_identity_incomplete_scope_and_stale_exception_do_not_read_properties(self):
        self.setUp_filter()
        self.add_walls([200, 210])
        # Conflicting duplicate representations must fail before any GetElement.
        root = self.base.ElementsSelectService.SelectAllElements.return_value[-1]
        duplicate = self.element(10, name="Wall_TypeUUID")
        duplicate.GetModelElementUUID.return_value = root.GetModelElementUUID()
        duplicate.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000099"
        self.base.ElementsSelectService.SelectAllElements.return_value.append(duplicate)
        result = self.run_filter()
        self.assertEqual(result["state"], "blocked")
        self.base.GetElement.assert_not_called()

    def test_invalid_contract_rejects_before_document_and_native_access(self):
        self.setUp_filter()
        invalid = [self.request(threshold={"value": True, "unit": "mm"}),
                   self.request(threshold={"value": float("inf"), "unit": "mm"}),
                   self.request(threshold={"value": 1001, "unit": "m"}),
                   self.request(threshold={"value": 2, "unit": "inch"}),
                   self.request(threshold={"value": 2, "unit": []}),
                   self.request(max_walls=101),
                   self.request(exclude_model_uuids=["00000000-0000-0000-0000-000000000000"]),
                   self.request(extra=True)]
        for request in invalid:
            with self.subTest(request=request):
                self.assert_code("invalid_payload", lambda: self.service.handle(
                    self.coord.GetInputViewDocument, self.base, self.settings, self.ifw, request))
        self.coord.GetInputViewDocument.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.GetElement.assert_not_called()

    def test_ui_failure_reports_unknown_and_trace_failure_prevents_ui_calls(self):
        self.setUp_filter()
        self.add_walls([200])
        self.ifw.HighlightService.HighlightElements.side_effect = RuntimeError("UI unavailable")
        result = self.run_filter(action="highlight")
        self.assertEqual(result["state"], "unknown")
        self.assertIsNone(result["counts"]["highlighted"])
        self.ifw.HighlightService.HighlightElements.reset_mock(side_effect=True)
        self.ifw.HighlightService.CancelAllHighlightedElements.reset_mock()
        self.service.trace_path = self.path.parent
        result = self.run_filter(action="highlight")
        self.assertEqual(result["state"], "blocked")
        self.ifw.HighlightService.CancelAllHighlightedElements.assert_not_called()

    def test_missing_highlight_symbol_is_detected_before_clearing_existing_highlights(self):
        self.setUp_filter()
        self.add_walls([200])
        self.ifw.HighlightService.HighlightElements = None
        result = self.run_filter(action="highlight")
        self.assertEqual(result["state"], "blocked")
        self.assertFalse(result["ui_calls_started"])
        self.assertTrue(result["criterion_complete"])
        self.assertTrue(result["is_full_wall_filter"])
        self.ifw.HighlightService.CancelAllHighlightedElements.assert_not_called()

    def test_final_trace_failure_after_highlight_reports_unknown_with_ui_started(self):
        self.setUp_filter()
        # Exercise the final trace failure independently of Windows fsync
        # latency. The native time-budget guards have separate clock tests.
        self.service.queries.clock = lambda: 0.0
        module = importlib.import_module("test_allplan_host.wall_filter")
        original = module.NativeProbeTrace.record
        def fail_completion(trace, api, state, **details):
            if api == "wall_filter" and state == "completed":
                raise module.BridgeError("probe_trace_unavailable", "full trace", 409)
            return original(trace, api, state, **details)
        with patch.object(module.NativeProbeTrace, "record", fail_completion):
            result = self.run_filter(action="highlight")
        self.assertEqual(result["state"], "unknown")
        self.assertIn("final trace record failed", result["message"])
        self.assertTrue(result["ui_calls_started"])
        self.ifw.HighlightService.HighlightElements.assert_called_once()
        self.assertTrue(result["criterion_complete"])

