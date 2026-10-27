"""Getter-only exact Beam/Slab diagnostics; SDK doubles are not native PASS."""
import json
import sys
import unittest
import weakref
from types import SimpleNamespace
from unittest.mock import patch

from pydantic import TypeAdapter, ValidationError

from allplan_mcp.property_models import PropertyProbeRequest
import test_component_identity as identity
from trace_test_support import install_memory_trace


class BeamElement:
    def __init__(self, material):
        self.Properties = SimpleNamespace(Material=material)


class StructuralBeamElement:
    # Deliberately no generic Properties or setter methods.
    def __init__(self, material):
        self.StructuralBeamProperties = SimpleNamespace(Material=material)


class SlabElement:
    def __init__(self, material):
        self.Properties = SimpleNamespace(Material=material)


class MaterialComparisonTests(unittest.TestCase):
    setUp = identity.ComponentIdentityTests.setUp
    prepare_context = identity.ComponentIdentityTests.prepare_context
    prepare = identity.ComponentIdentityTests.prepare
    adapter = identity.ComponentIdentityTests.adapter
    native = identity.ComponentIdentityTests.native
    element = identity.ComponentIdentityTests.element
    probe = identity.ComponentIdentityTests.probe
    fixture = identity.ComponentIdentityTests.fixture
    null_adapter = staticmethod(identity.ComponentIdentityTests.null_adapter)
    assert_code = identity.ComponentIdentityTests.assert_code

    def material_fixture(self, elements=None, *, durable=False):
        self.fixture(elements or [self.element(name="SkeletonBeam_TypeUUID")])
        self.target = self.native_elements[0]
        self.handler.model_queries.clock = lambda: 0.0
        self.base.eAttibuteReadState.ReadAll = "ReadAll"
        self.base.eAttibuteReadState.ReadAllAndComputable = "ReadAllAndComputable"
        self.base.AttributeService.AttributeType = SimpleNamespace(String=11)
        self.base.AttributeService.GetAttributeType.side_effect = None
        self.base.AttributeService.GetAttributeType.return_value = 11
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: "Materiał"
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: 508
        for element in self.native_elements:
            element.GetAttributes.return_value = [(508, "Żelbet")]
        self.natives = {id(element): StructuralBeamElement("native") for element in self.native_elements}
        self.base.GetElement.side_effect = lambda element: self.natives[id(element)]
        arch = SimpleNamespace(BeamElement=BeamElement, StructuralBeamElement=StructuralBeamElement, SlabElement=SlabElement)
        modules = patch.dict(sys.modules, {"NemAll_Python_ArchElements": arch})
        modules.start()
        self.addCleanup(modules.stop)
        trace_class = sys.modules[self.handler.property_probes.__module__].NativeProbeTrace
        if not durable:
            self.trace_records = install_memory_trace(self, trace_class)
        return self.target

    def request(self, **changes):
        return {"phase": "material_comparison", "drawing_file": 101,
                "model_uuid": self.target.GetModelElementUUID(), "view_uuid": self.target.GetElementUUID(),
                "attribute_ids": [508], **changes}

    def comparison(self, **changes):
        result = self.probe(**self.request(**changes))
        self.base.ModifyElements.assert_not_called()
        self.base.DeleteElements.assert_not_called()
        self.assertFalse(result["property_write_available"])
        self.assertEqual(result["setter_calls_started"], 0)
        self.assertFalse(self.handler.model_queries.selections)
        self.assertEqual(result["storage_coupling"], "not_established")
        self.assertEqual(result["persistence"], "not_checked")
        json.dumps(result, allow_nan=False)
        return result

    def test_documented_runtime_getters_work_without_any_setters(self):
        target = self.material_fixture()
        for kind, cls, accessor in (
            ("Beam_TypeUUID", BeamElement, "Properties"),
            ("SkeletonBeam_TypeUUID", BeamElement, "Properties"),
            ("SkeletonBeam_TypeUUID", StructuralBeamElement, "StructuralBeamProperties"),
            ("Slab_TypeUUID", SlabElement, "Properties"),
            ("MultiSlab_TypeUUID", SlabElement, "Properties"),
        ):
            with self.subTest(kind=kind, native_class=cls.__name__):
                target.GetElementAdapterType.return_value.GetTypeName.return_value = kind
                self.natives[id(target)] = cls("")
                result = self.comparison()
                self.assertEqual(result["state"], "observed", result)
                value = result["representations"][0]["target"]["value"]
                self.assertEqual(value["native_material"]["value"], "")
                self.assertEqual(value["native_material"]["access_path"], cls.__name__ + "." + accessor + ".Material")
                self.assertEqual(value["native_material"]["owner_ref"], value["ref"])
                self.assertEqual(result["metadata"][0]["name"]["value"], "Materiał")
                self.assertEqual(result["metadata"][0]["name_id_round_trip"]["value"], 508)
                self.assertEqual(value["read_modes"]["ReadAll"]["value"][0]["value"], "Żelbet")
        self.assertFalse(self.path.exists())

    def test_slab_child_and_optional_parent_keep_distinct_native_values_and_lineage(self):
        child = self.element(2, name="Slab_TypeUUID")
        parent = self.element(3, name="MultiSlab_TypeUUID", attrs=[(508, "parent-attribute")])
        self.material_fixture([child])
        self.parents[id(child)] = parent
        self.children[id(parent)] = [child]
        self.natives[id(child)], self.natives[id(parent)] = SlabElement(""), SlabElement("parent-native")
        result = self.comparison(include_parent=True)
        representation = result["representations"][0]
        target, owner = representation["target"]["value"], representation["parent"]["value"]["evidence"]
        self.assertEqual(target["native_material"]["value"], "")
        self.assertEqual(owner["native_material"]["value"], "parent-native")
        self.assertNotEqual(target["ref"]["model_uuid"], owner["ref"]["model_uuid"])
        self.assertEqual(target["ancestry"]["value"]["lineage"][1], owner["ref"])
        self.assertEqual([call.args[0] for call in self.base.GetElement.call_args_list], [child, parent])

    def test_conflicting_exact_wrappers_retain_each_material_and_parent_view_edge(self):
        first, second = self.element(2, name="SkeletonBeam_TypeUUID"), self.element(2, name="SkeletonBeam_TypeUUID")
        self.material_fixture([first, second])
        self.natives[id(first)], self.natives[id(second)] = StructuralBeamElement("A"), StructuralBeamElement("B")
        child = self.element(3, name="SkeletonAxis_TypeUUID")
        alternate_parent = self.element(2, name="SkeletonBeam_TypeUUID")
        alternate_parent.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000099"
        self.children[id(first)] = [child]
        self.parents[id(child)] = alternate_parent
        result = self.comparison()
        self.assertFalse(result["representation_consensus"])
        self.assertEqual(result["state"], "not_checked")
        values = [row["target"]["value"] for row in result["representations"]]
        self.assertEqual({value["native_material"]["value"] for value in values}, {"A", "B"})
        edge = values[0]["children"]["value"]["child_parent_edges"][0]
        self.assertNotEqual(edge["parent"]["view_uuid"], values[0]["ref"]["view_uuid"])
        self.assertEqual(result["counts"]["conflicting_model_identities"], 0)

    def test_child_failure_and_attribute_omission_do_not_erase_native_read(self):
        target = self.material_fixture()
        target.GetAttributes.return_value = []
        self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements.side_effect = RuntimeError("private")
        result = self.comparison()
        value = result["representations"][0]["target"]["value"]
        self.assertEqual(value["native_material"]["value"], "native")
        self.assertEqual(value["ancestry"]["status"], "observed")
        self.assertEqual(value["children"]["status"], "not_checked")
        self.assertFalse(value["read_modes"]["ReadAll"]["value"][0]["absence_proven"])
        self.assertFalse(result["evidence_complete"])
        self.assertNotIn("private", json.dumps(result))

    def test_failed_native_getter_leaves_attribute_values_and_class_available(self):
        target = self.material_fixture()
        class BrokenProperties:
            @property
            def Material(self):
                raise RuntimeError("private SDK message")
        self.natives[id(target)].StructuralBeamProperties = BrokenProperties()
        result = self.comparison()
        value = result["representations"][0]["target"]["value"]
        self.assertEqual(value["native_representation"]["value"]["name"], "StructuralBeamElement")
        self.assertEqual(value["native_material"]["status"], "not_checked")
        self.assertEqual(value["read_modes"]["ReadAll"]["value"][0]["value"], "Żelbet")
        self.assertNotIn("private SDK message", json.dumps(result))
        self.assertEqual(sum(row["api"] == "StructuralBeamProperties.Material" and row["state"] == "started"
                             for row in self.trace_records), 1)

    def test_unsupported_runtime_class_or_family_never_guesses_property_accessor(self):
        target = self.material_fixture()
        self.natives[id(target)] = SlabElement("wrong family")
        value = self.comparison()["representations"][0]["target"]["value"]
        self.assertEqual(value["native_material"]["reason"], "native_material_read_route_unsupported")
        target.GetElementAdapterType.return_value.GetTypeName.return_value = "Column_TypeUUID"
        self.natives[id(target)] = StructuralBeamElement("wrong family")
        value = self.comparison()["representations"][0]["target"]["value"]
        self.assertEqual(value["native_material"]["status"], "not_checked")
        self.assertFalse(any(row["api"] == "StructuralBeamProperties.Material" for row in self.trace_records))

    def test_metadata_roundtrip_mismatch_keeps_values_but_marks_incomplete(self):
        self.material_fixture()
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: 509
        result = self.comparison()
        self.assertEqual(result["metadata"][0]["name_id_round_trip"]["reason"], "name_id_round_trip_mismatch")
        self.assertEqual(result["representations"][0]["target"]["value"]["native_material"]["value"], "native")
        self.assertFalse(result["evidence_complete"])

    def test_missing_structural_accessor_and_invalid_material_never_fall_back_or_coerce(self):
        target = self.material_fixture()
        native = self.natives[id(target)]
        native.Properties = SimpleNamespace(Material="must not read generic fallback")
        del native.StructuralBeamProperties
        value = self.comparison()["representations"][0]["target"]["value"]
        self.assertEqual(value["native_material"]["status"], "not_checked")
        self.assertFalse(any(row["api"] == "StructuralBeamProperties.Material" for row in self.trace_records))
        class Unknown:
            def __str__(self):
                raise AssertionError("Unknown values must never be stringified")
        for material in (Unknown(), "x" * 256, None, 10):
            native.StructuralBeamProperties = SimpleNamespace(Material=material)
            value = self.comparison()["representations"][0]["target"]["value"]
            self.assertEqual(value["native_material"]["status"], "not_checked")
            self.assertEqual(value["read_modes"]["ReadAll"]["status"], "observed")

    def test_identity_drift_after_scan_is_visible_without_native_or_attribute_reads(self):
        target = self.material_fixture()
        def change_identity(doc, ident):
            target.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000099"
            return "Materiał"
        self.base.AttributeService.GetAttributeName.side_effect = change_identity
        result = self.comparison()
        self.assertEqual(result["representations"][0]["target"]["status"], "not_checked")
        self.base.GetElement.assert_not_called()
        target.GetAttributes.assert_not_called()

    def test_trace_failure_at_material_boundary_prevents_getter_and_attribute_reads(self):
        target = self.material_fixture()
        trace_class = sys.modules[self.handler.property_probes.__module__].NativeProbeTrace
        record = trace_class.record
        def failed_record(trace, api, state, **details):
            if api == "StructuralBeamProperties.Material" and state == "started":
                raise self.module.BridgeError("probe_trace_unavailable", "full trace", 409)
            return record(trace, api, state, **details)
        with patch.object(trace_class, "record", failed_record):
            self.assert_code("probe_trace_unavailable", self.comparison)
        target.GetAttributes.assert_not_called()

    def test_budget_exhausted_by_getter_prevents_following_attribute_reads(self):
        target = self.material_fixture()
        now = [0.0]
        self.handler.model_queries.clock = lambda: now[0]
        limit = self.handler.model_queries.SCAN_SECONDS
        class SlowProperties:
            @property
            def Material(self):
                now[0] = limit
                return "native"
        self.natives[id(target)].StructuralBeamProperties = SlowProperties()
        self.assert_code("scan_limit_exceeded", self.comparison)
        target.GetAttributes.assert_not_called()

    def test_wrong_view_and_wrapper_limit_stop_before_native_and_attribute_reads(self):
        target = self.material_fixture()
        self.assert_code("probe_scope_unavailable", lambda: self.comparison(
            view_uuid="10000000-0000-4000-8000-000000000099"))
        wrappers = [self.element(name="SkeletonBeam_TypeUUID") for _ in range(17)]
        self.base.ElementsSelectService.SelectAllElements.return_value = wrappers
        self.target = wrappers[0]
        self.assert_code("probe_scope_unavailable", self.comparison)
        self.base.GetElement.assert_not_called()
        target.GetAttributes.assert_not_called()

    def test_contract_rejects_null_ids_boolean_ids_duplicates_and_unknown_keys_before_document(self):
        self.material_fixture()
        contract = TypeAdapter(PropertyProbeRequest)
        for changes in ({"model_uuid": "00000000-0000-0000-0000-000000000000"},
                        {"attribute_ids": [True]}, {"attribute_ids": [508, 508]}, {"setter": True}):
            with self.subTest(changes=changes):
                request = self.request(**changes)
                with self.assertRaises(ValidationError):
                    contract.validate_python(request)
                self.assert_code("invalid_payload", lambda: self.probe(**request))
        self.coord.GetInputViewDocument.assert_not_called()

    def slab_child_fixture(self, *, durable=False):
        child = self.element(2, name="Slab_TypeUUID", attrs=[(508, "child-attribute")])
        parent = self.element(3, name="MultiSlab_TypeUUID")
        self.material_fixture([parent], durable=durable)  # SelectAll exposes only the aggregate.
        self.target = child
        self.parents[id(child)] = parent
        self.children[id(parent)] = [child]
        for adapter in (child, parent):
            adapter.IsDeleted.return_value = False
        self.natives[id(child)] = SlabElement(" ")
        self.natives[id(parent)] = SlabElement("parent-native")
        self.parent_ref = {"model_uuid": parent.GetModelElementUUID(), "view_uuid": parent.GetElementUUID()}
        return child, parent

    def test_explicit_parent_finds_unenumerated_child_without_substituting_aggregate(self):
        child, parent = self.slab_child_fixture()
        self.assert_code("probe_scope_unavailable", self.comparison)
        self.base.GetElement.assert_not_called()
        result = self.comparison(parent_ref=self.parent_ref, include_parent=True)
        self.assertEqual(result["state"], "observed", result)
        row = result["representations"][0]
        self.assertEqual(row["target"]["value"]["native_material"]["value"], " ")
        self.assertEqual(row["target"]["value"]["read_modes"]["ReadAll"]["value"][0]["value"], "child-attribute")
        self.assertEqual(row["parent"]["value"]["evidence"]["native_material"]["value"], "parent-native")
        self.assertEqual(result["ref"]["model_uuid"], child.GetModelElementUUID())
        self.assertEqual(result["ref"]["type_uuid"], child.GetElementAdapterType().GetGuid())
        self.assertEqual(result["counts"]["matched_model_identities"], 1)  # direct scan only
        self.assertFalse(result["identity_resolution"]["target_in_direct_scan"])
        self.assertTrue(result["identity_resolution"]["child_inventory_complete"])
        self.assertEqual(result["identity_resolution"]["parent_ref"]["model_uuid"], parent.GetModelElementUUID())
        self.assertEqual([call.args[0] for call in self.base.GetElement.call_args_list], [child, parent])

    def test_explicit_parent_preserves_alternate_parent_view_without_claiming_equivalence(self):
        child, parent = self.slab_child_fixture()
        alternate = self.element(3, name="MultiSlab_TypeUUID")
        alternate.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000099"
        alternate.IsDeleted.return_value = False
        self.parents[id(child)] = alternate
        self.children[id(alternate)] = [child]
        self.natives[id(alternate)] = SlabElement("alternate-parent")
        result = self.comparison(parent_ref=self.parent_ref, include_parent=True)
        resolution = result["identity_resolution"]
        self.assertNotEqual(resolution["child_parent_edges"][0]["parent"]["view_uuid"], resolution["parent_ref"]["view_uuid"])
        self.assertEqual(result["representations"][0]["parent"]["value"]["evidence"]["ref"]["view_uuid"], alternate.GetElementUUID())
        self.assertEqual(result["physical_target_equivalence"], "not_established")

    def test_explicit_parent_rejects_wrong_or_missing_exact_refs_before_value_reads(self):
        child, parent = self.slab_child_fixture()
        for changes in (
            {"view_uuid": "10000000-0000-4000-8000-000000000099"},
            {"model_uuid": "00000000-0000-4000-8000-000000000099"},
            {"parent_ref": {**self.parent_ref, "view_uuid": "10000000-0000-4000-8000-000000000099"}},
            {"parent_ref": {**self.parent_ref, "model_uuid": "00000000-0000-4000-8000-000000000099"}},
        ):
            with self.subTest(changes=changes):
                self.assert_code("probe_scope_unavailable", lambda: self.comparison(**{"parent_ref": self.parent_ref, **changes}))
        self.base.GetElement.assert_not_called()
        child.GetAttributes.assert_not_called()
        parent.GetAttributes.assert_not_called()

    def test_explicit_parent_never_scans_children_of_other_families_or_other_roots(self):
        child, parent = self.slab_child_fixture()
        unrelated = self.element(4, name="MultiSlab_TypeUUID")
        self.base.ElementsSelectService.SelectAllElements.return_value = [parent, unrelated]
        parent.GetElementAdapterType.return_value.GetTypeName.return_value = "Wall_TypeUUID"
        self.assert_code("probe_scope_unavailable", lambda: self.comparison(parent_ref=self.parent_ref))
        service = self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements
        service.assert_not_called()
        self.base.GetElement.assert_not_called()

    def test_explicit_parent_rejects_cross_file_stale_wrong_family_and_wrong_edge(self):
        for failure in ("cross_file", "deleted_child", "null_parent", "wrong_family", "wrong_edge", "null_edge", "deleted_edge"):
            with self.subTest(failure=failure):
                child, parent = self.slab_child_fixture()
                if failure == "cross_file":
                    child.GetDrawingfileNumber.return_value = 102
                elif failure == "deleted_child":
                    child.IsDeleted.return_value = True
                elif failure == "null_parent":
                    parent.IsNull.return_value = True
                elif failure == "wrong_family":
                    child.GetElementAdapterType.return_value.GetTypeName.return_value = "Beam_TypeUUID"
                elif failure == "wrong_edge":
                    self.parents[id(child)] = self.element(4, name="MultiSlab_TypeUUID")
                elif failure == "null_edge":
                    self.parents[id(child)] = self.null_adapter()
                else:
                    edge = self.element(3, name="MultiSlab_TypeUUID")
                    edge.IsDeleted.return_value = True
                    self.parents[id(child)] = edge
                self.assert_code("probe_scope_unavailable", lambda: self.comparison(parent_ref=self.parent_ref))
                self.base.GetElement.assert_not_called()
                child.GetAttributes.assert_not_called()

    def test_explicit_parent_requires_child_membership_on_every_parent_wrapper(self):
        child, parent = self.slab_child_fixture()
        second = self.element(3, name="MultiSlab_TypeUUID")
        second.IsDeleted.return_value = False
        self.base.ElementsSelectService.SelectAllElements.return_value = [parent, second]
        self.children[id(second)] = []
        self.assert_code("probe_scope_unavailable", lambda: self.comparison(parent_ref=self.parent_ref))
        self.base.GetElement.assert_not_called()
        child.GetAttributes.assert_not_called()

    def test_explicit_parent_keeps_all_child_wrappers_and_conflicting_materials(self):
        child, parent = self.slab_child_fixture()
        second = self.element(2, name="Slab_TypeUUID", attrs=[(508, "second")])
        second.IsDeleted.return_value = False
        self.parents[id(second)] = parent
        self.children[id(parent)].append(second)
        self.natives[id(second)] = SlabElement("different")
        result = self.comparison(parent_ref=self.parent_ref)
        self.assertEqual(result["representation_count"], 2)
        self.assertFalse(result["representation_consensus"])
        self.assertEqual(result["state"], "not_checked")
        self.assertEqual({r["target"]["value"]["native_material"]["value"] for r in result["representations"]}, {" ", "different"})

    def test_explicit_parent_includes_direct_wrappers_instead_of_hiding_conflicts(self):
        child, parent = self.slab_child_fixture()
        direct = self.element(2, name="Slab_TypeUUID", attrs=[(508, "direct")])
        direct.IsDeleted.return_value = False
        self.parents[id(direct)] = parent
        self.natives[id(direct)] = SlabElement("direct")
        self.base.ElementsSelectService.SelectAllElements.return_value = [parent, direct]
        result = self.comparison(parent_ref=self.parent_ref)
        self.assertTrue(result["identity_resolution"]["target_in_direct_scan"])
        self.assertEqual(result["representation_count"], 2)
        self.assertFalse(result["representation_consensus"])

    def test_explicit_parent_distinguishes_other_direct_view_from_exact_target_presence(self):
        child, parent = self.slab_child_fixture()
        other_view = self.element(2, name="Slab_TypeUUID")
        other_view.GetElementUUID.return_value = "10000000-0000-4000-8000-000000000099"
        self.base.ElementsSelectService.SelectAllElements.return_value = [parent, other_view]
        result = self.comparison(parent_ref=self.parent_ref)
        self.assertFalse(result["identity_resolution"]["target_in_direct_scan"])
        self.assertEqual(result["other_view_uuids"], [other_view.GetElementUUID()])
        self.assertEqual(result["representation_count"], 1)
        self.base.GetElement.assert_called_once_with(child)
        other_view.GetAttributes.assert_not_called()

    def test_explicit_parent_bounds_child_visits_and_parent_and_target_wrappers(self):
        for limit in ("children", "parents", "targets"):
            with self.subTest(limit=limit):
                child, parent = self.slab_child_fixture()
                if limit == "children":
                    self.children[id(parent)] = [self.element(i + 10) for i in range(257)]
                    expected = "scan_limit_exceeded"
                elif limit == "parents":
                    self.base.ElementsSelectService.SelectAllElements.return_value = [self.element(3, name="MultiSlab_TypeUUID") for _ in range(17)]
                    expected = "probe_scope_unavailable"
                else:
                    self.children[id(parent)] = [self.element(2, name="Slab_TypeUUID") for _ in range(17)]
                    expected = "probe_scope_unavailable"
                self.assert_code(expected, lambda: self.comparison(parent_ref=self.parent_ref))
                self.base.GetElement.assert_not_called()
                child.GetAttributes.assert_not_called()

    def test_explicit_parent_getter_failure_is_not_retried_or_exposed(self):
        child, parent = self.slab_child_fixture()
        service = self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements
        service.side_effect = RuntimeError("private native detail")
        try:
            self.comparison(parent_ref=self.parent_ref)
        except self.module.BridgeError as exc:
            self.assertEqual(exc.code, "probe_scope_unavailable")
            self.assertNotIn("private", str(exc))
        else:
            self.fail("Expected a closed child read failure")
        service.assert_called_once_with(parent, True)
        self.base.GetElement.assert_not_called()
        child.GetAttributes.assert_not_called()

    def test_explicit_parent_trace_failure_and_budget_stop_before_further_reads(self):
        child, parent = self.slab_child_fixture()
        trace_class = sys.modules[self.handler.property_probes.__module__].NativeProbeTrace
        record = trace_class.record
        def fail(trace, api, state, **details):
            if api == "MaterialChild.GetChildModelElements" and state == "started":
                raise self.module.BridgeError("probe_trace_unavailable", "trace unavailable", 409)
            return record(trace, api, state, **details)
        service = self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements
        with patch.object(trace_class, "record", fail):
            self.assert_code("probe_trace_unavailable", lambda: self.comparison(parent_ref=self.parent_ref))
        service.assert_not_called()
        now = [0.0]
        self.handler.model_queries.clock = lambda: now[0]
        def slow(*args):
            now[0] = self.handler.model_queries.SCAN_SECONDS
            return [child]
        service.side_effect = slow
        self.assert_code("scan_limit_exceeded", lambda: self.comparison(parent_ref=self.parent_ref))
        self.base.GetElement.assert_not_called()
        child.GetAttributes.assert_not_called()

    def test_explicit_parent_allows_256_children_and_ignores_unrelated_root_children(self):
        child, parent = self.slab_child_fixture()
        siblings = [self.element(i + 10) for i in range(255)]
        self.children[id(parent)] = [child, *siblings]
        for sibling in siblings:
            self.parents[id(sibling)] = parent
        unrelated = self.element(999, name="MultiSlab_TypeUUID")
        self.base.ElementsSelectService.SelectAllElements.return_value = [parent, unrelated]
        result = self.comparison(parent_ref=self.parent_ref)
        self.assertEqual(result["identity_resolution"]["child_visits"], 256)
        for call in self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements.call_args_list:
            self.assertIsNot(call.args[0], unrelated)
        for sibling in siblings:
            sibling.GetAttributes.assert_not_called()
        self.base.GetElement.assert_called_once_with(child)

    def test_explicit_parent_contract_is_strict_and_phase_specific_before_document(self):
        self.slab_child_fixture()
        contract = TypeAdapter(PropertyProbeRequest)
        for changes in (
            {"parent_ref": None}, {"parent_ref": {}},
            {"parent_ref": {**self.parent_ref, "view_uuid": "00000000-0000-0000-0000-000000000000"}},
            {"parent_ref": {**self.parent_ref, "model_uuid": self.target.GetModelElementUUID()}},
            {"parent_ref": {**self.parent_ref, "drawing_file": 101}},
            {"parent_ref": self.parent_ref, "phase": "attribute_evidence"},
        ):
            with self.subTest(changes=changes):
                request = self.request(**changes)
                with self.assertRaises(ValidationError):
                    contract.validate_python(request)
                self.assert_code("invalid_payload", lambda: self.probe(**request))
        self.coord.GetInputViewDocument.assert_not_called()

    def test_explicit_parent_retains_child_container_through_native_read(self):
        child, parent = self.slab_child_fixture()
        refs, test = [], self
        class Owner(list):
            pass
        def children(adapter, include_hidden):
            owner = Owner([child] if adapter is parent else [])
            refs.append(weakref.ref(owner))
            return owner
        self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements.side_effect = children
        class Properties:
            @property
            def Material(self):
                test.assertIsNotNone(refs[0]())
                return " "
        self.natives[id(child)].Properties = Properties()
        self.comparison(parent_ref=self.parent_ref)
        self.assertTrue(refs)
        self.assertTrue(all(ref() is None for ref in refs))

    def test_explicit_parent_durable_trace_precedes_child_sdk_call_and_storage_failure_stops(self):
        child, parent = self.slab_child_fixture(durable=True)
        service = self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements
        def children(adapter, include_hidden):
            records = [json.loads(line) for line in self.path.read_text().splitlines()]
            if adapter is parent:
                self.assertEqual(records[-1]["api"], "MaterialChild.GetChildModelElements")
                self.assertEqual(records[-1]["state"], "started")
                self.assertEqual(records[-1]["model_uuid"], child.GetModelElementUUID())
                self.assertEqual(records[-1]["parent_view_uuid"], self.parent_ref["view_uuid"])
                return [child]
            return []
        service.side_effect = children
        self.comparison(parent_ref=self.parent_ref)
        self.handler.property_probes.trace_path = self.path.parent
        service.reset_mock()
        self.base.GetElement.reset_mock()
        self.assert_code("probe_trace_unavailable", lambda: self.comparison(parent_ref=self.parent_ref))
        service.assert_not_called()
        self.base.GetElement.assert_not_called()

    def test_durable_trace_precedes_material_getter_and_storage_failure_stops_reads(self):
        target = self.material_fixture(durable=True)
        test = self
        class TracedProperties:
            @property
            def Material(self):
                records = [json.loads(line) for line in test.path.read_text().splitlines()]
                test.assertEqual(records[-1]["api"], "StructuralBeamProperties.Material")
                test.assertEqual(records[-1]["state"], "started")
                return "native"
        self.natives[id(target)].StructuralBeamProperties = TracedProperties()
        self.comparison()
        self.handler.property_probes.trace_path = self.path.parent
        self.base.GetElement.reset_mock()
        target.GetAttributes.reset_mock()
        self.assert_code("probe_trace_unavailable", self.comparison)
        self.base.GetElement.assert_not_called()
        target.GetAttributes.assert_not_called()

    def test_enumeration_owner_is_alive_through_material_and_released_afterward(self):
        target = self.material_fixture()
        refs, test = [], self
        class Owner(list):
            pass
        def select(doc):
            owner = Owner([target])
            refs.append(weakref.ref(owner))
            return owner
        self.base.ElementsSelectService.SelectAllElements.side_effect = select
        class Properties:
            @property
            def Material(self):
                test.assertIsNotNone(refs[-1]())
                return "native"
        self.natives[id(target)].StructuralBeamProperties = Properties()
        self.comparison()
        self.assertIsNone(refs[-1]())


if __name__ == "__main__":
    unittest.main()
