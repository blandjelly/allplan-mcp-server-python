"""Offline evidence semantics; no native host, HTTP server or package builds."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from allplan_mcp.wall_report_analysis import MAX_REPORT_BYTES, analyze_report, load_report

MODEL = '00000000-0000-4000-8000-000000000002'


def report(thickness=200, material='C25/30'):
    health = {'ok': True, 'runtime': {'host_session_id': 'reported-session'}}
    probe = {'schema_version': 'm4-property-probe-1', 'phase': 'wall_sample', 'state': 'observed', 'host_session_id': 'reported-session',
             'read_only': True, 'usable_for_write': False, 'model_data_changed': False, 'counts': {'sampled_walls': 1},
             'scope': {'included_files': [{'drawing_file': 101, 'state': 'active_foreground', 'write_eligibility': 'not_checked'}]},
             'coverage': {'requested_scope_complete': True, 'returned_fields_complete': True},
             'sample': {'ref': {'drawing_file': 101, 'model_uuid': MODEL, 'component_kind': 'top_level_component'},
                        'fields': {'type_name': {'status': 'observed', 'value': 'Wall_TypeUUID'}},
                        'tier_count': 1,
                        'total_thickness_mm': {'status': 'observed', 'value': thickness, 'unit': 'mm', 'source': 'single_tier_native_Thickness'},
                        'native_material': {'status': 'observed', 'value': material, 'source': 'WallTierProperties.Material'}}}
    return {'schema_version': 'm4-wall-owner-1', 'state': 'awaiting_owner_observation', 'model_setters_requested': False,
            'steps': [{'name': 'health_before', 'tool': 'allplan_health', 'state': 'response_received', 'response': copy.deepcopy(health)},
                      {'name': 'one_wall_sample', 'tool': 'model_property_probe', 'state': 'response_received',
                       'request': {'phase': 'wall_sample', 'drawing_file': 101}, 'response': probe},
                      {'name': 'health_after', 'tool': 'allplan_health', 'state': 'response_received', 'response': copy.deepcopy(health)}]}


def probe(value):
    return value['steps'][1]['response']


class WallReportAnalysisTests(unittest.TestCase):
    def test_strict_boundary_recomputed_and_input_not_modified(self):
        for value, expected in ((180, True), (239.9, True), (240, False), (250, False)):
            with self.subTest(value=value):
                source = report(value)
                probe(source)['sample']['criterion'] = {'matches_assuming_native_mm': not expected}
                original = copy.deepcopy(source)
                result = analyze_report(source)
                self.assertEqual(result['criterion_matches_assuming_mm'], expected)
                self.assertEqual(result['decision'], 'material_change_candidate_assuming_mm' if expected else 'outside_threshold_assuming_mm')
                self.assertEqual(source, original)

    def test_exact_native_material_label_is_conditional_and_has_no_aliases(self):
        for material, same in (('C35', True), ('C35/45', False), ('c35', False), (' C35 ', False), ('', False)):
            with self.subTest(material=material):
                result = analyze_report(report(material=material))
                self.assertEqual(result['native_label_equals_requested'], same)
                self.assertEqual(result['decision'], 'same_native_label_assuming_mm' if same else 'material_change_candidate_assuming_mm')
                self.assertFalse(result['usable_for_write'])
                self.assertEqual(result['material_binding'], 'not_checked')
        source = report()
        del probe(source)['sample']['native_material']
        probe(source)['sample']['attribute:508'] = {'status': 'observed', 'value': 'C35'}
        probe(source)['sample']['surface'] = {'status': 'observed', 'value': 'C35'}
        self.assertEqual(analyze_report(source)['decision'], 'not_checked')

    def test_exclusion_uses_file_and_uuid_and_cannot_create_a_write_plan(self):
        source = report()
        self.assertEqual(analyze_report(source, excluded_refs=[(101, MODEL)])['decision'], 'excluded')
        self.assertEqual(analyze_report(source, excluded_refs=[(102, MODEL)])['decision'], 'material_change_candidate_assuming_mm')
        result = analyze_report(source)
        for key in ('plan_id', 'plan_hash', 'execution_id', 'changes', 'operations', 'apply_request'):
            self.assertNotIn(key, result)

    def test_invalid_values_units_and_sources_remain_unknown(self):
        for value in (True, None, '200', 0, -1, float('nan'), float('inf'), 10**1000):
            with self.subTest(value=repr(value)[:30]):
                self.assertEqual(analyze_report(report(value))['decision'], 'not_checked')
        for field, key, value in (('total_thickness_mm', 'unit', 'cm'),
                                  ('total_thickness_mm', 'source', 'bounding_box'),
                                  ('total_thickness_mm', 'status', 'not_checked'),
                                  ('native_material', 'value', None),
                                  ('native_material', 'source', 'attribute:508'),
                                  ('native_material', 'value', 'x' * 8193)):
            source = report()
            probe(source)['sample'][field][key] = value
            self.assertEqual(analyze_report(source)['decision'], 'not_checked')

    def test_multitier_partial_or_failed_reads_do_not_become_candidates(self):
        for count in (0, 2):
            source = report()
            probe(source)['sample']['tier_count'] = count
            probe(source)['state'] = 'unsupported'
            self.assertEqual(analyze_report(source)['decision'], 'unsupported')
        source = report()
        probe(source)['sample']['tier_count'] = True
        self.assertEqual(analyze_report(source)['decision'], 'not_checked')
        for state in ('not_checked', 'unsupported'):
            source = report()
            probe(source)['state'] = state
            self.assertEqual(analyze_report(source)['decision'], 'not_checked')
        source = report()
        source['steps'][-1]['state'] = 'request_pending'
        self.assertEqual(analyze_report(source)['decision'], 'not_checked')
        source = report()
        source['steps'].append(copy.deepcopy(source['steps'][1]))
        self.assertEqual(analyze_report(source)['decision'], 'not_checked')

    def test_schema_root_scope_request_and_session_must_agree(self):
        mutations = [lambda r: r.update(schema_version='other'),
                     lambda r: probe(r).update(schema_version='other'),
                     lambda r: probe(r).update(host_session_id='other'),
                     lambda r: r['steps'][1]['request'].update(drawing_file=102),
                     lambda r: r['steps'][1]['request'].update(model_uuid='00000000-0000-4000-8000-000000000099'),
                     lambda r: probe(r)['scope']['included_files'][0].update(state='passive_background'),
                     lambda r: probe(r)['coverage'].update(requested_scope_complete=False),
                     lambda r: probe(r)['sample']['ref'].update(component_kind='model_identity'),
                     lambda r: probe(r)['sample']['fields']['type_name'].update(value='Column_TypeUUID'),
                     lambda r: r.update(model_setters_requested=True),
                     lambda r: probe(r).update(model_data_changed=True),
                     lambda r: r['steps'][-1]['response']['runtime'].update(host_session_id='other'),
                     lambda r: r['steps'][-1]['response'].update(ok=False)]
        for mutate in mutations:
            source = report()
            mutate(source)
            self.assertEqual(analyze_report(source)['decision'], 'not_checked')

    def test_forged_acceptance_flags_never_promote_saved_evidence(self):
        source = report(material='C35')
        for obj in (source, probe(source), probe(source)['sample']):
            obj.update(runtime_verified=True, units_runtime_verified=True, allplan_acceptance='accepted_on_build',
                       evaluation_apply_available=True, material_write_available=True)
        result = analyze_report(source)
        self.assertFalse(result['usable_for_write'])
        self.assertFalse(result['evaluation_apply_available'])
        self.assertFalse(result['runtime_verified'])
        self.assertFalse(result['native_model_access'])
        self.assertFalse(result['model_data_changed'])
        self.assertEqual(result['allplan_acceptance'], 'not_run')
        self.assertEqual(result['units'], 'assumed_native_mm_not_verified')
        self.assertEqual(result['current_model_values'], 'not_checked')
        self.assertEqual(result['source_authenticity'], 'not_verified')

    def test_invalid_target_and_exceptions_are_rejected(self):
        for label in ('', ' ', 'C35\n', 'x' * 129, None):
            with self.assertRaises(ValueError):
                analyze_report(report(), target_material=label)
        for refs in ([(True, MODEL)], [(101, 'bad')], [(101,)], [(101, '00000000-0000-0000-0000-000000000000')]):
            with self.assertRaises(ValueError):
                analyze_report(report(), excluded_refs=refs)

    def test_json_reader_rejects_ambiguous_nonfinite_and_oversized_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            for text in ('{"state":1,"state":2}', '{"value":NaN}', '{"value":Infinity}', '{"value":1e999}', '{'):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    load_report(path)
                self.assertEqual(path.read_text(), text)
            path.write_bytes(b' ' * (MAX_REPORT_BYTES + 1))
            with self.assertRaises(ValueError):
                load_report(path)

    def test_cli_runs_without_dependencies_or_network_and_never_overwrites_input(self):
        root = Path(__file__).resolve().parents[1]
        env = {**os.environ, 'PYTHONPATH': str(root / 'src')}
        script = "import socket,runpy; socket.socket=lambda *a,**k: (_ for _ in ()).throw(RuntimeError('network forbidden')); runpy.run_module('allplan_mcp.wall_report_analysis',run_name='__main__')"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            path.write_text(json.dumps(report()), encoding='utf-8')
            original = path.read_bytes()
            result = subprocess.run([sys.executable, '-S', '-c', script, str(path)], env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output['decision'], 'material_change_candidate_assuming_mm')
            self.assertEqual(len(output['source_json_sha256']), 64)
            self.assertEqual(path.read_bytes(), original)
            path.write_text('{')
            result = subprocess.run([sys.executable, '-S', '-m', 'allplan_mcp.wall_report_analysis', str(path)], env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertEqual(path.read_text(), '{')
