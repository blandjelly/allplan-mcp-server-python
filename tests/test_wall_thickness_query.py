"""Single-tier Wall thickness reads exposed through the M1 query contract."""
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

import test_m1_completion as fixtures
import test_wall_probe as wall_fixtures


class WallThicknessQueryTests(unittest.TestCase):
    setUp = fixtures.M1CompletionTests.setUp
    prepare_context = fixtures.M1CompletionTests.prepare_context
    prepare = fixtures.M1CompletionTests.prepare
    native = fixtures.M1CompletionTests.native
    adapter = fixtures.M1CompletionTests.adapter
    element = fixtures.M1CompletionTests.element
    request = fixtures.M1CompletionTests.request
    query = fixtures.M1CompletionTests.query

    def wall(self, thickness=200, tiers=1):
        tier = types.SimpleNamespace(Thickness=thickness)
        properties = types.SimpleNamespace(
            TierCount=tiers,
            GetWallTierProperties=MagicMock(return_value=tier))
        return wall_fixtures.WallElement(properties), properties, tier

    def install_arch_type(self):
        patcher = patch.dict(sys.modules, {
            "NemAll_Python_ArchElements": types.SimpleNamespace(WallElement=wall_fixtures.WallElement)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_lt_240_uses_native_tier_thickness_and_never_geometry(self):
        first = self.element(1, name="Wall_TypeUUID")
        second = self.element(2, name="Wall_TypeUUID")
        self.native([first, second])
        self.install_arch_type()
        wall_200, props_200, _ = self.wall(200)
        wall_240, props_240, _ = self.wall(240)
        self.base.GetElement.side_effect = lambda adapter: wall_200 if adapter is first else wall_240

        result = self.query(component_kind="semantic_component", fields=["wall.total_thickness_mm"],
                            predicate={"field": "wall.total_thickness_mm", "op": "lt", "value": 240})

        self.assertEqual(result["counts"]["matched_model_identities"], 1)
        self.assertEqual(result["counts"]["nonmatching_model_identities"], 1)
        self.assertEqual(result["elements"][0]["fields"]["wall.total_thickness_mm"],
                         {"status": "observed", "value": 200.0})
        self.assertEqual(self.base.GetElement.call_count, 2)
        props_200.GetWallTierProperties.assert_called_once_with(1)
        props_240.GetWallTierProperties.assert_called_once_with(1)
        for adapter in (first, second):
            adapter.GetModelGeometry.assert_not_called()

    def test_multitier_thickness_is_unknown_and_never_selects_a_tier(self):
        wall_adapter = self.element(1, name="Wall_TypeUUID")
        self.native([wall_adapter])
        self.install_arch_type()
        native_wall, properties, _ = self.wall(200, tiers=2)
        self.base.GetElement.return_value = native_wall

        result = self.query(component_kind="semantic_component", fields=["wall.total_thickness_mm"],
                            predicate={"field": "wall.total_thickness_mm", "op": "lt", "value": 240})

        self.assertEqual(result["counts"]["predicate_not_checked"], 1)
        self.assertEqual(result["counts"]["matched_model_identities"], 0)
        properties.GetWallTierProperties.assert_not_called()

    def test_existing_query_without_thickness_request_never_resolves_native_wall(self):
        wall_adapter = self.element(1, name="Wall_TypeUUID")
        self.native([wall_adapter])
        result = self.query(component_kind="semantic_component", fields=["layer_id"])
        self.assertEqual(result["counts"]["matched_model_identities"], 1)
        self.assertNotIn("wall.total_thickness_mm", result["elements"][0]["fields"])
        self.base.GetElement.assert_not_called()
        wall_adapter.GetModelGeometry.assert_not_called()

    def test_nonwall_and_unsupported_representation_fail_closed_without_geometry_fallback(self):
        column = self.element(1, name="Column_TypeUUID")
        self.native([column])
        self.install_arch_type()
        result = self.query(component_kind="semantic_component", fields=["wall.total_thickness_mm"],
                            predicate={"field": "wall.total_thickness_mm", "op": "lt", "value": 240})
        self.assertEqual(result["counts"]["predicate_not_checked"], 1)
        self.base.GetElement.assert_not_called()
        column.GetModelGeometry.assert_not_called()

        wall_adapter = self.element(2, name="Wall_TypeUUID")
        self.native([wall_adapter])
        self.base.GetElement.return_value = object()
        result = self.query(component_kind="semantic_component", fields=["wall.total_thickness_mm"],
                            predicate={"field": "wall.total_thickness_mm", "op": "lt", "value": 240})
        self.assertEqual(result["counts"]["predicate_not_checked"], 1)
        wall_adapter.GetModelGeometry.assert_not_called()

    def test_budget_bridge_error_propagates_without_becoming_unknown(self):
        wall_adapter = self.element(1, name="Wall_TypeUUID")
        self.native([wall_adapter])
        self.install_arch_type()
        native_wall, _, _ = self.wall(200)
        self.base.GetElement.return_value = native_wall
        readers = __import__("test_allplan_host.native_readers", fromlist=["wall_total_thickness"])
        calls = [0]
        def budget():
            calls[0] += 1
            if calls[0] == 4:
                raise self.module.BridgeError("scan_limit_exceeded", "budget", 409)
        with self.assertRaises(self.module.BridgeError) as error:
            readers.wall_total_thickness(wall_adapter, self.base, budget)
        self.assertEqual(error.exception.code, "scan_limit_exceeded")


if __name__ == "__main__":
    unittest.main()
