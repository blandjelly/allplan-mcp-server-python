"""Focused M4 recovery coverage for multiple live native views and wrappers."""
import copy
import importlib
import unittest
from uuid import uuid4

import test_model_edit as fixtures


class MultiViewRecoveryTests(unittest.TestCase):
    """Use the existing model-edit native fakes without importing test cases."""

    setUp = fixtures.ModelEditTests.setUp
    adapter = fixtures.ModelEditTests.adapter
    native = fixtures.ModelEditTests.native
    prepare = fixtures.ModelEditTests.prepare
    prepare_context = fixtures.ModelEditTests.prepare_context
    fixture = fixtures.ModelEditTests.fixture
    element = fixtures.ModelEditTests.element
    setter_fakes = fixtures.ModelEditTests.setter_fakes
    attribute_catalog = fixtures.ModelEditTests.attribute_catalog
    request = fixtures.ModelEditTests.request
    call = fixtures.ModelEditTests.call
    preview = fixtures.ModelEditTests.preview
    plan_request = fixtures.ModelEditTests.plan_request
    highlight = fixtures.ModelEditTests.highlight
    apply = fixtures.ModelEditTests.apply
    recover = fixtures.ModelEditTests.recover
    assert_code = fixtures.ModelEditTests.assert_code

    def setUp(self):
        fixtures.ModelEditTests.setUp(self)
        self.directory = importlib.import_module("tempfile").TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.handler.repair_plans.executor.path = importlib.import_module("pathlib").Path(self.directory.name)

    def _beam_representation(self, source, ident, *, values=None, view_uuid=None, type_uuid=None):
        replica = self.element(ident, name="Beam_TypeUUID", attrs=copy.deepcopy(
            values if values is not None else source.GetAttributes.return_value))
        replica.GetDrawingfileNumber.return_value = source.GetDrawingfileNumber.return_value
        replica.GetModelElementUUID.return_value = source.GetModelElementUUID.return_value
        replica.GetElementAdapterType.return_value.GetGuid.return_value = (
            type_uuid if type_uuid is not None
            else source.GetElementAdapterType.return_value.GetGuid.return_value)
        if view_uuid is not None:
            replica.GetElementUUID.return_value = view_uuid
        replica.GetCommonProperties.return_value.Layer = source.GetCommonProperties.return_value.Layer
        for method, value in (("IsDeleted", False), ("IsNull", False), ("IsValid", True),
                              ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                              ("IsInMacro", True), ("IsLabelElement", False)):
            getattr(replica, method).return_value = value
        return replica

    def _attach(self, *elements):
        self.base.ElementsSelectService.SelectAllElements.return_value = list(elements)

    def _old_style_unknown(self, *, after_write):
        beam = self.fixture(("300X500",))[0]
        beam.GetElementAdapterType.return_value.GetTypeName.return_value = "Beam_TypeUUID"
        self.attribute_catalog({935: "Klasa odporności ogniowej"})
        self.attribute_type_names[935] = "String"
        self.setter_fakes([beam])
        setter = self.base.ElementsAttributeService.ChangeAttributes.side_effect

        def lose_reply(attributes, targets, *flags):
            if after_write:
                setter(attributes, targets, *flags)
            raise RuntimeError("synthetic lost setter reply")

        self.base.ElementsAttributeService.ChangeAttributes.side_effect = lose_reply
        plan = self.preview(predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 935},
            "value_type": "text", "value": "450X450", "mode": "replace"}])
        self.assertTrue(plan["changes"][0].get("target_view_uuid"))
        self.highlight(plan)
        self.base.ElementsAttributeService.ChangeAttributes.reset_mock()
        stopped = self.apply(plan)
        self.assertEqual(stopped["outcomes"][0]["state"], "unknown")
        executor = self.handler.repair_plans.executor
        record = executor.load(stopped["execution_id"])
        # Simulate a valid 0.21.1 journal target, before view binding existed.
        record["changes"][0].pop("target_view_uuid", None)
        executor.save(record)
        return beam, stopped["execution_id"]

    def test_legacy_unbound_record_recovers_unanimous_old_and_new_views(self):
        for after_write, expected in ((False, "old_value_observed"), (True, "new_value_observed")):
            with self.subTest(expected=expected):
                self.setUp()
                beam, execution_id = self._old_style_unknown(after_write=after_write)
                replica = self._beam_representation(beam, 9)
                self._attach(beam, replica)
                result = self.recover(execution_id)
                self.assertEqual(result["recovery"]["observations"][0]["state"], expected)
                self.assertEqual(result["outcomes"][0]["state"], "reconciled")
                self.assertFalse(result["write_blocked"])
                self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)

    def test_legacy_unbound_disagreeing_or_unreadable_views_keep_write_blocked(self):
        for mode in ("different", "unreadable", "integer_bool", "wrong_type"):
            with self.subTest(mode=mode):
                self.setUp()
                if mode == "integer_bool":
                    beam = self.fixture(("",))[0]
                    beam.GetElementAdapterType.return_value.GetTypeName.return_value = "Beam_TypeUUID"
                    beam.GetAttributes.return_value.extend([(20001, 0)])
                    self.attribute_catalog({20001: "Element nośny"})
                    self.attribute_type_names[20001] = "Integer"
                    self.setter_fakes([beam])
                    self.base.ElementsAttributeService.ChangeAttributes.side_effect = RuntimeError("lost")
                    plan = self.preview(predicate=None, changes=[{
                        "target": {"kind": "attribute", "attribute_id": 20001},
                        "value_type": "integer", "value": 1, "mode": "replace"}])
                    self.highlight(plan)
                    self.base.ElementsAttributeService.ChangeAttributes.reset_mock()
                    stopped = self.apply(plan)
                    execution_id = stopped["execution_id"]
                    record = self.handler.repair_plans.executor.load(execution_id)
                    record["changes"][0].pop("target_view_uuid", None)
                    self.handler.repair_plans.executor.save(record)
                    replica = self._beam_representation(beam, 9, values=[(935, ""), (20001, True)])
                else:
                    beam, execution_id = self._old_style_unknown(after_write=False)
                    replica = self._beam_representation(beam, 9)
                    if mode == "different":
                        replica.GetAttributes.return_value = [(935, "450X450")]
                    elif mode == "unreadable":
                        replica.GetAttributes.side_effect = RuntimeError("view read unavailable")
                    else:
                        replica.GetElementAdapterType.return_value.GetGuid.return_value = (
                            "30000000-0000-4000-8000-000000000009")
                self._attach(beam, replica)
                result = self.recover(execution_id)
                observation = result["recovery"]["observations"][0]
                self.assertIn(observation["state"], {"unknown", "conflict"})
                self.assertEqual(result["outcomes"][0]["state"], "unknown")
                self.assertTrue(result["write_blocked"])
                self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)

    def test_same_view_distinct_wrappers_must_agree(self):
        beam, execution_id = self._old_style_unknown(after_write=False)
        replica = self._beam_representation(
            beam, 9, values=[(935, "450X450")], view_uuid=beam.GetElementUUID.return_value)
        self._attach(beam, replica)
        result = self.recover(execution_id)
        self.assertIn(result["recovery"]["observations"][0]["state"], {"unknown", "conflict"})
        self.assertTrue(result["write_blocked"])
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)

    def test_view_bound_write_uses_one_setter_and_all_view_readback_consensus(self):
        beam = self.fixture(("300X500",))[0]
        beam.GetElementAdapterType.return_value.GetTypeName.return_value = "Beam_TypeUUID"
        replica = self._beam_representation(beam, 9)
        self._attach(beam, replica)
        self.attribute_catalog({935: "Klasa odporności ogniowej"})
        self.attribute_type_names[935] = "String"
        self.setter_fakes([beam])

        def mirrored_setter(attributes, targets, *flags):
            for element in (beam, replica):
                current = list(element.GetAttributes.return_value)
                for ident, value in attributes:
                    current = [(key, value if key == ident else old) for key, old in current]
                element.GetAttributes.return_value = current

        self.base.ElementsAttributeService.ChangeAttributes.side_effect = mirrored_setter
        plan = self.preview(predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 935},
            "value_type": "text", "value": "450X450", "mode": "replace"}])
        change = plan["changes"][0]
        self.assertIn(change["target_view_uuid"], {beam.GetElementUUID.return_value,
                                                   replica.GetElementUUID.return_value})
        self.highlight(plan)
        result = self.apply(plan)
        self.assertEqual(result["state"], "completed")
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)
        self.assertEqual(len(result["outcomes"][0]["representation_consensus"]["representations"]), 2)

    def test_large_raw_readbacks_do_not_multiply_by_representation_count(self):
        beam, execution_id = self._old_style_unknown(after_write=False)
        beam.GetAttributes.return_value = [(935, "x" * 8192)]
        replicas = [self._beam_representation(beam, ident, view_uuid=str(uuid4()))
                    for ident in range(2, 65)]
        self._attach(beam, *replicas)
        result = self.recover(execution_id)
        observed = result["recovery"]["observations"][0]
        self.assertEqual(observed["readback"]["value"], "x" * 8192)
        proof = observed["representation_consensus"]
        self.assertTrue(proof["agreed"])
        self.assertEqual(len(proof["representations"]), 64)
        self.assertLess(len(importlib.import_module("json").dumps(proof)), 25000)
        self.assertTrue(result["write_blocked"])  # unanimous, but neither old nor new
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)

    def test_missing_reviewed_view_rejects_before_journal_or_setter(self):
        beam = self.fixture(("300X500",))[0]
        beam.GetElementAdapterType.return_value.GetTypeName.return_value = "Beam_TypeUUID"
        self.attribute_catalog({935: "Klasa odporności ogniowej"})
        self.attribute_type_names[935] = "String"
        self.setter_fakes([beam])
        plan = self.preview(predicate=None, changes=[{
            "target": {"kind": "attribute", "attribute_id": 935},
            "value_type": "text", "value": "450X450", "mode": "replace"}])
        self.highlight(plan)
        replacement = self._beam_representation(beam, 9)
        self._attach(replacement)
        self.assert_code("repair_conflict", lambda: self.apply(plan))
        self.assertEqual(list(self.handler.repair_plans.executor.path.glob("*.json")), [])
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()


if __name__ == "__main__":
    unittest.main()
