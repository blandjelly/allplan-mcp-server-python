"""Material regressions for Column properties and unavailable Wall geometry."""
import copy
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import test_model_edit
import test_wall_material_edit as wall_fixtures


class ColumnElement:
    def __init__(self, properties):
        self.Properties = properties

    def SetProperties(self, properties):
        self.Properties = properties


class ColumnMaterialTests(unittest.TestCase):
    def setUp(self):
        self.fixture = wall_fixtures.WallMaterialEditTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.native = self.fixture.native
        self.root = self.fixture.root
        self.root.GetElementAdapterType.return_value.GetTypeName.return_value = "Column_TypeUUID"
        self.native.children[id(self.root)] = []
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root]
        sys.modules["NemAll_Python_ArchElements"].ColumnElement = ColumnElement
        self.properties = wall_fixtures.TierProperties("Beton")
        self.properties.Material = "Beton"
        self.root.GetModelGeometry.side_effect = ValueError("unsupported column geometry")
        self.native.base.GetElement.side_effect = lambda _adapter: ColumnElement(copy.deepcopy(self.properties))
        self.native.base.ModifyElements.side_effect = self.modify

    def modify(self, doc, elements):
        self.assertEqual(len(elements), 1)
        self.assertIsInstance(elements[0], ColumnElement)
        self.properties = copy.deepcopy(elements[0].Properties)
        return elements

    def preview(self):
        return self.native.call(self.fixture.request(native_types=["Column_TypeUUID"]))

    def test_column_apply_readback_replay_recovery_and_no_op_without_geometry(self):
        before = copy.deepcopy(vars(self.properties))
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        change = plan["changes"][0]
        self.assertEqual(change["field"], "native.material")
        state = change["resource"]["native_material_state"]
        self.assertEqual(state["material_owner"], "column_properties")
        self.assertEqual(state["geometry"]["status"], "not_checked")
        self.native.highlight(plan)
        execution_id = uuid4().hex
        result = self.native.apply(plan, execution_id)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(result["outcomes"][0]["readback"], {"status": "observed", "value": "C35/45"})
        self.assertEqual(self.properties.Material, "C35/45")
        del before["Material"]
        after = vars(self.properties).copy()
        del after["Material"]
        self.assertEqual(before, after)
        self.assertTrue(self.native.apply(plan, execution_id)["replayed"])
        self.assertEqual(self.native.recover(execution_id)["state"], "completed")
        self.native.base.ModifyElements.assert_called_once()
        self.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertEqual(self.preview()["state"], "no_op")

    def test_column_unsupported_unrelated_properties_do_not_block(self):
        del self.properties.CommonProperties.Pen
        del self.properties.PlaneReferences
        self.properties.SurfaceElementProperties = object()
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        state = plan["changes"][0]["resource"]["native_material_state"]
        self.assertEqual(state["optional_properties"]["common"]["Pen"]["status"], "not_checked")
        self.native.highlight(plan)
        self.assertEqual(self.native.apply(plan)["state"], "completed")

    def test_column_material_or_observed_property_drift_prevents_setter(self):
        for field, changed in (("Material", "other"), ("Priority", 22)):
            with self.subTest(field=field):
                previous = getattr(self.properties, field)
                plan = self.preview()
                self.native.highlight(plan)
                setattr(self.properties, field, changed)
                self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
                self.native.base.ModifyElements.assert_not_called()
                setattr(self.properties, field, previous)

    def alternate_view(self):
        alias = self.native.element(20, name="Column_TypeUUID")
        for method in ("GetDrawingfileNumber", "GetModelElementUUID", "GetDisplayName", "GetAttributes"):
            getattr(alias, method).return_value = getattr(self.root, method).return_value
        alias.GetElementAdapterType.return_value.GetGuid.return_value = self.root.GetElementAdapterType.return_value.GetGuid.return_value
        alias.GetCommonProperties.return_value.Layer = self.root.GetCommonProperties.return_value.Layer
        for method, value in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                              ("IsInActiveDocument", True), ("IsInActiveLayer", True), ("IsLabelElement", False)):
            getattr(alias, method).return_value = value
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root, alias]
        return alias

    def test_same_material_across_views_with_different_optional_evidence_can_apply(self):
        alias = self.alternate_view()
        def get_element(adapter):
            props = copy.deepcopy(self.properties)
            if adapter is alias:
                del props.CommonProperties.Pen
            return ColumnElement(props)
        self.native.base.GetElement.side_effect = get_element
        plan = self.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["changes"][0]["target_view_uuid"], self.root.GetElementUUID())
        self.native.highlight(plan)
        self.assertEqual(self.native.apply(plan)["state"], "completed")
        self.native.base.ModifyElements.assert_called_once()

    def test_disagreeing_native_material_views_still_block(self):
        alias = self.alternate_view()
        def get_element(adapter):
            props = copy.deepcopy(self.properties)
            if adapter is alias:
                props.Material = "other"
            return ColumnElement(props)
        self.native.base.GetElement.side_effect = get_element
        plan = self.preview()
        self.assertFalse(plan["apply_available"], plan)
        self.assertEqual(plan["blocked"][0]["reason"], "old_value_unknown")
        self.assertEqual(plan["blocked"][0]["old_value"]["reason"], "native_material_representation_conflict")
        self.native.base.ModifyElements.assert_not_called()

    def test_column_lost_reply_recovers_without_setter_retry(self):
        def modify_then_lose(doc, elements):
            self.modify(doc, elements)
            raise RuntimeError("lost response")
        self.native.base.ModifyElements.side_effect = modify_then_lose
        plan = self.preview()
        self.native.highlight(plan)
        execution_id = uuid4().hex
        result = self.native.apply(plan, execution_id)
        self.assertEqual(result["outcomes"][0]["state"], "unknown", result)
        self.assertTrue(self.native.apply(plan, execution_id)["replayed"])
        recovered = self.native.recover(execution_id)
        self.assertEqual(recovered["outcomes"][0]["state"], "reconciled")
        self.native.base.ModifyElements.assert_called_once()

    def replaced_view_execution(self, *, lost_reply=False):
        alias = self.alternate_view()
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root]
        def replace(doc, elements):
            result = self.modify(doc, elements)
            self.native.base.ElementsSelectService.SelectAllElements.return_value = [alias]
            if lost_reply:
                raise RuntimeError("lost response after regeneration")
            return result
        self.native.base.ModifyElements.side_effect = replace
        plan = self.preview()
        self.native.highlight(plan)
        execution = uuid4().hex
        result = self.native.apply(plan, execution)
        self.assertEqual(result["outcomes"][0]["state"], "unknown", result)
        if not lost_reply:
            self.assertFalse(result["outcomes"][0]["representation_consensus"]["reviewed_view_present"])
        return execution, plan, alias

    def test_replaced_column_view_recovers_after_restart_and_unblocks_without_retry(self):
        for lost_reply in (False, True):
            with self.subTest(lost_reply=lost_reply):
                f = ColumnMaterialTests()
                f.setUp()
                self.addCleanup(f.doCleanups)
                execution, plan, alias = f.replaced_view_execution(lost_reply=lost_reply)
                self.assertEqual(f.properties.Material, "C35/45")
                executor = f.native.handler.repair_plans.executor
                f.native.handler.repair_plans.executor = type(executor)(executor.plans, executor.path)
                recovered = f.native.recover(execution)
                self.assertTrue(recovered["write_blocked"])
                proposal = recovered["recovery"]["reconciliation"]
                target = proposal["targets"][0]
                self.assertFalse(target["reviewed_view_present"])
                self.assertEqual(target["readback"], {"status": "observed", "value": "C35/45"})
                self.assertEqual(target["representations"][0]["view_uuid"], alias.GetElementUUID())
                resolved = f.native.call(proposal["request"])
                self.assertFalse(resolved["write_blocked"])
                self.assertFalse(resolved["outcomes"][0]["preservation_verified"])
                self.assertEqual(resolved["outcomes"][0]["original_outcome"]["state"], "unknown")
                self.assertTrue(f.native.apply(plan, execution)["replayed"])
                f.native.base.ModifyElements.assert_called_once()

    def test_replacement_view_disagreement_unreadable_or_changed_owner_keeps_lock(self):
        for defect in ("material", "unreadable", "owner", "missing"):
            with self.subTest(defect=defect):
                f = ColumnMaterialTests()
                f.setUp()
                self.addCleanup(f.doCleanups)
                execution, _, alias = f.replaced_view_execution()
                if defect == "missing":
                    alias.GetModelElementUUID.return_value = str(uuid4())
                elif defect == "owner":
                    f.native.parents[id(alias)] = f.native.element(99, name="Macro_TypeUUID")
                else:
                    other = f.alternate_view()
                    other.GetElementUUID.return_value = str(uuid4())
                    f.native.base.ElementsSelectService.SelectAllElements.return_value = [alias, other]
                    def get_element(adapter):
                        if adapter is other and defect == "unreadable":
                            raise AttributeError("unavailable native representation")
                        props = copy.deepcopy(f.properties)
                        if adapter is other:
                            props.Material = "other"
                            props.Priority += 1
                        return ColumnElement(props)
                    f.native.base.GetElement.side_effect = get_element
                recovered = f.native.recover(execution)
                self.assertTrue(recovered["write_blocked"])
                self.assertNotIn("reconciliation", recovered["recovery"])
                f.native.base.ModifyElements.assert_called_once()

    def test_replaced_view_before_apply_still_blocks_without_setter(self):
        alias = self.alternate_view()
        plan = self.preview()
        self.native.highlight(plan)
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [alias]
        self.native.assert_code("repair_conflict", lambda: self.native.apply(plan))
        self.native.base.ModifyElements.assert_not_called()

    def test_every_replacement_view_preservation_is_bound_to_reconciliation_hash(self):
        execution, _, alias = self.replaced_view_execution()
        other = self.alternate_view()
        other.GetElementUUID.return_value = str(uuid4())
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [alias, other]
        priority = [22]
        def get_element(adapter):
            props = copy.deepcopy(self.properties)
            if adapter is other:
                props.Priority = priority[0]
            return ColumnElement(props)
        self.native.base.GetElement.side_effect = get_element
        recovered = self.native.recover(execution)
        proposal = recovered["recovery"]["reconciliation"]
        representations = proposal["targets"][0]["representations"]
        self.assertEqual(len(representations), 2)
        self.assertTrue(all("preservation" in item for item in representations))
        self.assertNotEqual(representations[0]["preservation"]["current_sha256"],
                            representations[1]["preservation"]["current_sha256"])
        priority[0] += 1
        self.native.assert_code("repair_conflict", lambda: self.native.call(proposal["request"]))
        fresh = self.native.recover(execution)["recovery"]["reconciliation"]
        self.assertNotEqual(fresh["hash"], proposal["hash"])
        self.assertFalse(self.native.call(fresh["request"])["write_blocked"])
        self.native.base.ModifyElements.assert_called_once()

    def test_column_missing_material_or_setter_and_wrong_target_still_block(self):
        for defect in ("material", "setter", "native_type", "nested"):
            with self.subTest(defect=defect):
                old = copy.deepcopy(self.properties)
                if defect == "material":
                    del self.properties.Material
                elif defect == "setter":
                    self.properties.SetMaterial = None
                elif defect == "native_type":
                    self.native.base.GetElement.side_effect = lambda _adapter: SimpleNamespace(Properties=self.properties)
                else:
                    parent = self.native.element(99, name="Macro_TypeUUID")
                    self.native.parents[id(self.root)] = parent
                plan = self.preview()
                self.assertFalse(plan["apply_available"], plan)
                self.assertFalse(plan["changes"])
                self.native.base.ModifyElements.assert_not_called()
                self.properties = old
                self.native.parents.pop(id(self.root), None)
                self.native.base.GetElement.side_effect = lambda _adapter: ColumnElement(copy.deepcopy(self.properties))


class MaterialAttributeRegressionTests(unittest.TestCase):
    def test_exact_project_material_attribute_still_edits_wall_and_column(self):
        for kind in ("Wall_TypeUUID", "Column_TypeUUID", "Beam_TypeUUID", "SkeletonBeam_TypeUUID"):
            with self.subTest(kind=kind):
                native = test_model_edit.ModelEditTests()
                native.setUp()
                self.addCleanup(native.doCleanups)
                element = native.fixture(("",))[0]
                element.GetElementAdapterType.return_value.GetTypeName.return_value = kind
                element.GetAttributes.return_value = [(508, "Beton")]
                element.GetModelGeometry.side_effect = ValueError("unavailable geometry")
                native.attribute_catalog({508: "Materiał"})
                native.setter_fakes([element])
                plan = native.preview(native_types=[kind], predicate=None, changes=[{
                    "target": {"kind": "attribute", "name": "Materiał"}, "value": "Silikat"}])
                self.assertTrue(plan["apply_available"], plan)
                self.assertEqual(plan["changes"][0]["resource"]["attribute_id"], 508)
                native.highlight(plan)
                execution_id = uuid4().hex
                self.assertEqual(native.apply(plan, execution_id)["state"], "completed")
                self.assertEqual(dict(element.GetAttributes.return_value)[508], "Silikat")
                self.assertTrue(native.apply(plan, execution_id)["replayed"])
                native.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
                native.base.GetElement.assert_not_called()
                element.GetModelGeometry.assert_not_called()


class WallGeometryRegressionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = wall_fixtures.WallMaterialEditTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_reported_tier_geometry_valueerror_allows_apply_and_no_op(self):
        f = self.fixture
        f.tier.GetModelGeometry.side_effect = ValueError("private geometry failure")
        plan = f.preview()
        self.assertTrue(plan["apply_available"], plan)
        state = plan["changes"][0]["resource"]["native_material_state"]
        self.assertEqual(state["tier_geometry"], {"status": "not_checked", "reason": "geometry_stream_unavailable",
                                                  "error_type": "ValueError"})
        self.assertNotIn("private geometry failure", repr(plan))
        f.native.highlight(plan)
        self.assertEqual(f.native.apply(plan)["state"], "completed")
        self.assertEqual(f.preview()["state"], "no_op")

    def test_non_polyhedron_stream_is_evidence_without_geometry_validity_gate(self):
        f = self.fixture
        shape = SimpleNamespace(WriteToStream=lambda: (0, "non-polyhedron"), IsValid=Mock(return_value=False))
        f.tier.GetModelGeometry.return_value = shape
        plan = f.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["changes"][0]["resource"]["native_material_state"]["tier_geometry"]["status"], "observed")
        shape.IsValid.assert_not_called()
        f.native.highlight(plan)
        self.assertEqual(f.native.apply(plan)["state"], "completed")

    def test_unrelated_preservation_failure_does_not_disable_property_drift_check(self):
        f = self.fixture
        del f.properties.GetWallTierProperties(1).CommonProperties.Pen
        plan = f.preview()
        self.assertTrue(plan["apply_available"], plan)
        f.native.highlight(plan)
        f.properties.GetWallTierProperties(1).Priority += 1
        f.native.assert_code("repair_conflict", lambda: f.native.apply(plan))
        f.native.base.ModifyElements.assert_not_called()

    def test_later_metadata_failure_retains_earlier_geometry_drift_evidence(self):
        f = self.fixture
        opening = f.native.element(80, name="WindowDoor_TypeUUID", solid=wall_fixtures.Polyhedron("opening"))
        broken = f.native.element(81, name="AttributeContainer_TypeUUID")
        broken.GetAttributes.return_value = [(120, object())]
        f.native.parents[id(opening)] = f.root
        f.native.parents[id(broken)] = f.root
        f.native.children[id(f.root)] = [f.tier, opening, broken]
        plan = f.preview()
        self.assertTrue(plan["apply_available"], plan)
        state = plan["changes"][0]["resource"]["native_material_state"]
        self.assertEqual(state["partial_preservation"]["auxiliary_components"]["root"][0]["geometry"]["status"], "observed")
        f.native.highlight(plan)
        opening.GetModelGeometry.return_value.stream = "changed"
        f.native.assert_code("repair_conflict", lambda: f.native.apply(plan))
        f.native.base.ModifyElements.assert_not_called()

    def test_reflected_material_attribute_is_not_an_unrelated_invariant(self):
        f = self.fixture
        container = f.root_attribute_container(attributes=[(508, "C20/25"), (120, "preserved")])
        original = f.native.base.ModifyElements.side_effect
        def modify(doc, elements):
            result = original(doc, elements)
            container.GetAttributes.return_value = [(508, f.material), (120, "preserved")]
            return result
        f.native.base.ModifyElements.side_effect = modify
        plan = f.preview()
        f.native.highlight(plan)
        self.assertEqual(f.native.apply(plan)["state"], "completed")
        self.assertEqual(f.material, "C35/45")
        self.assertEqual(dict(container.GetAttributes.return_value)[508], "C35/45")

