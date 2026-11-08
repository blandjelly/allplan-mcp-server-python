"""Paired native property + same-named attribute (0.50.0) and the CalculationMode
post-setter identity regeneration rule; SDK doubles do not establish native PASS."""
import copy
import importlib
import json
import unittest
from pathlib import Path
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
        self.assertNotIn("paired_property_hint", plan)
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

    def test_single_place_attribute_120_on_the_beam_is_blocked_and_routed(self):
        # 0.51.1 trial (8cc1e687…): "only attribute 120" on the Beam also
        # changed the native CalculationMode 0 -> 2; one UI Undo restored both.
        f = self.family("Beam_TypeUUID", families.BeamElement, code=0, attribute="m3")
        single = {"target": {"kind": "attribute", "attribute_id": 120, "property_owner": "selected_element"},
                  "value": "m", "value_type": "auto"}
        plan = f.native.call(f.fixture.request(native_types=["Beam_TypeUUID"], changes=[single]))
        self.assertFalse(plan["apply_available"], plan)
        self.assertEqual(plan["changes"], [])
        blocked, = plan["blocked"]
        self.assertEqual((blocked["field"], blocked["reason"], blocked["native_field"]),
                         ("attribute:120", "attribute_write_also_changes_native_property",
                          "native.calculation_mode"))
        self.assertEqual(blocked["paired_route"],
                         {"target": {"kind": "paired_property", "property": "calculation_mode"}, "value": "m"})
        f.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        # The paired route plans both places; the attribute half is not blocked.
        paired_plan = self.plan(f, "m")
        self.assertTrue(paired_plan["apply_available"], paired_plan)
        self.assertEqual([c["field"] for c in paired_plan["changes"]],
                         ["native.calculation_mode", "attribute:120"])
        # Column: not observed in this direction, the single place stays open.
        g = self.family(code=0, attribute="m3")
        column = g.native.call(g.fixture.request(native_types=["Column_TypeUUID"], changes=[single]))
        self.assertTrue(column["apply_available"], column)
        self.assertEqual([c["field"] for c in column["changes"]], ["attribute:120"])

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
            "unlisted_family": ("SkeletonBeam_TypeUUID", "Material", self.column_state("v2", "c2")),
            "unlisted_field": ("Column_TypeUUID", "Thickness", self.column_state("v2", "c2")),
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

    def test_material_uses_the_same_family_rule_0510(self):
        """0.51.0: the renaming is a property of the family's ModifyElements."""
        before, after = self.column_state(), self.column_state("v2", "c2")
        for field in ("CalculationMode", "Material"):
            with self.subTest(field=field):
                accepted = self.module.identity_regeneration("Column_TypeUUID", field, before, after)
                self.assertEqual(accepted["view_map"], {"v1": "v2"})
        self.assertIsNone(self.module.identity_regeneration(
            "Column_TypeUUID", "Material", before, self.column_state("v2", "c2", common={"Pen": 2})))

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


TRIAL_0500_WALL_DOOR = Path(__file__).with_name("data") / "wall_door_calculation_mode_0500.json"
# Pairs read from the 0.50.0 trial's identity_diff (execution bd30912a…); the
# pairing of the two AttributeContainers is the one whose renamed evidence
# hashes to the logged post-setter evidence.
TRIAL_0500_RENAMES = {
    "40af011e-d3c2-4bc9-9569-455b9eec9e1f": "76ef73aa-90bd-4c3a-a998-07989b0fb572",  # door-tier container
    "f819e327-d677-405c-82c1-585a45f1542b": "e8bab07a-5a64-40dc-88b9-9eec75167b1c",  # root container
    "3f997788-393a-429c-b8c2-72d7b7889f4e": "f7e9188a-019d-4f2f-b152-9b1f2280f091",  # DoorSill model
    "f7cb9413-e631-4949-9e63-ace810f79eb5": "3bdfa64d-35cd-486c-a72e-ebeecad94ba4",  # DoorSill view
    "7cd38176-c421-4671-8add-ca1d6a0499f8": "def5095f-c354-46f7-abca-d9678f680c26",  # Door model
    "b2d2514f-ed79-4d9d-819e-3ee64128a705": "795be646-2b1c-47cd-ae9b-ede532372b9d",  # Door view
}


class WallDoorRegenerationTests(unittest.TestCase):
    """0.50.0 trial: a paired write on the Wall with a door stopped `unknown`
    because the setter also regenerated the Door and DoorSill identities, so
    attribute 120 was never written. 0.50.1 lists both types for the Wall."""

    def setUp(self):
        g = families.NativeMaterialFamiliesTests()
        f = g.fixture("Column_TypeUUID", families.columns.ColumnElement)
        self.addCleanup(g.doCleanups)
        package = f.native.module.__package__
        self.module = importlib.import_module(package + ".wall_material")
        self.fingerprint = importlib.import_module(package + ".query_contracts").fingerprint
        self.trial = json.loads(TRIAL_0500_WALL_DOOR.read_text(encoding="utf-8"))

    def after(self, renames=TRIAL_0500_RENAMES):
        return self.module._canonical(self.module._rename(self.trial["bound_state"], renames))

    def test_trial_evidence_is_a_renaming_of_door_and_containers(self):
        reported = self.trial["reported_preservation"]
        before = self.trial["bound_state"]
        self.assertEqual(self.fingerprint(before), reported["before_sha256"])
        after = self.after()
        # Fixture fidelity: the reconstruction is exactly the logged post-setter evidence.
        self.assertEqual(self.fingerprint(after), reported["current_sha256"])
        self.assertEqual(self.module.identity_diff(before, after), reported["identity_diff"])
        accepted = self.module.identity_regeneration("Wall_TypeUUID", "CalculationMode", before, after)
        self.assertIsNotNone(accepted)
        self.assertEqual(accepted["view_map"], {})
        self.assertEqual(sorted(p["type_name"] for p in accepted["regenerated_identities"]),
                         ["AttributeContainer_TypeUUID", "AttributeContainer_TypeUUID",
                          "DoorSill_TypeUUID", "Door_TypeUUID"])
        pairs = {p["old_model_uuid"]: p["new_model_uuid"] for p in accepted["regenerated_identities"]}
        self.assertEqual(pairs, {old: new for old, new in TRIAL_0500_RENAMES.items()
                                 if old in {"40af011e-d3c2-4bc9-9569-455b9eec9e1f",
                                            "f819e327-d677-405c-82c1-585a45f1542b",
                                            "3f997788-393a-429c-b8c2-72d7b7889f4e",
                                            "7cd38176-c421-4671-8add-ca1d6a0499f8"}})

    def test_door_renaming_stays_strict(self):
        before = self.trial["bound_state"]
        door_reveal = before["partial_preservation"]["auxiliary_components"]["root"][0]["children"][0]["children"][0]
        self.assertEqual(door_reveal["ownership"]["target"]["type_name"], "DoorReveal_TypeUUID")
        cases = {}
        changed = self.after()
        reveal = changed["partial_preservation"]["auxiliary_components"]["root"][0]["children"][0]["children"]
        for item in reveal:
            if item["ownership"]["target"]["type_name"] == "DoorReveal_TypeUUID":
                item["geometry"]["stream_sha256"] = "0" * 64
        cases["door_reveal_geometry"] = ("Wall_TypeUUID", "CalculationMode", changed)
        cases["door_tier_regenerated"] = ("Wall_TypeUUID", "CalculationMode", self.after(
            {**TRIAL_0500_RENAMES, "82b89213-157f-4ac5-82ea-0cba3f533270": str(uuid4())}))
        cases["column_family"] = ("Column_TypeUUID", "CalculationMode", self.after())
        for name, (kind, field, after) in cases.items():
            with self.subTest(case=name):
                self.assertIsNone(self.module.identity_regeneration(kind, field, before, after))
        # 0.51.0: the same Wall rule covers Material and a window; an
        # unlisted opening type is still rejected.
        self.assertIsNotNone(self.module.identity_regeneration("Wall_TypeUUID", "Material", before, self.after()))
        window = json.loads(json.dumps(before).replace("Door_TypeUUID", "Window_TypeUUID"))
        window_after = self.module._canonical(self.module._rename(window, TRIAL_0500_RENAMES))
        self.assertIsNotNone(self.module.identity_regeneration("Wall_TypeUUID", "CalculationMode",
                                                               window, window_after))
        niche = json.loads(json.dumps(before).replace("Door_TypeUUID", "Niche_TypeUUID"))
        niche_after = self.module._canonical(self.module._rename(niche, TRIAL_0500_RENAMES))
        self.assertIsNone(self.module.identity_regeneration("Wall_TypeUUID", "CalculationMode",
                                                            niche, niche_after))

    def test_wall_with_door_paired_write_writes_the_attribute_after_regeneration(self):
        wall = families.columns.wall_fixtures.WallMaterialEditTests("setUp")
        wall.setUp()
        self.addCleanup(wall.doCleanups)
        native, root = wall.native, wall.root
        shape = families.columns.wall_fixtures.Polyhedron
        native.base.eAttibuteReadState.ReadAll = "ReadAll"
        wall.properties.GetWallTierProperties(1).CalculationMode = 0
        root.GetAttributes.return_value = [(935, ""), (120, "m3")]
        bind_attribute_120(native)
        door_tier = native.element(60, name="DoorTier_TypeUUID", solid=shape("door-tier"))
        reveal = native.element(61, name="DoorReveal_TypeUUID", solid=shape("door-reveal"))

        def door(ident):
            parts = (native.element(ident, name="Door_TypeUUID", solid=shape("door")),
                     native.element(ident + 1, name="DoorSill_TypeUUID", solid=shape("sill")),
                     native.element(ident + 2, name="AttributeContainer_TypeUUID", solid=shape("meta")))
            parts[2].GetAttributes.return_value = [(508, "door")]
            return parts

        old, new = door(70), door(80)
        for before, after in zip(old, new):
            # Regenerated components keep their SDK type; only identities change.
            after.GetElementAdapterType.return_value.GetGuid.return_value = (
                before.GetElementAdapterType.return_value.GetGuid.return_value)

        def attach(parts):
            opening, sill, container = parts
            native.children[id(root)] = [wall.tier, opening]
            native.children[id(opening)] = [door_tier]
            native.children[id(door_tier)] = [sill, reveal, container]
            for child, parent in ((opening, root), (door_tier, opening), (sill, door_tier),
                                  (reveal, door_tier), (container, door_tier)):
                native.parents[id(child)] = parent

        attach(old)
        native.base.ElementsSelectService.SelectAllElements.return_value = [root]
        modify = native.base.ModifyElements.side_effect

        def regenerate(doc, elements):
            result = modify(doc, elements)
            attach(new)
            return result

        native.base.ModifyElements.side_effect = regenerate
        plan = native.call(wall.request(changes=[
            {"target": {"kind": "paired_property", "property": "calculation_mode"}, "value": "m"}]))
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual([c["field"] for c in plan["changes"]], ["native.calculation_mode", "attribute:120"])
        native.highlight(plan)
        execution = uuid4().hex
        result = native.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        first, second = result["outcomes"]
        self.assertEqual((first["state"], first["readback"]), ("applied", {"status": "observed", "value": 2}))
        drift = first["representation_consensus"]["representations"][0]["accepted_preservation_drift"]
        self.assertEqual(drift["accepted"], "identities_regenerated_evidence_otherwise_equal")
        self.assertEqual(sorted(p["type_name"] for p in drift["regenerated_identities"]),
                         ["AttributeContainer_TypeUUID", "DoorSill_TypeUUID", "Door_TypeUUID"])
        self.assertEqual(drift["view_map"], {})
        self.assertEqual((second["state"], second["reason"]), ("applied", "readback_matches"))
        self.assertNotIn("effective_target_view_uuid", second)
        self.assertEqual(dict(root.GetAttributes.return_value)[120], "m")
        self.assertEqual(wall.properties.GetWallTierProperties(1).CalculationMode, 2)
        native.base.ModifyElements.assert_called_once()
        self.assertEqual(native.base.ElementsAttributeService.ChangeAttributes.call_args.args[0], [(120, "m")])
        self.assertTrue(native.apply(plan, execution)["replayed"])
        native.base.ModifyElements.assert_called_once()

    def test_unlisted_opening_regeneration_still_skips_the_attribute(self):
        wall = families.columns.wall_fixtures.WallMaterialEditTests("setUp")
        wall.setUp()
        self.addCleanup(wall.doCleanups)
        native, root = wall.native, wall.root
        shape = families.columns.wall_fixtures.Polyhedron
        wall.properties.GetWallTierProperties(1).CalculationMode = 0
        root.GetAttributes.return_value = [(935, ""), (120, "m3")]
        bind_attribute_120(native)
        # Window_TypeUUID is listed from 0.51.0; a niche is still unlisted.
        old = native.element(70, name="Niche_TypeUUID", solid=shape("niche"))
        new = native.element(80, name="Niche_TypeUUID", solid=shape("niche"))
        new.GetElementAdapterType.return_value.GetGuid.return_value = (
            old.GetElementAdapterType.return_value.GetGuid.return_value)
        native.children[id(root)] = [wall.tier, old]
        native.parents[id(old)] = native.parents[id(new)] = root
        native.base.ElementsSelectService.SelectAllElements.return_value = [root]
        modify = native.base.ModifyElements.side_effect

        def regenerate(doc, elements):
            result = modify(doc, elements)
            native.children[id(root)] = [wall.tier, new]
            return result

        native.base.ModifyElements.side_effect = regenerate
        plan = native.call(wall.request(changes=[
            {"target": {"kind": "paired_property", "property": "calculation_mode"}, "value": "m"}]))
        native.highlight(plan)
        execution = uuid4().hex
        result = native.apply(plan, execution)
        first, second = result["outcomes"]
        self.assertEqual(first["state"], "unknown", result)
        diff = first["representation_consensus"]["representations"][0]["preservation"]["identity_diff"]
        self.assertEqual(diff["removed"]["items"][0].split("|")[0], "Niche_TypeUUID")
        self.assertEqual((second["state"], second["reason"]), ("skipped", "not_attempted"))
        native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertTrue(native.recover(execution)["write_blocked"])
        native.base.ModifyElements.assert_called_once()


if __name__ == "__main__":
    unittest.main()
