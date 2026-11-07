"""Native CalculationMode writes (0.49.0); SDK doubles do not establish native PASS."""
import copy
import importlib
import unittest
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError

from allplan_mcp.model_edit_models import ModelEditRequest
import test_native_material_columns as columns
import test_native_material_families as families


class CalculationModeTests(unittest.TestCase):
    def column(self, *, attribute_120="m", mirror=True):
        f = columns.ColumnMaterialTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        f.properties.CalculationMode = 2
        f.root.GetAttributes.return_value = [(935, ""), (120, attribute_120)]
        labels = {0: "m3", 1: "m2", 2: "m", 3: "Pcs", 4: "kg"}

        def modify(doc, elements):
            f.modify(doc, elements)
            if mirror:
                f.root.GetAttributes.return_value = [(935, ""), (120, labels[f.properties.CalculationMode])]
            return elements

        f.native.base.ModifyElements.side_effect = modify
        return f

    def request(self, f, value="m3", **updates):
        request = f.fixture.request(native_types=["Column_TypeUUID"],
                                    changes=[{"target": {"kind": "native_calculation_mode"}, "value": value}])
        request.update(updates)
        return request

    def preview(self, f, value="m3", **updates):
        return f.native.call(self.request(f, value, **updates))

    def module(self, f, name):
        return importlib.import_module(f.native.module.__package__ + "." + name)

    def test_column_apply_reports_native_readback_and_separate_mirror_then_no_op(self):
        f = self.column()
        before = copy.deepcopy(vars(f.properties))
        plan = self.preview(f)
        self.assertTrue(plan["apply_available"], plan)
        change, = plan["changes"]
        self.assertEqual((change["field"], change["operation"], change["property_role"]),
                         ("native.calculation_mode", "set_native_calculation_mode", "native_property"))
        self.assertEqual((change["old_value"], change["new_value"]), ({"status": "observed", "value": 2}, 0))
        self.assertEqual(change["resource"]["new_label"], "m3")
        state = change["resource"]["native_property_state"]
        self.assertEqual(state["native_field"], "CalculationMode")
        self.assertNotIn("CalculationMode", state["optional_properties"]["tier"])
        self.assertEqual(state["optional_properties"]["tier"]["Material"], "Beton")
        self.assertNotIn("native_material_state", change["resource"])
        mirror, = plan["criteria"]["native_property_mirror"]
        self.assertEqual(mirror["observation"], {"status": "observed", "value": "m"})
        f.native.highlight(plan)
        execution = uuid4().hex
        result = f.native.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        outcome = result["outcomes"][0]
        self.assertEqual(outcome["readback"], {"status": "observed", "value": 0})
        crosscheck = outcome["representation_consensus"]["mirror_crosscheck"]
        self.assertEqual((crosscheck["verdict"], crosscheck["new_label"], crosscheck["old_label"]),
                         ("matches_new_label", "m3", "m"))
        self.assertEqual(crosscheck["acceptance"], "owner_review_required_not_part_of_readback")
        preflight = result["target_preflight"][0]["representation_consensus"]["mirror_crosscheck"]
        self.assertEqual(preflight["verdict"], "matches_old_label")
        after = vars(f.properties).copy()
        self.assertEqual(after.pop("CalculationMode"), 0)
        before.pop("CalculationMode")
        self.assertEqual(before, after)
        self.assertTrue(f.native.apply(plan, execution)["replayed"])
        f.native.base.ModifyElements.assert_called_once()
        f.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertEqual(self.preview(f)["state"], "no_op")

    def test_diverging_attribute_120_is_reported_not_accepted_or_hidden(self):
        f = self.column(mirror=False)
        plan = self.preview(f, 1)
        f.native.highlight(plan)
        result = f.native.apply(plan)
        # Native readback decides the native write; attribute 120 stays a
        # separately reported observation for the owner's mirror decision.
        self.assertEqual(result["outcomes"][0]["readback"], {"status": "observed", "value": 1})
        crosscheck = result["outcomes"][0]["representation_consensus"]["mirror_crosscheck"]
        self.assertEqual(crosscheck["verdict"], "matches_old_label")
        self.assertEqual(crosscheck["values"], ["m"])

    def test_single_place_plan_hints_at_a_diverging_attribute_120(self):
        # 0.50.0 trial: plain requests routed to native_calculation_mode left a
        # diverging attribute 120 unchanged, once as a no-op plan.
        f = self.column(attribute_120="m3")
        no_op = self.preview(f, "m")
        self.assertEqual(no_op["state"], "no_op")
        hint = no_op["paired_property_hint"]
        self.assertEqual(hint["new_label"], "m")
        self.assertEqual(hint["plain_request"], {"target": {"kind": "paired_property",
                                                            "property": "calculation_mode"}, "value": "m"})
        row, = hint["attribute_differs"]
        self.assertEqual((row["attribute_id"], row["observation"]), (120, {"status": "observed", "value": "m3"}))
        self.assertEqual(row["ref"]["model_uuid"], f.root.GetModelElementUUID.return_value)
        plan = self.preview(f, "kg")
        self.assertEqual(plan["paired_property_hint"]["attribute_differs"][0]["observation"]["value"], "m3")
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual([c["field"] for c in plan["changes"]], ["native.calculation_mode"])
        self.assertNotIn("paired_property_hint", self.preview(f, "m3"))
        excluded = self.preview(f, "m", exclude_model_uuids=[f.root.GetModelElementUUID.return_value])
        self.assertNotIn("paired_property_hint", excluded)
        f.native.base.ModifyElements.assert_not_called()

    def test_wall_tier_route_preserves_material_and_other_scalars(self):
        wall = columns.wall_fixtures.WallMaterialEditTests()
        wall.setUp()
        self.addCleanup(wall.doCleanups)
        tier = wall.properties.GetWallTierProperties(1)
        before = copy.deepcopy(vars(tier))
        plan = wall.native.call(wall.request(changes=[
            {"target": {"kind": "native_calculation_mode"}, "value": "Pcs"}]))
        self.assertTrue(plan["apply_available"], plan)
        change, = plan["changes"]
        self.assertEqual(change["resource"]["native_property_state"]["material_owner"], "wall_tier_1")
        self.assertEqual(change["resource"]["native_property_state"]["tier"]["Material"], "C20/25")
        wall.native.highlight(plan)
        result = wall.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        after = copy.deepcopy(vars(wall.properties.GetWallTierProperties(1)))
        self.assertEqual(after.pop("CalculationMode"), 3)
        before.pop("CalculationMode")
        self.assertEqual(before, after)

    def test_beam_route_and_unsupported_families(self):
        f = families.NativeMaterialFamiliesTests()
        beam = f.fixture("Beam_TypeUUID", families.BeamElement)
        self.addCleanup(f.doCleanups)
        beam.properties.CalculationMode = 0
        plan = beam.native.call(beam.fixture.request(native_types=["Beam_TypeUUID"], changes=[
            {"target": {"kind": "native_calculation_mode"}, "value": "m"}]))
        self.assertTrue(plan["apply_available"], plan)
        beam.native.highlight(plan)
        self.assertEqual(beam.native.apply(plan)["state"], "completed")
        self.assertEqual(beam.properties.CalculationMode, 2)
        for kind, reason in (("MultiSlab_TypeUUID", "slab_calculation_mode_uses_multislab_attribute_120"),
                             ("Slab_TypeUUID", "slab_calculation_mode_uses_multislab_attribute_120"),
                             ("SkeletonBeam_TypeUUID", "native_calculation_mode_family_unsupported")):
            with self.subTest(kind=kind):
                g = families.NativeMaterialFamiliesTests()
                other = g.fixture(kind, families.SlabElement if "Slab" in kind else families.BeamElement)
                self.addCleanup(g.doCleanups)
                plan = other.native.call(other.fixture.request(native_types=[kind], changes=[
                    {"target": {"kind": "native_calculation_mode"}, "value": "m3"}]))
                self.assertFalse(plan["apply_available"], plan)
                row, = plan["blocked"]
                self.assertEqual(row["reason"], reason)
                if "Slab" in kind:
                    self.assertEqual(row["attribute_route"]["attribute_id"], 120)
                    self.assertEqual(row["attribute_route"]["default_owner"], "MultiSlab_TypeUUID")
                other.native.base.GetElement.assert_not_called()
                other.native.base.ModifyElements.assert_not_called()

    def test_property_drift_and_out_of_range_codes_never_reach_the_setter(self):
        for field, changed in (("Material", "other"), ("Priority", 22), ("CalculationMode", 3)):
            with self.subTest(field=field):
                f = self.column()
                plan = self.preview(f)
                f.native.highlight(plan)
                setattr(f.properties, field, changed)
                f.native.assert_code("repair_conflict", lambda: f.native.apply(plan))
                f.native.base.ModifyElements.assert_not_called()
        f = self.column()
        f.properties.CalculationMode = 7
        plan = self.preview(f)
        self.assertFalse(plan["apply_available"])
        self.assertEqual(plan["blocked"][0]["reason"], "old_value_unknown")
        self.assertEqual(plan["blocked"][0]["observation"]["reason"], "native_calculation_mode_code_unavailable")

    def test_lost_reply_is_unknown_then_recovered_without_setter_retry(self):
        f = self.column()

        def modify_then_lose(doc, elements):
            f.modify(doc, elements)
            raise RuntimeError("lost response")

        f.native.base.ModifyElements.side_effect = modify_then_lose
        plan = self.preview(f)
        f.native.highlight(plan)
        execution = uuid4().hex
        self.assertEqual(f.native.apply(plan, execution)["outcomes"][0]["state"], "unknown")
        self.assertTrue(f.native.apply(plan, execution)["replayed"])
        recovered = f.native.recover(execution)
        self.assertEqual(recovered["outcomes"][0]["state"], "reconciled")
        self.assertEqual(recovered["outcomes"][0]["reason"], "new_value_observed")
        f.native.base.ModifyElements.assert_called_once()

    def test_forged_changes_fail_validation_and_executor_scope(self):
        f = self.column()
        plan = self.preview(f)
        material = self.module(f, "wall_material")
        executor = self.module(f, "repair_execution").RepairExecutor
        self.assertTrue(material.valid_change(plan["changes"][0]))
        self.assertTrue(executor.model_edit_scope(plan))
        forgeries = {
            "same_code": lambda c: c.update(new_value=2, resource={**c["resource"], "new_label": "m"}),
            "label": lambda c: c["resource"].update(new_label="m2"),
            "code": lambda c: c.update(new_value=5),
            "boolean": lambda c: c.update(new_value=False),
            "schema": lambda c: c["resource"]["native_property_state"].update(schema_version="m4-native-material-state-3"),
            "field": lambda c: c["resource"]["native_property_state"].update(native_field="Material"),
            "material_state": lambda c: c["resource"].update(
                native_material_state=c["resource"]["native_property_state"]),
            "family": lambda c: c.update(native_type="MultiSlab_TypeUUID"),
            "mirror": lambda c: c["resource"].update(mirror_attribute_id=508),
        }
        for name, forge in forgeries.items():
            with self.subTest(name=name):
                forged = copy.deepcopy(plan)
                forge(forged["changes"][0])
                self.assertFalse(material.valid_change(forged["changes"][0]))
                self.assertFalse(executor.model_edit_scope(forged))
        native = self.module(f, "native_model_edit")
        bad = copy.deepcopy(plan["changes"][0])
        bad["new_value"] = 2
        f.native.assert_code("target_not_writable", lambda: native.write(f.native.base, f.root, bad))
        f.native.base.ModifyElements.assert_not_called()

    def test_request_contract_on_host_and_mcp(self):
        f = self.column()
        adapter = TypeAdapter(ModelEditRequest)
        good = self.request(f, "kg")
        adapter.validate_python(good)
        adapter.validate_python(self.request(f, 4))
        invalid = [
            self.request(f, "M3"), self.request(f, 5), self.request(f, True), self.request(f, "4"),
            self.request(f, "m", attribute_ids=[120]),
            self.request(f, "m", predicate={"field": "attribute:120", "op": "eq", "value": "m"}),
            {**good, "changes": good["changes"] + [{"target": {"kind": "layer", "short_name": "W1"}}]},
            {**good, "changes": [{"target": {"kind": "native_calculation_mode", "tier_index": 1}, "value": "m"}]},
        ]
        for request in invalid:
            with self.subTest(request=request["changes"], ids=request.get("attribute_ids")):
                with self.assertRaises(ValidationError):
                    adapter.validate_python(request)
                f.native.assert_code("invalid_payload", lambda: f.native.call(request))
        adapter.validate_python(self.request(f, "m", attribute_ids=[1200]))
        f.native.base.ModifyElements.assert_not_called()


if __name__ == "__main__":
    unittest.main()
