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
