"""Numbering and mark execution against stateful native fakes, not native acceptance."""
import copy
import importlib
import unittest

from allplan_mcp.office_standard import load_office_standard
import test_supported_execution as supported


class MarkExecutionTests(unittest.TestCase):
    setUp = supported.SupportedExecutionTests.setUp
    prepare_context = supported.SupportedExecutionTests.prepare_context
    prepare = supported.SupportedExecutionTests.prepare
    adapter = supported.SupportedExecutionTests.adapter
    native = supported.SupportedExecutionTests.native
    element = supported.SupportedExecutionTests.element
    resources = supported.SupportedExecutionTests.resources
    fixture = supported.SupportedExecutionTests.fixture
    assert_code = supported.SupportedExecutionTests.assert_code
    request = supported.SupportedExecutionTests.request
    preview = supported.SupportedExecutionTests.preview
    writable_fixture = supported.SupportedExecutionTests.writable_fixture
    apply_request = supported.SupportedExecutionTests.apply_request
    apply = supported.SupportedExecutionTests.apply
    call = supported.SupportedExecutionTests.call
    recover = supported.SupportedExecutionTests.recover

    def marks_fixture(self):
        elements = self.writable_fixture()
        def attribute(data, targets, undefined, deleted):
            self.assertFalse(undefined)
            self.assertFalse(deleted)
            current = dict(targets[0].GetAttributes.return_value)
            self.assertIn(data[0][0], current)
            current.update(data)
            targets[0].GetAttributes.return_value = list(current.items())
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = attribute
        return elements

    def numbering_request(self, **overrides):
        standard = load_office_standard('native-model-qa-demo-mark-numbering')
        return self.request(repairs=[], numbering=standard['numbering'], workflow={
            'kind': 'office_standard_preview', **{k: standard[k] for k in
                ('standard_id', 'standard_version', 'standard_fingerprint')}}, **overrides)

    def test_numbering_is_stable_across_adapter_order_preserves_valid_and_applies_once(self):
        elements = self.marks_fixture()
        self.base.ElementsSelectService.SelectAllElements.reset_mock()
        plan = self.call(self.numbering_request())
        self.base.ElementsSelectService.SelectAllElements.assert_called_once()
        expected = {str(elements[2].GetModelElementUUID()): 'S03', str(elements[3].GetModelElementUUID()): 'S04'}
        self.assertEqual({c['ref']['model_uuid']: c['new_value'] for c in plan['changes']}, expected)
        self.assertTrue(plan['evaluation_apply_available'])
        self.assertEqual(plan['mark_validation']['remaining_duplicate_groups'], 0)
        self.assertEqual(plan['mark_validation']['remaining_missing_marks'], 0)
        self.base.ElementsSelectService.SelectAllElements.return_value = list(reversed(elements))
        second = self.call(self.numbering_request())
        self.assertEqual(second['changes'], plan['changes'])
        self.assertEqual(second['numbering'], plan['numbering'])
        request = self.apply(second, workflow_kind='office_standard_preview')
        result = self.call(request)
        self.assertEqual(result['state'], 'completed')
        self.assertTrue(result['audited_fields_match_plan'])
        self.assertEqual(result['audit_after']['counts']['findings'], 2)
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 2)
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        service = importlib.import_module('test_allplan_host.model_repair').RepairPlanService
        self.handler.repair_plans = service(self.handler.model_queries, self.directory.name)
        self.assertTrue(self.call(request)['replayed'])
        self.assertEqual([o['state'] for o in self.recover(request)['recovery']['observations']], ['new_value_observed'] * 2)
        noop = self.call(self.numbering_request())
        self.assertEqual(noop['changes'], [])
        self.assertFalse(noop['evaluation_apply_available'])
        self.assertEqual(self.base.ElementsAttributeService.ChangeAttributes.call_count, 2)

    def test_explicit_mark_assignment_reuses_readback_and_exact_replay_after_undo(self):
        elements = self.marks_fixture()
        plan = self.preview(repairs=[{'rule_id': 'QA-001', 'model_uuid': str(elements[2].GetModelElementUUID()), 'value': 'S03'}])
        request = self.apply(plan)
        self.assertEqual(self.call(request)['state'], 'completed')
        elements[2].GetAttributes.return_value = [(20001, '<niezdefiniowany>'), (20002, 'NEW')]
        self.assertTrue(self.call(request)['replayed'])
        self.assertEqual(self.recover(request)['recovery']['observations'][0]['state'], 'old_value_observed')
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()

    def test_excluded_duplicate_is_keeper_and_all_peers_reserve_normalized_numbers(self):
        elements = self.marks_fixture()
        elements[4].GetAttributes.return_value = [(20001, ' s03 '), (20002, 'NEW')]
        request = self.numbering_request(selection={'where': {'field': 'layer_id', 'op': 'exists'},
            'exclude_model_uuids': [str(elements[3].GetModelElementUUID())]})
        request['audit']['profile']['string_policies']['mark']['case_sensitive'] = False
        plan = self.call(request)
        self.assertEqual({c['ref']['model_uuid']: c['new_value'] for c in plan['changes']},
                         {str(elements[1].GetModelElementUUID()): 'S04', str(elements[2].GetModelElementUUID()): 'S05'})
        self.assertEqual(plan['numbering']['preserved_duplicate_keepers'][0]['model_uuid'], str(elements[3].GetModelElementUUID()))
        elements[3].GetAttributes.return_value = [(20001, 'OTHER'), (20002, 'NEW')]
        self.assert_code('repair_conflict', lambda: self.call(self.apply(plan)))
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_collisions_unknown_and_absent_attribute_cannot_start_setters(self):
        elements = self.marks_fixture()
        collision = self.preview(repairs=[{'rule_id': 'QA-001', 'model_uuid': str(elements[2].GetModelElementUUID()), 'value': 'S06'}])
        self.assertFalse(collision['evaluation_apply_available'])
        self.assert_code('repair_scope_unavailable', lambda: self.call(self.apply(collision)))
        elements[0].GetAttributes.side_effect = RuntimeError('unknown peer')
        unknown = self.call(self.numbering_request())
        self.assertEqual(unknown['state'], 'not_checked')
        self.assertFalse(unknown['evaluation_apply_available'])
        elements[0].GetAttributes.side_effect = None
        elements[2].GetAttributes.return_value = [(20002, 'NEW')]
        absent = self.call(self.numbering_request())
        self.assertEqual(absent['numbering']['reason'], 'existing_string_mark_required')
        self.assertFalse(absent['evaluation_apply_available'])
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_changed_definition_or_missing_rules_reject_before_native_context(self):
        self.marks_fixture()
        valid = self.numbering_request()
        for change in ('prefix', 'boolean', 'rules', 'workflow', 'explicit'):
            request = copy.deepcopy(valid)
            if change == 'prefix': request['numbering']['prefix'] = 'X'
            elif change == 'boolean': request['numbering']['start'] = True
            elif change == 'rules': request['audit']['rule_ids'] = ['QA-001']
            elif change == 'workflow': request['workflow']['standard_version'] = '2.0.0'
            else: request['repairs'] = [{'rule_id': 'QA-001', 'model_uuid': str(self.fixture()[2].GetModelElementUUID()), 'value': 'S03'}]
            self.coord.GetInputViewDocument.reset_mock()
            self.assert_code('invalid_payload', lambda: self.call(request))
            self.coord.GetInputViewDocument.assert_not_called()

    def test_mark_failure_stops_remaining_targets_and_recovery_does_not_resume(self):
        self.marks_fixture()
        plan = self.call(self.numbering_request())
        request = self.apply(plan)
        setter = self.base.ElementsAttributeService.ChangeAttributes.side_effect
        def lost_readback(*args):
            setter(*args)
            raise RuntimeError('reply lost after mark setter')
        self.base.ElementsAttributeService.ChangeAttributes.side_effect = lost_readback
        result = self.call(request)
        self.assertEqual([o['state'] for o in result['outcomes']], ['unknown', 'skipped'])
        self.assertTrue(self.call(request)['replayed'])
        recovery = self.recover(request)
        self.assertEqual([o['state'] for o in recovery['recovery']['observations']], ['new_value_observed', 'old_value_observed'])
        self.base.ElementsAttributeService.ChangeAttributes.assert_called_once()
