"""0.51.0: every setter of one typed model-edit Apply joins one UI Undo step.

SDK doubles only: they show which native calls are made and in which order,
not that Allplan merges the transactions (that is the owner's UI Undo count).
"""
import unittest
from uuid import uuid4

import test_model_edit as edit_fixtures
import test_paired_property as paired


class UndoGroupTests(unittest.TestCase):
    family = paired.PairedPropertyTests.family
    request = paired.PairedPropertyTests.request
    plan = paired.PairedPropertyTests.plan

    def record_calls(self, f):
        """Log setters and UndoRedoService calls in one ordered list."""
        calls = []
        service_type = f.native.module.AllplanIFW.UndoRedoService
        service_type.reset_mock()
        service_type.side_effect = None
        service = service_type.return_value
        service.CreateUndoStep.side_effect = lambda: calls.append("CreateUndoStep")

        def open_service(*args):
            calls.append("UndoRedoService")
            return service

        service_type.side_effect = open_service
        modify = f.native.base.ModifyElements.side_effect

        def modify_elements(doc, elements):
            calls.append("ModifyElements")
            return modify(doc, elements)

        f.native.base.ModifyElements.side_effect = modify_elements
        change = f.native.base.ElementsAttributeService.ChangeAttributes.side_effect

        def change_attributes(*args):
            calls.append("ChangeAttributes")
            return change(*args)

        f.native.base.ElementsAttributeService.ChangeAttributes.side_effect = change_attributes
        return calls, service_type, service

    def test_native_and_attribute_setters_share_one_undo_step(self):
        f = self.family(mirror=False)
        calls, service_type, service = self.record_calls(f)
        plan = self.plan(f, "m2")
        self.assertIn("one UI Undo step", plan["paired_property"]["undo"])
        execution = uuid4().hex
        result = f.native.apply(plan, execution)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(calls, ["UndoRedoService", "ModifyElements", "ChangeAttributes", "CreateUndoStep"])
        service_type.assert_called_once()
        self.assertEqual(service_type.call_args.args[1:], (True, True, True))
        group = result["undo_group"]
        self.assertEqual((group["status"], group["setters_in_step"]), ("created", 2))
        self.assertEqual(group["api"], "NemAll_Python_IFW_Input.UndoRedoService")
        self.assertEqual(group["flags"], {"isPassivateAll": True, "isLockPreviewDraw": True,
                                          "collectEleForMultipleTransactions": True})
        self.assertTrue(group["native_acceptance"].startswith("not_run"))
        self.assertIn("one UI Undo step", result["undo"])
        # Replay reads the journal only: no setter and no new undo step.
        self.assertTrue(f.native.apply(plan, execution)["replayed"])
        service_type.assert_called_once()
        service.CreateUndoStep.assert_called_once()

    def test_attribute_that_follows_the_native_write_keeps_one_setter_in_the_step(self):
        f = self.family()
        calls, service_type, _ = self.record_calls(f)
        result = f.native.apply(self.plan(f))
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(calls, ["UndoRedoService", "ModifyElements", "CreateUndoStep"])
        self.assertEqual((result["undo_group"]["status"], result["undo_group"]["setters_in_step"]),
                         ("created", 1))

    def test_single_change_plan_opens_no_undo_service(self):
        f = self.family(code=0, attribute="m")
        calls, service_type, _ = self.record_calls(f)
        plan = self.plan(f)
        self.assertEqual(len(plan["changes"]), 1)
        result = f.native.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(calls, ["ChangeAttributes"])
        service_type.assert_not_called()
        # 0.51.2: every typed Apply reports undo_group (0.51.1 trial).
        self.assertEqual(result["undo_group"], {"status": "not_requested", "reason": "single_change_plan"})
        self.assertTrue(result["undo"].startswith("one setter call"))

    def test_step_is_closed_after_an_unknown_native_outcome(self):
        f = self.family(mirror=False, children=("AttributeContainer_TypeUUID",),
                        regenerate=("Opening_TypeUUID",))
        calls, _, service = self.record_calls(f)
        execution = uuid4().hex
        result = f.native.apply(self.plan(f), execution)
        native, attribute = result["outcomes"]
        self.assertEqual((native["state"], attribute["state"]), ("unknown", "skipped"))
        self.assertEqual(calls, ["UndoRedoService", "ModifyElements", "CreateUndoStep"])
        self.assertEqual(result["undo_group"]["status"], "created")
        self.assertTrue(f.native.recover(execution)["write_blocked"])
        service.CreateUndoStep.assert_called_once()

    def test_step_is_closed_when_the_second_setter_raises(self):
        f = self.family(mirror=False)
        calls, _, _ = self.record_calls(f)

        def lost_reply(*args):
            calls.append("ChangeAttributes")
            raise RuntimeError("lost reply")

        f.native.base.ElementsAttributeService.ChangeAttributes.side_effect = lost_reply
        result = f.native.apply(self.plan(f, "m2"))
        native, attribute = result["outcomes"]
        self.assertEqual((native["state"], attribute["state"]), ("applied", "unknown"))
        self.assertEqual(calls, ["UndoRedoService", "ModifyElements", "ChangeAttributes", "CreateUndoStep"])
        self.assertEqual((result["undo_group"]["status"], result["undo_group"]["setters_in_step"]),
                         ("created", 2))

    def test_unavailable_service_still_runs_every_setter_and_says_so(self):
        f = self.family(mirror=False)
        calls, service_type, service = self.record_calls(f)
        service_type.side_effect = AttributeError("not in this runtime")
        result = f.native.apply(self.plan(f, "m2"))
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual(calls, ["ModifyElements", "ChangeAttributes"])
        group = result["undo_group"]
        self.assertEqual((group["status"], group["error_type"]), ("unavailable", "AttributeError"))
        self.assertIn("separate UI Undo step", group["effect"])
        service.CreateUndoStep.assert_not_called()
        self.assertTrue(result["undo"].startswith("not_checked"))

    def test_close_failure_never_changes_setter_outcomes(self):
        f = self.family(mirror=False)
        _, _, service = self.record_calls(f)
        service.CreateUndoStep.side_effect = RuntimeError("native detail")
        result = f.native.apply(self.plan(f, "m2"))
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual([o["state"] for o in result["outcomes"]], ["applied", "applied"])
        self.assertEqual((result["undo_group"]["status"], result["undo_group"]["error_type"]),
                         ("close_failed", "RuntimeError"))
        self.assertNotIn("native detail", str(result["undo_group"]))


class AttributeAndLayerUndoGroupTests(unittest.TestCase):
    """A plain typed plan with several setters (attribute + layer) is one step too."""
    setUp = edit_fixtures.ModelEditTests.setUp
    fixture = edit_fixtures.ModelEditTests.fixture
    setter_fakes = edit_fixtures.ModelEditTests.setter_fakes
    request = edit_fixtures.ModelEditTests.request
    call = edit_fixtures.ModelEditTests.call
    preview = edit_fixtures.ModelEditTests.preview
    plan_request = edit_fixtures.ModelEditTests.plan_request
    highlight = edit_fixtures.ModelEditTests.highlight
    apply = edit_fixtures.ModelEditTests.apply
    prepare = edit_fixtures.ModelEditTests.prepare
    prepare_context = edit_fixtures.ModelEditTests.prepare_context
    adapter = edit_fixtures.ModelEditTests.adapter
    element = edit_fixtures.ModelEditTests.element
    native = edit_fixtures.ModelEditTests.native
    attribute_catalog = edit_fixtures.ModelEditTests.attribute_catalog

    def test_attribute_and_layer_writes_share_one_undo_step(self):
        elements = self.fixture(("", "F60"))
        self.setter_fakes(elements)
        service_type = self.module.AllplanIFW.UndoRedoService
        service_type.reset_mock()
        plan = self.preview()
        self.assertEqual(plan["counts"]["changes"], 2)
        self.highlight(plan)
        result = self.apply(plan)
        self.assertEqual(result["state"], "completed", result)
        service_type.assert_called_once()
        service_type.return_value.CreateUndoStep.assert_called_once()
        self.assertEqual((result["undo_group"]["status"], result["undo_group"]["setters_in_step"]),
                         ("created", 2))
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 1)
        self.assertEqual(self.base.ElementsLayerService.ChangeLayer.call_count, 1)


if __name__ == "__main__":
    unittest.main()
