"""Guarded model-object deletion through the shared edit journal."""
import copy
import unittest
import importlib
from uuid import uuid4
from unittest.mock import MagicMock, patch

from pydantic import TypeAdapter, ValidationError
from allplan_mcp.model_edit_models import ModelEditRequest
import test_edit_ownership as fixtures


class ModelDeleteTests(unittest.TestCase):
    setUp = fixtures.EditOwnershipTests.setUp
    prepare_context = fixtures.EditOwnershipTests.prepare_context
    prepare = fixtures.EditOwnershipTests.prepare
    adapter = fixtures.EditOwnershipTests.adapter
    native = fixtures.EditOwnershipTests.native
    element = fixtures.EditOwnershipTests.element
    assert_code = fixtures.EditOwnershipTests.assert_code
    fixture = fixtures.EditOwnershipTests.fixture
    setter_fakes = fixtures.EditOwnershipTests.setter_fakes
    attribute_catalog = fixtures.fixtures.ModelEditTests.attribute_catalog
    request = fixtures.EditOwnershipTests.request
    call = fixtures.EditOwnershipTests.call
    preview = fixtures.EditOwnershipTests.preview
    plan_request = fixtures.EditOwnershipTests.plan_request
    highlight = fixtures.EditOwnershipTests.highlight
    apply = fixtures.EditOwnershipTests.apply
    recover = fixtures.EditOwnershipTests.recover

    def delete_request(self, **updates):
        request = self.request(predicate={"field": "attribute:935", "op": "eq", "value": ""},
                               changes=[{"target": {"kind": "delete"}}])
        request.update(updates)
        return request

    def _broken_opening_preview(self, *, sdk_failure=False):
        opening = self.fixture(("",))[0]
        opening.GetElementAdapterType.return_value.GetTypeName.return_value = "WindowDoor_TypeUUID"
        tier = self.element(2, name="DoorTier_TypeUUID")
        null_parent = MagicMock()
        null_parent.IsNull.return_value = True
        self.parents[id(opening)] = null_parent
        if sdk_failure:
            self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements = (
                lambda *_args: (_ for _ in ()).throw(RuntimeError("private child read detail")))
        else:
            unrelated = self.element(3, name="Wall_TypeUUID")
            self.children[id(opening)] = [tier]
            self.parents[id(tier)] = unrelated
        plan = self.preview(predicate=None, native_types=["WindowDoor_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertFalse(plan["apply_available"])
        self.assertEqual(len(plan["blocked"]), 1)
        self.base.DeleteElements.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        return plan["blocked"][0]

    def test_preview_exposes_bounded_child_owner_diagnostic_without_write(self):
        blocked = self._broken_opening_preview()
        self.assertEqual(blocked["reason"], "delete_ownership_unavailable")
        self.assertEqual(blocked["observation"]["reason"], "component_child_owner_mismatch")
        self.assertEqual(blocked["observation"]["diagnostic"],
                         {"stage": "child_parent_identity", "error_type": "ValueError"})

    def test_preview_exposes_bounded_native_read_diagnostic_without_write(self):
        blocked = self._broken_opening_preview(sdk_failure=True)
        self.assertEqual(blocked["reason"], "delete_ownership_unavailable")
        self.assertEqual(blocked["observation"]["reason"], "component_read_unavailable")
        self.assertEqual(blocked["observation"]["diagnostic"],
                         {"stage": "children", "error_type": "RuntimeError"})
        self.assertNotIn("private child read detail", str(blocked))

    def live_elements(self):
        # DeleteElements removes the object from the freshly enumerated model.
        self.base.ElementsSelectService.SelectAllElements.side_effect = lambda doc: [
            element for element in self.elements if not element.IsDeleted()
        ]

    def alternate_view(self, source, index):
        alias = self.element(index)
        alias.GetDrawingfileNumber.return_value = source.GetDrawingfileNumber.return_value
        alias.GetModelElementUUID.return_value = source.GetModelElementUUID.return_value
        alias.GetElementAdapterType.return_value.GetTypeName.return_value = (
            source.GetElementAdapterType.return_value.GetTypeName.return_value)
        alias.GetElementAdapterType.return_value.GetGuid.return_value = (
            source.GetElementAdapterType.return_value.GetGuid.return_value)
        return alias

    def column_with_attribute_container(self):
        target = self.fixture(("",))[0]
        container = self.element(2, name="AttributeContainer_TypeUUID")
        parent_view = self.alternate_view(target, 3)
        self.parents[id(target)] = self.null_parent()
        self.parents[id(container)] = parent_view
        self.children[id(target)] = [container]
        self.elements = [target, container]
        self.live_elements()
        return target, container, parent_view

    @staticmethod
    def null_parent():
        parent = MagicMock()
        parent.IsNull.return_value = True
        return parent

    def test_delete_request_is_exclusive_with_field_edits(self):
        self.fixture(("",))
        self.assert_code("invalid_payload", lambda: self.preview(changes=[
            {"target": {"kind": "delete"}},
            {"target": {"kind": "attribute", "attribute_id": 935}, "value": "new"},
        ]))
        self.assert_code("invalid_payload", lambda: self.preview(changes=[
            {"target": {"kind": "delete"}}, {"target": {"kind": "delete"}},
        ]))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.DeleteElements.assert_not_called()

        TypeAdapter(ModelEditRequest).validate_python(self.delete_request())
        with self.assertRaises(ValidationError):
            TypeAdapter(ModelEditRequest).validate_python(self.delete_request(changes=[
                {"target": {"kind": "delete"}},
                {"target": {"kind": "attribute", "attribute_id": 935}, "value": "new"},
            ]))

    def test_native_material_tier_index_is_a_strict_literal_integer(self):
        from allplan_mcp.model_edit_models import ModelEditRequest
        request = self.request(predicate=None, changes=[{"target": {
            "kind": "native_material", "tier_index": 1}, "value": "C35/45"}])
        TypeAdapter(ModelEditRequest).validate_python(request)
        host_contracts = importlib.import_module(self.module.__package__ + ".model_edit_contracts")
        host_contracts.validate_request(request)
        for tier_index in (True, 1.0, 2):
            invalid = {**request, "changes": [{"target": {
                "kind": "native_material", "tier_index": tier_index}, "value": "C35/45"}]}
            with self.subTest(tier_index=tier_index):
                with self.assertRaises(ValidationError):
                    TypeAdapter(ModelEditRequest).validate_python(invalid)
                self.assert_code("invalid_payload", lambda: host_contracts.validate_request(invalid))

    def test_column_delete_previews_highlights_and_removes_only_included_target(self):
        self.elements = self.fixture(("", ""))
        target, peer = self.elements
        peer.GetAttributes.return_value = [(935, "peer")]
        self.live_elements()
        deleted = []

        def delete_elements(doc, adapters):
            self.assertEqual(len(adapters), 1)
            deleted.extend(adapters)
            adapters[0].IsDeleted.return_value = True

        self.base.DeleteElements.side_effect = delete_elements
        excluded_uuid = peer.GetModelElementUUID()
        plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                            exclude_model_uuids=[excluded_uuid],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["counts"]["matched"], 1)
        self.assertEqual(plan["counts"]["excluded"], 1)
        self.assertEqual(plan["counts"]["changes"], 1)
        change = plan["changes"][0]
        self.assertEqual(change["operation"], "delete_element")
        self.assertEqual(change["field"], "element_exists")
        self.assertEqual(change["old_value"], {"status": "observed", "value": True})
        self.assertIs(change["new_value"], False)
        self.assertEqual(change["ref"]["model_uuid"], target.GetModelElementUUID())
        ownership = change["resource"]["delete_ownership"]
        self.assertEqual(ownership["status"], "observed")
        self.assertEqual(ownership["value"]["lineage"], [ownership["value"]["target"]])
        self.assertEqual(self.highlight(plan)["state"], "submitted")
        shown = self.module.AllplanIFW.HighlightService.HighlightElements.call_args.args[0]
        self.assertEqual([id(item) for item in shown], [id(target)])

        execution_id = uuid4().hex
        result = self.apply(plan, execution_id)
        self.assertEqual(result["state"], "completed", result)
        self.assertTrue(result["audited_fields_match_plan"])
        self.assertEqual([id(item) for item in deleted], [id(target)])
        self.base.DeleteElements.assert_called_once()
        self.assertFalse(peer.IsDeleted.return_value)
        self.assertEqual(peer.GetAttributes.return_value, [(935, "peer")])
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.base.DeleteElements.assert_called_once()

    def test_three_column_delete_uses_one_native_submission_after_all_write_ahead_markers(self):
        fixture = self.fixture(("", "", "", "peer"))
        targets, peer = fixture[:3], fixture[3]
        containers = [self.element(20 + index, name="AttributeContainer_TypeUUID")
                      for index in range(len(targets))]
        for container in containers:
            for method, value in (("IsDeleted", False), ("IsValid", True),
                                  ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                                  ("IsLabelElement", False)):
                getattr(container, method).return_value = value
        for target, container in zip(targets, containers):
            self.parents[id(target)] = self.null_parent()
            self.parents[id(container)] = target
            self.children[id(target)] = [container]
        self.elements = [*targets, *containers, peer]
        self.live_elements()
        plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                            exclude_model_uuids=[peer.GetModelElementUUID()],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["counts"]["changes"], 3)
        self.highlight(plan)
        execution_id = uuid4().hex
        journal_path = self.plans.executor.path / (execution_id + ".json")
        submitted = []

        def delete_elements(doc, adapters):
            from pathlib import Path
            import json
            saved = json.loads(Path(journal_path).read_text(encoding="utf-8"))
            self.assertEqual(saved["native_delete_batch"], {
                "method": "DeleteElements", "target_count": 3,
                "submission": "may_have_run", "native_undo": "not_checked"})
            self.assertEqual([item["state"] for item in saved["outcomes"]], ["unknown"] * 3)
            submitted.extend(adapters)
            for item in [*adapters, *containers]:
                item.IsDeleted.return_value = True

        self.base.DeleteElements.side_effect = delete_elements
        result = self.apply(plan, execution_id)
        self.assertEqual(result["state"], "completed", result)
        self.assertEqual([item["state"] for item in result["outcomes"]], ["applied"] * 3)
        self.assertEqual(result["native_delete_batch"]["submission"], "returned")
        self.assertEqual(result["native_delete_batch"]["target_count"], 3)
        self.assertEqual([id(item) for item in submitted], [id(item) for item in targets])
        self.assertFalse(peer.IsDeleted.return_value)
        self.base.DeleteElements.assert_called_once()
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.base.DeleteElements.assert_called_once()

    def test_three_column_delete_partial_native_failure_marks_every_target_unknown_and_recovers_read_only(self):
        targets = self.fixture(("", "", ""))
        self.elements = targets
        self.live_elements()
        plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(plan["apply_available"], plan)
        self.highlight(plan)
        execution_id = uuid4().hex
        attempts = []

        def partial_delete(doc, adapters):
            attempts.append([item.GetModelElementUUID() for item in adapters])
            self.assertEqual(len(adapters), 3)
            adapters[0].IsDeleted.return_value = True
            raise RuntimeError("native batch reply failed after partial deletion")

        self.base.DeleteElements.side_effect = partial_delete
        result = self.apply(plan, execution_id)
        self.assertEqual(result["state"], "stopped")
        self.assertEqual([item["state"] for item in result["outcomes"]], ["unknown"] * 3)
        self.assertTrue(all(item["stage"] == "setter" for item in result["outcomes"]))
        self.assertEqual(result["native_delete_batch"]["submission"], "may_have_run")
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        recovered = self.recover(execution_id)
        self.assertTrue(recovered["read_only"])
        self.assertEqual([item["state"] for item in recovered["recovery"]["observations"]],
                         ["new_value_observed", "old_value_observed", "old_value_observed"])
        self.assertEqual(len(attempts), 1)
        self.base.DeleteElements.assert_called_once()

    def test_three_column_late_write_guard_failure_submits_no_partial_delete(self):
        targets = self.fixture(("", "", ""))
        self.elements = targets
        self.live_elements()
        plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.highlight(plan)
        model_delete = importlib.import_module(self.module.__package__ + ".model_delete")
        original_guard = model_delete.final_write_guard
        checked = []

        def drift_on_last(base, element, change, doc, check):
            checked.append(element)
            if element is targets[-1]:
                element.IsDeleted.return_value = True
            return original_guard(base, element, change, doc, check)

        with patch.object(model_delete, "final_write_guard", side_effect=drift_on_last):
            result = self.apply(plan, uuid4().hex)
        self.assertEqual([id(item) for item in checked], [id(item) for item in targets])
        self.assertEqual(result["state"], "stopped")
        self.assertEqual([item["state"] for item in result["outcomes"]], ["unknown"] * 3)
        self.base.DeleteElements.assert_not_called()

    def test_three_column_partial_subtree_readback_still_observes_remaining_batch_targets(self):
        fixture = self.fixture(("", "", "", "peer"))
        targets, peer = fixture[:3], fixture[3]
        containers = [self.element(40 + index, name="AttributeContainer_TypeUUID")
                      for index in range(len(targets))]
        for container in containers:
            for method, value in (("IsDeleted", False), ("IsValid", True),
                                  ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                                  ("IsLabelElement", False)):
                getattr(container, method).return_value = value
        for target, container in zip(targets, containers):
            self.parents[id(target)] = self.null_parent()
            self.parents[id(container)] = target
            self.children[id(target)] = [container]
        self.elements = [*targets, *containers, peer]
        self.live_elements()

        def partially_delete(doc, adapters):
            self.assertEqual(len(adapters), 3)
            for target in adapters:
                target.IsDeleted.return_value = True
            for container in containers[1:]:
                container.IsDeleted.return_value = True

        self.base.DeleteElements.side_effect = partially_delete
        plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                            exclude_model_uuids=[peer.GetModelElementUUID()],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(plan["apply_available"], plan)
        self.assertEqual(plan["counts"]["changes"], 3)
        self.assertEqual([item["model_uuid"] for item in plan["changes"][0]["resource"]["delete_ownership"]["value"]["descendants"]],
                         [containers[0].GetModelElementUUID()])
        self.highlight(plan)
        result = self.apply(plan, uuid4().hex)
        self.assertEqual([item["state"] for item in result["outcomes"]],
                         ["unknown", "applied", "applied"], result["outcomes"])
        self.assertEqual(self.base.DeleteElements.call_count, 1)

    def test_three_column_native_crash_keeps_batch_unknown_across_restart(self):
        targets = self.fixture(("", "", ""))
        self.elements = targets
        self.live_elements()
        plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.highlight(plan)
        execution_id = uuid4().hex

        def crash_after_first_delete(doc, adapters):
            adapters[0].IsDeleted.return_value = True
            raise SystemExit("simulated process interruption during native batch")

        self.base.DeleteElements.side_effect = crash_after_first_delete
        with self.assertRaises(SystemExit):
            self.apply(plan, execution_id)
        record = self.plans.executor.load(execution_id)
        self.assertEqual([item["state"] for item in record["outcomes"]], ["unknown"] * 3)
        service = importlib.import_module(self.module.__package__ + ".model_repair").RepairPlanService
        self.handler.repair_plans = service(self.handler.model_queries, self.plans.executor.path)
        self.handler.repair_plans.trace_path = self.plans.trace_path
        replay = self.apply(plan, execution_id)
        self.assertTrue(replay["replayed"])
        recovered = self.recover(execution_id)
        self.assertTrue(recovered["read_only"])
        self.assertEqual([item["state"] for item in recovered["recovery"]["observations"]],
                         ["new_value_observed", "old_value_observed", "old_value_observed"])
        self.base.DeleteElements.assert_called_once()

    def test_column_delete_accepts_child_parent_alias_view_and_replays_once(self):
        target, container, parent_view = self.column_with_attribute_container()

        def delete_elements(doc, adapters):
            self.assertEqual([id(item) for item in adapters], [id(target)])
            target.IsDeleted.return_value = True
            container.IsDeleted.return_value = True

        self.base.DeleteElements.side_effect = delete_elements
        plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(plan["apply_available"], plan)
        value = plan["changes"][0]["resource"]["delete_ownership"]["value"]
        direct_edge = value["child_parent_edges"][0]
        descendant_edge = value["descendant_parent_edges"][0]
        self.assertEqual(direct_edge["child"]["model_uuid"], container.GetModelElementUUID())
        self.assertEqual(direct_edge["parent"]["view_uuid"], parent_view.GetElementUUID())
        self.assertEqual(descendant_edge["child"]["model_uuid"], container.GetModelElementUUID())
        self.assertEqual(descendant_edge["parent"]["view_uuid"], parent_view.GetElementUUID())
        self.assertNotEqual(direct_edge["parent"]["view_uuid"], target.GetElementUUID())
        self.highlight(plan)

        execution_id = uuid4().hex
        result = self.apply(plan, execution_id)
        self.assertEqual(result["state"], "completed", result)
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.base.DeleteElements.assert_called_once()

    def test_column_delete_conflicts_when_child_parent_view_changes_after_preview(self):
        target, _container, _parent_view = self.column_with_attribute_container()
        plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(plan["apply_available"], plan)
        self.highlight(plan)
        self.parents[id(self.children[id(target)][0])] = self.alternate_view(target, 4)
        self.assert_code("repair_conflict", lambda: self.apply(plan))
        self.base.DeleteElements.assert_not_called()

    def test_column_delete_conflicts_when_child_enumeration_changes_after_preview(self):
        target, _container, _parent_view = self.column_with_attribute_container()
        plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(plan["apply_available"], plan)
        self.highlight(plan)
        added = self.element(5, name="AttributeContainer_TypeUUID")
        self.parents[id(added)] = self.alternate_view(target, 6)
        self.children[id(target)].append(added)
        self.elements.append(added)

        self.assert_code("repair_conflict", lambda: self.apply(plan))
        self.base.DeleteElements.assert_not_called()

    def test_column_delete_rejects_child_parent_model_type_and_file_mismatch(self):
        for mismatch in ("model", "type", "file"):
            with self.subTest(mismatch=mismatch):
                target, container, parent_view = self.column_with_attribute_container()
                if mismatch == "model":
                    parent_view.GetModelElementUUID.return_value = self.element(4).GetModelElementUUID.return_value
                elif mismatch == "type":
                    parent_view.GetElementAdapterType.return_value.GetTypeName.return_value = "Wall_TypeUUID"
                else:
                    parent_view.GetDrawingfileNumber.return_value = 102
                plan = self.preview(predicate=None, native_types=["Column_TypeUUID"],
                                    changes=[{"target": {"kind": "delete"}}])
                self.assertFalse(plan["apply_available"])
                self.assertEqual(plan["blocked"][0]["reason"], "delete_ownership_unavailable")
                self.assertEqual(plan["blocked"][0]["observation"]["reason"],
                                 "component_child_owner_mismatch")
                self.base.DeleteElements.assert_not_called()

    def test_late_parent_appearance_conflicts_before_delete(self):
        target = self.fixture(("",))[0]
        self.elements = [target]
        target.GetElementAdapterType.return_value.GetTypeName.return_value = "Slab_TypeUUID"
        plan = self.preview(predicate=None, native_types=["Slab_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(plan["apply_available"], plan)
        self.highlight(plan)
        parent = self.element(2, name="MultiSlab_TypeUUID")
        self.parents[id(target)] = parent
        self.children[id(parent)] = [target]
        self.assert_code("repair_conflict", lambda: self.apply(plan))
        self.base.DeleteElements.assert_not_called()

    def test_parented_slab_delete_is_blocked_but_root_multislab_delete_is_allowed(self):
        slab, aggregate = fixtures.EditOwnershipTests.slab_fixture(self)
        self.elements = [slab, aggregate]
        blocked = self.preview(predicate=None, native_types=["Slab_TypeUUID"],
                               changes=[{"target": {"kind": "delete"}}])
        self.assertFalse(blocked["apply_available"])
        self.assertEqual(blocked["blocked"][0]["reason"], "delete_parent_requires_explicit_owner")
        self.base.DeleteElements.assert_not_called()

        aggregate.GetElementAdapterType.return_value.GetTypeName.return_value = "MultiSlab_TypeUUID"
        allowed = self.preview(predicate=None, native_types=["MultiSlab_TypeUUID"],
                               changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(allowed["apply_available"], allowed)
        self.assertEqual(allowed["changes"][0]["ref"]["model_uuid"], aggregate.GetModelElementUUID())
        ownership = allowed["changes"][0]["resource"]["delete_ownership"]
        self.assertEqual(ownership["status"], "observed")
        self.assertEqual(ownership["value"]["lineage"], [ownership["value"]["target"]])
        self.assertIn(slab.GetModelElementUUID(),
                      [child["model_uuid"] for child in ownership["value"]["children"]])
        self.live_elements()
        def cascade_delete(doc, adapters):
            # The native root delete is expected to cascade to its owned Slab.
            self.assertEqual([item.GetModelElementUUID() for item in adapters],
                             [aggregate.GetModelElementUUID()])
            aggregate.IsDeleted.return_value = True
            slab.IsDeleted.return_value = True
        self.base.DeleteElements.side_effect = cascade_delete
        self.highlight(allowed)
        applied = self.apply(allowed, uuid4().hex)
        self.assertEqual(applied["state"], "completed", applied)
        self.assertEqual(self.base.DeleteElements.call_count, 1)

    def test_multislab_delete_is_blocked_when_owned_slab_is_excluded(self):
        slab, aggregate = fixtures.EditOwnershipTests.slab_fixture(self)
        self.elements = [slab, aggregate]
        aggregate.GetElementAdapterType.return_value.GetTypeName.return_value = "MultiSlab_TypeUUID"
        plan = self.preview(predicate=None, native_types=["Slab_TypeUUID", "MultiSlab_TypeUUID"],
                            exclude_model_uuids=[slab.GetModelElementUUID()],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertFalse(plan["apply_available"], plan)
        self.assertEqual(plan["changes"], [])
        self.assertIn("delete_contains_excluded_descendant", {item["reason"] for item in plan["blocked"]})
        self.base.DeleteElements.assert_not_called()

    def test_parented_windowdoor_opening_deletes_without_deleting_parent_wall(self):
        wall = self.fixture(("",))[0]
        wall.GetElementAdapterType.return_value.GetTypeName.return_value = "Wall_TypeUUID"
        opening = self.element(2, name="WindowDoor_TypeUUID")
        tier = self.element(3, name="DoorTier_TypeUUID")
        reveal = self.element(4, name="DoorReveal_TypeUUID")
        for method, value in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                              ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                              ("IsLabelElement", False)):
            for adapter in (opening, tier, reveal):
                getattr(adapter, method).return_value = value
        self.parents[id(opening)] = wall
        self.parents[id(tier)] = opening
        self.parents[id(reveal)] = opening
        self.children[id(wall)] = [opening]
        self.children[id(opening)] = [tier, reveal]
        self.elements = [wall, opening, tier, reveal]
        self.base.ElementsSelectService.SelectAllElements.return_value = self.elements
        self.live_elements()

        def delete_opening(doc, adapters):
            self.assertEqual([item.GetModelElementUUID() for item in adapters],
                             [opening.GetModelElementUUID()])
            opening.IsDeleted.return_value = True
            tier.IsDeleted.return_value = True
            reveal.IsDeleted.return_value = True

        self.base.DeleteElements.side_effect = delete_opening
        plan = self.preview(predicate=None, native_types=["WindowDoor_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.assertTrue(plan["apply_available"], plan)
        opening_change = plan["changes"][0]
        self.assertEqual(opening_change["native_type"], "WindowDoor_TypeUUID")
        self.assertEqual(opening_change["resource"]["delete_ownership"]["value"]["lineage"][1]["model_uuid"],
                         wall.GetModelElementUUID())
        self.highlight(plan)
        result = self.apply(plan, uuid4().hex)
        self.assertEqual(result["state"], "completed", result)
        self.assertFalse(wall.IsDeleted.return_value)
        self.assertTrue(opening.IsDeleted.return_value)
        self.assertTrue(tier.IsDeleted.return_value)
        self.assertTrue(reveal.IsDeleted.return_value)
        self.base.DeleteElements.assert_called_once()

    def test_delete_ownership_preserves_component_read_failure_diagnostic(self):
        import importlib
        ComponentReadError = importlib.import_module(self.module.__package__ + ".component_ownership").ComponentReadError
        ownership = importlib.import_module(self.module.__package__ + ".model_delete").ownership

        target = self.fixture(("",))[0]
        target.GetElementAdapterType.return_value.GetTypeName.return_value = "WindowDoor_TypeUUID"
        self.adapter_module.BaseElementAdapterParentElementService.GetParentElement = (
            lambda _element: (_ for _ in ()).throw(ComponentReadError(
                "parent", "component_read_unavailable", "RuntimeError")))
        result = ownership(target)
        self.assertEqual(result["status"], "not_checked")
        self.assertIsNone(result["value"])
        self.assertEqual(result["reason"], "component_read_unavailable")
        self.assertEqual(result["diagnostic"], {"stage": "parent", "error_type": "RuntimeError"})
        self.assertNotIn("message", result["diagnostic"])

    def test_delete_descendant_scan_failure_has_its_own_bounded_diagnostic(self):
        import importlib
        ownership = importlib.import_module(self.module.__package__ + ".model_delete").ownership
        target = self.fixture(("",))[0]
        child_service = self.adapter_module.BaseElementAdapterChildElementsService
        calls = [0]

        def get_children(*_args):
            calls[0] += 1
            # Root ownership reads direct children once for its manifest and
            # again during the exact descendant consistency check. Fail only
            # on the latter descendant enumeration.
            if calls[0] <= 2:
                return []
            raise RuntimeError("private descendant read detail")

        child_service.GetChildModelElements = get_children
        result = ownership(target)
        self.assertEqual(result["status"], "not_checked")
        self.assertIsNone(result["value"])
        self.assertEqual(result["reason"], "delete_subtree_unavailable")
        self.assertEqual(result["diagnostic"], {"stage": "deletion_descendants", "error_type": "RuntimeError"})
        self.assertNotIn("private descendant read detail", str(result))

    def test_windowdoor_delete_is_unknown_when_parent_wall_disappears(self):
        wall = self.fixture(("",))[0]
        wall.GetElementAdapterType.return_value.GetTypeName.return_value = "Wall_TypeUUID"
        opening = self.element(2, name="WindowDoor_TypeUUID")
        for method, value in (("IsNull", False), ("IsDeleted", False), ("IsValid", True),
                              ("IsInActiveDocument", True), ("IsInActiveLayer", True),
                              ("IsLabelElement", False)):
            getattr(opening, method).return_value = value
        self.parents[id(opening)] = wall
        self.children[id(wall)] = [opening]
        self.elements = [wall, opening]
        self.base.ElementsSelectService.SelectAllElements.return_value = [wall, opening]
        self.live_elements()

        def delete_parent_and_opening(doc, adapters):
            opening.IsDeleted.return_value = True
            wall.IsDeleted.return_value = True

        self.base.DeleteElements.side_effect = delete_parent_and_opening
        plan = self.preview(predicate=None, native_types=["WindowDoor_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.highlight(plan)
        execution_id = uuid4().hex
        result = self.apply(plan, execution_id)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.base.DeleteElements.assert_called_once()

    def test_partial_cascade_readback_is_unknown_and_never_retries_delete(self):
        slab, aggregate = fixtures.EditOwnershipTests.slab_fixture(self)
        aggregate.GetElementAdapterType.return_value.GetTypeName.return_value = "MultiSlab_TypeUUID"
        self.elements = [slab, aggregate]
        self.live_elements()
        self.base.DeleteElements.side_effect = lambda doc, adapters: aggregate.IsDeleted.__setattr__("return_value", True)
        plan = self.preview(predicate=None, native_types=["MultiSlab_TypeUUID"],
                            changes=[{"target": {"kind": "delete"}}])
        self.highlight(plan)
        execution_id = uuid4().hex
        result = self.apply(plan, execution_id)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.base.DeleteElements.assert_called_once()

    def test_forged_deletion_ownership_is_rejected_at_final_setter(self):
        target = self.fixture(("",))[0]
        plan = self.preview(predicate=None, changes=[{"target": {"kind": "delete"}}])
        forged = plan["changes"][0]
        forged["resource"]["delete_ownership"]["value"]["lineage"] = []
        native = importlib.import_module(self.module.__package__ + ".native_model_edit")
        self.assert_code("target_not_writable", lambda: native.write(self.base, target, forged))
        self.base.DeleteElements.assert_not_called()

    def test_batch_final_boundary_rejects_legacy_adapter_version_before_native_call(self):
        target = self.fixture(("",))[0]
        plan = self.preview(predicate=None, changes=[{"target": {"kind": "delete"}}])
        change = copy.deepcopy(plan["changes"][0])
        change["adapter_version"] = "m3-model-edit-1"
        model_delete = importlib.import_module(self.module.__package__ + ".model_delete")
        self.assert_code("target_not_writable", lambda: model_delete.write_batch(
            self.base, [target], [change], self.coord.GetInputViewDocument()))
        self.base.DeleteElements.assert_not_called()

    def test_final_delete_write_guard_stops_when_budget_expires(self):
        target = self.fixture(("",))[0]
        plan = self.preview(predicate=None, changes=[{"target": {"kind": "delete"}}])
        native = importlib.import_module(self.module.__package__ + ".native_model_edit")
        bridge_error = importlib.import_module(self.module.__package__ + ".transport").BridgeError

        def expired():
            raise bridge_error("scan_limit_exceeded", "Injected final write budget expiry", 409)

        self.assert_code("scan_limit_exceeded", lambda: native.write(
            self.base, target, plan["changes"][0], check=expired))
        self.base.DeleteElements.assert_not_called()

    def test_lost_delete_reply_is_unknown_and_replay_does_not_delete_again(self):
        self.elements = self.fixture(("",))
        target = self.elements[0]
        self.live_elements()
        attempts = []

        def delete_then_lose_reply(doc, adapters):
            attempts.append(adapters[0].GetModelElementUUID())
            adapters[0].IsDeleted.return_value = True
            raise RuntimeError("delete completed but native reply was lost")

        self.base.DeleteElements.side_effect = delete_then_lose_reply
        plan = self.preview(predicate=None, changes=[{"target": {"kind": "delete"}}])
        self.highlight(plan)
        execution_id = uuid4().hex
        result = self.apply(plan, execution_id)
        self.assertEqual(result["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.assertEqual(attempts, [target.GetModelElementUUID()])

        self.base.DeleteElements.reset_mock()
        recovered = self.recover(execution_id)
        self.assertTrue(recovered["read_only"])
        self.assertEqual(recovered["outcomes"][0]["state"], "reconciled")
        self.assertEqual(recovered["recovery"]["observations"][0]["state"], "new_value_observed")
        self.base.DeleteElements.assert_not_called()

    def test_incomplete_fresh_scan_cannot_prove_absence_or_authorize_retry(self):
        self.elements = self.fixture(("",))
        target = self.elements[0]
        attempts = []

        def delete_then_fail_scan(doc, adapters):
            attempts.append(adapters[0].GetModelElementUUID())
            target.IsDeleted.return_value = True
            self.base.ElementsSelectService.SelectAllElements.side_effect = RuntimeError("scan interrupted")

        self.base.DeleteElements.side_effect = delete_then_fail_scan
        plan = self.preview(predicate=None, changes=[{"target": {"kind": "delete"}}])
        self.highlight(plan)
        execution_id = uuid4().hex
        applied = self.apply(plan, execution_id)
        self.assertEqual(applied["outcomes"][0]["state"], "unknown")
        self.assertTrue(self.apply(plan, execution_id)["replayed"])
        self.assertEqual(attempts, [target.GetModelElementUUID()])

        recovered = self.recover(execution_id)
        self.assertTrue(recovered["read_only"])
        self.assertEqual(recovered["outcomes"][0]["state"], "unknown")
        self.assertEqual(attempts, [target.GetModelElementUUID()])

    def test_unavailable_or_passive_file_identity_cannot_prove_deletion(self):
        for signed_file in (0, -101):
            with self.subTest(signed_file=signed_file):
                target = self.fixture(("",))[0]
                def lose_file_identity(doc, adapters):
                    target.GetDrawingfileNumber.return_value = signed_file
                self.base.DeleteElements.reset_mock()
                self.base.DeleteElements.side_effect = lose_file_identity
                plan = self.preview(predicate=None, changes=[{"target": {"kind": "delete"}}])
                self.highlight(plan)
                execution_id = uuid4().hex
                result = self.apply(plan, execution_id)
                self.assertEqual(result["outcomes"][0]["state"], "unknown")
                self.assertTrue(self.apply(plan, execution_id)["replayed"])
                self.base.DeleteElements.assert_called_once()
                recovered = self.recover(execution_id)
                self.assertEqual(recovered["outcomes"][0]["state"], "unknown")
                self.assertTrue(recovered["read_only"])
                self.base.DeleteElements.assert_called_once()

