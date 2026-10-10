"""Shared snapshot selection, read-only workflow boundaries and source conflicts."""
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

import test_model_repair as fixtures


class StandardSelectionTests(unittest.TestCase):
    setUp = fixtures.RepairTests.setUp
    prepare_context = fixtures.RepairTests.prepare_context
    prepare = fixtures.RepairTests.prepare
    adapter = fixtures.RepairTests.adapter
    native = fixtures.RepairTests.native
    element = fixtures.RepairTests.element
    resources = fixtures.RepairTests.resources
    fixture = fixtures.RepairTests.fixture
    assert_code = fixtures.RepairTests.assert_code
    request = fixtures.RepairTests.request
    preview = fixtures.RepairTests.preview
    revalidate = fixtures.RepairTests.revalidate

    def test_selection_and_exceptions_use_one_full_scan_and_excluded_edits_still_conflict(self):
        elements = self.fixture()
        self.base.ElementsSelectService.SelectAllElements.reset_mock()
        plan = self.preview(selection={"where": {"field": "status", "op": "eq", "value": "NWE"}})
        self.base.ElementsSelectService.SelectAllElements.assert_called_once()
        self.assertEqual([c['locator']['mark']['value'] for c in plan['changes']], ['S06'])
        self.assertIn('selection_predicate_false', [e['reason'] for e in plan['exclusions']])
        self.assertEqual(plan['selection_result']['selected_elements'], 1)
        self.assertTrue(plan['evaluation_apply_available'])
        excluded = str(elements[5].GetModelElementUUID())
        plan = self.preview(selection={"where": {"field": "layer_id", "op": "exists"},
                                       "exclude_model_uuids": [excluded]})
        self.assertEqual([c['locator']['mark']['value'] for c in plan['changes']], ['S05'])
        self.assertEqual(plan['selection_result']['excluded_elements'], 1)
        self.assertEqual(plan['counts']['audit_findings'], 5)
        self.assertIn('selection_exception', [e['reason'] for e in plan['exclusions']])
        self.assertEqual(self.revalidate(plan)['state'], 'unchanged')
        elements[5].GetAttributes.return_value = [(20001, 'S06'), (20002, 'EXISTING')]
        self.assertEqual(self.revalidate(plan)['state'], 'conflict')
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_unknown_predicate_survives_negation_and_blocks_plan_readiness(self):
        elements = self.fixture()
        elements[2].GetAttributes.return_value = [(20002, 'NEW')]
        plan = self.preview(selection={"where": {"not": {"field": "mark", "op": "eq", "value": "S06"}}})
        self.assertGreater(plan['selection_result']['predicate_not_checked'], 0)
        self.assertEqual(plan['state'], 'not_checked')
        self.assertFalse(plan['evaluation_apply_available'])

    def test_invalid_selectors_are_validated_before_context_and_absent_exceptions_reject(self):
        self.fixture()
        for selection in ({'where': {'field': 'display_name', 'op': 'exists'}},
                          {'where': {'field': 'layer_id', 'op': 'eq'}},
                          {'where': {'field': 'layer_id', 'op': 'exists'}, 'exclude_model_uuids': [{}]}):
            with self.subTest(selection=selection):
                self.coord.GetInputViewDocument.reset_mock()
                self.assert_code('invalid_payload', lambda: self.preview(selection=selection))
                self.coord.GetInputViewDocument.assert_not_called()
        self.assert_code('finding_stale', lambda: self.preview(selection={
            'where': {'field': 'layer_id', 'op': 'exists'}, 'exclude_model_uuids': [str(uuid4())]}))
        self.assertFalse(self.handler.repair_plans.plans)

    def test_workflow_metadata_is_hashed_immutable_and_cannot_use_legacy_acknowledgement(self):
        self.fixture()
        with tempfile.TemporaryDirectory() as directory:
            self.handler.repair_plans.executor.path = Path(directory)
            workflow = {'kind': 'office_standard_preview', 'standard_id': 'demo',
                        'standard_version': '1.0.0', 'standard_fingerprint': 'a' * 64}
            plan = self.preview(workflow=workflow)
            self.assertEqual(len(plan['changes']), 2)
            self.assertTrue(plan['evaluation_apply_available'])
            plan['workflow']['standard_version'] = '2.0.0'
            saved = self.handler.repair_plans.plans[plan['plan_id']]['plan']
            self.assertEqual(saved['workflow']['standard_version'], '1.0.0')
            self.assert_code('repair_scope_unavailable', lambda: self.handler.handle('/fix-model-issues', {
                'schema_version': 'm3-repair-1', 'action': 'apply', 'plan_id': plan['plan_id'],
                'plan_hash': plan['plan_hash'], 'execution_id': uuid4().hex,
                'acknowledgement': 'disposable_copy_reviewed_two_repairs'}))
            self.assertFalse(list(Path(directory).glob('*.json')))
            self.base.ElementsLayerService.ChangeLayer.assert_not_called()
            self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
