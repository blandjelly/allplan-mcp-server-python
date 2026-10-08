"""M1 completion contracts/native orchestration, using fake geometry and resources."""
import copy
import importlib
import json
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

import test_model_query as fixtures
from allplan_mcp.demo_profile import load_demo_profile


class Solid:
    def __init__(self, minimum=(-200, -200, 0), maximum=(200, 200, 3000)):
        self.minimum, self.maximum = minimum, maximum


class Bounds:
    def __init__(self, solid):
        self.solid = solid
    def IsValid(self):
        return True
    def GetMin(self):
        return types.SimpleNamespace(**dict(zip('XYZ', self.solid.minimum)))
    def GetMax(self):
        return types.SimpleNamespace(**dict(zip('XYZ', self.solid.maximum)))


class M1CompletionTests(unittest.TestCase):
    setUp = fixtures.QueryTests.setUp
    prepare_context = fixtures.QueryTests.prepare_context
    prepare = fixtures.QueryTests.prepare
    adapter = fixtures.QueryTests.adapter
    request = fixtures.QueryTests.request
    query = fixtures.QueryTests.query
    follow = fixtures.QueryTests.follow
    assert_code = fixtures.QueryTests.assert_code

    def native(self, adapters=None):
        self.prepare(adapters)
        self.parents, self.children = {}, {}
        self.adapter_module = types.SimpleNamespace(
            BaseElementAdapterParentElementService=types.SimpleNamespace(GetParentElement=lambda e: self.parents.get(id(e), types.SimpleNamespace(IsNull=lambda: True))),
            BaseElementAdapterChildElementsService=types.SimpleNamespace(GetChildModelElements=lambda e, hidden: self.children.get(id(e), [])))
        modules = patch.dict(sys.modules, {'NemAll_Python_IFW_ElementAdapter': self.adapter_module})
        modules.start()
        self.addCleanup(modules.stop)
        self.geometry.Polyhedron3D = Solid
        self.geometry.BRep3D = type('BRep', (Solid,), {})
        self.geometry.eServiceResult.NO_ERR = 2
        self.geometry.CalcMinMax.side_effect = lambda s: (Bounds(s), 2)
        self.settings.AllplanGlobalSettings.GetOffsetPoint.return_value = types.SimpleNamespace(X=100000, Y=200000, Z=500)
        self.spatial = importlib.import_module('test_allplan_host.spatial_contracts')
        self.profile_contracts = importlib.import_module('test_allplan_host.profile_contracts')

    def element(self, ident=1, number=101, name='Column_TypeUUID', solid=None, attrs=None):
        e = self.adapter(number=number, ident=ident, attrs=attrs)
        e.GetElementAdapterType.return_value.GetTypeName.return_value = name
        e.GetElementAdapterType.return_value.GetGuid.return_value = ('ac9415e3-4337-4860-8cd4-2f0d48596f12' if name == 'Column_TypeUUID' else f'20000000-0000-4000-8000-{ident:012d}')
        e.GetModelGeometry.return_value = solid if solid is not None else Solid()
        e.IsNull.return_value = False
        return e

    def resources(self):
        ids = {'MCP_QA_MARK': 20001, 'MCP_QA_STATUS': 20002}
        names = {v:k for k,v in ids.items()}
        self.base.AttributeService.GetAttributeID.side_effect = lambda doc, name: ids.get(name, -1)
        self.base.AttributeService.GetAttributeName.side_effect = lambda doc, ident: names[ident]
        self.base.AttributeService.GetAttributeType.return_value = 67
        self.base.LayerService.GetIDByShortName.side_effect = lambda name, doc: {'Ogólne01':7, 'Ogólne02':8}[name]
        self.base.LayerService.GetShortNameByID.side_effect = lambda ident, docid: {7:'Ogólne01',8:'Ogólne02'}[ident]
        self.base.LayerService.GetNameByID.side_effect = lambda ident, docid: {7:'QA Structure',8:'QA Review'}[ident]

    def test_conversion_scales_then_applies_offset_once_and_round_trips(self):
        self.native()
        point = self.spatial.convert_point([1,2,3], 'm', 'model_local','project_global',[100000,200000,500])
        self.assertEqual(point,[101000,202000,3500])
        self.assertEqual(self.spatial.convert_point(point,'mm','project_global','model_local',[100000,200000,500]),[1000,2000,3000])
        self.assertEqual(self.spatial.convert_point([1,2,3],'cm','model_local','model_local',[9,9,9]),[10,20,30])

    def test_spatial_touching_inclusive_exclusive_and_containment_tolerance(self):
        self.native()
        box = {'min':[0,0,0],'max':[1,1,1]}
        requested = {'min':[1,0,0],'max':[2,1,1],'relation':'intersects','boundary':'inclusive','frame':'model_local'}
        self.assertTrue(self.spatial.matches_box(box,requested))
        self.assertFalse(self.spatial.matches_box(box,{**requested,'boundary':'exclusive'}))
        outer = {**requested,'min':[0.1,0,0],'max':[1,1,1],'relation':'contained'}
        self.assertFalse(self.spatial.matches_box(box,outer))
        self.assertTrue(self.spatial.matches_box(box,{**outer,'tolerance_mm':0.1}))

    def test_geometry_fields_are_mm_and_independent_of_display_units(self):
        self.native([self.element()])
        first=self.query(fields=['bounding_box_mm','size_z_mm'])
        self.settings.GetLengthUnit.return_value=6
        second=self.follow(first)
        self.assertEqual(first['elements'],second['elements'])
        values=first['elements'][0]['fields']
        self.assertEqual(values['size_z_mm']['value'],3000)
        self.assertEqual(values['bounding_box_mm']['value']['min'],[-200,-200,0])
        self.assertFalse(values['bounding_box_mm']['value']['offset_applied'])

    def test_global_box_and_center_apply_offset_without_scaling_dimensions(self):
        self.native([self.element()])
        result=self.query(coordinate_frame='project_global',fields=['bounding_box_mm','center_x_mm','size_z_mm'])
        values=result['elements'][0]['fields']
        self.assertEqual(values['bounding_box_mm']['value']['min'],[99800,199800,500])
        self.assertEqual(values['center_x_mm']['value'],100000)
        self.assertEqual(values['size_z_mm']['value'],3000)
        self.assertTrue(values['bounding_box_mm']['value']['offset_applied'])

    def test_missing_geometry_excludes_spatial_candidate_as_not_checked(self):
        e=self.element();e.GetModelGeometry.return_value=None
        self.native([e])
        result=self.query(spatial_box={'min':[-300,-300,-1],'max':[300,300,3001],'relation':'contained','boundary':'inclusive','frame':'model_local'})
        self.assertEqual(result['counts']['predicate_not_checked'],1)
        self.assertEqual(result['elements'],[])
        self.assertFalse(result['coverage']['requested_scope_complete'])

    def test_nonfinite_geometry_and_service_failure_are_not_checked(self):
        self.native([self.element(solid=Solid((float('nan'),0,0),(1,1,1)))])
        result=self.query(fields=['size_z_mm'])
        self.assertEqual(result['elements'][0]['fields']['size_z_mm']['status'],'not_checked')
        self.geometry.CalcMinMax.side_effect=lambda s:(Bounds(s),999)
        result=self.query(fields=['bounding_box_mm'])
        self.assertFalse(result['coverage']['returned_fields_complete'])

    def test_geometry_change_in_rejected_candidate_invalidates_selection(self):
        first,second=self.element(),self.element(2,solid=Solid((5000,0,0),(5400,400,1000)))
        self.native([first,second])
        result=self.query(predicate={'field':'size_z_mm','op':'eq','value':3000})
        second.GetModelGeometry.return_value=Solid((5000,0,0),(5400,400,3000))
        self.assert_code('selection_stale',lambda:self.follow(result))

    def test_offset_change_invalidates_global_geometry_selection(self):
        self.native([self.element()])
        result=self.query(fields=['bounding_box_mm'],coordinate_frame='project_global')
        self.settings.AllplanGlobalSettings.GetOffsetPoint.return_value.X+=1
        self.assert_code('selection_stale',lambda:self.follow(result))

    def test_top_level_counts_ten_fixture_components_without_children_or_labels(self):
        roots=[self.element(i) for i in range(1,7)]+[self.element(i,name='Beam_TypeUUID') for i in (7,8)]+[self.element(9,name='Wall_TypeUUID'),self.element(10,name='Slab_TypeUUID')]
        tier=self.element(11,name='WallTier_TypeUUID');label=self.element(12,name='Text_TypeUUID')
        self.native([*roots,tier,label]);self.parents[id(tier)]=roots[8]
        result=self.query(component_kind='top_level_component',fields=['display_name'])
        self.assertEqual(result['counts']['matched_model_identities'],10)
        self.assertEqual(result['counts']['duplicate_representations'],1)
        self.assertEqual(result['counts']['non_component_adapters'],1)
        summary=self.follow(result,'summary')
        self.assertEqual(summary['summary']['type_names'],{'Beam_TypeUUID':2,'Column_TypeUUID':6,'Slab_TypeUUID':1,'Wall_TypeUUID':1})

    def test_hierarchy_cycle_and_cross_file_parent_do_not_become_components(self):
        first,other=self.element(),self.element(2,number=102)
        self.native([first]);self.parents[id(first)]=first
        result=self.query(component_kind='top_level_component')
        self.assertEqual(result['counts']['hierarchy_not_checked'],1)
        self.assertEqual(result['elements'],[])
        self.parents[id(first)]=other
        result=self.query(component_kind='top_level_component')
        self.assertFalse(result['coverage']['requested_scope_complete'])

    def test_parent_root_views_stay_separate_without_false_component_conflict(self):
        first,second=self.element(),self.element()
        second.GetElementUUID.return_value='10000000-0000-4000-8000-000000000002'
        self.native([first,second])
        result=self.query(component_kind='top_level_component')
        self.assertEqual(result['counts']['matched_model_identities'],1)
        self.assertEqual(result['counts']['conflicting_model_identities'],0)
        self.assertEqual(len(result['elements'][0]['view_uuids']),2)
        self.assertNotIn('view_uuid',result['elements'][0]['fields']['hierarchy']['value']['root'])

    def test_wall_bounds_union_all_tiers_and_do_not_require_parent_geometry(self):
        wall=self.element(name='Wall_TypeUUID')
        tiers=[self.element(i,name='WallTier_TypeUUID',solid=Solid((0,y,0),(4000,y+100,3000))) for i,y in ((2,0),(3,100))]
        self.native([wall]);self.children[id(wall)]=tiers
        result=self.query(component_kind='top_level_component',fields=['bounding_box_mm','size_y_mm'])
        self.assertEqual(result['elements'][0]['fields']['size_y_mm']['value'],200)

    def test_profile_rejects_unbound_or_unknown_schema_and_invalid_rule_reference(self):
        self.native()
        for mutation in (lambda p:p.update(schema_version='draft-1'),lambda p:p['bindings']['attributes']['mark'].update(attribute_id=None),lambda p:p['rules'][0].update(attribute='unknown')):
            p=load_demo_profile();mutation(p)
            self.assert_code('invalid_payload',lambda:self.handler.handle('/model-query',{'schema_version':'m1-query-1','action':'profile','profile':p}))
        self.base.AttributeService.GetAttributeID.assert_not_called()

    def test_profile_resolves_exact_names_types_layers_and_configured_levels(self):
        self.native();self.resources()
        result=self.handler.handle('/model-query',{'schema_version':'m1-query-1','action':'profile','profile':load_demo_profile()})
        self.assertEqual(result['status'],'bound_for_read')
        self.assertEqual(result['attributes']['mark']['value']['attribute_id'],20001)
        self.assertEqual(result['layers']['review']['value']['layer_id'],8)
        self.assertFalse(result['active_for_write'])
        context=self.handler.handle('/get-model-context',{'profile':load_demo_profile()})
        self.assertEqual(context['levels']['source'],'profile_configuration_not_native_BWS')
        self.base.CreateElements.assert_not_called()

    def test_profile_unresolved_ids_preserve_lookup_stage_and_do_not_scan(self):
        self.native(); self.resources()
        self.base.AttributeService.GetAttributeID.side_effect = None
        self.base.AttributeService.GetAttributeID.return_value = 0
        self.base.LayerService.GetIDByShortName.side_effect = None
        self.base.LayerService.GetIDByShortName.return_value = -1
        result = self.handler.handle('/model-query', {'schema_version':'m1-query-1', 'action':'profile', 'profile':load_demo_profile()})
        self.assertEqual(result['status'], 'not_checked')
        self.assertEqual(result['attributes']['mark']['diagnostic'], {'requested_name':'MCP_QA_MARK', 'stage':'GetAttributeID', 'returned_id':0})
        self.assertEqual(result['layers']['review']['diagnostic'], {'requested_short_name':'Ogólne02', 'stage':'GetIDByShortName', 'returned_id':-1})
        self.base.AttributeService.GetAttributeName.assert_not_called()
        self.assertEqual(len(self.handler.model_queries.selections), 0)

    def test_profile_type_mismatch_and_native_exception_preserve_safe_diagnostics(self):
        self.native(); self.resources()
        self.base.AttributeService.GetAttributeType.return_value = 73
        self.base.LayerService.GetShortNameByID.side_effect = RuntimeError('native details must not be published')
        result = self.handler.handle('/model-query', {'schema_version':'m1-query-1', 'action':'profile', 'profile':load_demo_profile()})
        diagnostic = result['attributes']['status']['diagnostic']
        self.assertEqual(diagnostic['stage'], 'attribute_round_trip')
        self.assertEqual(diagnostic['returned_type_code'], 73)
        self.assertEqual(diagnostic['expected_type_code'], 67)
        self.assertEqual(result['layers']['structure']['diagnostic']['stage'], 'GetShortNameByID')
        self.assertNotIn('native details', json.dumps(result))

    def test_owner_profile_uses_distinct_unicode_existing_layers_and_old_profile_still_validates(self):
        self.native(); self.resources()
        profile = load_demo_profile()
        self.assertEqual(profile['profile_version'], '1.0.1')
        self.assertEqual(profile['bindings']['layers'], {'structure':{'short_name':'Ogólne01'}, 'review':{'short_name':'Ogólne02'}})
        profile['profile_version'] = '1.0.0'
        profile['bindings']['layers'] = {'structure':{'short_name':'MCP_QA_STRUCTURE'}, 'review':{'short_name':'MCP_QA_REVIEW'}}
        self.profile_contracts.validate_profile(profile)

    def test_profile_missing_resource_and_wrong_native_type_code_block_query(self):
        self.native([self.element()]);self.resources()
        self.base.AttributeService.GetAttributeID.side_effect=None
        self.base.AttributeService.GetAttributeID.return_value=-1
        self.assert_code('profile_unbound',lambda:self.query(profile=load_demo_profile(),fields=['mark']))
        self.resources();self.base.AttributeService.GetAttributeType.return_value=73
        self.assert_code('profile_unbound',lambda:self.query(profile=load_demo_profile(),fields=['mark']))
        self.assertEqual(len(self.handler.model_queries.selections),0)

    def test_profile_aliases_and_family_filter_return_two_s02_columns(self):
        elements=[self.element(i,attrs=[(20001,mark),(20002,'NEW')]) for i,mark in enumerate(('S01','S02','','S02','S05','S06'),1)]
        self.native(elements);self.resources()
        result=self.query(profile=load_demo_profile(),fields=['mark','status'],predicate={'field':'mark','op':'eq','value':'S02'})
        self.assertEqual(result['counts']['matched_model_identities'],2)
        self.assertEqual(result['profile_binding']['status'],'bound_for_read')

    def test_profile_metadata_change_and_hierarchy_change_invalidate_reuse(self):
        e=self.element(attrs=[(20001,'S01'),(20002,'NEW')])
        self.native([e]);self.resources()
        result=self.query(profile=load_demo_profile(),fields=['mark'])
        self.base.LayerService.GetNameByID.side_effect=None;self.base.LayerService.GetNameByID.return_value='Changed'
        self.assert_code('selection_stale',lambda:self.follow(result))
        result=self.query(component_kind='top_level_component')
        self.parents[id(e)]=self.element(2)
        self.assert_code('selection_stale',lambda:self.follow(result))

    def test_invalid_spatial_frames_and_aliases_are_rejected_before_native_reads(self):
        self.native()
        for changes in ({'fields':['mark']},{'component_kind':{}},{'spatial_box':{'min':[0,0,0],'max':[-1,1,1],'frame':'model_local','relation':'contained','boundary':'inclusive'}},
                        {'spatial_box':{'min':[0,0,0],'max':[10**1000,1,1],'frame':'model_local','relation':'contained','boundary':'inclusive'}},
                        {'coordinate_frame':'model_local','spatial_box':{'min':[0,0,0],'max':[1,1,1],'frame':'project_global','relation':'intersects','boundary':'inclusive'}}):
            self.assert_code('invalid_payload',lambda:self.query(**changes))
        self.base.ElementsSelectService.SelectAllElements.assert_not_called()

    def test_combined_dimension_and_spatial_filter_observes_one_c01(self):
        self.native([self.element(),self.element(2,solid=Solid((5800,-200,0),(6200,200,3000)))])
        result=self.query(fields=['bounding_box_mm'],predicate={'field':'size_z_mm','op':'eq','value':3000,'tolerance':1},
                          spatial_box={'min':[-201,-201,-1],'max':[201,201,3001],'frame':'model_local','relation':'contained','boundary':'exclusive'})
        self.assertEqual(result['counts']['matched_model_identities'],1)

    def test_geometry_budget_failure_never_creates_selection(self):
        e=self.element();self.native([e])
        now=[0];self.handler.model_queries.clock=lambda:now[0]
        def delayed():
            now[0]=6
            return Solid()
        e.GetModelGeometry.side_effect=delayed
        self.assert_code('scan_limit_exceeded',lambda:self.query(fields=['size_z_mm']))
        self.assertEqual(len(self.handler.model_queries.selections),0)

    def test_unrequested_or_outside_scope_geometry_is_never_read(self):
        inside,outside=self.element(),self.element(2,number=104)
        self.native([inside,outside])
        self.query()
        inside.GetModelGeometry.assert_not_called()
        self.query(fields=['size_z_mm'])
        outside.GetModelGeometry.assert_not_called()

    def test_profile_resource_alias_collision_and_nonstring_values_are_rejected(self):
        self.native([self.element(attrs=[(20001, None),(20002,'NEW')])]);self.resources()
        result=self.query(profile=load_demo_profile(),fields=['mark'])
        self.assertEqual(result['elements'][0]['fields']['mark']['status'],'not_checked')
        self.base.AttributeService.GetAttributeID.side_effect=lambda doc,name:20001
        self.base.AttributeService.GetAttributeName.side_effect=lambda doc,ident:'MCP_QA_MARK'
        self.assert_code('profile_unbound',lambda:self.query(profile=load_demo_profile(),fields=['mark']))

    def test_negating_failed_dimension_read_never_turns_unknown_into_pass(self):
        e=self.element();e.GetModelGeometry.return_value=None
        self.native([e])
        result=self.query(predicate={'not':{'field':'size_z_mm','op':'eq','value':3000}})
        self.assertEqual(result['counts']['predicate_not_checked'],1)
        self.assertEqual(result['elements'],[])
