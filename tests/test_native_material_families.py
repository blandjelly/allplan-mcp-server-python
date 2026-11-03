"""Exact architectural material routes; SDK doubles do not establish native PASS."""
import copy
import importlib
import sys
import unittest
from uuid import uuid4

import test_native_material_columns as columns
import test_wall_material_edit as walls


class BeamElement(columns.ColumnElement):
    pass


class StructuralBeamElement:
    """2026 structural API deliberately has no Properties/SetProperties."""
    def __init__(self, properties):
        self.StructuralBeamProperties = properties

    def SetStructuralBeamProperties(self, properties):
        self.StructuralBeamProperties = properties


class SlabElement(columns.ColumnElement):
    pass


class NativeMaterialFamiliesTests(unittest.TestCase):
    def fixture(self, kind, native_class):
        f = columns.ColumnMaterialTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        f.root.GetElementAdapterType.return_value.GetTypeName.return_value = kind
        arch = sys.modules["NemAll_Python_ArchElements"]
        arch.BeamElement, arch.StructuralBeamElement, arch.SlabElement = BeamElement, StructuralBeamElement, SlabElement
        f.native.base.GetElement.side_effect = lambda _: native_class(copy.deepcopy(f.properties))

        def modify(doc, elements):
            self.assertEqual(len(elements), 1)
            self.assertIsInstance(elements[0], native_class)
            props = (elements[0].StructuralBeamProperties if native_class is StructuralBeamElement
                     else elements[0].Properties)
            f.properties = copy.deepcopy(props)
            return elements

        f.native.base.ModifyElements.side_effect = modify
        f.preview = lambda: f.native.call(f.fixture.request(native_types=[kind]))
        return f

    def test_beam_and_slab_material_apply_readback_replay_and_no_op(self):
        for kind, cls in (("Beam_TypeUUID", BeamElement), ("SkeletonBeam_TypeUUID", BeamElement),
                          ("SkeletonBeam_TypeUUID", StructuralBeamElement), ("Slab_TypeUUID", SlabElement),
                          ("MultiSlab_TypeUUID", SlabElement)):
            with self.subTest(kind=kind, representation=cls.__name__):
                f = self.fixture(kind, cls)
                if kind == "MultiSlab_TypeUUID":
                    f.properties.Material = ""
                before = copy.deepcopy(vars(f.properties))
                plan = f.preview()
                self.assertTrue(plan["apply_available"], plan)
                self.assertEqual(plan["changes"][0]["native_type"], kind)
                self.assertEqual(plan["changes"][0]["resource"]["native_material_state"]["native_class"], cls.__name__)
                f.native.highlight(plan)
                execution = uuid4().hex
                result = f.native.apply(plan, execution)
                self.assertEqual(result["state"], "completed", result)
                self.assertEqual(result["outcomes"][0]["readback"]["value"], "C35/45")
                after = vars(f.properties).copy()
                del before["Material"], after["Material"]
                self.assertEqual(before, after)
                self.assertTrue(f.native.apply(plan, execution)["replayed"])
                f.native.base.ModifyElements.assert_called_once()
                f.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
                self.assertEqual(f.preview()["state"], "no_op")

    def test_structural_beam_requires_its_documented_setter(self):
        f = self.fixture("SkeletonBeam_TypeUUID", StructuralBeamElement)
        class WrongSetter(StructuralBeamElement):
            SetStructuralBeamProperties = None
            def SetProperties(self, properties):
                raise AssertionError("Generic setter must never be used")
        f.native.base.GetElement.side_effect = lambda _: WrongSetter(copy.deepcopy(f.properties))
        plan = f.preview()
        self.assertFalse(plan["apply_available"], plan)
        self.assertFalse(plan["changes"])
        f.native.base.ModifyElements.assert_not_called()

    def test_slab_tier_is_an_exact_target_without_redirection_to_aggregate(self):
        f = self.fixture("Slab_TypeUUID", SlabElement)
        parent = f.native.element(98, name="MultiSlab_TypeUUID")
        f.native.parents[id(f.root)] = parent
        f.native.children[id(parent)] = [f.root]
        plan = f.preview()
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["changes"][0]["ref"]["model_uuid"], f.root.GetModelElementUUID())
        f.native.highlight(plan)
        self.assertEqual(f.native.apply(plan)["state"], "completed")
        self.assertTrue(all(call.args[0] is f.root for call in f.native.base.GetElement.call_args_list))

    def test_wrong_representation_and_nested_non_slab_owner_still_block(self):
        f = self.fixture("SkeletonBeam_TypeUUID", SlabElement)
        plan = f.preview()
        self.assertFalse(plan["apply_available"])
        f.native.base.GetElement.side_effect = lambda _: BeamElement(copy.deepcopy(f.properties))
        f.native.parents[id(f.root)] = f.native.element(98, name="Macro_TypeUUID")
        self.assertFalse(f.preview()["apply_available"])
        f.native.base.ModifyElements.assert_not_called()

    def test_material_and_lineage_drift_block_slab_setter(self):
        f = self.fixture("MultiSlab_TypeUUID", SlabElement)
        plan = f.preview()
        f.native.highlight(plan)
        f.properties.Material = "changed"
        f.native.assert_code("repair_conflict", lambda: f.native.apply(plan))
        f.properties.Material = "Beton"
        plan = f.preview()
        f.native.highlight(plan)
        f.native.parents[id(f.root)] = f.native.element(98, name="Macro_TypeUUID")
        f.native.assert_code("repair_conflict", lambda: f.native.apply(plan))
        f.native.base.ModifyElements.assert_not_called()

    def test_aggregate_child_geometry_drift_blocks_the_native_material_setter(self):
        f = self.fixture("MultiSlab_TypeUUID", SlabElement)
        tier = f.native.element(98, name="Slab_TypeUUID", solid=walls.Polyhedron("slab-tier"))
        f.native.parents[id(tier)] = f.root
        f.native.children[id(f.root)] = [tier]
        plan = f.preview()
        self.assertTrue(plan["apply_available"], plan)
        f.native.highlight(plan)
        tier.GetModelGeometry.return_value.stream = "changed slab geometry"
        f.native.assert_code("repair_conflict", lambda: f.native.apply(plan))
        f.native.base.ModifyElements.assert_not_called()

    def test_native_parent_and_child_cannot_be_written_in_one_plan(self):
        f = self.fixture("MultiSlab_TypeUUID", SlabElement)
        child = f.native.element(98, name="Slab_TypeUUID")
        f.native.parents[id(child)] = f.root
        f.native.children[id(f.root)] = [child]
        f.native.base.ElementsSelectService.SelectAllElements.return_value = [f.root, child]
        plan = f.native.call(f.fixture.request(native_types=["Slab_TypeUUID", "MultiSlab_TypeUUID"]))
        self.assertFalse(plan["apply_available"], plan)
        self.assertIn("overlapping_slab_property_owners", {item["reason"] for item in plan["blocked"]})
        f.native.base.ModifyElements.assert_not_called()

    def test_beam_lost_response_is_recovered_without_repeating_setter(self):
        f = self.fixture("SkeletonBeam_TypeUUID", BeamElement)
        setter = f.native.base.ModifyElements.side_effect

        def lost(*args):
            setter(*args)
            raise RuntimeError("lost response")

        f.native.base.ModifyElements.side_effect = lost
        plan = f.preview()
        f.native.highlight(plan)
        execution = uuid4().hex
        result = f.native.apply(plan, execution)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(f.native.apply(plan, execution)["replayed"])
        self.assertEqual(f.native.recover(execution)["outcomes"][0]["state"], "reconciled")
        f.native.base.ModifyElements.assert_called_once()

    def beam_with_regenerated_children(self, kind="Beam_TypeUUID", native_class=BeamElement,
                                       original=("AttributeContainer_TypeUUID", "WallAxis_TypeUUID"),
                                       regenerated=None, before_apply=False):
        """ModifyElements (or a pre-Apply edit) replaces the root's children."""
        f = self.fixture(kind, native_class)
        old = [f.native.element(97 - n, name=name) for n, name in enumerate(original)]
        for child in old:
            f.native.parents[id(child)] = f.root
        f.native.children[id(f.root)] = list(old)
        new = [f.native.element(90 - n, name=name)
               for n, name in enumerate(original if regenerated is None else regenerated)]
        for child in new:
            f.native.parents[id(child)] = f.root
        setter = f.native.base.ModifyElements.side_effect

        def modify(doc, elements):
            result = setter(doc, elements)
            f.native.children[id(f.root)] = list(new)
            return result

        if not before_apply:
            f.native.base.ModifyElements.side_effect = modify
        plan = f.preview()
        self.assertTrue(plan["apply_available"], plan)
        f.native.highlight(plan)
        if before_apply:
            f.native.children[id(f.root)] = list(new)
        return f, plan, old, new

    def test_beam_regenerated_auxiliary_children_are_accepted_after_setter(self):
        # 0.44.1/0.44.2 native trials: readback and UI showed C30/37 and
        # ModifyElements replaced only the AttributeContainer and WallAxis
        # children one-for-one under the unchanged root; UI Undo restored them.
        f, plan, old, new = self.beam_with_regenerated_children()
        execution = uuid4().hex
        result = f.native.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        outcome = result["outcomes"][0]
        self.assertEqual((outcome["state"], outcome["reason"]), ("applied", "readback_matches"))
        self.assertEqual(outcome["readback"], {"status": "observed", "value": "C35/45"})
        consensus = outcome["representation_consensus"]
        self.assertTrue(consensus["agreed"])
        reviewed = consensus["representations"][0]
        self.assertNotIn("reason", reviewed)
        self.assertNotIn("preservation", reviewed)
        accepted = reviewed["accepted_preservation_drift"]
        self.assertEqual(accepted["accepted"], "auxiliary_children_regenerated")
        self.assertEqual(accepted["changed_sections"], ["component_tree"])
        diff = accepted["component_tree_diff"]
        self.assertEqual(diff["child_type_changes"],
                         {"AttributeContainer_TypeUUID": {"removed": 1, "added": 1},
                          "WallAxis_TypeUUID": {"removed": 1, "added": 1}})
        self.assertEqual((diff["root_changes"], diff["flag_changes"], diff["lineage_changed"]), ({}, {}, False))
        self.assertTrue(all(any(c.GetModelElementUUID() in item for item in diff["children_removed"]["items"])
                            for c in old))
        self.assertTrue(all(any(c.GetModelElementUUID() in item for item in diff["children_added"]["items"])
                            for c in new))
        self.assertTrue(f.native.apply(plan, execution)["replayed"])
        f.native.base.ModifyElements.assert_called_once()

    def test_regeneration_before_apply_still_blocks_the_setter(self):
        f, plan, _, _ = self.beam_with_regenerated_children(before_apply=True)
        f.native.assert_code("repair_conflict", lambda: f.native.apply(plan))
        f.native.base.ModifyElements.assert_not_called()

    def test_other_post_setter_tree_drift_stays_unknown_with_named_diff(self):
        cases = {
            "unlisted_child_type": dict(original=("AttributeContainer_TypeUUID", "Opening_TypeUUID"),
                                        regenerated=("AttributeContainer_TypeUUID", "Opening_TypeUUID")),
            "child_lost": dict(regenerated=("AttributeContainer_TypeUUID",)),
            "child_added": dict(regenerated=("AttributeContainer_TypeUUID", "WallAxis_TypeUUID",
                                             "WallAxis_TypeUUID")),
            "type_swapped": dict(regenerated=("AttributeContainer_TypeUUID", "AttributeContainer_TypeUUID")),
            "unlisted_family": dict(kind="Column_TypeUUID", native_class=columns.ColumnElement),
        }
        for name, options in cases.items():
            with self.subTest(case=name):
                f, plan, _, _ = self.beam_with_regenerated_children(**options)
                execution = uuid4().hex
                outcome = f.native.apply(plan, execution)["outcomes"][0]
                self.assertEqual(outcome["state"], "unknown", outcome)
                consensus = outcome["representation_consensus"]
                self.assertEqual(consensus["reconciliation_readback"], {"status": "observed", "value": "C35/45"})
                representation = consensus["representations"][0]
                self.assertNotIn("accepted_preservation_drift", representation)
                self.assertIn(representation["reason"], {"native_material_invariants_changed"})
                self.assertEqual(representation["preservation"]["component_tree_diff"]["status"], "observed")
                recovery = f.native.recover(execution)
                self.assertTrue(recovery["write_blocked"])
                target = recovery["recovery"]["reconciliation"]["targets"][0]
                self.assertIn("component_tree_diff", target["representations"][0]["preservation"])
                f.native.base.ModifyElements.assert_called_once()

    def test_regeneration_classifier_requires_identical_root_sections_and_edges(self):
        module = importlib.import_module(self.fixture("Beam_TypeUUID", BeamElement).native.module.__package__
                                         + ".wall_material")
        root = {"type_name": "Beam_TypeUUID", "model_uuid": "r", "view_uuid": "a"}
        child = lambda n, kind="AttributeContainer_TypeUUID": {"type_name": kind, "model_uuid": "m%d" % n,
                                                               "view_uuid": "v%d" % n}

        def state(children, parent=root, **extra):
            return {"geometry": {"stream_sha256": "g"}, "hierarchy": {"target": root},
                    "component_tree": {"target": root, "lineage": [root], "terminal_root": root,
                                       "parent_chain_complete": True, "children_complete": True,
                                       "children": children,
                                       "child_parent_edges": [{"child": c, "parent": parent} for c in children]},
                    **extra}

        accepted = module.regenerated_auxiliary_children
        self.assertTrue(accepted("Beam_TypeUUID", state([child(1)]), state([child(2)])))
        self.assertFalse(accepted("Beam_TypeUUID", state([child(1)]), state([child(1)])))
        self.assertFalse(accepted("Wall_TypeUUID", state([child(1)]), state([child(2)])))
        moved = {**root, "view_uuid": "b"}
        self.assertFalse(accepted("Beam_TypeUUID", state([child(1)]), state([child(2)], parent=moved)))
        changed = state([child(2)])
        changed["geometry"] = {"stream_sha256": "other"}
        self.assertFalse(accepted("Beam_TypeUUID", state([child(1)]), changed))
        incomplete = state([child(1)])
        incomplete["component_tree"]["children_complete"] = False
        self.assertFalse(accepted("Beam_TypeUUID", incomplete, state([child(2)])))
        lineage = state([child(2)])
        lineage["component_tree"]["lineage"] = [root, moved]
        self.assertFalse(accepted("Beam_TypeUUID", state([child(1)]), lineage))
        doubled = state([child(2)])
        doubled["component_tree"]["child_parent_edges"].append({"child": child(2), "parent": moved})
        self.assertFalse(accepted("Beam_TypeUUID", state([child(1)]), doubled))

    def test_component_tree_diff_is_bounded_and_reports_unobserved_trees(self):
        module = importlib.import_module(self.fixture("Beam_TypeUUID", BeamElement).native.module.__package__
                                         + ".wall_material")
        self.assertEqual(module.component_tree_diff(None, {"target": {}})["status"], "not_checked")
        ref = lambda n: {"type_name": "AttributeContainer_TypeUUID", "model_uuid": "m%d" % n, "view_uuid": "v%d" % n}
        root = {"type_name": "Beam_TypeUUID", "model_uuid": "r", "view_uuid": "a"}
        before = {"target": root, "lineage": [root], "children": [ref(n) for n in range(10)]}
        after = {"target": {**root, "view_uuid": "b"}, "lineage": [root], "children": []}
        diff = module.component_tree_diff(before, after)
        self.assertEqual(diff["children_removed"]["count"], 10)
        self.assertEqual(len(diff["children_removed"]["items"]), module.MAX_TREE_DIFF_ITEMS)
        self.assertTrue(diff["children_removed"]["truncated"])
        self.assertEqual(diff["root_changes"]["target"]["current"], "Beam_TypeUUID|r|b")


class MaterialEvidenceBudgetTests(unittest.TestCase):
    def setUp(self):
        self.f = walls.WallMaterialEditTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def test_durable_trace_latency_has_a_bounded_material_allowance(self):
        f, now = self.f, [0.0]
        trace = importlib.import_module(f.native.module.__package__ + ".property_probe").NativeProbeTrace
        from unittest.mock import patch
        f.native.handler.model_queries.clock = lambda: now[0]

        def record(*args, **kwargs):
            now[0] += 0.012

        with patch.object(trace, "record", record):
            self.assertTrue(f.preview()["apply_available"])
        self.assertGreater(now[0], 5.0)
        self.assertLess(now[0], 10.0)
        now[0] = 0.0

        def slow(*args, **kwargs):
            now[0] += 0.1

        with patch.object(trace, "record", slow):
            f.native.assert_code("scan_limit_exceeded", f.preview)
        f.native.base.ModifyElements.assert_not_called()

    def test_material_skips_nonmatching_peers_but_revalidation_detects_new_match(self):
        f = self.f
        peer = f.native.element(98, name="Wall_TypeUUID")
        peer_props = walls.WallProperties("peer-material")
        peer_props.GetWallTierProperties(1).Thickness = 200.0
        selected = f.native.base.GetElement.side_effect
        f.native.base.GetElement.side_effect = lambda adapter: (
            walls.FakeWallElement(copy.deepcopy(peer_props)) if adapter is peer else selected(adapter))
        f.native.base.ElementsSelectService.SelectAllElements.return_value = [f.root, f.tier, peer]
        predicate = {"field": "wall.total_thickness_mm", "op": "eq", "value": 240.0}
        plan = f.preview(predicate=predicate)
        self.assertTrue(plan["apply_available"], plan)
        material_roots = {row.get("model_uuid") for row in f.trace_records if row["api"] == "Native.material_observation"}
        self.assertEqual(material_roots, {f.root.GetModelElementUUID()})
        f.native.highlight(plan)
        peer_props.GetWallTierProperties(1).Thickness = 240.0
        f.native.assert_code("repair_conflict", lambda: f.native.apply(plan))
        f.native.base.ModifyElements.assert_not_called()
