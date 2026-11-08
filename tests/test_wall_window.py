"""0.51.0: native Material on Walls, paired material, and a Wall with a window.

0.50.1 trial (2026-11-07): native Material writes on the Wall 240 (9ed2e229…)
and the Wall 200 with door (37196703…) reached the value but stayed
`unknown` with the same changed sections as the accepted CalculationMode
renamings; the paired material plan on the Wall 200 was blocked because
attribute 508 is not stored there. SDK doubles only; no native PASS.
"""
import unittest
from uuid import uuid4

import test_native_material_families as families
import test_paired_property as paired

Polyhedron = families.columns.wall_fixtures.Polyhedron


class WallFixture:
    """A single-tier Wall with optional opening subtrees whose parts can regenerate."""

    def __init__(self, case, attributes=((935, ""), (508, "Silikat"))):
        self.wall = families.columns.wall_fixtures.WallMaterialEditTests("setUp")
        self.wall.setUp()
        case.addCleanup(self.wall.doCleanups)
        self.native, self.root = self.wall.native, self.wall.root
        self.native.base.eAttibuteReadState.ReadAll = "ReadAll"
        self.wall.material = "TEST"
        self.wall.properties.GetWallTierProperties(1).Material = "TEST"
        self.wall.properties.GetWallTierProperties(1).CalculationMode = 0
        self.root.GetAttributes.return_value = list(attributes) + [(120, "m3")]
        paired.bind_attribute_120(self.native)
        self.native.base.ElementsSelectService.SelectAllElements.return_value = [self.root]
        self.tier_lists = []
        # Position of the WallTier among the Wall's enumerated children
        # (0 = first, None = last); the native order is not documented.
        self.tier_position = 0

    def part(self, ident, name, attrs=None):
        element = self.native.element(ident, name=name, solid=Polyhedron(name))
        if attrs is not None:
            element.GetAttributes.return_value = attrs
        return element

    def window(self, ident, keep):
        """Window -> WindowTier -> (Sill, WindowReveal -> SmartPart -> AC, AC); 0.50.1 query."""
        tier, reveal = keep
        window = self.part(ident, "Window_TypeUUID")
        sill = self.part(ident + 1, "Sill_TypeUUID")
        smart = self.part(ident + 2, "WindowOpeningSmartPart_TypeUUID")
        smart_meta = self.part(ident + 3, "AttributeContainer_TypeUUID", [(508, "frame"), (900, "SP")])
        tier_meta = self.part(ident + 4, "AttributeContainer_TypeUUID", [(508, "window"), (901, "WT")])
        return {window: self.root, tier: window, sill: tier, reveal: tier, smart: reveal,
                smart_meta: smart, tier_meta: tier}

    def root_container(self, ident):
        return {self.part(ident, "AttributeContainer_TypeUUID", [(508, "root"), (902, "R")]): self.root}

    def attach(self, *subtrees):
        parents = {self.wall.tier: self.root}
        for subtree in subtrees:
            parents.update(subtree)
        children = {}
        for child, parent in parents.items():
            self.native.parents[id(child)] = parent
            children.setdefault(id(parent), []).append(child)
        for parent_id in list(self.native.children):
            self.native.children[parent_id] = []
        self.native.children.update(children)
        root_children = self.native.children[id(self.root)]
        root_children.remove(self.wall.tier)
        root_children.insert(len(root_children) if self.tier_position is None else self.tier_position,
                             self.wall.tier)
        for listed in self.tier_lists:
            # 0.50.1 query: the WallTier also enumerates the opening tier,
            # whose parent is the opening (component_child_owner_mismatch).
            self.native.children.setdefault(id(self.wall.tier), []).append(listed)

    def same_types(self, old, new):
        """A regenerated part keeps its SDK type UUID; only identities change."""
        for before, after in zip(old, new):
            after.GetElementAdapterType.return_value.GetGuid.return_value = (
                before.GetElementAdapterType.return_value.GetGuid.return_value)

    def regenerate_on_write(self, *subtrees, tier_position=0):
        modify = self.native.base.ModifyElements.side_effect

        def regenerate(doc, elements):
            result = modify(doc, elements)
            self.tier_position = tier_position
            self.attach(*subtrees)
            return result

        self.native.base.ModifyElements.side_effect = regenerate

    def plan(self, change):
        plan = self.native.call(self.wall.request(changes=[change]))
        if plan.get("apply_available"):
            self.native.highlight(plan)
        return plan

    def attribute(self, ident):
        return dict(self.root.GetAttributes.return_value).get(ident)


PAIRED_MATERIAL = {"target": {"kind": "paired_property", "property": "material"}, "value": "Cegła"}


class WallMaterialTests(unittest.TestCase):
    def test_paired_material_on_a_plain_wall_writes_both_places_in_one_step(self):
        # Wall 240: native "TEST", attribute 508 "Silikat" (0.48.0 / 0.50.1).
        w = WallFixture(self)
        old, new = w.root_container(40), w.root_container(41)
        w.same_types(old, new)
        w.attach(old)
        w.regenerate_on_write(new)
        plan = w.plan(PAIRED_MATERIAL)
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual([c["field"] for c in plan["changes"]], ["native.material", "attribute:508"])
        self.assertEqual(plan["changes"][1]["old_value"], {"status": "observed", "value": "Silikat"})
        self.assertEqual(plan["paired_property"]["attribute_follows_native"], [])
        execution = uuid4().hex
        result = w.native.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        native, attribute = result["outcomes"]
        drift = native["representation_consensus"]["representations"][0]["accepted_preservation_drift"]
        self.assertEqual(drift["accepted"], "identities_regenerated_evidence_otherwise_equal")
        self.assertEqual([p["type_name"] for p in drift["regenerated_identities"]],
                         ["AttributeContainer_TypeUUID"])
        self.assertEqual((attribute["state"], attribute["reason"]), ("applied", "readback_matches"))
        self.assertEqual((w.wall.material, w.attribute(508)), ("Cegła", "Cegła"))
        self.assertEqual((result["undo_group"]["status"], result["undo_group"]["setters_in_step"]),
                         ("created", 2))
        self.assertTrue(w.native.apply(plan, execution)["replayed"])
        w.native.base.ModifyElements.assert_called_once()

    def test_not_stored_attribute_follows_the_native_material_on_the_wall(self):
        # Wall 200 with door: attribute 508 absent from both read modes; the
        # owner saw the attributes palette follow the native write (0.50.1).
        w = WallFixture(self, attributes=((935, ""),))
        door_tier = w.part(60, "DoorTier_TypeUUID")
        reveal = w.part(61, "DoorReveal_TypeUUID")

        def door(ident):
            opening = w.part(ident, "Door_TypeUUID")
            sill = w.part(ident + 1, "DoorSill_TypeUUID")
            meta = w.part(ident + 2, "AttributeContainer_TypeUUID", [(508, "door")])
            return [opening, sill, meta], {opening: w.root, door_tier: opening, sill: door_tier,
                                           reveal: door_tier, meta: door_tier}

        old_parts, old = door(70)
        new_parts, new = door(80)
        w.same_types(old_parts, new_parts)
        w.attach(old)
        w.regenerate_on_write(new)
        plan = w.plan(PAIRED_MATERIAL)
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual([c["field"] for c in plan["changes"]], ["native.material"])
        follows, = plan["paired_property"]["attribute_follows_native"]
        self.assertEqual((follows["field"], follows["reason"]),
                         ("attribute:508", "paired_attribute_not_stored_follows_native"))
        self.assertEqual(follows["observation"]["status"], "absent")
        self.assertTrue(follows["observation"]["presence_proven"])
        self.assertEqual(plan["criteria"]["attribute_read_mode"], "all_and_computable")
        result = w.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        drift = result["outcomes"][0]["representation_consensus"]["representations"][0][
            "accepted_preservation_drift"]
        self.assertEqual(sorted(p["type_name"] for p in drift["regenerated_identities"]),
                         ["AttributeContainer_TypeUUID", "DoorSill_TypeUUID", "Door_TypeUUID"])
        w.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertEqual(result["undo_group"]["status"], "not_requested")
        self.assertIsNone(w.attribute(508))

    def test_single_place_native_material_hints_at_a_differing_attribute_508(self):
        w = WallFixture(self)
        plan = w.plan({"target": {"kind": "native_material", "tier_index": 1}, "value": "Cegła"})
        hint = plan["paired_property_hint"]
        self.assertEqual(hint["property"], "material")
        self.assertEqual(hint["plain_request"], PAIRED_MATERIAL)
        row, = hint["attribute_differs"]
        self.assertEqual((row["attribute_id"], row["observation"]["value"]), (508, "Silikat"))
        self.assertIn("does not carry over", hint["use"])
        self.assertEqual([c["field"] for c in plan["changes"]], ["native.material"])
        absent = WallFixture(self, attributes=((935, ""),))
        plan = absent.plan({"target": {"kind": "native_material", "tier_index": 1}, "value": "Cegła"})
        self.assertNotIn("paired_property_hint", plan)
        self.assertNotIn("paired_property_hint", w.plan(PAIRED_MATERIAL))

    def test_unlisted_regeneration_after_native_material_stays_unknown_with_identity_diff(self):
        w = WallFixture(self)
        old = {w.part(40, "Niche_TypeUUID"): w.root}
        new = {w.part(41, "Niche_TypeUUID"): w.root}
        w.same_types(list(old), list(new))
        w.attach(old)
        w.regenerate_on_write(new)
        execution = uuid4().hex
        result = w.native.apply(w.plan(PAIRED_MATERIAL), execution)
        native, attribute = result["outcomes"]
        self.assertEqual((native["state"], attribute["state"]), ("unknown", "skipped"))
        preservation = native["representation_consensus"]["representations"][0]["preservation"]
        self.assertEqual(preservation["identity_diff"]["removed"]["items"][0].split("|")[0], "Niche_TypeUUID")
        w.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.assertTrue(w.native.recover(execution)["write_blocked"])



class ColumnPairedMaterialTests(unittest.TestCase):
    family = paired.PairedPropertyTests.family
    request = paired.PairedPropertyTests.request
    plan = paired.PairedPropertyTests.plan

    def test_column_paired_material_without_stored_508_is_blocked(self):
        # The follows-native rule is observed on the Wall only (0.50.1).
        f = self.family()
        f.root.GetAttributes.return_value = [(935, ""), (120, "m")]
        f.properties.Material = "Beton"
        plan = self.plan(f, "C30/37", "material")
        self.assertEqual(plan["state"], "not_checked")
        blocked, = plan["blocked"]
        self.assertEqual((blocked["field"], blocked["reason"]),
                         ("attribute:508", "replace_requires_existing_attribute"))
        self.assertEqual(plan["paired_property"]["attribute_follows_native"], [])
        f.native.base.ModifyElements.assert_not_called()


class WallWithWindowTests(unittest.TestCase):
    def window_wall(self, attributes=((935, ""), (508, "Silikat")), tier_lists=False,
                    tier_before=0, tier_after=0):
        w = WallFixture(self, attributes)
        w.tier_position = tier_before
        keep = (w.part(50, "WindowTier_TypeUUID"), w.part(51, "WindowReveal_TypeUUID"))
        if tier_lists:
            w.tier_lists.append(keep[0])
        old, new = w.window(60, keep), w.window(70, keep)
        old_meta, new_meta = w.root_container(80), w.root_container(81)
        w.same_types([p for p in old if p not in keep] + list(old_meta),
                     [p for p in new if p not in keep] + list(new_meta))
        w.attach(old, old_meta)
        w.regenerate_on_write(new, new_meta, tier_position=tier_after)
        return w

    def test_paired_calculation_mode_accepts_the_window_regeneration(self):
        w = self.window_wall()
        plan = w.plan({"target": {"kind": "paired_property", "property": "calculation_mode"}, "value": "m"})
        self.assertTrue(plan["apply_available"], plan)
        result = w.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        drift = result["outcomes"][0]["representation_consensus"]["representations"][0][
            "accepted_preservation_drift"]
        self.assertEqual(sorted(p["type_name"] for p in drift["regenerated_identities"]),
                         ["AttributeContainer_TypeUUID", "AttributeContainer_TypeUUID",
                          "AttributeContainer_TypeUUID", "Sill_TypeUUID",
                          "WindowOpeningSmartPart_TypeUUID", "Window_TypeUUID"])
        self.assertEqual(drift["view_map"], {})
        self.assertEqual(w.attribute(120), "m")
        self.assertEqual(result["undo_group"]["setters_in_step"], 2)

    def test_paired_material_on_the_window_wall(self):
        w = self.window_wall()
        result = w.native.apply(w.plan(PAIRED_MATERIAL))
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual((w.wall.material, w.attribute(508)), ("Cegła", "Cegła"))

    def test_window_tier_listed_under_the_wall_tier_is_a_bound_shared_child(self):
        # 0.51.0 trial: the WallTier also enumerates the WindowTier, whose
        # parent is the Window. 0.51.1 binds that edge instead of falling back
        # to partial evidence (component_child_owner_mismatch).
        w = self.window_wall(tier_lists=True)
        plan = w.plan(PAIRED_MATERIAL)
        self.assertTrue(plan["apply_available"], plan)
        state = plan["changes"][0]["resource"]["native_material_state"]
        self.assertNotIn("partial_preservation", state)
        self.assertNotIn("preservation_diagnostic", state)
        shared, = state["tier_hierarchy"]["shared_children"]
        self.assertEqual((shared["child"]["type_name"], shared["parent"]["type_name"]),
                         ("WindowTier_TypeUUID", "Window_TypeUUID"))
        self.assertNotIn(shared["child"], state["tier_hierarchy"]["children"])
        window, = state["auxiliary_components"]["root"]
        self.assertIn(shared["child"], window["ownership"]["children"])
        self.assertEqual(state["auxiliary_components"]["tier"], [])
        result = w.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        drift = result["outcomes"][0]["representation_consensus"]["representations"][0][
            "accepted_preservation_drift"]
        self.assertIn("Window_TypeUUID", {p["type_name"] for p in drift["regenerated_identities"]})
        self.assertEqual((w.wall.material, w.attribute(508)), ("Cegła", "Cegła"))

    def test_window_wall_regeneration_that_reorders_the_children_is_accepted(self):
        # 0.51.0 trial (a47dca16…, 5346fd71…): only Window, Sill and two
        # AttributeContainers were renamed, yet both writes stayed unknown.
        # The partial evidence held whatever was enumerated before the
        # WallTier, so regenerated parts listed after it changed its shape.
        for change, expected in ((PAIRED_MATERIAL, ("Cegła", "Cegła")),
                                 ({"target": {"kind": "paired_property", "property": "calculation_mode"},
                                   "value": "m"}, None)):
            with self.subTest(change=change["target"]["property"]):
                w = self.window_wall(tier_lists=True, tier_before=None, tier_after=0)
                result = w.native.apply(w.plan(change))
                self.assertEqual(result["state"], "completed", result)
                self.assertEqual([o["state"] for o in result["outcomes"]], ["applied", "applied"])
                self.assertEqual(result["undo_group"]["setters_in_step"], 2)
                if expected:
                    self.assertEqual((w.wall.material, w.attribute(508)), expected)
                else:
                    self.assertEqual(w.attribute(120), "m")

    def test_a_tier_child_owned_by_a_non_opening_stays_partial(self):
        w = WallFixture(self)
        meta = w.root_container(80)
        w.tier_lists.append(next(iter(meta)))
        w.attach(meta)
        plan = w.plan(PAIRED_MATERIAL)
        state = plan["changes"][0]["resource"]["native_material_state"]
        self.assertEqual(state["preservation_diagnostic"]["reason"], "component_child_owner_mismatch")

    def test_regenerated_window_tier_or_changed_reveal_geometry_stays_unknown(self):
        w = WallFixture(self)
        tier, reveal = w.part(50, "WindowTier_TypeUUID"), w.part(51, "WindowReveal_TypeUUID")
        new_tier = w.part(52, "WindowTier_TypeUUID")
        w.same_types([tier], [new_tier])
        old, new = w.window(60, (tier, reveal)), w.window(70, (new_tier, reveal))
        w.same_types([p for p in old if p not in (tier, reveal)], [p for p in new if p not in (new_tier, reveal)])
        w.attach(old)
        w.regenerate_on_write(new)
        result = w.native.apply(w.plan(PAIRED_MATERIAL))
        self.assertEqual(result["outcomes"][0]["state"], "unknown", result)
        w.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

        g = WallFixture(self)
        keep = (g.part(50, "WindowTier_TypeUUID"), g.part(51, "WindowReveal_TypeUUID"))
        old, new = g.window(60, keep), g.window(70, keep)
        g.same_types([p for p in old if p not in keep], [p for p in new if p not in keep])
        g.attach(old)
        modify = g.native.base.ModifyElements.side_effect

        def regenerate_and_move(doc, elements):
            result = modify(doc, elements)
            g.attach(new)
            keep[1].GetModelGeometry.return_value = Polyhedron("moved-reveal")
            return result

        g.native.base.ModifyElements.side_effect = regenerate_and_move
        result = g.native.apply(g.plan(PAIRED_MATERIAL))
        self.assertEqual(result["outcomes"][0]["state"], "unknown", result)
        g.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        preservation = result["outcomes"][0]["representation_consensus"]["representations"][0]["preservation"]
        residual = preservation["regeneration_residual"]
        self.assertEqual((residual["status"], residual["unpaired_types"]), ("observed", []))
        # A different shape differs in the exact, shape and structure hashes.
        self.assertEqual(sorted(row["path"].rsplit("/", 1)[1] for row in residual["paths"]),
                         ["shape_sha256", "stream_sha256", "structure_sha256"])
        for row in residual["paths"]:
            self.assertTrue(row["path"].startswith("/auxiliary_components/root/[Window_TypeUUID|"), row)
            self.assertIn("/[WindowReveal_TypeUUID|00000000-0000-4000-8000-000000000051]/geometry/", row["path"])

    def reserialize(self, w, keep, tier_stream, reveal_stream, tier_after=None, reveal_after=None, new=None):
        """Regenerate the Window and re-serialize its kept tier/reveal geometry."""
        tier, reveal = keep
        tier.GetModelGeometry.return_value = Polyhedron(tier_stream)
        reveal.GetModelGeometry.return_value = Polyhedron(reveal_stream)
        modify = w.native.base.ModifyElements.side_effect

        def regenerate(doc, elements):
            result = modify(doc, elements)
            if new is not None:
                w.attach(*new)
            tier.GetModelGeometry.return_value = Polyhedron(tier_after or tier_stream)
            reveal.GetModelGeometry.return_value = Polyhedron(reveal_after or reveal_stream)
            return result

        w.native.base.ModifyElements.side_effect = regenerate

    def regenerating_window_wall(self):
        w = WallFixture(self)
        keep = (w.part(50, "WindowTier_TypeUUID"), w.part(51, "WindowReveal_TypeUUID"))
        w.tier_lists.append(keep[0])
        old, new = w.window(60, keep), w.window(70, keep)
        old_meta, new_meta = w.root_container(80), w.root_container(81)
        w.same_types([p for p in old if p not in keep] + list(old_meta),
                     [p for p in new if p not in keep] + list(new_meta))
        w.attach(old, old_meta)
        w.old_subtrees = (old, old_meta)
        return w, keep, (new, new_meta)

    TIER = "Polyhedron3D 8 0.0 0.0 0.0 1010.0 0.0 0.0 1010.0 300.0 0.0 0.0 300.0 1500.0"
    TIER_NOISE = "Polyhedron3D 8 0.0 -0.0 1e-12 1010.0000000000002 0.0 0.0 1010.0 300.0 0.0 0.0 300.0 1500.0"
    REVEAL = "Polyhedron3D 4 -12.5 0.0 1010.0 300.0"
    REVEAL_NOISE = "Polyhedron3D 4 -12.499999999999998 0.0 1010.0 300.00000000000006"

    def test_window_tier_and_reveal_reserialized_within_tolerance_are_accepted(self):
        # 0.51.1 trial (5008fcbe…, c1395fe6…, 3c5df3d9…): the regenerated
        # Window left WindowTier/WindowReveal identities but changed their
        # exact stream hashes, identically for CalculationMode and Material.
        for change, check in ((PAIRED_MATERIAL, lambda w: (w.wall.material, w.attribute(508))),
                              ({"target": {"kind": "paired_property", "property": "calculation_mode"},
                                "value": "m"}, lambda w: w.attribute(120))):
            with self.subTest(change=change["target"]["property"]):
                w, keep, new = self.regenerating_window_wall()
                self.reserialize(w, keep, self.TIER, self.REVEAL, self.TIER_NOISE, self.REVEAL_NOISE, new)
                plan = w.plan(change)
                self.assertTrue(plan["apply_available"], plan)
                state = plan["changes"][0]["resource"][
                    "native_material_state" if change is PAIRED_MATERIAL else "native_property_state"]
                window, = state["auxiliary_components"]["root"]
                geometry = window["children"][0]["geometry"]
                self.assertEqual(set(geometry), {"status", "stream_sha256", "shape_sha256",
                                                 "structure_sha256", "numbers"})
                result = w.native.apply(plan)
                self.assertEqual(result["state"], "completed", result)
                self.assertEqual([o["state"] for o in result["outcomes"]], ["applied", "applied"])
                drift = result["outcomes"][0]["representation_consensus"]["representations"][0][
                    "accepted_preservation_drift"]
                self.assertEqual(drift["accepted"], "identities_regenerated_evidence_otherwise_equal")
                reserialized = drift["reserialized_geometry"]
                self.assertEqual(reserialized["accepted"], "opening_geometry_reserialized_shape_equal")
                self.assertEqual([row["type_name"] for row in reserialized["components"]],
                                 ["WindowReveal_TypeUUID", "WindowTier_TypeUUID"])
                for row in reserialized["components"]:
                    self.assertNotEqual(row["before_stream_sha256"], row["after_stream_sha256"])
                self.assertEqual(result["undo_group"]["setters_in_step"], 2)
                self.assertEqual(check(w), ("Cegła", "Cegła") if change is PAIRED_MATERIAL else "m")

    def test_opening_geometry_beyond_the_tolerance_or_restructured_stays_unknown(self):
        for label, tier_after, expected in (
                ("moved", "Polyhedron3D 8 0.0 0.0 0.0 1010.5 0.0 0.0 1010.0 300.0 0.0 0.0 300.0 1500.0",
                 ["shape_sha256", "stream_sha256"]),
                ("reordered", "Polyhedron3D 8 0.0 0.0 0.0 1010.0 0.0 0.0 1010.0 300.0 0.0 0.0 300.0 1500.0 0.0",
                 ["numbers", "shape_sha256", "stream_sha256", "structure_sha256"])):
            with self.subTest(label=label):
                w, keep, new = self.regenerating_window_wall()
                self.reserialize(w, keep, self.TIER, self.REVEAL, tier_after, self.REVEAL_NOISE, new)
                execution = uuid4().hex
                result = w.native.apply(w.plan(PAIRED_MATERIAL), execution)
                native, attribute = result["outcomes"]
                self.assertEqual((native["state"], attribute["state"]), ("unknown", "skipped"))
                residual = native["representation_consensus"]["representations"][0]["preservation"][
                    "regeneration_residual"]
                tier_rows = sorted(row["path"].rsplit("/", 1)[1] for row in residual["paths"]
                                   if "/[WindowTier_TypeUUID|" in row["path"]
                                   and "/[WindowReveal_TypeUUID|" not in row["path"])
                self.assertEqual(tier_rows, expected)
                self.assertTrue(w.native.recover(execution)["write_blocked"])
                w.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_reserialized_geometry_without_a_renamed_window_stays_unknown(self):
        # Only the parts below a regenerated (renamed) Window may re-serialize.
        w, keep, _ = self.regenerating_window_wall()
        old_window, old_meta = w.old_subtrees
        new_meta = w.root_container(82)
        w.same_types(list(old_meta), list(new_meta))
        self.reserialize(w, keep, self.TIER, self.REVEAL, self.TIER_NOISE, self.REVEAL_NOISE,
                         new=(old_window, new_meta))
        result = w.native.apply(w.plan(PAIRED_MATERIAL))
        native = result["outcomes"][0]
        self.assertEqual(native["state"], "unknown", result)
        preservation = native["representation_consensus"]["representations"][0]["preservation"]
        self.assertEqual([item.split("|")[0] for item in preservation["identity_diff"]["removed"]["items"]],
                         ["AttributeContainer_TypeUUID"])
        self.assertTrue(any(row["path"].endswith("/geometry/stream_sha256")
                            for row in preservation["regeneration_residual"]["paths"]))

    def test_door_parts_do_not_get_the_window_geometry_tolerance(self):
        w = WallFixture(self)
        door_tier, reveal = w.part(60, "DoorTier_TypeUUID"), w.part(61, "DoorReveal_TypeUUID")

        def door(ident):
            opening = w.part(ident, "Door_TypeUUID")
            sill = w.part(ident + 1, "DoorSill_TypeUUID")
            return [opening, sill], {opening: w.root, door_tier: opening, sill: door_tier, reveal: door_tier}

        old_parts, old = door(70)
        new_parts, new = door(80)
        w.same_types(old_parts, new_parts)
        w.attach(old)
        self.reserialize(w, (door_tier, reveal), self.TIER, self.REVEAL, self.TIER_NOISE, self.REVEAL_NOISE,
                         new=(new,))
        result = w.native.apply(w.plan(PAIRED_MATERIAL))
        native = result["outcomes"][0]
        self.assertEqual(native["state"], "unknown", result)
        residual = native["representation_consensus"]["representations"][0]["preservation"]["regeneration_residual"]
        self.assertTrue(residual["paths"], residual)
        self.assertTrue(all("/geometry/stream_sha256" in row["path"] for row in residual["paths"]), residual)


class GeometryShapeTests(unittest.TestCase):
    def test_shape_ignores_numeric_noise_and_structure_ignores_numbers(self):
        import importlib
        w = WallFixture(self)
        geometry_shape = importlib.import_module(w.native.module.__package__ + ".wall_material").geometry_shape
        exact = geometry_shape("P 2 0.0 1010.0 300.0")
        noise = geometry_shape("P 2 -0.0 1010.0000000000002 3.0e2")
        moved = geometry_shape("P 2 0.0 1010.5 300.0")
        longer = geometry_shape("P 2 0.0 1010.0 300.0 1")
        self.assertEqual(exact, noise)
        self.assertEqual(exact["numbers"], 4)
        self.assertNotEqual(exact["shape_sha256"], moved["shape_sha256"])
        self.assertEqual(exact["structure_sha256"], moved["structure_sha256"])
        self.assertNotEqual(exact["structure_sha256"], longer["structure_sha256"])


if __name__ == "__main__":
    unittest.main()
