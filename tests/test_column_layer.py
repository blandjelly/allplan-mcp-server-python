"""M4 criterion edits exercised through the real shared executor with native fakes."""
import copy
import importlib
import json
import tempfile
import unittest
import weakref
from pathlib import Path
from uuid import uuid4

import test_model_properties as fixtures


class ColumnLayerTests(unittest.TestCase):
    setUp = fixtures.PropertyTests.setUp
    prepare_context = fixtures.PropertyTests.prepare_context
    prepare = fixtures.PropertyTests.prepare
    adapter = fixtures.PropertyTests.adapter
    native = fixtures.PropertyTests.native
    element = fixtures.PropertyTests.element
    assert_code = fixtures.PropertyTests.assert_code

    def fixture(self, values=("", "R60", "<niezdefiniowany>")):
        elements = [self.element(i, attrs=[(83, v)]) for i, v in enumerate(values, 1)]
        fixtures.PropertyTests.fixture(self, elements)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.plans = self.handler.repair_plans
        self.plans.trace_path = Path(self.directory.name) / 'probe.jsonl'
        self.plans.executor.path = Path(self.directory.name) / 'repairs'
        for e in elements:
            for method, value in (("IsDeleted", False), ("IsValid", True), ("IsInActiveDocument", True),
                                  ("IsInActiveLayer", True), ("IsInMacro", True), ("IsLabelElement", False)):
                getattr(e, method).return_value = value
        def layer(targets, name):
            self.assertEqual(name, "W1")
            targets[0].GetCommonProperties.return_value.Layer = 8
        self.base.ElementsLayerService.ChangeLayer.side_effect = layer
        return elements

    def call(self, **request):
        result = self.handler.handle('/column-layer', {'schema_version': 'm4-column-layer-1', **request})
        json.dumps(result, allow_nan=False)
        for method in ('GetEnumValues', 'GetAttributeType', 'GetAttributeUnit', 'GetAttributeControlType'):
            getattr(self.base.AttributeService, method).assert_not_called()
        self.base.ElementsAttributeService.ChangeAttributes.assert_not_called()
        return result

    def preview(self, **changes):
        return self.call(**{'action': 'preview', 'drawing_file': 101, **changes})

    def plan_request(self, plan):
        return {'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash']}

    def highlight(self, plan):
        return self.call(action='highlight', **self.plan_request(plan))

    def apply(self, plan, **changes):
        return self.call(action='apply', **self.plan_request(plan), execution_id=uuid4().hex,
                         acknowledgement='disposable_copy_reviewed_plan', **changes)

    def test_full_workflow_highlights_exact_changing_targets_apply_replay_and_no_op(self):
        elements = self.fixture()
        plan = self.preview()
        self.assertEqual(plan['counts']['changes'], 2)
        self.assertNotIn('audit', self.plans.plans[plan['plan_id']]['request'])
        self.assertEqual(self.highlight(plan)['state'], 'submitted')
        sent = self.module.AllplanIFW.HighlightService.HighlightElements.call_args.args[0]
        self.assertEqual([id(e) for e in sent], [id(elements[0]), id(elements[2])])
        request = dict(action='apply', **self.plan_request(plan), execution_id=uuid4().hex, acknowledgement='disposable_copy_reviewed_plan')
        result = self.call(**request)
        self.assertEqual(result['state'], 'completed')
        self.assertTrue(result['audited_fields_match_plan'])
        self.assertIn('criteria_after', result)
        self.assertNotIn('audit_request', result)
        self.assertEqual(self.base.ElementsLayerService.ChangeLayer.call_count, 2)
        self.assertTrue(self.call(**request)['replayed'])
        next_plan = self.preview()
        self.assertEqual(next_plan['state'], 'no_op')
        self.assertEqual(next_plan['counts']['no_op'], 2)
        self.assertFalse(next_plan['changes'])

    def test_value_states_are_distinct_and_omission_is_unknown_not_a_write_target(self):
        elements = self.fixture((None, '', '  ', '<niezdefiniowany>', 'R60', 0, 'x'))
        elements[-1].GetAttributes.return_value = []
        plan = self.preview()
        self.assertEqual([c['value_state'] for c in plan['criteria']['checks']],
                         ['null', 'empty', 'empty', 'undefined', 'present', 'unsupported_value_type', 'absent_from_readall_unknown'])
        self.assertFalse(plan['evaluation_apply_available'])
        self.assert_code('repair_scope_unavailable', lambda: self.highlight(plan))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_missing_or_ambiguous_names_fail_before_scan_or_UI(self):
        self.fixture()
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: -1
        self.assert_code('property_binding_unavailable', self.preview)
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: {'Odporność ogniowa': 83, 'Fire resistance': 84}[name]
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: {83: 'Odporność ogniowa', 84: 'Fire resistance'}[ident]
        self.assert_code('property_binding_unavailable', self.preview)
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_apply_requires_highlight_and_rechecks_full_source_including_nonmatch(self):
        elements = self.fixture()
        plan = self.preview()
        self.assert_code('presentation_required', lambda: self.apply(plan))
        self.highlight(plan)
        elements[1].GetAttributes.return_value = [(83, '')]
        self.assert_code('repair_conflict', lambda: self.apply(plan))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_new_column_resource_changes_and_expiry_conflict_before_write(self):
        for mutation in ('new_column', 'resource', 'expiry'):
            with self.subTest(mutation=mutation):
                elements = self.fixture()
                plan = self.preview()
                self.highlight(plan)
                if mutation == 'new_column':
                    self.base.ElementsSelectService.SelectAllElements.return_value.append(self.element(10, attrs=[(83, '')]))
                elif mutation == 'resource':
                    self.base.LayerService.GetIDByShortName.side_effect = lambda name, doc: 9
                    self.base.LayerService.GetShortNameByID.side_effect = lambda ident, doc: 'W1'
                else:
                    self.plans.plans[plan['plan_id']]['created'] -= 301
                self.assert_code('plan_expired' if mutation == 'expiry' else 'repair_conflict', lambda: self.apply(plan))
                self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_exception_and_existing_W1_are_not_highlighted_or_written(self):
        elements = self.fixture(('', '', ''))
        elements[1].GetCommonProperties.return_value.Layer = 8
        plan = self.preview(exclude_model_uuids=[elements[0].GetModelElementUUID()])
        self.assertEqual(plan['counts']['changes'], 1)
        self.highlight(plan)
        sent = self.module.AllplanIFW.HighlightService.HighlightElements.call_args.args[0]
        self.assertEqual([id(e) for e in sent], [id(elements[2])])
        self.assertEqual(self.apply(plan)['state'], 'completed')
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()

    def test_unwritable_later_target_prevents_all_setters(self):
        elements = self.fixture()
        plan = self.preview()
        self.highlight(plan)
        elements[2].IsInActiveLayer.return_value = False
        self.assert_code('target_not_writable', lambda: self.apply(plan))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_native_failure_journal_unknown_recovery_restart_and_undo_do_not_repeat(self):
        elements = self.fixture()
        plan = self.preview()
        self.highlight(plan)
        def crash(targets, name):
            targets[0].GetCommonProperties.return_value.Layer = 8
            raise RuntimeError('lost native reply')
        self.base.ElementsLayerService.ChangeLayer.side_effect = crash
        request = dict(action='apply', **self.plan_request(plan), execution_id=uuid4().hex, acknowledgement='disposable_copy_reviewed_plan')
        result = self.call(**request)
        self.assertEqual(result['outcomes'][0]['state'], 'unknown')
        self.assertEqual(result['outcomes'][1]['state'], 'skipped')
        cls = importlib.import_module('test_allplan_host.model_repair').RepairPlanService
        self.handler.repair_plans = cls(self.handler.model_queries, self.plans.executor.path)
        self.handler.repair_plans.trace_path = self.plans.trace_path
        self.assertTrue(self.call(**request)['replayed'])
        result = self.call(action='recover', execution_id=request['execution_id'])
        self.assertEqual(result['recovery']['observations'][0]['state'], 'new_value_observed')
        elements[0].GetCommonProperties.return_value.Layer = 7
        result = self.call(action='recover', execution_id=request['execution_id'])
        self.assertEqual(result['recovery']['observations'][0]['state'], 'old_value_observed')
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()

    def test_native_container_lives_through_target_reads_and_setter(self):
        elements = self.fixture()
        class Owner(list):
            pass
        owners = []
        def select(doc):
            owner = Owner(elements)
            owners.append(weakref.ref(owner))
            return owner
        self.base.ElementsSelectService.SelectAllElements.side_effect = select
        def layer(targets, name):
            self.assertIsNotNone(owners[-1]())
            targets[0].GetCommonProperties.return_value.Layer = 8
        self.base.ElementsLayerService.ChangeLayer.side_effect = layer
        plan = self.preview()
        self.highlight(plan)
        self.assertEqual(self.apply(plan)['state'], 'completed')
        self.assertTrue(all(o() is None for o in owners))

    def test_unwritable_trace_or_UI_failure_prevents_apply_and_native_retries(self):
        self.fixture()
        self.plans.trace_path = Path(self.directory.name)
        self.assert_code('probe_trace_unavailable', self.preview)
        self.base.AttributeService.GetAttributeID.assert_not_called()
        self.plans.trace_path = Path(self.directory.name) / 'trace.jsonl'
        plan = self.preview()
        self.module.AllplanIFW.HighlightService.HighlightElements.side_effect = RuntimeError('UI failed')
        self.assertEqual(self.highlight(plan)['state'], 'unknown')
        self.assert_code('presentation_required', lambda: self.apply(plan))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_over_limit_and_passive_scope_are_not_applicable(self):
        self.fixture([''] * 33)
        self.assertFalse(self.preview()['evaluation_apply_available'])
        self.assertFalse(self.preview(drawing_file=102)['evaluation_apply_available'])

    def test_invalid_payload_rejected_before_any_native_access(self):
        self.assert_code('invalid_payload', lambda: self.call(action='preview', drawing_file=True))
        self.assert_code('invalid_payload', lambda: self.call(action='preview', drawing_file=101, attribute_names=[]))
        self.coord.GetInputViewDocument.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_noncolumns_never_receive_new_attribute_or_geometry_reads(self):
        elements = self.fixture()
        wall = self.element(10, name='Wall_TypeUUID')
        wall.GetAttributes.side_effect = AssertionError('Unaccepted wall property access')
        wall.GetModelGeometry.side_effect = AssertionError('Unaccepted wall geometry access')
        self.base.ElementsSelectService.SelectAllElements.return_value.append(wall)
        plan = self.preview()
        self.highlight(plan)
        self.assertEqual(self.apply(plan)['state'], 'completed')
        wall.GetAttributes.assert_not_called()
        wall.GetModelGeometry.assert_not_called()

    def test_full_large_result_highlights_only_plan_targets_and_clear_invalidates_submission(self):
        elements = self.fixture(['R60'] * 201 + ['', ''])
        plan = self.preview()
        result = self.highlight(plan)
        self.assertEqual(result['counts']['submitted_model_identities'], 2)
        self.handler.handle('/model-selection', {'schema_version': 'm4-selection-1', 'action': 'clear_highlight'})
        self.assert_code('presentation_required', lambda: self.apply(plan))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
