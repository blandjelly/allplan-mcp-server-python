"""M2 checks use fake adapters/resources and recorded JSON, never native acceptance."""
import copy
import importlib
import json
import types
import unittest
from pathlib import Path
from pydantic import TypeAdapter

import test_m1_completion as fixtures
from allplan_mcp.audit_models import AuditRequest
from allplan_mcp.demo_profile import load_audit_profile, load_demo_profile


class AuditTests(unittest.TestCase):
    setUp = fixtures.M1CompletionTests.setUp
    prepare_context = fixtures.M1CompletionTests.prepare_context
    prepare = fixtures.M1CompletionTests.prepare
    adapter = fixtures.M1CompletionTests.adapter
    native = fixtures.M1CompletionTests.native
    element = fixtures.M1CompletionTests.element
    resources = fixtures.M1CompletionTests.resources
    assert_code = fixtures.M1CompletionTests.assert_code

    def fixture(self):
        marks = ['S01', 'S02', '<niezdefiniowany>', 'S02', 'S05', 'S06']
        centers = [(0, 0), (6000, 0), (12000, 0), (0, 6000), (6000, 6000), (12000, 6000)]
        elements = []
        for i, (mark, (x,y)) in enumerate(zip(marks,centers), 1):
            e = self.element(i, attrs=[(20001,mark),(20002,'NWE' if i == 6 else 'NEW')],
                             solid=fixtures.Solid((x-200,y-200,0),(x+200,y+200,3000)))
            e.GetCommonProperties.return_value.Layer = 8 if i == 5 else 7
            elements.append(e)
        elements.extend([self.element(7, number=-102, attrs=[(20001,'S02')]),
                         self.element(8, number=103, attrs=[(20001,'S02')]),
                         self.element(9,name='Beam_TypeUUID',attrs=[(20001,'S02')])])
        self.native(elements)
        self.resources()
        self.audit_contracts = importlib.import_module('test_allplan_host.audit_contracts')
        return elements

    def request(self, **changes):
        return {'schema_version':'m2-audit-1',
                'scope':{'drawing_files':[101],'include_passive':False,'visibility':'api_select_all'},
                'profile':load_audit_profile(), **changes}

    def audit(self, **changes):
        result = self.handler.handle('/model-audit',self.request(**changes))
        json.dumps(result,allow_nan=False)
        self.base.CreateElements.assert_not_called()
        self.assertEqual(len(self.handler.model_queries.selections),0)
        return result

    def test_demo_five_findings_with_raw_evidence_scope_and_locators(self):
        self.fixture()
        result=self.audit()
        self.assertEqual(result['counts']['elements'],6)
        self.assertEqual(result['counts']['findings'],5)
        self.assertEqual(result['counts']['affected_elements'],5)
        self.assertEqual(result['counts']['duplicate_groups'],1)
        self.assertEqual(result['counts']['fail'],5)
        self.assertEqual(result['counts']['pass'],18)
        self.assertEqual(result['counts']['not_applicable'],1)
        self.assertEqual(result['counts']['not_checked'],0)
        self.assertTrue(result['coverage']['audit_complete'])
        self.assertTrue(result['coverage']['uses_full_snapshot'])
        self.assertFalse(result['usable_for_write'])
        self.assertFalse(result['runtime_verified'])
        by_rule={r['rule_id']:[f for f in result['findings'] if f['rule_id']==r['rule_id']] for r in result['rules']}
        self.assertEqual([len(by_rule[k]) for k in by_rule],[1,2,1,1])
        self.assertEqual(by_rule['QA-001'][0]['evidence']['raw']['value'],'<niezdefiniowany>')
        self.assertEqual(by_rule['QA-001'][0]['locator']['center_mm']['value'],[12000,0,1500])
        self.assertEqual(by_rule['QA-003'][0]['locator']['center_mm']['value'],[6000,6000,1500])
        self.assertEqual(by_rule['QA-002'][0]['evidence']['group_id'],by_rule['QA-002'][1]['evidence']['group_id'])
        self.assertEqual({f['ref']['drawing_file'] for f in result['findings']},{101})
        self.assertIn('5 findings on 5 elements',result['report_text'])
        self.assertIn('SZ_OGÓ01',result['report_text'])
        self.assertEqual(result['report_fingerprint'],self.audit()['report_fingerprint'])

    def test_rules_subsets_validate_and_use_complete_snapshot(self):
        self.fixture()
        result=self.audit(rule_ids=['QA-002'])
        self.assertEqual(result['counts']['findings'],2)
        self.assertEqual(result['counts']['elements'],6)
        self.assertEqual(result['counts']['rules'],1)
        for ids in ([],['QA-002','QA-002'],['QA-999'],[True]):
            self.assert_code('invalid_payload',lambda:self.audit(rule_ids=ids))

    def test_read_profile_kept_byte_identical_and_m2_resource_matches_example(self):
        profile=load_audit_profile()
        self.assertEqual(profile['read_profile'],load_demo_profile())
        root=Path(__file__).resolve().parents[1]
        self.assertEqual(profile,json.loads((root/'profiles/examples/native-model-qa.audit.json').read_text(encoding='utf-8')))
        TypeAdapter(AuditRequest).validate_python({'profile':profile,'scope':self.request()['scope']})

    def test_absent_null_empty_literal_and_types_have_explicit_semantics(self):
        elements=self.fixture()
        for raw, expected in [([], 'fail'),([(20001,None)],'fail'),([(20001,'')],'fail'),
                              ([(20001,'  ')],'fail'),([(20001,' <niezdefiniowany> ')],'fail'),
                              ([(20001,0)],'not_checked'),([(20001,False)],'not_checked'),
                              ([(20001,'s01')],'pass')]:
            elements[0].GetAttributes.return_value=raw+[(20002,'NEW')]
            result=self.audit(rule_ids=['QA-001'])
            self.assertEqual(result['checks'][0]['state'],expected)
        profile=load_audit_profile()
        profile['string_policies']['mark']['missing']['literals']=[]
        elements[0].GetAttributes.return_value=[(20001,'<niezdefiniowany>'),(20002,'NEW')]
        self.assertEqual(self.audit(profile=profile,rule_ids=['QA-001'])['counts']['findings'],0)
        profile['string_policies']['mark']['missing']['null']=False
        elements[0].GetAttributes.return_value=[(20001,None)]
        self.assertEqual(self.audit(profile=profile,rule_ids=['QA-001'])['checks'][0]['state'],'not_checked')

    def test_failed_reads_and_unknown_peer_never_become_unique_pass(self):
        elements=self.fixture()
        elements[0].GetAttributes.side_effect=RuntimeError('read failed')
        result=self.audit()
        self.assertGreater(result['counts']['not_checked'],0)
        self.assertFalse(result['coverage']['audit_complete'])
        unique=[c for c in result['checks'] if c['rule_id']=='QA-002']
        self.assertEqual(unique[4]['state'],'not_checked')
        self.assertEqual(unique[1]['state'],'fail')
        self.assertEqual(unique[3]['state'],'fail')

    def test_empty_and_unloaded_scope_distinguish_not_applicable_and_not_checked(self):
        self.fixture()
        self.base.ElementsSelectService.SelectAllElements.return_value=[]
        result=self.audit()
        self.assertEqual(result['state'],'not_applicable')
        self.assertTrue(result['coverage']['audit_complete'])
        self.base.DrawingFileService.return_value.GetFileState.return_value=[(102,1)]
        result=self.audit()
        self.assertEqual(result['state'],'not_checked')
        self.assertFalse(result['coverage']['audit_complete'])
        self.assertEqual(result['omissions'][0]['drawing_file'],101)
        self.assertTrue(all(r['state']=='not_checked' for r in result['rules']))

    def test_uniqueness_is_per_file_and_family_with_explicit_larger_profile(self):
        self.fixture()
        profile=load_audit_profile()
        profile['read_profile']['scope']['drawing_files']=[101,102]
        result=self.audit(profile=profile,scope={'drawing_files':[101,102],'include_passive':True,'visibility':'api_select_all'},rule_ids=['QA-002'])
        self.assertEqual(result['counts']['findings'],2)
        self.assertEqual(result['counts']['elements'],7)
        self.assertEqual(result['checks'][-1]['state'],'pass')
        self.assertEqual(result['checks'][-1]['ref']['drawing_file'],102)
        # A missing native attribute in passive files is unknown, not missing.
        result=self.audit(profile=profile,scope={'drawing_files':[101,102],'include_passive':True,'visibility':'api_select_all'},rule_ids=['QA-004'])
        self.assertEqual(result['checks'][-1]['state'],'not_checked')

    def test_profile_resource_failure_blocks_audit_before_enumeration(self):
        self.fixture()
        self.base.ElementsSelectService.SelectAllElements.reset_mock()
        self.base.AttributeService.GetAttributeType.return_value=2
        self.assert_code('profile_unbound',self.audit)
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_changed_source_reruns_and_updates_evidence_no_cached_finding_authority(self):
        elements=self.fixture()
        first=self.audit()
        elements[5].GetAttributes.return_value=[(20001,'S06'),(20002,'NEW')]
        second=self.audit()
        self.assertEqual(second['counts']['findings'],4)
        self.assertNotEqual(first['source_fingerprint'],second['source_fingerprint'])
        self.assertNotEqual(first['report_fingerprint'],second['report_fingerprint'])
        self.assertEqual(first['findings'][0]['finding_id'],second['findings'][0]['finding_id'])
        self.handler=self.module.RequestHandler(self.coord)
        third=self.audit()
        self.assertNotEqual(second['query_session_id'],third['query_session_id'])
        self.assertNotEqual(second['findings'][0]['finding_id'],third['findings'][0]['finding_id'])

    def test_duplicates_deduplicate_views_and_conflicting_identity_degrades_coverage(self):
        elements=self.fixture()
        self.base.ElementsSelectService.SelectAllElements.return_value=elements+[elements[0]]
        self.assertEqual(self.audit()['counts']['findings'],5)
        conflict=self.element(1,attrs=[(20001,'OTHER'),(20002,'NEW')])
        self.base.ElementsSelectService.SelectAllElements.return_value=elements+[conflict]
        result=self.audit()
        self.assertFalse(result['coverage']['requested_scope_complete'])
        self.assertGreater(result['counts']['not_checked'],0)

    def test_dimension_rules_use_mm_tolerance_and_preserve_unknown(self):
        elements=self.fixture()
        profile=load_audit_profile()
        profile['rules']=[{'rule_id':'QA-005','kind':'dimension_range','field':'size_z_mm',
                           'min_mm':3000.0,'max_mm':3000.0,'tolerance_mm':1.0,
                           'severity':'error','remedy':'Review the observed axis-aligned height.'}]
        self.assertEqual(self.audit(profile=profile)['counts']['pass'],6)
        elements[0].GetModelGeometry.return_value=fixtures.Solid((-200,-200,0),(200,200,3001))
        self.assertEqual(self.audit(profile=profile)['counts']['findings'],0)
        elements[0].GetModelGeometry.return_value=fixtures.Solid((-200,-200,0),(200,200,3001.01))
        self.assertEqual(self.audit(profile=profile)['counts']['findings'],1)
        elements[0].GetModelGeometry.return_value=None
        result=self.audit(profile=profile)
        self.assertEqual(result['checks'][0]['state'],'not_checked')
        self.assertFalse(result['coverage']['audit_complete'])

    def test_missing_locator_geometry_does_not_invent_rule_failure(self):
        elements=self.fixture()
        elements[2].GetModelGeometry.return_value=None
        result=self.audit()
        self.assertEqual(result['counts']['findings'],5)
        self.assertTrue(result['coverage']['audit_complete'])
        self.assertFalse(result['coverage']['returned_fields_complete'])
        missing=result['findings'][0]['locator']['center_mm']
        self.assertEqual(missing['status'],'not_checked')

    def test_invalid_profiles_and_scope_never_call_native_read(self):
        self.fixture()
        bad=[]
        for mutate in [lambda p:p.update(schema_version='wrong'),
                       lambda p:p['rules'][0].update(attribute='unknown'),
                       lambda p:p['rules'][0].update(severity='fatal'),
                       lambda p:p['rules'].append(copy.deepcopy(p['rules'][0])),
                       lambda p:p['rules'][1].update(uniqueness_scope=['drawing_file']),
                       lambda p:p['rules'][1].update(ignore_missing=1),
                       lambda p:p['string_policies']['mark'].update(trim=1),
                       lambda p:p['rules'][3].update(allowed_values=['NEW','NEW']),
                       lambda p:p['rules'][3].update(allowed_values=['<niezdefiniowany>']),
                       lambda p:p.update(extra=True)]:
            p=load_audit_profile();mutate(p);bad.append(self.request(profile=p))
        bad.extend([self.request(scope={'drawing_files':[102],'include_passive':True,'visibility':'api_select_all'}),
                    self.request(max_adapters=True),self.request(rule_ids=['unknown']),
                    self.request(scope={'drawing_files':[101,101],'include_passive':False,'visibility':'api_select_all'})])
        self.base.ElementsSelectService.SelectAllElements.reset_mock()
        self.base.AttributeService.GetAttributeID.reset_mock()
        for request in bad:
            self.assert_code('invalid_payload',lambda:self.handler.handle('/model-audit',request))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.base.AttributeService.GetAttributeID.assert_not_called()

    def test_incident_scope_returns_http_error_without_escaping_ui_or_reading_model(self):
        from allplan_mcp.allplan_client import AllplanHostClient, AllplanHostError
        from test_transport import stop_test_server
        self.fixture()
        transport = importlib.import_module('test_allplan_host.transport')
        escaped = []
        def managed_dispatch(callback):
            try:
                result = callback()
            except BaseException:
                escaped.append(True)
                raise
            json.dumps(result, allow_nan=False)
            return result
        server = transport.BridgeServer(('127.0.0.1',0),self.handler,managed_dispatch)
        server.start()
        self.addCleanup(stop_test_server,self,server)
        client = AllplanHostClient(f'http://127.0.0.1:{server.server_port}')
        self.settings.AllplanVersion.MainReleaseName.reset_mock()
        self.coord.GetInputViewDocument.reset_mock()
        request = self.request(scope={'drawing_files':[101,102],'include_passive':True,'visibility':'api_select_all'})
        with self.assertRaises(AllplanHostError) as error:
            client.post('/model-audit',request)
        self.assertEqual(error.exception.code,'invalid_payload')
        self.assertIn('Requested audit files exceed the explicit profile scope.',str(error.exception))
        self.assertEqual(escaped,[])
        self.settings.AllplanVersion.MainReleaseName.assert_not_called()
        self.coord.GetInputViewDocument.assert_not_called()
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.assertTrue(client.post('/get-allplan-version')['version'])

    def test_read_and_report_budgets_fail_without_partial_selection(self):
        self.fixture()
        self.assert_code('scan_limit_exceeded',lambda:self.audit(max_adapters=1))
        self.handler.model_queries.MAX_SNAPSHOT_BYTES=20000
        # Six elements fit the scan but the combined findings/checks exceed 20 KiB.
        self.assert_code('scan_limit_exceeded',self.audit)
        self.assertEqual(len(self.handler.model_queries.selections),0)

    def test_rules_share_the_scan_time_budget(self):
        self.fixture()
        now=[100]
        service=self.handler.model_queries
        service.clock=lambda:now[0]
        original=service._scan
        def slow_scan(*args):
            result=original(*args)
            now[0]+=6
            return result
        service._scan=slow_scan
        self.assert_code('scan_limit_exceeded',self.audit)

    def test_malformed_dimension_rules_are_rejected_before_resources(self):
        self.fixture()
        profile=load_audit_profile()
        base={'rule_id':'QA-005','kind':'dimension_range','field':'size_z_mm','min_mm':3000.0,
              'max_mm':3000.0,'tolerance_mm':1.0,'severity':'error','remedy':'Review height.'}
        self.base.AttributeService.GetAttributeID.reset_mock()
        for change in ({'field':[]},{'field':'attribute:1'},{'min_mm':4000.0},{'tolerance_mm':True},
                       {'max_mm':float('inf')},{'min_mm':-1.0},{'tolerance_mm':-1.0}):
            profile['rules']=[{**base,**change}]
            self.assert_code('invalid_payload',lambda:self.audit(profile=profile))
        self.base.AttributeService.GetAttributeID.assert_not_called()

    def test_string_normalization_is_declared_and_preserves_raw_case(self):
        elements=self.fixture()
        elements[0].GetAttributes.return_value=[(20001,' s02 '),(20002,'new')]
        sensitive=self.audit()
        self.assertEqual(sensitive['counts']['findings'],6)
        profile=load_audit_profile()
        for p in profile['string_policies'].values():p['case_sensitive']=False
        result=self.audit(profile=profile)
        duplicates=[f for f in result['findings'] if f['rule_id']=='QA-002']
        self.assertEqual(len(duplicates),3)
        self.assertEqual(duplicates[0]['evidence']['raw']['value'],' s02 ')
        self.assertEqual(duplicates[0]['evidence']['normalized_value'],'s02')
