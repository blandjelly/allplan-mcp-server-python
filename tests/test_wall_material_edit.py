"""Single-tier native Wall material edits with detached SDK object fakes."""
import copy
import importlib
import json
import sys
import types
import unittest
import weakref
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

    def alternate_wall_view(self, index):
        """Return another view wrapper for the same native Wall model."""
        alias = self.native.element(index, name="Wall_TypeUUID")
        alias.GetDrawingfileNumber.return_value = self.root.GetDrawingfileNumber.return_value
        alias.GetModelElementUUID.return_value = self.root.GetModelElementUUID.return_value
        alias.GetElementAdapterType.return_value.GetTypeName.return_value = "Wall_TypeUUID"
        alias.GetElementAdapterType.return_value.GetGuid.return_value = (
            self.root.GetElementAdapterType.return_value.GetGuid.return_value)
        return alias

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
        self.assertEqual(change["field"], "native.material")
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

    def test_detailed_tier_keeps_its_native_owners_through_optional_reads(self):
        module = importlib.import_module(self.native.module.__package__ + ".wall_material")
        owners = []

        class BorrowedTier(TierProperties):
            def __getattribute__(self, name):
                if name in module._SCALARS or name in {"CommonProperties", "PlaneReferences", "SurfaceElementProperties"}:
                    refs = object.__getattribute__(self, "owner_refs")
                    if any(ref() is None for ref in refs):
                        raise RuntimeError("Native property owner was released")
                return super().__getattribute__(name)

        def get_wall(_adapter):
            props = WallProperties(self.material)
            native = FakeWallElement(props)
            tier = BorrowedTier(self.material)
            tier.owner_refs = weakref.ref(native), weakref.ref(props)
            props._tiers = [tier]
            owners.append(tier.owner_refs)
            return native

        self.native.base.GetElement.side_effect = get_wall
        _, state, native, props = module.snapshot(self.native.base, self.root)
        self.assertEqual(len(owners), 2)  # Keep the independent material comparison.
        self.assertEqual(state["optional_properties"]["tier"]["Thickness"], 240.0)
        self.assertEqual(state["optional_properties"]["common"]["Pen"], 5)
        self.assertIs(owners[1][0](), native)
        self.assertIs(owners[1][1](), props)
        self.assertTrue(all(ref() is None for ref in owners[0]))
        self.native.base.ModifyElements.assert_not_called()

    def test_second_material_read_still_rejects_drift(self):
        module = importlib.import_module(self.native.module.__package__ + ".wall_material")
        count = [0]

        def get_wall(_adapter):
            count[0] += 1
            return FakeWallElement(WallProperties(self.material if count[0] == 1 else "changed"))

        self.native.base.GetElement.side_effect = get_wall
        self.native.assert_code("repair_conflict", lambda: module.snapshot(self.native.base, self.root))
        self.native.base.ModifyElements.assert_not_called()

    def test_material_trace_is_durable_before_getter_and_has_exact_root_view(self):
        path = self.native.plans.trace_path
        accesses = []

        def material(*args):
            if args:  # The fake's constructor sets its detached property.
                return
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            last = records[-1]
            self.assertEqual((last["api"], last["state"]), ("WallTierProperties.Material", "started"))
            self.assertEqual(last["drawing_file"], 101)
            self.assertEqual(last["model_uuid"], self.root.GetModelElementUUID())
            self.assertEqual(last["view_uuid"], self.root.GetElementUUID())
            accesses.append(last)
            return "C20/25"

        with patch.object(TierProperties, "Material", new_callable=PropertyMock, create=True) as value:
            value.side_effect = material
            plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.assertTrue(accesses)
        trace_text = path.read_text(encoding="utf-8")
        self.assertNotIn("C20/25", trace_text)
        self.assertNotIn("C35/45", trace_text)
        self.native.base.ModifyElements.assert_not_called()

    def test_trace_failure_prevents_material_getter_and_remains_a_bridge_error(self):
        module = importlib.import_module(self.native.module.__package__ + ".wall_material")
        trace_module = importlib.import_module(self.native.module.__package__ + ".property_probe")
        trace = trace_module.NativeProbeTrace(self.native.plans.trace_path, "material_test")
        record = trace.record
        accesses = []

        def record_or_stop(api, state, **details):
            if api == "WallTierProperties.Material" and state == "started":
                raise self.native.module.BridgeError("probe_trace_unavailable", "Injected storage failure", 409)
            return record(api, state, **details)

        def material(*args):
            if not args:
                accesses.append(True)
            return "C20/25"

        trace.record = record_or_stop
        with patch.object(TierProperties, "Material", new_callable=PropertyMock, create=True) as value:
            value.side_effect = material
            self.native.assert_code("probe_trace_unavailable", lambda: module.preview_observation(
                self.native.base, self.root, trace=trace))
        self.assertEqual(accesses, [])
        self.native.base.ModifyElements.assert_not_called()

    def test_material_accepts_same_model_parent_view_and_binds_observed_edge(self):
        parent_view = self.alternate_wall_view(20)
        self.native.parents[id(self.tier)] = parent_view
        # Keep the exact Wall view as the query target. The material adapter
        # separately observes the tier's parent wrapper and must bind that edge.
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root]

        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        state = plan["changes"][0]["resource"]["native_material_state"]
        edge = state["hierarchy"]["child_parent_edges"][0]
        self.assertEqual(edge["parent"]["view_uuid"], parent_view.GetElementUUID())
        self.assertEqual(state["tier_hierarchy"]["lineage"][1]["view_uuid"],
                         parent_view.GetElementUUID())
        self.assertNotEqual(edge["parent"]["view_uuid"], self.root.GetElementUUID())

        self.native.highlight(plan)
        result = self.native.apply(plan, uuid4().hex)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(self.material, "C35/45")
        self.assertEqual(result["outcomes"][0]["readback"],
                         {"status": "observed", "value": "C35/45"})
        self.native.base.ModifyElements.assert_called_once()

    def test_material_parent_view_drift_conflicts_before_modify(self):
        parent_view = self.alternate_wall_view(23)
        self.native.parents[id(self.tier)] = parent_view
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root]
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.native.highlight(plan)

        self.native.parents[id(self.tier)] = self.alternate_wall_view(24)
        self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
        self.native.base.ModifyElements.assert_not_called()

    def test_auxiliary_tier_parent_mismatch_is_a_preservation_diagnostic(self):
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root]
        for mismatch in ("model", "type", "file"):
            with self.subTest(mismatch=mismatch):
                parent_view = self.alternate_wall_view(21)
                if mismatch == "model":
                    parent_view.GetModelElementUUID.return_value = (
                        self.native.element(22).GetModelElementUUID.return_value)
                elif mismatch == "type":
                    parent_view.GetElementAdapterType.return_value.GetTypeName.return_value = "Door_TypeUUID"
                else:
                    parent_view.GetDrawingfileNumber.return_value = 102
                self.native.parents[id(self.tier)] = parent_view

                plan = self.preview()
                self.assertTrue(plan["apply_available"], plan)
                blocker = plan["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
                self.assertEqual(blocker["reason"],
                                 "component_child_owner_mismatch")
                self.native.base.ModifyElements.assert_not_called()

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

    def test_multiple_tiers_are_blocked_and_opening_shape_is_eligible(self):
        for tier_count in (0, 2):
            with self.subTest(tier_count=tier_count):
                self.properties = WallProperties("C20/25", tier_count=tier_count)
                multi_tier = self.preview()
                self.assertFalse(multi_tier["apply_available"], multi_tier)
                self.assertFalse(multi_tier["changes"])
                blocker = next(item for item in multi_tier["blocked"]
                               if item["field"] == "native.material")
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
        self.assertTrue(with_opening["apply_available"], with_opening)
        self.assertEqual(with_opening["counts"]["changes"], 1)
        self.assertEqual(with_opening["criteria"]["required_field_failures"], [])
        self.assertEqual(with_opening["criteria"]["operation_eligibility_failures"], [])
        self.native.highlight(with_opening)
        result = self.native.apply(with_opening)
        self.assertEqual(result["state"], "completed", result)
        self.native.base.ModifyElements.assert_called_once()

    def test_auxiliary_wall_child_types_are_eligible_with_explicit_geometry_coverage(self):
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

                self.assertTrue(plan["apply_available"], plan)
                self.assertEqual(plan["counts"]["changes"], 1)
                self.assertEqual(plan["criteria"]["required_field_failures"], [])
                self.assertEqual(plan["criteria"]["operation_eligibility_failures"], [])
                evidence = plan["changes"][0]["resource"]["native_material_state"]["auxiliary_components"]["root"][0]
                self.assertEqual(evidence["ownership"]["target"]["type_name"], child_type)
                self.assertEqual(evidence["geometry"]["status"], "not_checked")
                self.assertEqual(plan["criteria"]["checks"][0]["decision"], "matched")
                self.native.base.ModifyElements.assert_not_called()

    def test_already_desired_material_with_auxiliary_child_is_no_op(self):
        child = self.native.element(22, name="Door_TypeUUID")
        self.native.children[id(self.root)] = [self.tier, child]
        self.native.parents[id(child)] = self.root
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, child]
        request = self.request()
        request["changes"][0]["value"] = self.material

        plan = self.native.call(request)

        self.assertEqual(plan["state"], "no_op")
        self.assertFalse(plan["apply_available"], plan)
        self.assertFalse(plan["changes"], plan)
        self.assertEqual(plan["criteria"]["required_field_failures"], [])
        self.assertEqual(plan["criteria"]["operation_eligibility_failures"], [])
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
                       if item["field"] == "native.material")
        expected = {"status": "not_checked", "value": None,
                    "reason": "native_material_read_unavailable",
                    "diagnostic": {"stage": "material_value", "error_type": "RuntimeError"}}
        self.assertEqual(blocker["reason"], "old_value_unknown")
        self.assertEqual(blocker["old_value"], expected)
        self.assertEqual(blocker["observation"], expected)
        required = next(item for item in plan["criteria"]["required_field_failures"]
                        if item["field"] == "native.material")
        self.assertEqual(required["observation"], expected)
        eligibility = next(item for item in plan["criteria"]["operation_eligibility_failures"]
                           if item["field"] == "native.material")
        self.assertEqual(eligibility["old_value"], expected)
        self.assertEqual(eligibility["observation"], expected)
        self.assertNotIn("private material getter detail", repr(plan))
        self.assertEqual(set_material.call_count, 0)
        self.assertEqual(set_properties.call_count, 0)
        self.native.base.ModifyElements.assert_not_called()

    def test_reported_240mm_wall_axis_under_tier_allows_material_apply(self):
        self.material = "Beton"
        tier_child = self.native.element(21, name="WallAxis_TypeUUID")
        tier_child.GetModelGeometry.return_value = SimpleNamespace()
        self.native.children[id(self.tier)] = [tier_child]
        self.native.parents[id(tier_child)] = self.tier
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, tier_child]

        plan = self.preview(changes=[{"target": {"kind": "native_material", "tier_index": 1}, "value": "Silikat"}])

        self.assertTrue(plan["apply_available"], plan)
        evidence = plan["changes"][0]["resource"]["native_material_state"]["auxiliary_components"]["tier"][0]
        self.assertEqual(evidence["ownership"]["lineage"][1]["model_uuid"], self.tier.GetModelElementUUID())
        self.assertEqual(evidence["ownership"]["target"]["type_name"], "WallAxis_TypeUUID")
        self.assertEqual(evidence["geometry"], {"status": "not_checked", "reason": "geometry_stream_unsupported"})
        self.native.highlight(plan)
        result = self.native.apply(plan, uuid4().hex)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(self.material, "Silikat")
        self.native.base.ModifyElements.assert_called_once()

    def auxiliary_tree(self):
        """A mixed subtree that previously failed several child-shape guards."""
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        opening = self.native.element(51, name="WindowDoor_TypeUUID", solid=Polyhedron("opening"))
        macro = self.native.element(52, name="Macro_TypeUUID", solid=Polyhedron("macro"))
        metadata = self.native.element(53, name="AttributeContainer_TypeUUID", solid=Polyhedron("metadata"))
        metadata.GetAttributes.return_value = [(120, "preserved")]
        self.native.children[id(self.root)] = [self.tier, opening]
        self.native.children[id(opening)] = [macro]
        self.native.children[id(macro)] = [metadata]
        for child, parent in ((opening, self.root), (macro, opening), (metadata, macro)):
            self.native.parents[id(child)] = parent
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root]
        return opening, macro, metadata

    def test_mixed_auxiliary_subtree_preserves_geometry_and_nested_metadata_through_apply(self):
        opening, macro, metadata = self.auxiliary_tree()
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        evidence = plan["changes"][0]["resource"]["native_material_state"]["auxiliary_components"]["root"][0]
        self.assertEqual(evidence["geometry"]["status"], "observed")
        self.assertEqual(evidence["children"][0]["geometry"]["status"], "observed")
        self.assertEqual(evidence["children"][0]["children"][0]["stored_attributes"][0]["value"], "preserved")
        self.assertEqual(evidence["children"][0]["children"][0]["geometry"]["status"], "observed")
        self.native.highlight(plan)
        self.native.children[id(self.root)].reverse()
        result = self.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(metadata.GetAttributes.return_value, [(120, "preserved")])
        self.assertEqual(macro.GetModelGeometry.return_value.stream, "macro")
        self.native.base.ModifyElements.assert_called_once()

    def test_auxiliary_subtree_drift_conflicts_before_modify(self):
        for drift in ("identity", "parent", "children", "geometry", "metadata", "metadata_geometry", "geometry_coverage"):
            with self.subTest(drift=drift):
                opening, macro, metadata = self.auxiliary_tree()
                plan = self.preview()
                self.assertTrue(plan["apply_available"], plan)
                self.native.highlight(plan)
                if drift == "identity":
                    macro.GetModelElementUUID.return_value = str(uuid4())
                elif drift == "parent":
                    self.native.parents[id(macro)] = self.root
                elif drift == "children":
                    self.native.children[id(macro)] = []
                elif drift == "geometry":
                    macro.GetModelGeometry.return_value.stream = "changed"
                elif drift == "metadata":
                    metadata.GetAttributes.return_value = [(120, "changed")]
                elif drift == "metadata_geometry":
                    metadata.GetModelGeometry.return_value.stream = "changed"
                else:
                    macro.GetModelGeometry.return_value = SimpleNamespace()
                self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
                self.native.base.ModifyElements.assert_not_called()

    def test_auxiliary_geometry_drift_after_modify_is_unknown_and_recovery_never_retries(self):
        _, macro, _ = self.auxiliary_tree()
        original = self.native.base.ModifyElements.side_effect

        def modify_then_drift(doc, elements):
            original(doc, elements)
            macro.GetModelGeometry.return_value.stream = "changed-after-write"

        self.native.base.ModifyElements.side_effect = modify_then_drift
        plan = self.preview()
        self.native.highlight(plan)
        execution_id = uuid4().hex
        result = self.native.apply(plan, execution_id)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.native.apply(plan, execution_id)["replayed"])
        recovered = self.native.recover(execution_id)
        self.assertTrue(recovered["read_only"])
        self.assertEqual(recovered["outcomes"][0]["state"], "unknown")
        self.native.base.ModifyElements.assert_called_once()

    def test_auxiliary_geometry_failures_are_bounded_and_nonblocking(self):
        opening, _, _ = self.auxiliary_tree()
        secret = "private native geometry detail"
        opening.GetModelGeometry.side_effect = RuntimeError(secret)
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        evidence = plan["changes"][0]["resource"]["native_material_state"]["auxiliary_components"]["root"][0]
        self.assertEqual(evidence["geometry"], {"status": "not_checked", "reason": "geometry_stream_unavailable",
                                               "error_type": "RuntimeError"})
        self.assertNotIn(secret, repr(plan))
        self.native.highlight(plan)
        self.assertEqual(self.native.apply(plan)["state"], "completed")
        self.native.base.ModifyElements.assert_called_once()

    def test_auxiliary_geometry_uses_sdk_success_enum(self):
        opening, _, _ = self.auxiliary_tree()
        success = object()
        sys.modules["NemAll_Python_Geometry"].eGeometryErrorCode.eOK = success
        self.tier.GetModelGeometry.return_value.WriteToStream = lambda: (success, "tier")
        opening.GetModelGeometry.return_value.WriteToStream = lambda: (success, "opening")
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        evidence = plan["changes"][0]["resource"]["native_material_state"]["auxiliary_components"]["root"][0]
        self.assertEqual(evidence["geometry"]["status"], "observed")

    def test_unreadable_auxiliary_subtrees_allow_material_and_no_op(self):
        for defect in ("duplicate", "cross_file", "owner", "parent_cycle"):
            with self.subTest(defect=defect):
                opening, macro, metadata = self.auxiliary_tree()
                if defect == "duplicate":
                    self.native.children[id(opening)] = [macro, macro]
                elif defect == "cross_file":
                    macro.GetDrawingfileNumber.return_value = 102
                elif defect == "owner":
                    self.native.parents[id(metadata)] = opening
                else:
                    self.native.parents[id(opening)] = macro
                for desired in ("C35/45", self.material):
                    plan = self.preview(changes=[{
                        "target": {"kind": "native_material", "tier_index": 1}, "value": desired}])
                    if desired == self.material:
                        self.assertEqual(plan["state"], "no_op")
                        self.assertFalse(plan["changes"])
                    else:
                        self.assertTrue(plan["apply_available"], plan)
                        self.assertEqual(plan["blocked"], [])
                        diagnostic = plan["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
                        self.assertEqual(diagnostic["status"], "not_checked")
                    self.native.base.ModifyElements.assert_not_called()

    def test_auxiliary_count_and_byte_budgets_are_shared_across_subtrees(self):
        self.auxiliary_tree()
        module = importlib.import_module(self.native.module.__package__ + ".wall_material")
        for constant, reason, limit in (("_MAX_AUXILIARY_COMPONENTS", "wall_material_component_limit", 2),
                                        ("_MAX_COMPONENT_SNAPSHOT_BYTES", "wall_material_component_snapshot_limit", 5000)):
            with self.subTest(constant=constant), patch.object(module, constant, limit):
                plan = self.preview()
                self.assertTrue(plan["apply_available"], plan)
                blocker = plan["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
                self.assertEqual(blocker["reason"], reason)
                self.native.base.ModifyElements.assert_not_called()

    def test_tier_lineage_blocker_includes_bounded_identity_and_child_evidence(self):
        bad_tier = self.native.element(27, name="WallTier_TypeUUID", solid=Polyhedron())
        foreign_wall = self.alternate_wall_view(28)
        foreign_wall.GetModelElementUUID.return_value = (
            self.native.element(29).GetModelElementUUID.return_value)
        self.native.parents[id(bad_tier)] = foreign_wall
        self.native.parents[id(foreign_wall)] = self.native.adapter_module.BaseElementAdapterParentElementService.GetParentElement(
            self.root)
        descendants = [self.native.element(40 + index, name="Unknown_TypeUUID") for index in range(9)]
        self.native.children[id(bad_tier)] = descendants
        for child in descendants:
            self.native.parents[id(child)] = bad_tier

        child_service = self.native.adapter_module.BaseElementAdapterChildElementsService
        original = child_service.GetChildModelElements
        self.addCleanup(setattr, child_service, "GetChildModelElements", original)
        root_reads = [0]

        def enumerate_children(adapter, include_hidden):
            if adapter is self.root:
                root_reads[0] += 1
                return [self.tier] if root_reads[0] == 1 else [bad_tier]
            return original(adapter, include_hidden)

        child_service.GetChildModelElements = enumerate_children
        module = importlib.import_module(self.native.module.__package__ + ".wall_material")
        _, preservation_state, preservation = module.preview_observation(self.native.base, self.root)

        self.assertIsNotNone(preservation_state)
        preservation = preservation_state["preservation_diagnostic"]
        self.assertEqual(preservation["reason"], "wall_material_tier_hierarchy_unsupported")
        evidence = preservation["diagnostic"]["evidence"]
        self.assertEqual(evidence["selected_wall"]["model_uuid"],
                         self.root.GetModelElementUUID.return_value)
        self.assertEqual(evidence["tier_lineage"][1]["model_uuid"],
                         foreign_wall.GetModelElementUUID.return_value)
        self.assertEqual(evidence["tier_child_count"], 9)
        self.assertEqual(len(evidence["tier_children_sample"]), 8)
        self.native.base.ModifyElements.assert_not_called()

    def test_tier_attribute_container_leaf_is_bound_with_raw_stored_values(self):
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        container = self.native.element(21, name="AttributeContainer_TypeUUID")
        container.GetAttributes.return_value = [(120, "m3"), (1371, 0), (1500, [1, 2.5])]
        self.native.children[id(self.tier)] = [container]
        self.native.parents[id(container)] = self.tier
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, container]

        plan = self.preview()

        self.assertTrue(plan["apply_available"], plan)
        state = plan["changes"][0]["resource"]["native_material_state"]
        self.assertEqual(len(state["tier_attribute_containers"]), 1)
        evidence = state["tier_attribute_containers"][0]
        self.assertEqual(evidence["ownership"]["target"]["type_name"], "AttributeContainer_TypeUUID")
        self.assertEqual(evidence["ownership"]["lineage"][1]["model_uuid"],
                         self.tier.GetModelElementUUID.return_value)
        self.assertEqual([row["attribute_id"] for row in evidence["stored_attributes"]], [120, 1371, 1500])
        self.assertEqual(evidence["stored_attributes"][0]["value"], "m3")
        self.assertEqual(evidence["stored_attributes"][2]["value"], [1, 2.5])

        self.native.base.ElementsSelectService.SelectAllElements.assert_called()
        self.native.highlight(plan)
        result = self.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        self.native.base.ModifyElements.assert_called_once()

    def test_attribute_container_collection_only_needs_iteration(self):
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        container = self.native.element(21, name="AttributeContainer_TypeUUID")
        container.GetAttributes.return_value = [(120, "m3")]
        self.native.children[id(self.tier)] = [container]
        self.native.parents[id(container)] = self.tier
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, container]
        child_service = self.native.adapter_module.BaseElementAdapterChildElementsService
        original = child_service.GetChildModelElements
        self.addCleanup(setattr, child_service, "GetChildModelElements", original)
        tier_reads = [0]

        class IterationOnlyCollection:
            def __iter__(self):
                return iter([container])

        def enumerate_children(adapter, include_hidden):
            if adapter is self.tier:
                tier_reads[0] += 1
                if tier_reads[0] == 2:
                    return IterationOnlyCollection()
            return original(adapter, include_hidden)

        child_service.GetChildModelElements = enumerate_children
        plan = self.preview()

        self.assertTrue(plan["apply_available"], plan)
        self.assertGreaterEqual(tier_reads[0], 2)
        self.assertEqual(len(plan["changes"][0]["resource"]["native_material_state"][
            "tier_attribute_containers"]), 1)
        self.native.base.ModifyElements.assert_not_called()

    def test_repeated_tier_enumeration_accepts_same_model_alternate_wrapper(self):
        alternate = self.native.element(21, name="WallTier_TypeUUID", solid=Polyhedron())
        alternate.GetDrawingfileNumber.return_value = self.tier.GetDrawingfileNumber.return_value
        alternate.GetModelElementUUID.return_value = self.tier.GetModelElementUUID.return_value
        alternate.GetElementAdapterType.return_value.GetGuid.return_value = (
            self.tier.GetElementAdapterType.return_value.GetGuid.return_value)
        alternate.GetModelGeometry.return_value = self.tier.GetModelGeometry.return_value
        self.native.parents[id(alternate)] = self.root
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root]
        child_service = self.native.adapter_module.BaseElementAdapterChildElementsService
        original = child_service.GetChildModelElements
        self.addCleanup(setattr, child_service, "GetChildModelElements", original)
        root_reads = [0]

        def enumerate_children(adapter, include_hidden):
            if adapter is self.root:
                root_reads[0] += 1
                return [self.tier] if root_reads[0] % 2 == 1 else [alternate]
            return original(adapter, include_hidden)

        child_service.GetChildModelElements = enumerate_children
        plan = self.preview()

        self.assertTrue(plan["apply_available"], plan)
        bound_child = plan["changes"][0]["resource"]["native_material_state"][
            "hierarchy"]["children"][0]
        self.assertEqual(bound_child["view_uuid"], self.tier.GetElementUUID.return_value)
        self.assertNotEqual(bound_child["view_uuid"], alternate.GetElementUUID.return_value)
        self.native.highlight(plan)
        result = self.native.apply(plan, uuid4().hex)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(self.material, "C35/45")
        self.native.base.ModifyElements.assert_called_once()

    def test_unknown_metadata_value_is_nonblocking(self):
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        container = self.native.element(21, name="AttributeContainer_TypeUUID")
        container.GetAttributes.return_value = [(120, object())]
        self.native.children[id(self.tier)] = [container]
        self.native.parents[id(container)] = self.tier
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, container]

        plan = self.preview()

        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(len(plan["changes"]), 1)
        diagnostic = plan["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
        self.assertEqual(diagnostic["diagnostic"]["stage"],
                         "material_attribute_container_values")
        self.native.base.ModifyElements.assert_not_called()

    def test_tier_metadata_container_identity_or_value_drift_conflicts_before_modify(self):
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        container = self.native.element(21, name="AttributeContainer_TypeUUID")
        container.GetAttributes.return_value = [(120, "m3")]
        self.native.children[id(self.tier)] = [container]
        self.native.parents[id(container)] = self.tier
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root, self.tier, container]

        for drift in ("identity", "value"):
            with self.subTest(drift=drift):
                plan = self.preview()
                self.assertTrue(plan["apply_available"], plan)
                self.native.highlight(plan)
                if drift == "identity":
                    replacement = self.native.element(22, name="AttributeContainer_TypeUUID")
                    replacement.GetAttributes.return_value = [(120, "m3")]
                    self.native.parents[id(replacement)] = self.tier
                    self.native.children[id(self.tier)] = [replacement]
                else:
                    container.GetAttributes.return_value = [(120, "m4")]
                self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
                self.native.base.ModifyElements.assert_not_called()
                self.native.children[id(self.tier)] = [container]
                container.GetAttributes.return_value = [(120, "m3")]

    def test_tier_metadata_lineage_accepts_same_model_parent_view(self):
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        container = self.native.element(21, name="AttributeContainer_TypeUUID")
        container.GetAttributes.return_value = [(120, "m3")]
        tier_view = self.native.element(22, name="WallTier_TypeUUID")
        tier_view.GetDrawingfileNumber.return_value = self.tier.GetDrawingfileNumber.return_value
        tier_view.GetModelElementUUID.return_value = self.tier.GetModelElementUUID.return_value
        tier_view.GetElementAdapterType.return_value.GetTypeName.return_value = "WallTier_TypeUUID"
        tier_view.GetElementAdapterType.return_value.GetGuid.return_value = (
            self.tier.GetElementAdapterType.return_value.GetGuid.return_value)
        self.native.parents[id(tier_view)] = self.root
        self.native.children[id(self.tier)] = [container]
        self.native.parents[id(container)] = tier_view
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root, self.tier, container]

        plan = self.preview()

        self.assertTrue(plan["apply_available"], plan)
        lineage = plan["changes"][0]["resource"]["native_material_state"][
            "tier_attribute_containers"][0]["ownership"]["lineage"]
        self.assertEqual(len(lineage), 3)
        self.assertEqual(lineage[1]["model_uuid"], self.tier.GetModelElementUUID.return_value)
        self.assertNotEqual(lineage[1]["view_uuid"], self.tier.GetElementUUID.return_value)

    def test_material_metadata_drift_after_modify_is_unknown_and_replay_never_repeats_modify(self):
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        container = self.native.element(21, name="AttributeContainer_TypeUUID")
        container.GetAttributes.return_value = [(120, "m3")]
        self.native.children[id(self.tier)] = [container]
        self.native.parents[id(container)] = self.tier
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root, self.tier, container]

        def modify_and_change_metadata(doc, elements):
            self.properties = copy.deepcopy(elements[0].Properties)
            self.material = self.properties.GetWallTierProperties(1).Material
            container.GetAttributes.return_value = [(120, "m4")]

        self.native.base.ModifyElements.side_effect = modify_and_change_metadata
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.native.highlight(plan)
        execution_id = uuid4().hex

        result = self.native.apply(plan, execution_id)

        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertEqual(self.material, "C35/45")
        self.assertTrue(self.native.apply(plan, execution_id)["replayed"])
        self.assertEqual(self.native.base.ModifyElements.call_count, 1)

    def root_attribute_container(self, index=31, attributes=None):
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        container = self.native.element(index, name="AttributeContainer_TypeUUID")
        container.GetAttributes.return_value = ([(120, "root-metadata"), (1371, 0)]
                                                if attributes is None else attributes)
        self.native.children[id(self.root)] = [self.tier, container]
        self.native.parents[id(container)] = self.root
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, container]
        return container

    def test_root_attribute_container_leaf_preserves_lineage_values_and_tier_metadata(self):
        tier_container = self.native.element(30, name="AttributeContainer_TypeUUID")
        tier_container.GetAttributes.return_value = [(120, "tier-metadata"), (1500, [1, 2.5])]
        self.native.children[id(self.tier)] = [tier_container]
        self.native.parents[id(tier_container)] = self.tier
        root_container = self.root_attribute_container()
        self.native.children[id(self.tier)] = [tier_container]
        self.native.parents[id(tier_container)] = self.tier
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, tier_container, root_container]
        before = self.snapshot_invariants()

        plan = self.preview()

        self.assertTrue(plan["apply_available"], plan)
        state = plan["changes"][0]["resource"]["native_material_state"]
        self.assertEqual(len(state["tier_attribute_containers"]), 1)
        self.assertEqual(len(state["root_attribute_containers"]), 1)
        tier_evidence = state["tier_attribute_containers"][0]
        root_evidence = state["root_attribute_containers"][0]
        self.assertEqual(root_evidence["ownership"]["target"]["type_name"],
                         "AttributeContainer_TypeUUID")
        self.assertEqual(root_evidence["ownership"]["lineage"][1]["model_uuid"],
                         self.root.GetModelElementUUID.return_value)
        self.assertEqual(tier_evidence["ownership"]["lineage"][1]["model_uuid"],
                         self.tier.GetModelElementUUID.return_value)
        self.assertEqual([row["attribute_id"] for row in root_evidence["stored_attributes"]],
                         [120, 1371])
        self.assertEqual([row["attribute_id"] for row in tier_evidence["stored_attributes"]],
                         [120, 1500])
        self.assertEqual(root_evidence["stored_attributes"][0]["value"], "root-metadata")
        self.assertEqual(tier_evidence["stored_attributes"][1]["value"], [1, 2.5])

        self.native.highlight(plan)
        self.native.children[id(self.root)] = [root_container, self.tier]
        result = self.native.apply(plan, uuid4().hex)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(self.material, "C35/45")
        self.assertEqual(self.snapshot_invariants(), before)
        self.assertEqual(root_container.GetAttributes.return_value, [(120, "root-metadata"), (1371, 0)])
        self.assertEqual(tier_container.GetAttributes.return_value, [(120, "tier-metadata"), (1500, [1, 2.5])])
        self.native.base.ModifyElements.assert_called_once()

    def test_root_attribute_value_drift_conflicts_before_modify(self):
        container = self.root_attribute_container()
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.native.highlight(plan)
        container.GetAttributes.return_value = [(120, "changed"), (1371, 0)]

        self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
        self.native.base.ModifyElements.assert_not_called()

    def test_root_attribute_collection_identity_drift_conflicts_before_modify(self):
        container = self.root_attribute_container()
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.native.highlight(plan)
        replacement = self.native.element(32, name="AttributeContainer_TypeUUID")
        replacement.GetAttributes.return_value = copy.deepcopy(container.GetAttributes.return_value)
        self.native.parents[id(replacement)] = self.root
        self.native.children[id(self.root)] = [self.tier, replacement]

        self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
        self.native.base.ModifyElements.assert_not_called()

    def test_duplicate_children_are_rejected_but_nested_metadata_and_siblings_are_eligible(self):
        container = self.root_attribute_container()
        self.native.children[id(self.root)] = [self.tier, container, container]
        duplicate = self.preview()
        self.assertTrue(duplicate["apply_available"], duplicate)
        self.assertEqual(len(duplicate["changes"]), 1)
        blocker = duplicate["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
        self.assertEqual(blocker["reason"],
                         "component_child_identity_ambiguous")
        self.assertEqual(blocker["diagnostic"]["stage"], "child_identity")
        self.native.base.ModifyElements.assert_not_called()

        self.native.children[id(self.root)] = [self.tier, container]
        nested = self.native.element(33, name="Unknown_TypeUUID")
        self.native.children[id(container)] = [nested]
        self.native.parents[id(nested)] = container
        nested_plan = self.preview()
        self.assertTrue(nested_plan["apply_available"], nested_plan)
        nested_state = nested_plan["changes"][0]["resource"]["native_material_state"]
        self.assertEqual(nested_state["root_attribute_containers"][0]["children"][0][
            "ownership"]["target"]["type_name"], "Unknown_TypeUUID")
        self.native.children[id(container)] = []

        unknown = self.native.element(34, name="Door_TypeUUID")
        self.native.children[id(self.root)] = [self.tier, container, unknown]
        self.native.parents[id(unknown)] = self.root
        unknown_plan = self.preview()
        self.assertTrue(unknown_plan["apply_available"], unknown_plan)
        self.native.base.ModifyElements.assert_not_called()

    def test_native_property_tier_count_does_not_require_a_tier_adapter(self):
        container = self.root_attribute_container()
        self.native.children[id(self.root)] = [container]
        missing_tier = self.preview()
        self.assertTrue(missing_tier["apply_available"], missing_tier)
        self.assertEqual(len(missing_tier["changes"]), 1)
        blocker = missing_tier["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
        self.native.base.ModifyElements.assert_not_called()

        second_tier = self.native.element(35, name="WallTier_TypeUUID", solid=Polyhedron())
        self.native.parents[id(second_tier)] = self.root
        self.native.children[id(self.root)] = [self.tier, second_tier, container]
        multiple_tiers = self.preview()
        self.assertTrue(multiple_tiers["apply_available"], multiple_tiers)
        self.assertEqual(len(multiple_tiers["changes"]), 1)
        blocker = multiple_tiers["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
        self.native.base.ModifyElements.assert_not_called()

    def test_root_attribute_metadata_drift_after_modify_is_unknown_and_recovery_never_retries(self):
        container = self.root_attribute_container()

        def modify_and_change_root_metadata(doc, elements):
            self.properties = copy.deepcopy(elements[0].Properties)
            self.material = self.properties.GetWallTierProperties(1).Material
            container.GetAttributes.return_value = [(120, "changed-after-write"), (1371, 0)]

        self.native.base.ModifyElements.side_effect = modify_and_change_root_metadata
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.native.highlight(plan)
        execution_id = uuid4().hex

        result = self.native.apply(plan, execution_id)

        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.native.apply(plan, execution_id)["replayed"])
        self.assertEqual(self.native.base.ModifyElements.call_count, 1)
        self.native.base.ModifyElements.reset_mock()
        recovered = self.native.recover(execution_id)
        self.assertTrue(recovered["read_only"])
        self.assertEqual(recovered["outcomes"][0]["state"], "unknown")
        self.native.base.ModifyElements.assert_not_called()

    def test_root_and_tier_attribute_containers_share_snapshot_budget(self):
        rows = [(ident, "x" * 1800) for ident in range(1, 101)]
        tier_container = self.native.element(36, name="AttributeContainer_TypeUUID")
        tier_container.GetAttributes.return_value = copy.deepcopy(rows)
        self.native.children[id(self.tier)] = [tier_container]
        self.native.parents[id(tier_container)] = self.tier
        root_container = self.root_attribute_container(attributes=copy.deepcopy(rows))
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, tier_container, root_container]

        plan = self.preview()

        self.assertTrue(plan["apply_available"], plan)
        blocker = plan["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
        self.assertEqual(blocker["reason"],
                         "wall_material_attribute_snapshot_limit")
        self.assertEqual(blocker["diagnostic"]["stage"], "material_children")
        self.native.base.ModifyElements.assert_not_called()

    def test_nested_metadata_and_unreadable_attributes_are_nonblocking(self):
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        container = self.native.element(21, name="AttributeContainer_TypeUUID")
        container.GetAttributes.return_value = [(120, "m3")]
        self.native.children[id(self.tier)] = [container]
        self.native.parents[id(container)] = self.tier
        nested = self.native.element(22, name="WindowDoor_TypeUUID")
        self.native.children[id(container)] = [nested]
        self.native.parents[id(nested)] = container
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, container, nested]

        plan = self.preview()

        self.assertTrue(plan["apply_available"], plan)
        state = plan["changes"][0]["resource"]["native_material_state"]
        self.assertEqual(state["tier_attribute_containers"][0]["children"][0][
            "ownership"]["target"]["model_uuid"], nested.GetModelElementUUID())
        self.native.base.ModifyElements.assert_not_called()

        self.native.children[id(container)] = []
        for values in (((120, "first"), (120, "duplicate")), ((True, "boolean id"),),
                       ((120, object()),)):
            with self.subTest(values=values):
                container.GetAttributes.return_value = list(values)
                invalid = self.preview()
                self.assertTrue(invalid["apply_available"], invalid)
                blocker = invalid["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
                self.assertEqual(blocker["diagnostic"]["stage"],
                                 "material_attribute_container_values")
                self.native.base.ModifyElements.assert_not_called()

    def test_attribute_container_snapshot_budget_fails_before_modify(self):
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        container = self.native.element(21, name="AttributeContainer_TypeUUID")
        container.GetAttributes.return_value = [(ident, "x" * 8192) for ident in range(1, 40)]
        self.native.children[id(self.tier)] = [container]
        self.native.parents[id(container)] = self.tier
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [
            self.root, self.tier, container]

        plan = self.preview()

        self.assertTrue(plan["apply_available"], plan)
        blocker = plan["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
        self.assertEqual(blocker["reason"], "wall_material_attribute_snapshot_limit")
        self.assertEqual(blocker["diagnostic"]["stage"],
                         "material_attribute_container_values")
        self.native.base.ModifyElements.assert_not_called()

    def test_changed_child_enumeration_is_nonblocking_at_preview(self):
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

        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(len(plan["changes"]), 1)
        blocker = plan["changes"][0]["resource"]["native_material_state"]["preservation_diagnostic"]
        self.assertEqual(blocker["reason"],
                         "wall_material_one_exact_tier_required")
        self.assertEqual(blocker["diagnostic"]["stage"], "material_children")
        self.assertGreaterEqual(root_reads[0], 2)
        self.native.base.ModifyElements.assert_not_called()

    def test_missing_preservation_evidence_is_rejected_at_final_setter(self):
        plan = self.preview()
        change = plan["changes"][0]
        del change["resource"]["native_material_state"]
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

    def test_missing_common_pen_has_nonblocking_bounded_diagnostic(self):
        del self.properties.GetWallTierProperties(1).CommonProperties.Pen
        module = importlib.import_module(self.native.module.__package__ + ".wall_material")
        with patch.object(TierProperties, "SetMaterial", autospec=True) as set_material, \
             patch.object(FakeWallElement, "SetProperties", autospec=True) as set_properties:
            plan = self.preview()

        old_value, preservation_state, preservation = module.preview_observation(
            self.native.base, self.root)
        self.assertEqual(old_value, {"status": "observed", "value": "C20/25"})
        self.assertIsNotNone(preservation_state)
        preservation = preservation_state["preservation_diagnostic"]
        self.assertEqual(preservation["reason"], "wall_material_read_unavailable")
        self.assertEqual(preservation["diagnostic"],
                         {"stage": "material_common_Pen", "error_type": "AttributeError"})
        expected = {"status": "not_checked", "value": None,
                    "reason": "wall_material_read_unavailable",
                    "diagnostic": {"stage": "material_common_Pen", "error_type": "AttributeError"}}
        observed, state = module.observation(self.native.base, self.root)
        self.assertEqual(observed, old_value)
        self.assertEqual(state["preservation_diagnostic"], expected)
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["blocked"], [])
        self.assertEqual(plan["criteria"]["required_field_failures"], [])
        self.assertEqual(plan["criteria"]["operation_eligibility_failures"], [])
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
        self.assertIsNotNone(preservation_state)
        preservation = preservation_state["preservation_diagnostic"]
        self.assertEqual(preservation["reason"], "wall_material_read_unavailable")
        self.assertEqual(preservation["diagnostic"],
                         {"stage": "material_axis", "error_type": "ValueError"})
        observed, state = module.observation(self.native.base, self.root)
        self.assertEqual(observed, old_value)
        self.assertEqual(state["preservation_diagnostic"], preservation)
        self.assertNotIn(secret, repr(observed))
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["blocked"], [])
        self.assertEqual(plan["criteria"]["required_field_failures"], [])
        self.assertEqual(plan["criteria"]["operation_eligibility_failures"], [])
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

