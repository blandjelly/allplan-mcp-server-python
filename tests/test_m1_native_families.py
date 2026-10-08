"""Observed native beam/slab hierarchy regressions; no live Allplan acceptance."""
import unittest
from unittest.mock import MagicMock

import test_m1_completion as fixtures

Solid = fixtures.Solid


class NativeFamilyTests(unittest.TestCase):
    setUp = fixtures.M1CompletionTests.setUp
    prepare_context = fixtures.M1CompletionTests.prepare_context
    prepare = fixtures.M1CompletionTests.prepare
    adapter = fixtures.M1CompletionTests.adapter
    request = fixtures.M1CompletionTests.request
    query = fixtures.M1CompletionTests.query
    follow = fixtures.M1CompletionTests.follow
    assert_code = fixtures.M1CompletionTests.assert_code
    native = fixtures.M1CompletionTests.native
    element = fixtures.M1CompletionTests.element

    def fixture(self):
        columns = [self.element(i) for i in range(1, 7)]
        beams = [self.element(i, name='SkeletonBeam_TypeUUID',
                              solid=Solid((0, 0, 3000), (6000, 300, 3500))) for i in (7, 8)]
        for beam in beams:
            beam.GetElementAdapterType.return_value.GetGuid.return_value = '53808df6-89e0-427e-81d6-1bd662823db1'
        wall = self.element(9, name='Wall_TypeUUID')
        slab = self.element(10, name='MultiSlab_TypeUUID')
        slab.GetElementAdapterType.return_value.GetGuid.return_value = '40910db6-25b8-43e3-8704-8bbf285143aa'
        axes = [self.element(i, name='SkeletonAxis_TypeUUID') for i in (11, 12)]
        wall_axes = [self.element(13, name='WallAxis_TypeUUID'), self.element(14, name='WallAxisLine_TypeUUID')]
        wall_tier = self.element(15, name='WallTier_TypeUUID', solid=Solid((20000, 0, 0), (24000, 200, 3000)))
        slab_tier = self.element(16, name='Slab_TypeUUID', solid=Solid((20000, 0, 3000), (24000, 4000, 3200)))
        reference = self.element(17, number=-102)
        self.native([*axes, *wall_axes, slab_tier, wall_tier, *columns, *beams, wall, slab, reference])
        for child, parent in zip(axes, beams):
            self.parents[id(child)] = parent
        for child in [*wall_axes, wall_tier]:
            self.parents[id(child)] = wall
        self.parents[id(slab_tier)] = slab
        self.children[id(wall)] = [*wall_axes, wall_tier]
        self.children[id(slab)] = [slab_tier]
        slab.GetModelGeometry.side_effect = AssertionError('aggregate slab must use tier solids')
        wall.GetModelGeometry.side_effect = AssertionError('wall must use tier solids')
        return beams, slab, slab_tier

    def test_observed_native_tree_counts_ten_components_and_one_passive_reference(self):
        beams, slab, tier = self.fixture()
        result = self.query(scope={'drawing_files': [101, 102, 103], 'include_passive': True, 'visibility': 'api_select_all'},
                            component_kind='top_level_component', fields=['bounding_box_mm', 'size_x_mm', 'size_y_mm', 'size_z_mm'])
        self.assertEqual(result['counts']['raw_adapters_visited'], 17)
        self.assertEqual(result['counts']['matched_model_identities'], 11)
        self.assertEqual(result['counts']['duplicate_representations'], 6)
        self.assertEqual(result['counts']['non_component_adapters'], 0)
        self.assertEqual(result['counts']['hierarchy_not_checked'], 0)
        self.assertTrue(result['coverage']['returned_fields_complete'])
        self.assertIn('SkeletonBeam_TypeUUID', result['coverage']['supported_component_types'])
        self.assertIn('MultiSlab_TypeUUID', result['coverage']['supported_component_types'])
        self.assertEqual(result['omissions'], [{'drawing_file': 103, 'reason': 'unloaded_or_unavailable'}])
        summary = self.follow(result, 'summary')['summary']
        self.assertEqual(summary['drawing_files'], {'101': 10, '102': 1})
        self.assertEqual(summary['type_names'], {'Column_TypeUUID': 7, 'SkeletonBeam_TypeUUID': 2, 'Wall_TypeUUID': 1, 'MultiSlab_TypeUUID': 1})
        found = {e['fields']['type_name']['value']: e for e in result['elements']}
        fields = found['MultiSlab_TypeUUID']['fields']
        self.assertEqual([fields[k]['value'] for k in ('size_x_mm', 'size_y_mm', 'size_z_mm')], [4000, 4000, 200])
        self.assertEqual(found['MultiSlab_TypeUUID']['ref']['type_uuid'], '40910db6-25b8-43e3-8704-8bbf285143aa')
        self.assertEqual(found['SkeletonBeam_TypeUUID']['ref']['type_uuid'], '53808df6-89e0-427e-81d6-1bd662823db1')
        slab.GetModelGeometry.assert_not_called()

    def test_aggregate_slab_unions_hidden_tiers_and_ignores_axis_geometry(self):
        slab = self.element(name='MultiSlab_TypeUUID')
        tiers = [self.element(i, name='Slab_TypeUUID', solid=Solid((0, 0, z), (4000, 4000, z + 100))) for i, z in ((2, 0), (3, 100))]
        axis = self.element(4, name='SkeletonAxis_TypeUUID', solid=Solid((-9999, -9999, -9999), (9999, 9999, 9999)))
        self.native([slab]); self.children[id(slab)] = [axis, *tiers]
        get_children = MagicMock(side_effect=lambda root, hidden: self.children[id(root)])
        self.adapter_module.BaseElementAdapterChildElementsService.GetChildModelElements = get_children
        result = self.query(component_kind='top_level_component', fields=['bounding_box_mm', 'size_z_mm'])
        self.assertEqual(result['elements'][0]['fields']['size_z_mm']['value'], 200)
        self.assertTrue(all(c.args[1] is True for c in get_children.call_args_list))
        slab.GetModelGeometry.assert_not_called(); axis.GetModelGeometry.assert_not_called()

    def test_slab_tier_change_invalidates_reusable_selection(self):
        beams, slab, tier = self.fixture()
        result = self.query(component_kind='top_level_component', fields=['size_z_mm'])
        tier.GetModelGeometry.return_value = Solid((20000, 0, 3000), (24000, 4000, 3300))
        self.assert_code('selection_stale', lambda: self.follow(result))

    def test_absent_cross_file_or_over_budget_slab_tiers_fail_closed(self):
        slab = self.element(name='MultiSlab_TypeUUID')
        self.native([slab])
        for children in ([], [self.element(2, number=102, name='Slab_TypeUUID')],
                         [self.element(i + 2, name='Slab_TypeUUID') for i in range(257)]):
            self.children[id(slab)] = children
            result = self.query(component_kind='top_level_component', fields=['size_z_mm'])
            self.assertEqual(result['counts']['matched_model_identities'], 1)
            self.assertEqual(result['elements'][0]['fields']['size_z_mm']['status'], 'not_checked')
            self.assertFalse(result['coverage']['returned_fields_complete'])
        slab.GetModelGeometry.assert_not_called()

    def test_unavailable_beam_solid_never_uses_axis_or_passes_spatial_filter(self):
        beam, axis = self.element(name='SkeletonBeam_TypeUUID'), self.element(2, name='SkeletonAxis_TypeUUID')
        self.native([axis, beam]); self.parents[id(axis)] = beam
        beam.GetModelGeometry.return_value = None
        result = self.query(component_kind='top_level_component', fields=['size_z_mm'])
        self.assertEqual(result['counts']['matched_model_identities'], 1)
        self.assertFalse(result['coverage']['returned_fields_complete'])
        axis.GetModelGeometry.assert_not_called()
        result = self.query(component_kind='top_level_component', predicate={'field': 'size_z_mm', 'op': 'eq', 'value': 500})
        self.assertEqual(result['counts']['matched_model_identities'], 0)
        self.assertEqual(result['counts']['predicate_not_checked'], 1)

    def test_other_framing_roots_remain_outside_supported_families(self):
        unknown = self.element(name='SkeletonColumn_TypeUUID')
        self.native([unknown])
        result = self.query(component_kind='top_level_component', fields=['display_name'])
        self.assertEqual(result['counts']['matched_model_identities'], 0)
        self.assertEqual(result['counts']['non_component_adapters'], 1)


if __name__ == '__main__':
    unittest.main()
