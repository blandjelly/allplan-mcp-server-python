"""Explicit mark proposals, whole-scope collision checks and reviewed eligibility."""
import copy
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError
from allplan_mcp.repair_models import RepairRequest
import test_model_repair as fixtures


class MarkPreviewTests(unittest.TestCase):
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

    def choices(self, elements):
        return [{'rule_id': 'QA-001', 'model_uuid': str(elements[2].GetModelElementUUID()), 'value': 'S03'},
                {'rule_id': 'QA-002', 'model_uuid': str(elements[3].GetModelElementUUID()), 'value': 'S04'}]

    def test_missing_and_one_duplicate_mark_are_explicit_fresh_and_revalidate_without_writes(self):
        elements = self.fixture()
        choices = self.choices(elements)
        self.base.ElementsSelectService.SelectAllElements.reset_mock()
        plan = self.preview(repairs=choices)
        self.base.ElementsSelectService.SelectAllElements.assert_called_once()
        self.assertEqual([(c['field'], c['old_value']['value'], c['new_value']) for c in plan['changes']],
                         [('attribute:20001', '<niezdefiniowany>', 'S03'), ('attribute:20001', 'S02', 'S04')])
        self.assertEqual(plan['state'], 'preview_ready')
        self.assertTrue(plan['evaluation_apply_available'])
        self.assertEqual(plan['mark_validation']['state'], 'validated')
        self.assertEqual(plan['mark_validation']['checked_elements'], 6)
        self.assertEqual(plan['mark_validation']['remaining_duplicate_groups'], 0)
        self.assertEqual(plan['mark_validation']['remaining_missing_marks'], 0)
        self.assertEqual(self.revalidate(plan)['state'], 'unchanged')
        choices[0]['value'] = 'HIDDEN'
        plan['mark_validation']['state'] = 'HIDDEN'
        saved = self.handler.repair_plans.plans[plan['plan_id']]
        self.assertEqual(saved['request']['repairs'][0]['value'], 'S03')
        self.assertEqual(saved['plan']['mark_validation']['state'], 'validated')

    def test_distinct_explicit_targets_can_share_a_unique_mark_rule(self):
        elements = self.fixture()
        choices = [{'rule_id': 'QA-002', 'model_uuid': str(elements[i].GetModelElementUUID()), 'value': value}
                   for i, value in [(1, 'S08'), (3, 'S09')]]
        plan = self.preview(repairs=choices)
        self.assertEqual({c['new_value'] for c in plan['changes']}, {'S08', 'S09'})
        self.assertEqual(plan['mark_validation']['remaining_duplicate_groups'], 0)
        self.assertEqual(plan['mark_validation']['remaining_missing_marks'], 1)
        public = self.request(repairs=choices)
        public.pop('schema_version'); public['audit'].pop('schema_version')
        self.assertEqual(len(TypeAdapter(RepairRequest).validate_python(public).repairs), 2)

    def test_collision_with_an_excluded_peer_and_between_proposals_blocks_readiness(self):
        elements = self.fixture()
        choices = self.choices(elements)
        choices[0]['value'] = 'S06'
        plan = self.preview(repairs=choices, selection={'where': {'field': 'layer_id', 'op': 'exists'},
                         'exclude_model_uuids': [str(elements[5].GetModelElementUUID())]})
        self.assertEqual(plan['state'], 'conflict')
        self.assertFalse(plan['evaluation_apply_available'])
        collision = plan['mark_validation']['collisions'][0]
        self.assertEqual(collision['normalized_value'], 'S06')
        self.assertEqual({r['model_uuid'] for r in collision['refs']},
                         {str(elements[i].GetModelElementUUID()) for i in (2, 5)})
        choices = self.choices(elements)
        choices[1]['value'] = 'S03'
        plan = self.preview(repairs=choices)
        self.assertEqual(plan['mark_validation']['collision_groups'], 1)
        self.assertEqual(plan['state'], 'conflict')

    def test_collision_normalization_uses_the_explicit_audit_policy(self):
        elements = self.fixture()
        request = self.request(repairs=self.choices(elements))
        request['audit']['profile']['string_policies']['mark']['case_sensitive'] = False
        request['repairs'][0]['value'] = ' s06 '
        plan = self.handler.handle('/fix-model-issues', request)
        self.assertEqual(plan['state'], 'conflict')
        self.assertEqual(plan['mark_validation']['collisions'][0]['normalized_value'], 's06')

    def test_invalid_mark_choices_reject_in_public_and_host_before_context(self):
        elements = self.fixture()
        valid = self.request(repairs=self.choices(elements))
        bad = []
        for value in ('', ' ', '<niezdefiniowany>', ' <niezdefiniowany> ', 'S03\n', 'S\x7f03'):
            request = copy.deepcopy(valid); request['repairs'][0]['value'] = value; bad.append(request)
        request = copy.deepcopy(valid); del request['repairs'][0]['model_uuid']; bad.append(request)
        request = copy.deepcopy(valid); request['repairs'][0]['model_uuid'] = 'NOT-A-UUID'; bad.append(request)
        request = copy.deepcopy(valid); request['repairs'][1]['model_uuid'] = request['repairs'][0]['model_uuid']; bad.append(request)
        request = copy.deepcopy(valid); request['audit']['rule_ids'] = ['QA-001']; request['repairs'] = request['repairs'][:1]; bad.append(request)
        request = self.request(); request['repairs'][0]['model_uuid'] = None; bad.append(request)
        for request in bad:
            with self.subTest(request=request['repairs']):
                self.coord.GetInputViewDocument.reset_mock()
                self.assert_code('invalid_payload', lambda: self.handler.handle('/fix-model-issues', request))
                self.coord.GetInputViewDocument.assert_not_called()
                public = copy.deepcopy(request); public.pop('schema_version'); public['audit'].pop('schema_version')
                with self.assertRaises(ValidationError): TypeAdapter(RepairRequest).validate_python(public)
        self.assertFalse(self.handler.repair_plans.plans)

    def test_absent_compliant_or_wrong_rule_targets_are_stale_not_ignored(self):
        elements = self.fixture()
        for target in (str(uuid4()), str(elements[0].GetModelElementUUID()), str(elements[1].GetModelElementUUID())):
            choices = self.choices(elements); choices[0]['model_uuid'] = target
            self.assert_code('finding_stale', lambda: self.preview(repairs=choices))
        self.assertFalse(self.handler.repair_plans.plans)

    def test_unchecked_peer_blocks_validation_and_excluded_peer_edits_conflict(self):
        elements = self.fixture()
        choices = self.choices(elements)
        selection = {'where': {'field': 'layer_id', 'op': 'exists'},
                     'exclude_model_uuids': [str(elements[5].GetModelElementUUID())]}
        plan = self.preview(repairs=choices, selection=selection)
        elements[5].GetAttributes.return_value = [(20001, 'OTHER'), (20002, 'NWE')]
        self.assertEqual(self.revalidate(plan)['state'], 'conflict')
        elements[5].GetAttributes.side_effect = RuntimeError('Unknown excluded mark')
        blocked = self.preview(repairs=choices, selection=selection)
        self.assertEqual(blocked['state'], 'not_checked')
        self.assertEqual(blocked['mark_validation']['state'], 'not_checked')
        self.assertGreater(blocked['mark_validation']['not_checked_elements'], 0)
        self.assertFalse(blocked['evaluation_apply_available'])

    def test_mark_metadata_keeps_legacy_ack_blocked_when_only_layer_status_proposals_remain(self):
        elements = self.fixture()
        audit = self.handler.handle('/model-audit', self.request()['audit'])
        ids = [f['finding_id'] for f in audit['findings'] if f['rule_id'] in {'QA-003', 'QA-004'}]
        repairs = self.request()['repairs'] + self.choices(elements)
        with tempfile.TemporaryDirectory() as directory:
            self.handler.repair_plans.executor.path = Path(directory)
            plan = self.preview(repairs=repairs, finding_ids=ids)
            self.assertEqual(plan['counts'], {'changes': 2, 'excluded_findings': 3, 'audit_findings': 5})
            self.assertTrue(plan['evaluation_apply_available'])
            self.assert_code('repair_scope_unavailable', lambda: self.handler.handle('/fix-model-issues', {
                'schema_version': 'm3-repair-1', 'action': 'apply', 'plan_id': plan['plan_id'],
                'plan_hash': plan['plan_hash'], 'execution_id': uuid4().hex,
                'acknowledgement': 'disposable_copy_reviewed_two_repairs'}))
            self.assertFalse(list(Path(directory).glob('*.json')))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
