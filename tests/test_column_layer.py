"""M4 criterion edits exercised through the real shared executor with native fakes."""
import importlib
import json
import tempfile
import unittest
import weakref
from pathlib import Path
from uuid import uuid4

import test_m1_completion as fixtures


class ColumnLayerTests(unittest.TestCase):
    setUp = fixtures.M1CompletionTests.setUp
    prepare_context = fixtures.M1CompletionTests.prepare_context
    prepare = fixtures.M1CompletionTests.prepare
    adapter = fixtures.M1CompletionTests.adapter
    native = fixtures.M1CompletionTests.native
    element = fixtures.M1CompletionTests.element
    assert_code = fixtures.M1CompletionTests.assert_code

    def fixture(self, values=("", "F60", "<niezdefiniowany>")):
        elements = [self.element(i, attrs=[(935, v)]) for i, v in enumerate(values, 1)]
        self.native(elements)
        self.attribute_catalog({935: "Klasa odporności ogniowej", 1398: "Odporność ogniowa"})
        self.base.LayerService.GetIDByShortName.side_effect = lambda name, doc: {"COL": 7, "W1": 8}.get(name, -1)
        self.base.LayerService.GetShortNameByID.side_effect = lambda ident, doc: {7: "COL", 8: "W1"}[ident]
        self.base.LayerService.GetNameByID.side_effect = lambda ident, doc: {7: "Columns", 8: "W1"}[ident]
        self.adapter_module.BaseElementAdapterList = list
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

    def attribute_catalog(self, names):
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: next(
            (ident for ident, actual in names.items() if actual == name), -1)
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: names[ident]

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

    def test_six_columns_use_classification_when_legacy_attribute_is_omitted(self):
        elements = self.fixture(('', 'F30', 'F60', '  ', 'F90', 'F120'))
        plan = self.preview()
        self.assertEqual(plan['criteria']['binding']['attribute'],
                         {'attribute_id': 935, 'name': 'Klasa odporności ogniowej'})
        self.assertEqual(plan['counts']['columns'], 6)
        self.assertEqual([c['decision'] for c in plan['criteria']['checks']],
                         ['change', 'nonmatching', 'nonmatching', 'change', 'nonmatching', 'nonmatching'])
        targets = [elements[0], elements[3]]
        self.assertEqual([c['ref']['model_uuid'] for c in plan['changes']],
                         [e.GetModelElementUUID() for e in targets])
        self.highlight(plan)
        sent = self.module.AllplanIFW.HighlightService.HighlightElements.call_args.args[0]
        self.assertEqual([id(e) for e in sent], [id(e) for e in targets])
        self.assertEqual(self.apply(plan)['state'], 'completed')
        calls = self.base.ElementsLayerService.ChangeLayer.call_args_list
        self.assertEqual([id(call.args[0][0]) for call in calls], [id(e) for e in targets])
        self.assertEqual([e.GetAttributes.return_value for e in elements],
                         [[(935, v)] for v in ('', 'F30', 'F60', '  ', 'F90', 'F120')])

    def test_legacy_attribute_values_cannot_change_classification_matches(self):
        elements = self.fixture(('', 'F30'))
        elements[0].GetAttributes.return_value.append((1398, 'F30'))
        elements[1].GetAttributes.return_value.append((1398, ''))
        plan = self.preview()
        self.assertEqual([c['decision'] for c in plan['criteria']['checks']], ['change', 'nonmatching'])
        self.highlight(plan)
        self.assertEqual(self.apply(plan)['state'], 'completed')
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()
        self.assertIs(self.base.ElementsLayerService.ChangeLayer.call_args.args[0][0], elements[0])

    def test_only_legacy_catalog_fails_before_scan_ui_or_writes(self):
        self.fixture()
        self.attribute_catalog({1398: 'Odporność ogniowa'})
        self.assert_code('property_binding_unavailable', self.preview)
        self.assertEqual([call.args[1] for call in self.base.AttributeService.GetAttributeID.call_args_list],
                         ['Klasa odporności ogniowej', 'Fire resistance classification'])
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        self.module.AllplanIFW.HighlightService.CancelAllHighlightedElements.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_english_classification_name_resolves_by_exact_round_trip(self):
        self.fixture()
        self.attribute_catalog({935: 'Fire resistance classification', 1398: 'Fire resistance'})
        plan = self.preview()
        self.assertEqual(plan['criteria']['binding']['attribute'],
                         {'attribute_id': 935, 'name': 'Fire resistance classification'})
        self.assertEqual(plan['counts']['changes'], 2)
        self.highlight(plan)
        self.assertEqual(self.apply(plan)['state'], 'completed')

    def test_explicit_custom_name_binds_catalog_id_without_assuming_935(self):
        elements = self.fixture(('', 'F30'))
        self.attribute_catalog({935: 'Klasa odporności ogniowej', 20017: 'Project classification'})
        elements[0].GetAttributes.return_value = [(935, 'F60'), (20017, '')]
        elements[1].GetAttributes.return_value = [(935, ''), (20017, 'F30')]
        plan = self.preview(attribute_names=['Project classification'])
        self.assertEqual(plan['criteria']['binding']['attribute'],
                         {'attribute_id': 20017, 'name': 'Project classification'})
        self.assertEqual([call.args[1] for call in self.base.AttributeService.GetAttributeID.call_args_list],
                         ['Project classification'])
        self.assertEqual([c['decision'] for c in plan['criteria']['checks']], ['change', 'nonmatching'])
        self.highlight(plan)
        self.assertEqual(self.apply(plan)['state'], 'completed')
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()
        self.assertIs(self.base.ElementsLayerService.ChangeLayer.call_args.args[0][0], elements[0])

    def test_missing_classification_stays_unknown_even_when_legacy_field_is_blank(self):
        elements = self.fixture(('F30',))
        elements[0].GetAttributes.return_value = [(1398, '')]
        plan = self.preview()
        self.assertEqual(plan['criteria']['checks'][0]['value_state'], 'absent_from_readall_unknown')
        self.assertEqual(plan['criteria']['checks'][0]['decision'], 'unknown')
        self.assertEqual(plan['changes'], [])
        self.assertFalse(plan['evaluation_apply_available'])
        self.assert_code('repair_scope_unavailable', lambda: self.highlight(plan))
        self.assert_code('presentation_required', lambda: self.apply(plan))
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_value_states_are_distinct_and_omission_is_unknown_not_a_write_target(self):
        elements = self.fixture((None, '', '  ', '<niezdefiniowany>', 'F60', 0, 'x'))
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
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: {'Klasa odporności ogniowej': 935, 'Fire resistance classification': 936}[name]
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: {935: 'Klasa odporności ogniowej', 936: 'Fire resistance classification'}[ident]
        self.assert_code('property_binding_unavailable', self.preview)
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_classification_name_round_trip_mismatch_never_scans_or_writes(self):
        self.fixture()
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: 'Odporność ogniowa'
        self.assert_code('property_binding_unavailable', self.preview)
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_apply_requires_highlight_and_rechecks_full_source_including_nonmatch(self):
        elements = self.fixture()
        plan = self.preview()
        self.assert_code('presentation_required', lambda: self.apply(plan))
        self.highlight(plan)
        elements[1].GetAttributes.return_value = [(935, '')]
        self.assert_code('repair_conflict', lambda: self.apply(plan))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_new_column_resource_changes_and_expiry_conflict_before_write(self):
        for mutation in ('new_column', 'resource', 'expiry'):
            with self.subTest(mutation=mutation):
                elements = self.fixture()
                plan = self.preview()
                self.highlight(plan)
                if mutation == 'new_column':
                    self.base.ElementsSelectService.SelectAllElements.return_value.append(self.element(10, attrs=[(935, '')]))
                elif mutation == 'resource':
                    self.base.LayerService.GetIDByShortName.side_effect = lambda name, doc: 9
                    self.base.LayerService.GetShortNameByID.side_effect = lambda ident, doc: 'W1'
                else:
                    self.plans.plans[plan['plan_id']]['created'] -= 301
                self.assert_code('plan_expired' if mutation == 'expiry' else 'repair_conflict', lambda: self.apply(plan))
                self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_exception_is_excluded_but_existing_W1_matches_without_write(self):
        elements = self.fixture(('', '', ''))
        elements[1].GetCommonProperties.return_value.Layer = 8
        plan = self.preview(exclude_model_uuids=[elements[0].GetModelElementUUID()])
        self.assertEqual(plan['counts']['changes'], 1)
        self.assertEqual(plan['counts']['highlight_targets'], 2)
        self.highlight(plan)
        sent = self.module.AllplanIFW.HighlightService.HighlightElements.call_args.args[0]
        self.assertEqual([id(e) for e in sent], [id(elements[1]), id(elements[2])])
        self.assertEqual(self.apply(plan)['state'], 'completed')
        self.base.ElementsLayerService.ChangeLayer.assert_called_once()
        self.assertIs(self.base.ElementsLayerService.ChangeLayer.call_args.args[0][0], elements[2])

    def test_owner_six_columns_highlight_all_missing_but_write_only_two_then_no_op(self):
        values = ('<niezdefiniowany>', 'F120', 'F120', 'F120', '<niezdefiniowany>', '<niezdefiniowany>')
        elements = self.fixture(values)
        elements[0].GetCommonProperties.return_value.Layer = 8
        plan = self.preview()
        targets = [elements[i] for i in (0, 4, 5)]
        self.assertEqual(plan['counts']['highlight_targets'], 3)
        self.assertEqual(plan['counts']['changes'], 2)
        self.assertEqual(plan['counts']['no_op'], 1)
        self.assertEqual(plan['highlight_targets'], [c['ref'] for c in plan['criteria']['checks']
                                                   if c['decision'] in {'change', 'no_op'}])
        self.assertEqual(self.highlight(plan)['counts']['submitted_model_identities'], 3)
        sent = self.module.AllplanIFW.HighlightService.HighlightElements.call_args.args[0]
        self.assertEqual([id(e) for e in sent], [id(e) for e in targets])
        self.assertEqual(self.apply(plan)['state'], 'completed')
        calls = self.base.ElementsLayerService.ChangeLayer.call_args_list
        self.assertEqual([id(c.args[0][0]) for c in calls], [id(elements[4]), id(elements[5])])
        next_plan = self.preview()
        self.assertEqual(next_plan['state'], 'no_op')
        self.assertEqual(next_plan['changes'], [])
        self.assertFalse(next_plan['evaluation_apply_available'])
        self.assertTrue(next_plan['evaluation_highlight_available'])
        self.assertEqual(self.highlight(next_plan)['counts']['submitted_model_identities'], 3)
        self.assert_code('repair_scope_unavailable', lambda: self.apply(next_plan))
        self.assertEqual(self.base.ElementsLayerService.ChangeLayer.call_count, 2)
        self.assertEqual([e.GetAttributes.return_value for e in elements], [[(935, v)] for v in values])

    def test_all_no_op_highlight_rejects_changed_criterion_before_UI(self):
        elements = self.fixture(('',))
        elements[0].GetCommonProperties.return_value.Layer = 8
        plan = self.preview()
        elements[0].GetAttributes.return_value = [(935, 'F120')]
        self.assert_code('repair_conflict', lambda: self.highlight(plan))
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

    def test_no_matches_clear_old_highlights_without_setters(self):
        self.fixture(('F120',))
        plan = self.preview()
        self.assertEqual(plan['highlight_targets'], [])
        self.assertEqual(self.highlight(plan)['counts']['submitted_model_identities'], 0)
        self.module.AllplanIFW.HighlightService.CancelAllHighlightedElements.assert_called_once()
        self.module.AllplanIFW.HighlightService.HighlightElements.assert_not_called()
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()

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
        elements = self.fixture(['F60'] * 201 + ['', ''])
        plan = self.preview()
        result = self.highlight(plan)
        self.assertEqual(result['counts']['submitted_model_identities'], 2)
        self.handler.handle('/model-selection', {'schema_version': 'm4-selection-1', 'action': 'clear_highlight'})
        self.assert_code('presentation_required', lambda: self.apply(plan))
        self.base.ElementsLayerService.ChangeLayer.assert_not_called()
