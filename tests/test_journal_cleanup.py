"""Confirmed archival preserves journal identity and resolved history."""
import copy
import importlib
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError
from allplan_mcp.repair_models import RepairRequest
import test_recovery_control as control


class JournalCleanupTests(unittest.TestCase):
    def setUp(self):
        self.native = control.RecoveryControlTests()
        self.native.setUp()
        self.addCleanup(self.native.doCleanups)
        self.native.fixture_ready()
        self.executor = self.native.handler.repair_plans.executor

    def call(self, request):
        return self.native.call(request)

    def preview(self):
        return self.call({'schema_version': 'm3-repair-1', 'action': 'preview_journal_cleanup',
                          'target': 'repair_records'})

    def confirm(self, preview):
        return self.call({'schema_version': 'm3-repair-1', 'action': 'cleanup_journal',
                          'target': 'repair_records', 'snapshot_hash': preview['snapshot_hash'],
                          'acknowledgement': 'confirmed_journal_cleanup'})

    def completed(self):
        plan = self.call(self.native.numbering_request())
        request = self.native.apply(plan)
        self.call(request)
        return request, self.executor.load(request['execution_id'])

    def clone_record(self, record, execution_id=None):
        result = copy.deepcopy(record)
        result['execution_id'] = execution_id or uuid4().hex
        self.executor.save(result)
        return result['execution_id']

    def test_empty_preview_needs_no_native_context_and_cleanup_requires_confirmation(self):
        self.native.coord.GetInputViewDocument.side_effect = AssertionError('No document needed')
        self.native.settings.AllplanVersion.MainReleaseName.side_effect = AssertionError('No native API needed')
        preview = self.preview()
        self.assertEqual(preview['state'], 'nothing_to_archive')
        self.assertEqual(preview['records'], [])
        self.assertFalse(preview['native_model_access'])
        self.assertFalse(preview['records_modified'])
        self.native.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

        adapter = TypeAdapter(RepairRequest)
        invalid = {'action': 'cleanup_journal', 'target': 'repair_records',
                   'snapshot_hash': '0' * 64}
        with self.assertRaises(ValidationError):
            adapter.validate_python(invalid)
        self.native.assert_code('invalid_payload', lambda: self.call({
            'schema_version': 'm3-repair-1', **invalid}))
        self.native.coord.GetInputViewDocument.assert_not_called()

    def test_archival_unblocks_capacity_preserves_bytes_replay_and_restart_history(self):
        request, record = self.completed()
        active_bytes = (self.executor.path / (request['execution_id'] + '.json')).read_bytes()
        for _ in range(127):
            self.clone_record(record)
        self.native.assert_code('repair_journal_full', lambda: self.call({
            **self.native.apply(self.call(self.native.numbering_request())),
            'execution_id': uuid4().hex}))
        preview = self.preview()
        self.assertEqual(preview['record_count'], 128)
        self.assertEqual(preview['eligible_count'], 128)
        result = self.confirm(preview)
        self.assertEqual(result['state'], 'archived')
        archive = self.executor.path / 'archive'
        self.assertEqual((archive / (request['execution_id'] + '.json')).read_bytes(), active_bytes)
        self.assertFalse((self.executor.path / (request['execution_id'] + '.json')).exists())

        # A new executor instance must find archived identity before checking capacity.
        service = type(self.native.handler.repair_plans)(self.native.handler.model_queries, self.native.directory.name)
        self.native.handler.repair_plans = service
        self.executor = service.executor
        self.native.base.ElementsSelectService.SelectAllElements.reset_mock()
        self.native.base.ElementsAttributeService.ChangeAttributes.reset_mock()
        replay = self.call(request)
        self.assertTrue(replay['replayed'])
        recovered = self.call({'schema_version': 'm3-repair-1', 'action': 'recover',
                               'execution_id': request['execution_id']})
        self.assertTrue(recovered['archived'])
        self.assertEqual(recovered['current_model_values'], 'not_checked')
        self.assertEqual(recovered['recovery_required'], False)
        self.native.base.ElementsSelectService.SelectAllElements.assert_not_called()
        self.native.base.ElementsAttributeService.ChangeAttributes.assert_not_called()

    def test_running_corrupt_and_oversized_records_are_protected(self):
        completed_request, completed_record = self.completed()
        running_record = copy.deepcopy(completed_record)
        running_id = uuid4().hex
        running_record['execution_id'] = running_id
        running_record['state'] = 'running'
        running_record['outcomes'] = [{'state': 'unknown'}, {'state': 'skipped'}]
        self.executor.save(running_record)
        corrupt_id = uuid4().hex
        (self.executor.path / (corrupt_id + '.json')).write_text('{bad json')
        oversized_id = uuid4().hex
        (self.executor.path / (oversized_id + '.json')).write_bytes(b' ' * (self.executor.MAX_RECORD_BYTES + 1))
        protected_names = {running_id + '.json', corrupt_id + '.json', oversized_id + '.json'}
        before = {p.name: p.read_bytes() for p in self.executor.path.glob('*.json')}
        preview = self.preview()
        self.assertEqual(preview['eligible_count'], 1)
        reasons = {r['execution_id']: r.get('reason') for r in preview['records'] if not r['eligible']}
        self.assertEqual(reasons[running_id], 'recovery_required')
        self.assertEqual(reasons[corrupt_id], 'unverifiable_or_oversized_record')
        self.assertEqual(reasons[oversized_id], 'unverifiable_or_oversized_record')
        self.confirm(preview)
        self.assertTrue(protected_names.issubset({p.name for p in self.executor.path.glob('*.json')}))
        self.assertEqual((self.executor.path / (running_id + '.json')).read_bytes(),
                         before[running_id + '.json'])
        self.assertEqual(self.executor.load(completed_request['execution_id']), completed_record)

    def test_unresolved_record_manually_placed_in_archive_cannot_claim_resolution(self):
        request, record = self.completed()
        record['state'] = 'running'
        record['outcomes'][0]['state'] = 'unknown'
        self.executor.save(record)
        archive = self.executor.path / 'archive'
        archive.mkdir()
        source = self.executor.path / (request['execution_id'] + '.json')
        source.rename(archive / source.name)
        self.native.assert_code('repair_journal_unavailable', lambda: self.executor.load(request['execution_id']))

    def test_stale_inventory_rejected_without_moving_records(self):
        _, record = self.completed()
        preview = self.preview()
        added = self.clone_record(record)
        before = {p.name: p.read_bytes() for p in self.executor.path.glob('*.json')}
        self.native.assert_code('journal_cleanup_conflict', lambda: self.confirm(preview))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.executor.path.glob('*.json')})
        self.assertFalse((self.executor.path / 'archive').exists())
        self.assertIsNotNone(self.executor.load(added))

    def test_inventory_over_128_and_scan_limit_are_bounded(self):
        _, record = self.completed()
        for _ in range(128):
            self.clone_record(record)
        preview = self.preview()
        self.assertEqual(preview['record_count'], 129)
        self.assertEqual(preview['eligible_count'], 129)
        result = self.confirm(preview)
        self.assertEqual(result['archived_count'], 129)
        self.assertEqual(list(self.executor.path.glob('*.json')), [])

        # The next scan is refused before presenting a truncated snapshot.
        for _ in range(1025):
            (self.executor.path / (uuid4().hex + '.json')).write_text('{}')
        self.native.assert_code('journal_cleanup_limit', self.preview)

    def test_archive_collisions_and_symlinks_are_protected(self):
        _, record = self.completed()
        archive = self.executor.path / 'archive'
        archive.mkdir()
        collision_id = self.clone_record(record)
        self.assertIsNotNone(self.executor.load(collision_id))
        collision_path = archive / (collision_id + '.json')
        collision_path.write_bytes(b'preserve collision')
        symlink_id = uuid4().hex
        link = self.executor.path / (symlink_id + '.json')
        target = self.executor.path / 'outside.json'
        target.write_bytes(b'outside')
        link.symlink_to(target)
        preview = self.preview()
        reasons = {r['execution_id']: r.get('reason') for r in preview['records'] if not r['eligible']}
        self.assertIn(reasons[collision_id], {'archive_collision', 'unverifiable_or_oversized_record'})
        self.assertEqual(reasons[symlink_id], 'unsafe_file')
        self.confirm(preview)
        self.assertTrue(link.is_symlink())
        self.assertTrue((self.executor.path / (collision_id + '.json')).exists())
        self.assertEqual(collision_path.read_bytes(), b'preserve collision')
        self.assertEqual(target.read_bytes(), b'outside')

    def test_partial_move_keeps_every_id_and_retry_uses_fresh_snapshot(self):
        base_request, record = self.completed()
        (self.executor.path / (base_request['execution_id'] + '.json')).unlink()
        first = self.clone_record(record)
        second = self.clone_record(record)
        originals = {identifier: (self.executor.path / (identifier + '.json')).read_bytes()
                     for identifier in (first, second)}
        preview = self.preview()
        import os
        real_os_replace = os.replace
        calls = []
        def fail_second_replace(source, target):
            if calls:
                raise OSError('injected archive failure')
            calls.append(Path(source).name)
            return real_os_replace(source, target)
        maintenance = importlib.import_module('test_allplan_host.journal_maintenance')
        with patch.object(maintenance.os, 'replace', side_effect=fail_second_replace):
            result = self.confirm(preview)
        self.assertEqual(result['state'], 'partial')
        archive = self.executor.path / 'archive'
        self.assertEqual(len(result['archived_execution_ids']), 1)
        self.assertEqual(calls, [result['archived_execution_ids'][0] + '.json'])
        for identifier, expected in originals.items():
            active = self.executor.path / (identifier + '.json')
            archived = archive / (identifier + '.json')
            self.assertEqual(active.exists() + archived.exists(), 1)
            self.assertEqual((archived if archived.exists() else active).read_bytes(), expected)

        fresh = self.preview()
        self.assertNotEqual(fresh['snapshot_hash'], preview['snapshot_hash'])
        retry = self.confirm(fresh)
        self.assertEqual(retry['state'], 'archived')
        for identifier, expected in originals.items():
            self.assertEqual((archive / (identifier + '.json')).read_bytes(), expected)

