"""Single-tier native Wall material edits with detached SDK object fakes."""
import copy
import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import PropertyMock, patch

from pydantic import TypeAdapter, ValidationError
from allplan_mcp.model_edit_models import ModelEditRequest
import test_model_edit as fixtures


class Polyhedron:
    def __init__(self, stream="wall-tier-geometry-v1"):
        self.stream = stream

    def IsValid(self):
        return True

    def WriteToStream(self):
        return 0, self.stream


class TierProperties:
    def __init__(self, material="C20/25"):
        values = {
            "Thickness": 240.0, "CalculationMode": 2, "CircleDivision": 24,
            "Factor": 1.25, "Priority": 7, "Trade": 3, "Name": "outer load bearing",
            "Status": 2, "Surface": "surface-existing", "BitmapName": "stone.bmp",
            "FaceStyle": 4, "Filling": "filling-existing", "Hatch": "hatch-existing",
            "Pattern": "pattern-existing", "BackgroundColor": 0x123456,
        }
        for name, value in values.items():
            setattr(self, name, value)
        self.Material = material
        self.CommonProperties = SimpleNamespace(
            Color=0x654321, ColorByLayer=False, ConstructionLine=True, DrawOrder=4,
            ForceColor=True, HelpConstruction=False, InSpecialWindow=False, Layer=17,
            PageNumber=2, Pen=5, PenByLayer=False, Printable=True, Stroke=6,
            StrokeByLayer=False, Visible=True, VisibleInsideZoomwindows=False,
            VisibleOutsideZoomwindows=True)
        self.PlaneReferences = ("top-plane-A", "bottom-plane-B")
        self.SurfaceElementProperties = {"surface": "preserve", "revision": 9}

    def SetMaterial(self, value):
        self.Material = value


class WallProperties:
    def __init__(self, material="C20/25", tier_count=1):
        self.TierCount = tier_count
        self.Axis = {"axis": "line", "start": [0, 0, 0], "end": [4000, 0, 0]}
        self.PathElementAxisType = 2
        self._tiers = [TierProperties(material) for _ in range(tier_count)]

    def GetWallTierProperties(self, index):
        return self._tiers[index - 1]


class FakeWallElement:
    def __init__(self, properties):
        self.Properties = properties

    def SetProperties(self, properties):
        self.Properties = properties


class WallMaterialEditTests(unittest.TestCase):
    def setUp(self):
        self.native = fixtures.ModelEditTests()
        self.native.setUp()
        self.addCleanup(self.native.doCleanups)
        self.root = self.native.fixture(("",))[0]
        self.root.GetElementAdapterType.return_value.GetTypeName.return_value = "Wall_TypeUUID"
        self.root.GetElementAdapterType.return_value.GetGuid.return_value = "20000000-0000-4000-8000-000000000001"
        self.root.GetCommonProperties.return_value.Layer = 17
        self.tier = self.native.element(10, name="WallTier_TypeUUID", solid=Polyhedron())
        for name, value in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                            ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                            ("IsLabelElement", False)):
            getattr(self.tier, name).return_value = value
        self.native.parents[id(self.tier)] = self.root
        self.native.children[id(self.root)] = [self.tier]
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root, self.tier]
        self.native.base.DrawingFileService.GetActiveFileNumber.return_value = 101
        self.material = "C20/25"
        self.properties = WallProperties(self.material)
        self.geometry_stream = ["wall-tier-geometry-v1"]
        self.sdk_modules = patch.dict(sys.modules, {
            "NemAll_Python_ArchElements": SimpleNamespace(WallElement=FakeWallElement),
            "NemAll_Python_Geometry": SimpleNamespace(
                Polyhedron3D=Polyhedron,
                eGeometryErrorCode=SimpleNamespace(eOK=0)),
        })
        self.sdk_modules.start()
        self.addCleanup(self.sdk_modules.stop)

        def get_wall(_adapter):
            props = copy.deepcopy(self.properties)
            if props._tiers:
                props._tiers[0].Material = self.material
            return FakeWallElement(props)

        self.native.base.GetElement.side_effect = get_wall

        def modify_elements(doc, elements):
            self.assertEqual(len(elements), 1)
            self.assertIsInstance(elements[0], FakeWallElement)
            self.properties = copy.deepcopy(elements[0].Properties)
            self.material = self.properties.GetWallTierProperties(1).Material
            return elements

        self.native.base.ModifyElements.side_effect = modify_elements

    def request(self, **updates):
        request = self.native.request(
            native_types=["Wall_TypeUUID"], predicate=None,
            changes=[{"target": {"kind": "native_material", "tier_index": 1}, "value": "C35/45"}])
        request.update(updates)
        return request

    def preview(self, **updates):
        return self.native.call(self.request(**updates))

    def snapshot_invariants(self):
        return {
            "scalars": {name: getattr(self.properties.GetWallTierProperties(1), name)
                        for name in ("Thickness", "CalculationMode", "CircleDivision", "Factor", "Priority",
                                     "Trade", "Name", "Status", "Surface", "BitmapName", "FaceStyle",
                                     "Filling", "Hatch", "Pattern", "BackgroundColor")},
            "common": vars(self.properties.GetWallTierProperties(1).CommonProperties).copy(),
            "axis": copy.deepcopy(self.properties.Axis),
            "path_axis_type": self.properties.PathElementAxisType,
            "planes": copy.deepcopy(self.properties.GetWallTierProperties(1).PlaneReferences),
            "surface_properties": copy.deepcopy(self.properties.GetWallTierProperties(1).SurfaceElementProperties),
            "geometry": self.tier.GetModelGeometry.return_value.stream,
        }

    def test_preview_highlight_apply_readback_replay_and_no_op_preserve_other_properties(self):
        before = self.snapshot_invariants()
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["counts"]["changes"], 1)
        change = plan["changes"][0]
        self.assertEqual(change["operation"], "set_native_material")
        self.assertEqual(change["field"], "wall.native_material")
        self.assertEqual(change["old_value"], {"status": "observed", "value": "C20/25"})
        self.assertEqual(change["new_value"], "C35/45")
        self.assertEqual(change["resource"]["tier_index"], 1)
        self.assertEqual(self.native.highlight(plan)["state"], "submitted")
        execution_id = uuid4().hex
        result = self.native.apply(plan, execution_id)
        self.assertEqual(result["state"], "completed", result)
        self.assertTrue(result["audited_fields_match_plan"])
        self.assertEqual(self.material, "C35/45")
        self.assertEqual(self.snapshot_invariants(), before)
        self.assertEqual(self.native.base.ModifyElements.call_count, 1)
        self.assertTrue(self.native.apply(plan, execution_id)["replayed"])
        self.assertEqual(self.native.base.ModifyElements.call_count, 1)
        self.assertEqual(self.preview()["state"], "no_op")

    def test_geometry_stream_drift_after_preview_conflicts_before_modify(self):
        plan = self.preview()
        self.native.highlight(plan)
        self.tier.GetModelGeometry.return_value.stream = "wall-tier-geometry-v2"
        self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
        self.native.base.ModifyElements.assert_not_called()

    def test_preservation_drift_after_preview_conflicts_before_modify(self):
        plan = self.preview()
        self.native.highlight(plan)
        self.properties.GetWallTierProperties(1).CommonProperties.Pen = 99
        self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
        self.native.base.ModifyElements.assert_not_called()

    def test_geometry_changed_by_modify_is_unknown_and_replay_never_repeats_modify(self):
        self.native.base.ModifyElements.side_effect = None

        def modify_and_change_geometry(doc, elements):
            self.properties = copy.deepcopy(elements[0].Properties)
            self.material = self.properties.GetWallTierProperties(1).Material
            self.tier.GetModelGeometry.return_value.stream = "mutated-by-modify"

        self.native.base.ModifyElements.side_effect = modify_and_change_geometry
        plan = self.preview()
        self.native.highlight(plan)
        execution_id = uuid4().hex
        result = self.native.apply(plan, execution_id)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.native.apply(plan, execution_id)["replayed"])
        self.assertEqual(self.native.base.ModifyElements.call_count, 1)

    def test_modify_no_op_is_failed_unchanged(self):
        self.native.base.ModifyElements.side_effect = lambda doc, elements: elements
        plan = self.preview()
        self.native.highlight(plan)
        result = self.native.apply(plan, uuid4().hex)
        self.assertEqual(result["outcomes"][0]["state"], "failed")
        self.assertEqual(result["outcomes"][0]["readback"], {"status": "observed", "value": "C20/25"})
        self.assertEqual(self.material, "C20/25")
        self.assertEqual(self.native.base.ModifyElements.call_count, 1)

    def test_multiple_tiers_and_openings_are_blocked_before_modify(self):
        for tier_count in (0, 2):
            with self.subTest(tier_count=tier_count):
                self.properties = WallProperties("C20/25", tier_count=tier_count)
                multi_tier = self.preview()
                self.assertFalse(multi_tier["apply_available"], multi_tier)
                self.assertFalse(multi_tier["changes"])
                blocker = next(item for item in multi_tier["blocked"]
                               if item["field"] == "wall.native_material")
                self.assertEqual(blocker["reason"], "old_value_unknown")
                self.assertEqual(blocker["observation"]["reason"],
                                 "wall_material_single_tier_required")
                self.assertEqual(blocker["observation"]["diagnostic"]["stage"],
                                 "material_tier_count")

        self.properties = WallProperties("C20/25", tier_count=1)
        opening = self.native.element(11, name="WindowDoor_TypeUUID")
        self.native.children[id(self.root)] = [self.tier, opening]
        self.native.parents[id(opening)] = self.root
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root, self.tier, opening]
        with_opening = self.preview()
        self.assertFalse(with_opening["apply_available"], with_opening)
        self.assertFalse(with_opening["changes"])
        self.assertEqual(with_opening["criteria"]["required_field_failures"], [])
        self.assertTrue(with_opening["criteria"]["operation_eligibility_failures"])
        opening_blocker = next(item for item in with_opening["blocked"]
                                if item["field"] == "wall.native_material")
        self.assertEqual(opening_blocker["reason"], "native_material_preservation_unavailable")
        self.assertEqual(opening_blocker["observation"]["reason"],
                         "wall_material_openings_unsupported")
        self.assertEqual(opening_blocker["observation"]["diagnostic"]["stage"],
                         "material_children")
        self.native.base.ModifyElements.assert_not_called()

    def test_unknown_wall_children_fail_closed_with_material_and_eligibility_separate(self):
        for child_type in ("Door_TypeUUID", "Window_TypeUUID", "Macro_TypeUUID",
                           "UnclassifiedChild_TypeUUID"):
            with self.subTest(child_type=child_type):
                self.native.base.ModifyElements.reset_mock()
                child = self.native.element(20, name=child_type)
                self.native.children[id(self.root)] = [self.tier, child]
                self.native.parents[id(child)] = self.root
                self.native.base.ElementsSelectService.SelectAllElements.return_value = [
                    self.root, self.tier, child]

                plan = self.preview()

                self.assertFalse(plan["apply_available"], plan)
                self.assertFalse(plan["changes"], plan)
                self.assertEqual(plan["criteria"]["required_field_failures"], [])
                self.assertTrue(plan["criteria"]["operation_eligibility_failures"])
                blocker = next(item for item in plan["blocked"]
                               if item["field"] == "wall.native_material")
                self.assertEqual(blocker["reason"], "native_material_preservation_unavailable")
                self.assertEqual(blocker["observation"]["reason"],
                                 "wall_material_child_type_unsupported")
                self.assertEqual(blocker["observation"]["diagnostic"]["stage"],
                                 "material_children")
                self.assertEqual(plan["criteria"]["checks"][0]["decision"], "matched")
                self.native.base.ModifyElements.assert_not_called()

    def test_already_desired_material_does_not_hide_unknown_child_eligibility_block(self):
        child = self.native.element(22, name="Door_TypeUUID")
        self.native.children[id(self.root)] = [self.tier, child]
        self.native.parents[id(child)] = self.root
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, child]
        request = self.request()
        request["changes"][0]["value"] = self.material

        plan = self.native.call(request)

        self.assertNotEqual(plan["state"], "no_op")
        self.assertFalse(plan["apply_available"], plan)
        self.assertFalse(plan["changes"], plan)
        self.assertEqual(plan["criteria"]["required_field_failures"], [])
        self.assertTrue(plan["criteria"]["operation_eligibility_failures"])
        blocker = next(item for item in plan["blocked"]
                       if item["field"] == "wall.native_material")
        self.assertEqual(blocker["old_value"], {"status": "observed", "value": self.material})
        self.assertEqual(blocker["reason"], "native_material_preservation_unavailable")
        self.assertEqual(blocker["observation"]["reason"],
                         "wall_material_child_type_unsupported")
        self.native.base.ModifyElements.assert_not_called()

    def test_material_read_failure_reports_unknown_field_and_eligibility_diagnostics(self):
        self.native.base.GetElement.side_effect = lambda _adapter: FakeWallElement(
            copy.deepcopy(self.properties))
        with patch.object(TierProperties, "Material", new_callable=PropertyMock, create=True,
                          side_effect=RuntimeError("private material getter detail")):
            with patch.object(TierProperties, "SetMaterial", autospec=True) as set_material, \
                 patch.object(FakeWallElement, "SetProperties", autospec=True) as set_properties:
                plan = self.preview()

        self.assertFalse(plan["apply_available"], plan)
        self.assertFalse(plan["changes"], plan)
        blocker = next(item for item in plan["blocked"]
                       if item["field"] == "wall.native_material")
        expected = {"status": "not_checked", "value": None,
                    "reason": "wall_material_read_unavailable",
                    "diagnostic": {"stage": "material_value", "error_type": "RuntimeError"}}
        self.assertEqual(blocker["reason"], "old_value_unknown")
        self.assertEqual(blocker["old_value"], expected)
        self.assertEqual(blocker["observation"], expected)
        required = next(item for item in plan["criteria"]["required_field_failures"]
                        if item["field"] == "wall.native_material")
        self.assertEqual(required["observation"], expected)
        eligibility = next(item for item in plan["criteria"]["operation_eligibility_failures"]
                           if item["field"] == "wall.native_material")
        self.assertEqual(eligibility["old_value"], expected)
        self.assertEqual(eligibility["observation"], expected)
        self.assertNotIn("private material getter detail", repr(plan))
        self.assertEqual(set_material.call_count, 0)
        self.assertEqual(set_properties.call_count, 0)
        self.native.base.ModifyElements.assert_not_called()

    def test_tier_with_child_is_blocked_as_unpreserved_hierarchy(self):
        tier_child = self.native.element(21, name="WallTierFace_TypeUUID")
        self.native.children[id(self.tier)] = [tier_child]
        self.native.parents[id(tier_child)] = self.tier
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, tier_child]

        plan = self.preview()

        self.assertFalse(plan["apply_available"], plan)
        self.assertFalse(plan["changes"], plan)
        blocker = next(item for item in plan["blocked"]
                       if item["field"] == "wall.native_material")
        self.assertEqual(blocker["reason"], "native_material_preservation_unavailable")
        self.assertEqual(blocker["observation"]["reason"],
                         "wall_material_tier_hierarchy_unsupported")
        self.assertEqual(blocker["observation"]["diagnostic"]["stage"], "material_tier_hierarchy")
        self.native.base.ModifyElements.assert_not_called()

    def test_changed_wall_child_enumeration_between_reads_blocks_before_modify(self):
        child_service = self.native.adapter_module.BaseElementAdapterChildElementsService
        original = child_service.GetChildModelElements
        root_reads = [0]

        def changing_children(adapter, include_hidden):
            if adapter is self.root:
                root_reads[0] += 1
                return [self.tier] if root_reads[0] == 1 else []
            return original(adapter, include_hidden)

        child_service.GetChildModelElements = changing_children
        plan = self.preview()

        self.assertFalse(plan["apply_available"], plan)
        self.assertFalse(plan["changes"], plan)
        blocker = next(item for item in plan["blocked"]
                       if item["field"] == "wall.native_material")
        self.assertEqual(blocker["reason"], "native_material_preservation_unavailable")
        self.assertEqual(blocker["observation"]["reason"],
                         "wall_material_one_exact_tier_required")
        self.assertEqual(blocker["observation"]["diagnostic"]["stage"], "material_children")
        self.assertGreaterEqual(root_reads[0], 2)
        self.native.base.ModifyElements.assert_not_called()

    def test_missing_preservation_evidence_is_rejected_at_final_setter(self):
        plan = self.preview()
        change = plan["changes"][0]
        del change["resource"]["wall_material_state"]
        native = importlib.import_module(self.native.module.__package__ + ".native_model_edit")
        self.native.assert_code("target_not_writable", lambda: native.write(self.native.base, self.root, change))
        self.native.base.ModifyElements.assert_not_called()

    def test_final_material_write_guard_stops_when_budget_expires(self):
        plan = self.preview()
        native = importlib.import_module(self.native.module.__package__ + ".native_model_edit")
        bridge_error = importlib.import_module(self.native.module.__package__ + ".transport").BridgeError

        def expired():
            raise bridge_error("scan_limit_exceeded", "Injected final write budget expiry", 409)

        self.native.assert_code("scan_limit_exceeded", lambda: native.write(
            self.native.base, self.root, plan["changes"][0], check=expired))
        self.native.base.ModifyElements.assert_not_called()

    def test_missing_common_pen_has_bounded_diagnostic_and_blocks_without_setters(self):
        del self.properties.GetWallTierProperties(1).CommonProperties.Pen
        module = importlib.import_module(self.native.module.__package__ + ".wall_material")
        with patch.object(TierProperties, "SetMaterial", autospec=True) as set_material, \
             patch.object(FakeWallElement, "SetProperties", autospec=True) as set_properties:
            plan = self.preview()

        old_value, preservation_state, preservation = module.preview_observation(
            self.native.base, self.root)
        self.assertEqual(old_value, {"status": "observed", "value": "C20/25"})
        self.assertIsNone(preservation_state)
        self.assertEqual(preservation["reason"], "wall_material_read_unavailable")
        self.assertEqual(preservation["diagnostic"],
                         {"stage": "material_common_Pen", "error_type": "AttributeError"})
        expected = {"status": "not_checked", "value": None,
                    "reason": "wall_material_read_unavailable",
                    "diagnostic": {"stage": "material_common_Pen", "error_type": "AttributeError"}}
        observed, state = module.observation(self.native.base, self.root)
        self.assertEqual(observed, expected)
        self.assertIsNone(state)
        self.assertFalse(plan["apply_available"], plan)
        blocker = next(item for item in plan["blocked"]
                       if item["field"] == "wall.native_material")
        self.assertEqual(blocker["reason"], "native_material_preservation_unavailable")
        self.assertEqual(blocker["observation"]["reason"], "wall_material_read_unavailable")
        self.assertEqual(blocker["observation"]["diagnostic"]["stage"], "material_common_Pen")
        self.assertEqual(plan["criteria"]["required_field_failures"], [])
        self.assertEqual(plan["criteria"]["operation_eligibility_failures"][0]["field"],
                         "wall.native_material")
        self.assertNotIn("CommonProperties", repr(plan))
        self.assertEqual(set_material.call_count, 0)
        self.assertEqual(set_properties.call_count, 0)
        self.native.base.ModifyElements.assert_not_called()

    def test_unstable_axis_repr_has_bounded_diagnostic_without_exception_message(self):
        secret = "axis repr must not escape"

        class UnstableAxis:
            def __repr__(self):
                raise ValueError(secret)

        self.properties.Axis = UnstableAxis()
        module = importlib.import_module(self.native.module.__package__ + ".wall_material")
        old_value, preservation_state, preservation = module.preview_observation(
            self.native.base, self.root)
        self.assertEqual(old_value, {"status": "observed", "value": "C20/25"})
        self.assertIsNone(preservation_state)
        self.assertEqual(preservation["reason"], "wall_material_read_unavailable")
        self.assertEqual(preservation["diagnostic"],
                         {"stage": "material_axis", "error_type": "ValueError"})
        observed, state = module.observation(self.native.base, self.root)
        self.assertEqual(observed, {"status": "not_checked", "value": None,
            "reason": "wall_material_read_unavailable",
            "diagnostic": {"stage": "material_axis", "error_type": "ValueError"}})
        self.assertIsNone(state)
        self.assertNotIn(secret, repr(observed))
        plan = self.preview()
        self.assertFalse(plan["apply_available"], plan)
        blocker = next(item for item in plan["blocked"]
                       if item["field"] == "wall.native_material")
        self.assertEqual(blocker["reason"], "native_material_preservation_unavailable")
        self.assertEqual(blocker["observation"]["diagnostic"]["stage"], "material_axis")
        self.assertEqual(plan["criteria"]["required_field_failures"], [])
        self.assertEqual(plan["criteria"]["operation_eligibility_failures"][0]["field"],
                         "wall.native_material")
        self.assertNotIn(secret, repr(plan))
        self.native.base.ModifyElements.assert_not_called()

    def test_material_observation_propagates_budget_and_trace_bridge_errors(self):
        module = importlib.import_module(self.native.module.__package__ + ".wall_material")
        bridge_error = importlib.import_module(self.native.module.__package__ + ".transport").BridgeError
        for code in ("scan_limit_exceeded", "trace_write_failed"):
            with self.subTest(code=code):
                error = bridge_error(code, "private bridge detail", 409)

                def stop(error=error):
                    raise error

                with self.assertRaises(bridge_error) as raised:
                    module.observation(self.native.base, self.root, stop)
                self.assertIs(raised.exception, error)
                self.assertEqual(raised.exception.code, code)
        self.native.base.ModifyElements.assert_not_called()

    def test_material_contract_requires_literal_tier_one_and_exact_nonempty_text(self):
        host_contracts = importlib.import_module(self.native.module.__package__ + ".model_edit_contracts")
        TypeAdapter(ModelEditRequest).validate_python(self.request())
        host_contracts.validate_request(self.request())
        bad_requests = []
        for tier_index in (True, 1.0, 2):
            request = self.request()
            request["changes"][0]["target"]["tier_index"] = tier_index
            bad_requests.append(request)
        missing = self.request()
        del missing["changes"][0]["target"]["tier_index"]
        bad_requests.append(missing)
        for value in ("   ", "C35\n/45"):
            request = self.request()
            request["changes"][0]["value"] = value
            bad_requests.append(request)
        for request in bad_requests:
            with self.subTest(request=request):
                with self.assertRaises(ValidationError):
                    TypeAdapter(ModelEditRequest).validate_python(request)
                self.native.assert_code("invalid_payload", lambda: host_contracts.validate_request(request))

    def test_non_geometry_scalar_drift_conflicts_before_modify(self):
        plan = self.preview()
        self.native.highlight(plan)
        self.properties.GetWallTierProperties(1).Thickness = 241.0
        self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
        self.native.base.ModifyElements.assert_not_called()

    def test_lost_modify_reply_recovers_read_only_without_repeating_modify(self):
        def modify_then_lose_reply(doc, elements):
            self.properties = copy.deepcopy(elements[0].Properties)
            self.material = self.properties.GetWallTierProperties(1).Material
            raise RuntimeError("ModifyElements committed but response was lost")

        self.native.base.ModifyElements.side_effect = modify_then_lose_reply
        plan = self.preview()
        self.native.highlight(plan)
        execution_id = uuid4().hex
        result = self.native.apply(plan, execution_id)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.native.apply(plan, execution_id)["replayed"])
        self.native.base.ModifyElements.assert_called_once()
        self.native.base.ModifyElements.reset_mock()
        recovered = self.native.recover(execution_id)
        self.assertTrue(recovered["read_only"])
        self.assertEqual(recovered["outcomes"][0]["state"], "reconciled")
        self.assertEqual(recovered["recovery"]["observations"][0]["state"], "new_value_observed")
        self.native.base.ModifyElements.assert_not_called()

