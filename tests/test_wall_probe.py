"""Native Wall boundaries with fakes; no Allplan acceptance."""
import sys
import types
import weakref
import unittest
from unittest.mock import MagicMock, patch

import test_property_probe as fixtures


class WallElement:
    def __init__(self, props):
        self.Properties = props


class Tier:
    Thickness = 200.0
    def __init__(self):
        self.read_material = MagicMock(return_value='C25/30')
    @property
    def Material(self):
        return self.read_material()


class WallProbeTests(unittest.TestCase):
    setUp = fixtures.PropertyProbeTests.setUp
    prepare_context = fixtures.PropertyProbeTests.prepare_context
    prepare = fixtures.PropertyProbeTests.prepare
    adapter = fixtures.PropertyProbeTests.adapter
    native = fixtures.PropertyProbeTests.native
    element = fixtures.PropertyProbeTests.element
    assert_code = fixtures.PropertyProbeTests.assert_code
    fixture = fixtures.PropertyProbeTests.fixture
    probe = fixtures.PropertyProbeTests.probe
    records = fixtures.PropertyProbeTests.records

    def wall_fixture(self):
        self.fixture()
        self.elements = self.base.ElementsSelectService.SelectAllElements.return_value
        self.tier = Tier()
        self.props = types.SimpleNamespace(TierCount=1, GetWallTierProperties=MagicMock(return_value=self.tier))
        self.wall = WallElement(self.props)
        self.base.GetElement.return_value = self.wall
        substitute = patch.dict(sys.modules, {'NemAll_Python_ArchElements': types.SimpleNamespace(WallElement=WallElement)})
        substitute.start()
        self.addCleanup(substitute.stop)

    def wall_probe(self, **changes):
        result = self.probe(phase='wall_sample', drawing_file=101, **changes)
        self.base.ModifyElements.assert_not_called()
        self.base.DeleteElements.assert_not_called()
        return result

    def test_single_wall_native_fields_not_attributes_geometry_or_C35_binding(self):
        self.wall_fixture()
        def get(adapter):
            self.assertIs(adapter, self.elements[1])
            self.assertEqual(self.records()[-1]['api'], 'BaseElements.GetElement')
            self.assertEqual(self.records()[-1]['state'], 'started')
            return self.wall
        self.base.GetElement.side_effect = get
        result = self.wall_probe()
        sample = result['sample']
        self.assertEqual(result['state'], 'observed')
        self.assertEqual(sample['tier_count'], 1)
        self.assertEqual(sample['total_thickness_mm']['value'], 200.0)
        self.assertEqual(sample['native_material']['value'], 'C25/30')
        self.assertTrue(sample['criterion']['matches_assuming_native_mm'])
        self.assertFalse(result['material_write_available'])
        self.assertFalse(result['units_runtime_verified'])
        self.assertFalse(result['is_full_wall_filter'])
        self.assertEqual(result['counts']['sampled_walls'], 1)
        for e in self.elements:
            e.GetAttributes.assert_not_called()
            e.GetModelGeometry.assert_not_called()
        self.assertEqual(self.props.GetWallTierProperties.call_args.args, (1,))
        self.assertFalse(self.handler.model_queries.selections)

    def test_strict_threshold_and_native_lengths_ignore_UI_units(self):
        self.wall_fixture()
        for value, matches in ((180, True), (239.9, True), (240, False), (250, False)):
            with self.subTest(value=value):
                self.tier.Thickness = value
                self.settings.GetLengthUnit.return_value = 1
                result = self.wall_probe()
                self.assertEqual(result['sample']['total_thickness_mm']['value'], float(value))
                self.assertEqual(result['sample']['criterion']['matches_assuming_native_mm'], matches)

    def test_multi_tier_stops_before_any_tier_is_chosen(self):
        self.wall_fixture()
        for count in (0, 2, 10000):
            self.props.TierCount = count
            result = self.wall_probe()
            self.assertEqual(result['state'], 'unsupported')
        self.props.GetWallTierProperties.assert_not_called()
        self.tier.read_material.assert_not_called()

    def test_invalid_thickness_stops_before_material_without_fallback(self):
        self.wall_fixture()
        for value in (True, 0, -1, float('nan'), float('inf'), '200', None):
            with self.subTest(value=repr(value)):
                self.tier.Thickness = value
                result = self.wall_probe()
                self.assertEqual(result['state'], 'not_checked')
                self.assertEqual(result['failed_api'], 'WallTierProperties.Thickness')
                self.assertNotIn('criterion', result['sample'])
        self.tier.read_material.assert_not_called()

    def test_material_failure_preserves_thickness_and_failed_native_boundary(self):
        self.wall_fixture()
        self.tier.read_material.side_effect = RuntimeError('native error')
        result = self.wall_probe()
        self.assertEqual(result['state'], 'not_checked')
        self.assertEqual(result['sample']['total_thickness_mm']['value'], 200)
        self.assertEqual(result['failed_api'], 'WallTierProperties.Material')
        self.tier.read_material.assert_called_once()
        self.assertEqual([r['api'] for r in self.records() if r['state'] == 'failed'], ['WallTierProperties.Material'])

    def test_missing_requested_root_passive_and_invalid_payload_never_read_native_wall(self):
        self.wall_fixture()
        self.assert_code('probe_scope_unavailable', lambda: self.wall_probe(model_uuid='00000000-0000-4000-8000-000000000099'))
        self.assert_code('probe_scope_unavailable', lambda: self.probe(phase='wall_sample', drawing_file=102))
        self.base.GetElement.assert_not_called()
        self.coord.GetInputViewDocument.reset_mock()
        for fields in ({'drawing_file': True}, {'drawing_file': 101, 'model_uuid': None},
                       {'drawing_file': 101, 'model_uuid': '00000000-0000-0000-0000-000000000000'},
                       {'drawing_file': 101, 'attribute_id': 935}):
            self.assert_code('invalid_payload', lambda: self.probe(phase='wall_sample', **fields))
        self.coord.GetInputViewDocument.assert_not_called()

    def test_wrong_native_type_does_not_access_properties(self):
        self.wall_fixture()
        self.base.GetElement.return_value = object()
        result = self.wall_probe()
        self.assertEqual(result['state'], 'unsupported')
        self.props.GetWallTierProperties.assert_not_called()

    def test_explicit_wall_identity_reads_only_that_root_from_multiple_walls(self):
        self.wall_fixture()
        other = self.element(3, name='Wall_TypeUUID')
        self.elements.append(other)
        requested = other.GetModelElementUUID()
        result = self.wall_probe(model_uuid=requested)
        self.assertEqual(result['sample']['ref']['model_uuid'], requested)
        self.assertEqual(result['counts']['matched_model_identities'], 2)
        self.assertEqual(result['counts']['sampled_walls'], 1)
        self.assertIs(self.base.GetElement.call_args.args[0], other)
        self.base.GetElement.assert_called_once()

    def test_native_enumeration_owner_retained_through_material_read_and_released(self):
        self.wall_fixture()
        class Owner(list):
            pass
        refs = []
        def select(doc):
            owner = Owner(self.elements)
            refs.append(weakref.ref(owner))
            return owner
        self.base.ElementsSelectService.SelectAllElements.side_effect = select
        def material():
            self.assertIsNotNone(refs[-1]())
            return 'C25/30'
        self.tier.read_material.side_effect = material
        self.assertEqual(self.wall_probe()['state'], 'observed')
        self.assertTrue(all(r() is None for r in refs))

    def test_trace_failure_blocks_before_new_native_calls_and_base_exception_stops(self):
        self.wall_fixture()
        self.handler.property_probes.trace_path = self.path.parent
        self.assert_code('probe_trace_unavailable', self.wall_probe)
        self.base.GetElement.assert_not_called()
        self.handler.property_probes.trace_path = self.path
        self.base.GetElement.side_effect = SystemExit('native exit')
        with self.assertRaises(SystemExit):
            self.wall_probe()
        self.props.GetWallTierProperties.assert_not_called()
        self.assertEqual(self.records()[-1]['state'], 'failed')
