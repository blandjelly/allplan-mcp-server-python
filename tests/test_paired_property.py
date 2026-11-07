"""Paired native property + same-named attribute (0.50.0) and the CalculationMode
post-setter identity regeneration rule; SDK doubles do not establish native PASS."""
import copy
import importlib
import unittest
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError

from allplan_mcp.model_edit_models import ModelEditRequest
import test_native_material_families as families

LABELS = {0: "m3", 1: "m2", 2: "m", 3: "Pcs", 4: "kg"}
CODES = {label: code for code, label in LABELS.items()}


def bind_attribute_120(native):
    """Attribute 120 "Rodzaj rozliczenia" as an SDK Enum with the SDK labels."""
    native.attribute_catalog({120: "Rodzaj rozliczenia", 508: "Materiał"})
    native.attribute_type_enum.Enum = 105
    native.attribute_type_names[120] = "Enum"
    native.base.AttributeService.GetEnumIDFromValueString.side_effect = lambda ident, label: CODES[label]
    native.base.AttributeService.GetEnumValueStringFromID.side_effect = lambda ident, key: LABELS[key]
    native.setter_fakes([])


class PairedPropertyTests(unittest.TestCase):
    def family(self, kind="Column_TypeUUID", native_class=families.columns.ColumnElement, *,
               code=2, attribute="m", mirror=True, children=(), regenerate=None, regenerate_view=False):
        g = families.NativeMaterialFamiliesTests()
        f = g.fixture(kind, native_class)
        self.addCleanup(g.doCleanups)
        f.properties.CalculationMode = code
        f.root.GetAttributes.return_value = [(935, ""), (120, attribute), (508, "Beton")]
        bind_attribute_120(f.native)
        old = [f.native.element(97 - n, name=name) for n, name in enumerate(children)]
        for child in old:
            f.native.parents[id(child)] = f.root
        f.native.children[id(f.root)] = list(old)
        new = [f.native.element(90 - n, name=name) for n, name in enumerate(regenerate or ())]
        type_guids = {name: child.GetElementAdapterType.return_value.GetGuid.return_value
                      for name, child in zip(children, old)}
        for name, child in zip(regenerate or (), new):
            f.native.parents[id(child)] = f.root
            # A regenerated child keeps its SDK type UUID; only identities change.
            if name in type_guids:
                child.GetElementAdapterType.return_value.GetGuid.return_value = type_guids[name]
        setter = f.native.base.ModifyElements.side_effect

        def modify(doc, elements):
            result = setter(doc, elements)
            if mirror:
                attributes = dict(f.root.GetAttributes.return_value)
                attributes[120] = LABELS[f.properties.CalculationMode]
                f.root.GetAttributes.return_value = list(attributes.items())
            if regenerate is not None:
                f.native.children[id(f.root)] = list(new)
            if regenerate_view:
                f.root.GetElementUUID.return_value = str(uuid4())
            return result

        f.native.base.ModifyElements.side_effect = modify
        f.kind = kind
        return f

    def request(self, f, value="m3", prop="calculation_mode", **updates):
        request = f.fixture.request(native_types=[f.kind], changes=[
            {"target": {"kind": "paired_property", "property": prop}, "value": value}])
        request.update(updates)
        return request

    def plan(self, f, value="m3", prop="calculation_mode", **updates):
        plan = f.native.call(self.request(f, value, prop, **updates))
        if plan.get("apply_available"):
            f.native.highlight(plan)
        return plan

    def module(self, f, name):
        return importlib.import_module(f.native.module.__package__ + "." + name)

    def attribute(self, f, ident=120):
        return dict(f.root.GetAttributes.return_value)[ident]

    def test_native_write_that_sets_the_attribute_needs_no_attribute_setter(self):
        f = self.family()
        plan = self.plan(f)
        self.assertTrue(plan["apply_available"], plan)
        native, attribute = plan["changes"]
        self.assertEqual((native["field"], native["new_value"]), ("native.calculation_mode", 0))
        self.assertEqual(native["resource"]["paired_property"], "calculation_mode")
        self.assertEqual(native["resource"]["paired_attribute_id"], 120)
        self.assertEqual((attribute["field"], attribute["new_value"]), ("attribute:120", "m3"))
        self.assertEqual(attribute["resource"]["paired_native_field"], "native.calculation_mode")
        self.assertEqual(attribute["resource"]["enum_binding"], {"enum_id": 0, "value": "m3"})
        summary = plan["paired_property"]
        self.assertEqual(summary["targets"][0]["changes"], ["native.calculation_mode", "attribute:120"])
        self.assertEqual(summary["attribute_only"], [])
        execution = uuid4().hex
        result = f.native.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        first, second = result["outcomes"]
        self.assertEqual((first["state"], first["readback"]), ("applied", {"status": "observed", "value": 0}))
        self.assertEqual((second["state"], second["reason"]),
                         ("applied", "paired_attribute_already_set_by_native_write"))
        self.assertEqual(second["setter_calls_started"], 0)
        self.assertEqual(second["readback"], {"status": "observed", "value": "m3"})
        self.assertTrue(result["audited_fields_match_plan"])
        f.native.base.ModifyElements.assert_called_once()
        f.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertTrue(f.native.apply(plan, execution)["replayed"])
        self.assertEqual(f.native.call(self.request(f))["state"], "no_op")

    def test_attribute_that_does_not_follow_is_written_after_the_native_value(self):
        f = self.family(mirror=False)
        plan = self.plan(f, "m2")
        result = f.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual([o["reason"] for o in result["outcomes"]], ["readback_matches", "readback_matches"])
        self.assertEqual((f.properties.CalculationMode, self.attribute(f)), (1, "m2"))
        f.native.base.ModifyElements.assert_called_once()
        self.assertEqual(f.native.base.ElementsAttributeService.ChangeAttributes.call_args.args[0], [(120, "m2")])

    def test_place_that_already_holds_the_value_gets_no_change(self):
        f = self.family(code=0, attribute="m")
        plan = self.plan(f)
        change, = plan["changes"]
        self.assertEqual(change["field"], "attribute:120")
        self.assertTrue(self.module(f, "repair_execution").RepairExecutor.model_edit_scope(plan))
        self.assertEqual(f.native.apply(plan)["state"], "completed")
        f.native.base.ModifyElements.assert_not_called()
        g = self.family(code=2, attribute="m3", mirror=False)
        plan = self.plan(g)
        self.assertEqual([c["field"] for c in plan["changes"]], ["native.calculation_mode"])
        self.assertEqual(g.native.apply(plan)["state"], "completed")
        g.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_regenerated_column_view_is_carried_to_the_attribute_write(self):
        f = self.family(mirror=False, children=("AttributeContainer_TypeUUID",),
                        regenerate=("AttributeContainer_TypeUUID",), regenerate_view=True)
        reviewed = f.root.GetElementUUID.return_value
        plan = self.plan(f)
        result = f.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        native, attribute = result["outcomes"]
        drift = native["representation_consensus"]["representations"][0]["accepted_preservation_drift"]
        self.assertEqual(drift["accepted"], "identities_regenerated_evidence_otherwise_equal")
        self.assertEqual(drift["view_map"], {reviewed: f.root.GetElementUUID.return_value})
        self.assertEqual(attribute["effective_target_view_uuid"], f.root.GetElementUUID.return_value)
        self.assertEqual(self.attribute(f), "m3")
        self.assertEqual(plan["changes"][1]["target_view_uuid"], reviewed)

    def test_native_only_beam_regeneration_is_accepted_for_calculation_mode(self):
        # 0.49.0 trial: Beam "Podciąg, wieniec" regenerated AttributeContainer
        # and WallAxis one-for-one; readback 2, owner UI check and UI Undo.
        children = ("AttributeContainer_TypeUUID", "WallAxis_TypeUUID")
        f = self.family("Beam_TypeUUID", families.BeamElement, code=0, attribute="m3",
                        children=children, regenerate=children)
        plan = f.native.call(f.fixture.request(native_types=["Beam_TypeUUID"], changes=[
            {"target": {"kind": "native_calculation_mode"}, "value": "m"}]))
        f.native.highlight(plan)
        result = f.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        drift = result["outcomes"][0]["representation_consensus"]["representations"][0]["accepted_preservation_drift"]
        self.assertEqual(drift["accepted"], "identities_regenerated_evidence_otherwise_equal")
        self.assertEqual(drift["view_map"], {})
        self.assertEqual(sorted(p["type_name"] for p in drift["regenerated_identities"]), sorted(children))

    def test_attribute_is_not_attempted_after_an_unknown_native_outcome(self):
        f = self.family(mirror=False, children=("AttributeContainer_TypeUUID",),
                        regenerate=("Opening_TypeUUID",))
        plan = self.plan(f)
        execution = uuid4().hex
        result = f.native.apply(plan, execution)
        native, attribute = result["outcomes"]
        self.assertEqual(native["state"], "unknown")
        self.assertEqual((attribute["state"], attribute["reason"]), ("skipped", "not_attempted"))
        f.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertEqual(self.attribute(f), "m")
        recovery = f.native.recover(execution)
        self.assertTrue(recovery["write_blocked"])
        f.native.base.ModifyElements.assert_called_once()

    def test_families_without_native_route_get_the_attribute_alone(self):
        f = self.family("SkeletonBeam_TypeUUID", families.BeamElement)
        plan = self.plan(f)
        self.assertTrue(plan["apply_available"], plan)
        change, = plan["changes"]
        self.assertEqual(change["field"], "attribute:120")
        skipped, = plan["paired_property"]["attribute_only"]
        self.assertEqual((skipped["field"], skipped["reason"]),
                         ("native.calculation_mode", "paired_property_attribute_only_for_family"))
        self.assertEqual(plan["criteria"]["required_field_failures"], [])
        self.assertEqual(f.native.apply(plan)["state"], "completed")
        f.native.base.GetElement.assert_not_called()
        f.native.base.ModifyElements.assert_not_called()

    def test_paired_material_sets_native_material_and_attribute_508(self):
        f = self.family("Beam_TypeUUID", families.BeamElement)
        f.properties.Material = ""
        plan = self.plan(f, "C30/37", "material")
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual([c["field"] for c in plan["changes"]], ["native.material", "attribute:508"])
        result = f.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual((f.properties.Material, self.attribute(f, 508)), ("C30/37", "C30/37"))

    def test_executor_scope_requires_the_exact_pair(self):
        f = self.family(mirror=False)
        plan = self.plan(f)
        executor = self.module(f, "repair_execution").RepairExecutor
        self.assertTrue(executor.model_edit_scope(plan))
        forgeries = {
            "unpaired": lambda c: c[1]["resource"].pop("paired_native_field"),
            "property": lambda c: c[1]["resource"].update(paired_property="material"),
            "native_marker": lambda c: c[0]["resource"].pop("paired_attribute_id"),
            "other_attribute": lambda c: c[1].update(field="attribute:935"),
        }
        for name, forge in forgeries.items():
            with self.subTest(name=name):
                forged = copy.deepcopy(plan)
                forge(forged["changes"])
                self.assertFalse(executor.model_edit_scope(forged))

    def test_request_contract_on_host_and_mcp(self):
        f = self.family()
        adapter = TypeAdapter(ModelEditRequest)
        for good in (self.request(f, "kg"), self.request(f, 4), self.request(f, "C30/37", "material"),
                     self.request(f, "m", attribute_ids=[120])):
            adapter.validate_python(good)
        base = self.request(f)
        invalid = [
            self.request(f, "M3"), self.request(f, 5), self.request(f, True), self.request(f, "", "material"),
            self.request(f, 3, "material"), self.request(f, "m", "trade"),
            {**base, "changes": base["changes"] + [{"target": {"kind": "layer", "short_name": "W1"}}]},
            {**base, "changes": [{"target": {"kind": "paired_property", "property": "material",
                                             "tier_index": 1}, "value": "C"}]},
        ]
        for request in invalid:
            with self.subTest(request=request["changes"]):
                with self.assertRaises(ValidationError):
                    adapter.validate_python(request)
                f.native.assert_code("invalid_payload", lambda: f.native.call(request))
        f.native.base.ModifyElements.assert_not_called()


class IdentityRegenerationTests(unittest.TestCase):
    def setUp(self):
        g = families.NativeMaterialFamiliesTests()
        f = g.fixture("Column_TypeUUID", families.columns.ColumnElement)
        self.addCleanup(g.doCleanups)
        self.module = importlib.import_module(f.native.module.__package__ + ".wall_material")

    @staticmethod
    def ref(kind, model, view=None):
        return {"type_name": kind, "model_uuid": model, "view_uuid": view or model}

    def column_state(self, view="v1", container="c1", **extra):
        root = self.ref("Column_TypeUUID", "root", view)
        edge_parent = self.ref("Column_TypeUUID", "root", "edge")
        child = self.ref("AttributeContainer_TypeUUID", container)
        tree = {"target": root, "lineage": [root], "terminal_root": root, "children": [child],
                "child_parent_edges": [{"child": child, "parent": edge_parent}],
                "parent_chain_complete": True, "children_complete": True}
        return {"hierarchy": {"target": root, "lineage": [root], "terminal_root": root, "children": []},
                "component_tree": tree, "optional_properties": {"tier": {"Priority": 100}, **extra}}

    def test_column_container_and_root_view_rename_is_accepted(self):
        accepted = self.module.identity_regeneration("Column_TypeUUID", "CalculationMode",
                                                     self.column_state(), self.column_state("v2", "c2"))
        self.assertEqual(accepted["view_map"], {"v1": "v2"})
        self.assertEqual({p["type_name"] for p in accepted["regenerated_identities"]},
                         {"Column_TypeUUID", "AttributeContainer_TypeUUID"})

    def test_any_other_drift_or_unlisted_scope_is_rejected(self):
        before = self.column_state()
        cases = {
            "property_changed": ("Column_TypeUUID", "CalculationMode",
                                 self.column_state("v2", "c2", common={"Pen": 2})),
            "no_identity_change": ("Column_TypeUUID", "CalculationMode", self.column_state(common={"Pen": 2})),
            "material_field": ("Column_TypeUUID", "Material", self.column_state("v2", "c2")),
            "beam_root_view": ("Beam_TypeUUID", "CalculationMode", self.column_state("v2", "c1")),
        }
        for name, (kind, field, after) in cases.items():
            with self.subTest(case=name):
                self.assertIsNone(self.module.identity_regeneration(kind, field, before, after))
        moved = self.column_state("v2", "c2")
        moved["hierarchy"]["target"] = self.ref("Column_TypeUUID", "other", "v2")
        self.assertIsNone(self.module.identity_regeneration("Column_TypeUUID", "CalculationMode", before, moved))
        unlisted = self.column_state("v1", "c2")
        unlisted["component_tree"]["children"][0]["type_name"] = "Opening_TypeUUID"
        self.assertIsNone(self.module.identity_regeneration("Column_TypeUUID", "CalculationMode", before, unlisted))

    def test_two_containers_pair_by_content(self):
        def wall(root_container, tier_container, priority=300):
            return {"root_attribute_containers": [{"target": self.ref("AttributeContainer_TypeUUID", root_container),
                                                   "values": ["a"]}],
                    "tier_attribute_containers": [{"target": self.ref("AttributeContainer_TypeUUID", tier_container),
                                                   "values": ["b"]}],
                    "tier": {"Priority": priority}}
        accepted = self.module.identity_regeneration("Wall_TypeUUID", "CalculationMode",
                                                     wall("r1", "t1"), wall("r2", "t2"))
        self.assertEqual(len(accepted["regenerated_identities"]), 2)
        self.assertIsNone(self.module.identity_regeneration("Wall_TypeUUID", "CalculationMode",
                                                            wall("r1", "t1"), wall("r2", "t2", 301)))
        swapped = wall("r2", "t2")
        swapped["root_attribute_containers"][0]["values"] = ["b"]
        swapped["tier_attribute_containers"][0]["values"] = ["a"]
        self.assertIsNone(self.module.identity_regeneration("Wall_TypeUUID", "CalculationMode",
                                                            wall("r1", "t1"), swapped))


if __name__ == "__main__":
    unittest.main()
