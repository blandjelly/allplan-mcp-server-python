"""Controlled unknown-result gate; inspection never resumes the skipped target."""
import argparse
import asyncio
import copy
import json
import os
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

from fastmcp import Client

from .repair_diagnostics import save

SCOPE = {'drawing_files': [101], 'include_passive': False, 'visibility': 'api_select_all'}
AUDIT = {'profile_id': 'native-model-qa-demo', 'scope': SCOPE}
QUERY = {'action': 'query', 'scope': SCOPE, 'profile_id': 'native-model-qa-demo',
         'component_kind': 'top_level_component', 'coordinate_frame': 'model_local',
         'fields': ['mark', 'status', 'layer_id', 'file_state', 'bounding_box_mm']}


def snapshot(response):
    if (not response['coverage']['requested_scope_complete']
            or not response['coverage']['returned_fields_complete']
            or len(response['elements']) != 6 or not response['page']['is_full_selection']):
        raise ValueError('Expected all six retained columns with complete fields')
    return {e['ref']['model_uuid']: {'ref': {k: v for k, v in e['ref'].items() if k != 'query_session_id'},
                                    'fields': copy.deepcopy(e['fields'])} for e in response['elements']}


def partial_snapshot(before, changes):
    expected = copy.deepcopy(before)
    first = changes[0]
    fields = expected[first['ref']['model_uuid']]['fields']
    for key in ('mark', first['field']):
        if key in fields:
            fields[key] = {'status': 'observed', 'value': first['new_value']}
    return expected


def persist_pointer(path, pointer):
    save(path.parent / ('m3-recovery-execution-' + pointer['execution_id'] + '.json'), pointer)
    save(path.parent / 'm3-last-recovery-execution.json', pointer)


class Gate:
    def __init__(self, client, path, report):
        self.client, self.path, self.report = client, path, report
        self.step = 'health_preflight'

    async def call(self, name, tool, request, valid):
        self.step = name
        result = await self.client.call_tool(tool, {'request': request} if request is not None else {})
        response = result.data
        ok = bool(valid(response))
        self.report['steps'].append({'name': name, 'ok': ok, 'request': copy.deepcopy(request),
                                     'response': response, 'mcp_content': [
                                         {'type': b.type, 'text': b.text} for b in result.content if b.type == 'text']})
        save(self.path, self.report)
        if not ok:
            raise ValueError(name + ' differs from the declared recovery gate')
        return response

    async def health(self, name, session=None, changed=False):
        expected = version('allplan-mcp-server')
        def valid(r):
            rt = r['runtime']
            current = rt.get('host_session_id')
            return (r.get('ok') is True and r.get('mcp_package_version') == expected
                    and rt.get('bridge_package', {}).get('version') == expected
                    and rt.get('installed_bridge_integrity', {}).get('status') == 'verified'
                    and bool(current) and (session is None or (current != session if changed else current == session)))
        return (await self.call(name, 'allplan_health', None, valid))['runtime']['host_session_id']

    async def audit(self, name, findings):
        return await self.call(name, 'model_audit', AUDIT, lambda r:
            r['coverage']['audit_complete'] is True and r['counts']['elements'] == 6
            and r['counts']['not_checked'] == 0 and r['counts']['findings'] == findings
            and sorted(f['rule_id'] for f in r['findings']) == (
                ['QA-001', 'QA-002', 'QA-002'] if findings == 3 else ['QA-002', 'QA-002']))

    async def fields(self, name, expected=None):
        result = await self.call(name, 'model_query', QUERY, lambda r:
                                snapshot(r) == expected if expected is not None else len(snapshot(r)) == 6)
        return snapshot(result)

    def failure(self, exc, state):
        if not self.report['steps'] or self.report['steps'][-1]['name'] != self.step:
            self.report['steps'].append({'name': self.step, 'ok': False})
        self.report.update(state=state, message=str(exc) +
                           '. Preserve logs and Local journal. Do not rerun the test or send a new Apply; use inspection only.')


async def collect_recovery_test(url, path, confirm=input):
    report = {'state': 'preflight', 'steps': [], 'allplan_acceptance': 'not_run'}
    pointer, pending, gate = None, False, None
    try:
        # The one-off gate cannot overwrite an execution identity, even if resolved.
        if (path.parent / 'm3-last-recovery-execution.json').exists():
            raise ValueError('A recovery-test identity already exists; keep it and use inspection only')
        async with Client(url, timeout=90) as client:
            gate = Gate(client, path, report)
            session = await gate.health('health_preflight')
            before = await gate.audit('audit_before', 3)
            baseline = await gate.fields('snapshot_before')
            preview = {'action': 'preview', 'standard_id': 'native-model-qa-demo-mark-numbering',
                       'standard_version': '1.0.0', 'scope': SCOPE}
            def valid_plan(r):
                changes = r.get('changes', [])
                return (r.get('state') == 'preview_ready' and r.get('read_only') is True
                        and r.get('evaluation_apply_available') is True and len(changes) == 2
                        and r['source_fingerprint'] == before['source_fingerprint']
                        and r['numbering']['state'] == 'validated' and r['mark_validation']['state'] == 'validated'
                        and [(c['rule_id'], c['old_value'].get('value'), c['new_value']) for c in changes]
                        == [('QA-001', '<niezdefiniowany>', 'S03'), ('QA-002', 'S02', 'S04')]
                        and all(c['operation'] == 'set_attribute' and c['property_role'] == 'mark'
                                and c['resource'] == before['profile_binding']['attributes']['mark']['value']
                                and c['locator']['center_mm']['status'] == 'observed'
                                and len(c['locator']['center_mm']['value']) == 3
                                and all(abs(a - b) <= 1 for a, b in zip(c['locator']['center_mm']['value'], center))
                                for c, center in zip(changes, ([12000, 0, 1500], [0, 6000, 1500]))))
            plan = await gate.call('numbering_preview', 'apply_office_standard', preview, valid_plan)
            await gate.audit('unchanged_preview_audit', 3)
            await gate.fields('unchanged_preview_snapshot', baseline)
            print(plan['report_text'])
            print('Test zapisze tylko C03=S03 i zatrzyma sie przed odczytem wyniku. C04 pozostanie S02.')
            print('Potem wymagany restart StartPythonHost i osobna inspekcja. Nie uzywaj Undo przed inspekcja.')
            if confirm('Wpisz SPRAWDZ ODZYSKIWANIE na tej samej jednorazowej kopii: ').strip() != 'SPRAWDZ ODZYSKIWANIE':
                report.update(state='cancelled', message='No Apply sent.')
                return report
            review = {'action': 'revalidate', 'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash']}
            await gate.call('revalidate', 'apply_office_standard', review, lambda r:
                            r.get('state') == 'unchanged' and r.get('evaluation_apply_available') is True)
            request = {**review, 'action': 'apply', 'execution_id': uuid4().hex,
                       'acknowledgement': 'disposable_copy_reviewed_recovery_test',
                       'evaluation_stop': 'after_first_setter_before_readback'}
            pointer = {'state': 'apply_pending', 'execution_id': request['execution_id'],
                       'apply_request': request, 'gate_host_session': session, 'changes': plan['changes'],
                       'baseline': baseline, 'expected_partial': partial_snapshot(baseline, plan['changes']), 'steps': []}
            report['execution_id'] = request['execution_id']
            persist_pointer(path, pointer)
            pending = True
            def unknown(r):
                nonlocal pending
                if r.get('state') == 'rejected' and r.get('native_setters_started') is False:
                    pending = False
                    pointer.update(state='rejected', native_setters_started=False)
                    persist_pointer(path, pointer)
                    report['native_setters_started'] = False
                    return False
                return (r.get('execution_id') == request['execution_id'] and r.get('state') == 'running'
                        and r.get('replayed') is False
                        and r.get('evaluation_control', {}).get('controlled_interruption') is True
                        and r.get('outcomes') == [{'state': 'unknown', 'reason': 'setter_may_have_run'},
                                                {'state': 'skipped', 'reason': 'not_attempted'}])
            result = await gate.call('controlled_unknown', 'apply_office_standard', request, unknown)
            pointer['state'] = 'awaiting_host_restart'
            persist_pointer(path, pointer)
            await gate.call('exact_id_replay_unknown', 'apply_office_standard', request, lambda r:
                r.get('read_only') is True and r.get('replayed') is True and r.get('state') == 'running'
                and r.get('outcomes') == result['outcomes'])
            # Reuse the invalidated plan with a NEW identity for the guard probe.
            # Even if the recovery guard regressed, the old plan cannot write.
            probe = {**review, 'action': 'apply', 'execution_id': uuid4().hex,
                     'acknowledgement': 'disposable_copy_reviewed_plan'}
            pointer.update(probe_request=probe, uncertain_probe=True)
            persist_pointer(path, pointer)
            await gate.call('new_identity_blocked', 'apply_office_standard', probe, lambda r:
                r.get('state') == 'rejected' and r.get('native_setters_started') is False
                and r.get('execution_id') == probe['execution_id']
                and r.get('error', {}).get('code') == 'repair_recovery_required')
            pointer['uncertain_probe'] = False
            persist_pointer(path, pointer)
            await gate.audit('partial_audit', 2)
            await gate.fields('partial_snapshot_only_c03', pointer['expected_partial'])
            await gate.health('health_after', session)
            pending = False
            report.update(state='awaiting_host_restart', message=
                'C03=S03, C04/C02=S02. No Undo yet. Stop/restart StartPythonHost in the same project; run M3 Recovery Inspect.cmd.')
    except Exception as exc:
        if pointer is not None and pending:
            pointer['state'] = 'unknown'
            persist_pointer(path, pointer)
        if gate:
            gate.failure(exc, 'rejected' if pointer and pointer.get('native_setters_started') is False
                         else 'unknown' if pending else 'blocked')
        else:
            report.update(state='blocked', message=str(exc))
    finally:
        save(path, report)
    return report


async def inspect_recovery(url, path, pointer_path, after_undo=False):
    report = {'state': 'inspection_pending', 'steps': [], 'read_only': True, 'allplan_acceptance': 'not_run'}
    gate = None
    try:
        previous = json.loads(pointer_path.read_text(encoding='utf-8'))
        report['execution_id'] = previous['execution_id']
        if previous.get('state') == 'rejected' and previous.get('native_setters_started') is False:
            report.update(state='rejected', native_setters_started=False,
                          message='The test Apply was rejected before setters; no recovery call sent. Preserve reports.')
            return report
        if previous.get('uncertain_probe'):
            raise ValueError('The separate guard-probe reply is unresolved; retain both identities for local Codex inspection')
        if after_undo and previous['state'] != 'recovered':
            raise ValueError('First reconcile in the restarted host; Undo check cannot skip that phase')
        async with Client(url, timeout=90) as client:
            gate = Gate(client, path, report)
            session = await gate.health('health_restarted', previous['gate_host_session'], changed=True)
            request = {'action': 'recover', 'execution_id': previous['execution_id']}
            values = ['old_value_observed', 'old_value_observed'] if after_undo else ['new_value_observed', 'old_value_observed']
            def valid(r):
                return (r.get('read_only') is True and r.get('action') == 'recover'
                        and r.get('execution_id') == previous['execution_id'] and r.get('state') == 'stopped'
                        and [o['state'] for o in r.get('outcomes', [])] == ['reconciled', 'skipped']
                        and [o['state'] for o in r.get('recovery', {}).get('observations', [])] == values)
            response = await gate.call('recover_original_id', 'fix_model_issues', request, valid)
            await gate.call('exact_id_replay_no_resume', 'apply_office_standard', previous['apply_request'], lambda r:
                r.get('read_only') is True and r.get('replayed') is True
                and r.get('state') == 'stopped' and r.get('outcomes') == response['outcomes'])
            await gate.audit('audit_after_inspection', 3 if after_undo else 2)
            await gate.fields('snapshot_after_inspection', previous['baseline'] if after_undo else previous['expected_partial'])
            await gate.health('health_after_inspection', session)
            previous['state'] = 'undo_checked' if after_undo else 'recovered'
            persist_pointer(path, previous)
            report.update(state='ready_for_ui_observation', message=(
                'Leave/save original copy after Undo: C03 undefined, C04/C02=S02; preserve C05/C06 and journal/logs.' if after_undo else
                'Recover observed C03=S03 and skipped C04=S02; no resume. Check UI/other elements, then one Undo and M3 Recovery Undo Check.cmd.'))
    except Exception as exc:
        if gate:
            gate.failure(exc, 'blocked')
        else:
            report.update(state='blocked', message=str(exc) + '. No Apply sent; preserve identity/logs.')
    finally:
        save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'recover', 'undo-check'])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--execution', type=Path, default=Path('logs/m3-last-recovery-execution.json'))
    args = parser.parse_args()
    path = args.output or Path('logs') / ('m3-recovery-' + args.action + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    url = os.getenv('MCP_URL', 'http://127.0.0.1:8888/mcp')
    report = asyncio.run(collect_recovery_test(url, path)) if args.action == 'check' else asyncio.run(
        inspect_recovery(url, path, args.execution, after_undo=args.action == 'undo-check'))
    print('M3 recovery: ' + report['state'] + '. JSON/TXT: ' + str(path.resolve()))
    print(report.get('message', ''))
    if report['state'] not in {'awaiting_host_restart', 'ready_for_ui_observation', 'cancelled'}:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
