"""One reviewed rule-based C04 mark write with excluded C02 and journal inspection."""
import argparse
import asyncio
import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastmcp import Client

from .recovery_diagnostics import AUDIT, Gate, partial_snapshot
from .repair_diagnostics import save


def persist(path, pointer):
    save(path.parent / ('m3-selected-mark-execution-' + pointer['execution_id'] + '.json'), pointer)
    save(path.parent / 'm3-last-selected-mark-execution.json', pointer)


async def journal(gate, name, execution=None):
    def valid(r):
        if not (r.get('schema_version') == 'm3-journal-inspection-1' and r.get('read_only') is True
                and r.get('native_model_access') is False and r.get('records_modified') is False
                and r.get('complete') is True
                and set(r.get('new_execution_blockers', [])) <= ({'journal_full'} if execution else set())):
            return False
        if execution is None:
            return r['remaining_slots'] >= 1
        records = [item for item in r['records'] if item.get('execution_id') == execution['execution_id']]
        return (len(records) == 1 and records[0]['integrity'] == 'verified'
                and records[0]['state'] == 'completed' and records[0]['changes'] == 1
                and records[0]['outcome_counts'] == {'applied': 1}
                and records[0]['plan_hash'] == execution['apply_request']['plan_hash']
                and records[0]['requires_recovery'] is False)
    return await gate.call(name, 'fix_model_issues', {'action': 'inspect_journal'}, valid)


def target(report, center, mark):
    candidates = [c for c in report['findings'] if c['rule_id'] in {'QA-001', 'QA-002'}
                  and c['locator']['mark'] == {'status': 'observed', 'value': mark}
                  and c['locator']['center_mm']['status'] == 'observed'
                  and len(c['locator']['center_mm']['value']) == 3
                  and all(abs(a - b) <= 1 for a, b in zip(c['locator']['center_mm']['value'], center))]
    if len(candidates) != 1:
        raise ValueError('Expected one exact retained column at ' + str(center))
    return candidates[0]['ref']['model_uuid']


async def selected_audit(gate, name, findings):
    return await gate.call(name, 'model_audit', AUDIT, lambda r:
        r['coverage']['audit_complete'] is True and r['counts']['elements'] == 6
        and r['counts']['not_checked'] == 0 and r['counts']['findings'] == findings
        and sorted(f['rule_id'] for f in r['findings']) == (
            ['QA-001', 'QA-002', 'QA-002'] if findings == 3 else ['QA-001']))


async def collect_selected_mark(url, path, confirm=input):
    report = {'state': 'preflight', 'steps': [], 'allplan_acceptance': 'not_run'}
    gate, pointer, sent = None, None, False
    try:
        if (path.parent / 'm3-last-selected-mark-execution.json').exists():
            raise ValueError('A selected-mark identity already exists. Keep it; use Recover or Undo Check only')
        async with Client(url, timeout=90) as client:
            gate = Gate(client, path, report)
            session = await gate.health('health_preflight')
            await journal(gate, 'journal_before')
            before = await selected_audit(gate, 'audit_before', 3)
            baseline = await gate.fields('snapshot_before')
            c02 = target(before, [6000, 0, 1500], 'S02')
            c04 = target(before, [0, 6000, 1500], 'S02')
            target(before, [12000, 0, 1500], '<niezdefiniowany>')
            preview = {'action': 'preview', 'audit': AUDIT,
                       'repairs': [{'rule_id': 'QA-002', 'model_uuid': c04, 'value': 'S04'}],
                       'selection': {'where': {'field': 'mark', 'op': 'eq', 'value': 'S02'},
                                     'exclude_model_uuids': [c02]}}
            def valid_plan(r):
                changes = r.get('changes', [])
                return (r.get('state') == 'preview_ready' and r.get('read_only') is True
                        and r.get('evaluation_apply_available') is True and len(changes) == 1
                        and r['source_fingerprint'] == before['source_fingerprint']
                        and r['workflow']['kind'] == 'rule_based_edit_preview'
                        and r['mark_validation']['state'] == 'validated'
                        and r['mark_validation']['uses_full_snapshot'] is True
                        and r['selection_result'] == {'selected_elements': 1, 'predicate_false': 4,
                                                     'excluded_elements': 1, 'predicate_not_checked': 0}
                        and changes[0]['ref']['model_uuid'] == c04 and changes[0]['rule_id'] == 'QA-002'
                        and changes[0]['operation'] == 'set_attribute' and changes[0]['property_role'] == 'mark'
                        and changes[0]['resource'] == before['profile_binding']['attributes']['mark']['value']
                        and changes[0]['old_value'] == {'status': 'observed', 'value': 'S02'}
                        and changes[0]['new_value'] == 'S04')
            plan = await gate.call('selected_mark_preview', 'rule_based_edit', preview, valid_plan)
            await gate.fields('snapshot_after_preview', baseline)
            print(plan['report_text'])
            print('Tylko zachowana kopia projektu: C04 S02 -> S04. C02 pozostaje S02, C03 niezdefiniowany.')
            if confirm('Wpisz ZMIEN C04 po sprawdzeniu jednej zmiany i kopii projektu: ').strip() != 'ZMIEN C04':
                report.update(state='cancelled', native_setters_started=False, message='No Apply sent.')
                return report
            review = {'action': 'revalidate', 'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash']}
            await gate.call('fresh_selected_revalidation', 'rule_based_edit', review, lambda r:
                            r.get('state') == 'unchanged' and r.get('evaluation_apply_available') is True)
            request = {**review, 'action': 'apply', 'execution_id': uuid4().hex,
                       'acknowledgement': 'disposable_copy_reviewed_plan'}
            expected = partial_snapshot(baseline, plan['changes'])
            pointer = {'state': 'apply_pending', 'execution_id': request['execution_id'],
                       'apply_request': request, 'baseline': baseline, 'expected': expected,
                       'gate_host_session': session, 'expected_changes': 1}
            report.update(execution_id=request['execution_id'], apply_request=copy.deepcopy(request))
            # Never send Apply unless both the immutable identity and last pointer are saved.
            save(path, report)
            persist(path, pointer)
            sent = True
            def valid_apply(r):
                if r.get('state') == 'rejected' and r.get('native_setters_started') is False:
                    pointer.update(state='rejected', native_setters_started=False)
                    persist(path, pointer)
                return (r.get('state') == 'completed' and r.get('execution_id') == request['execution_id']
                        and r.get('audited_fields_match_plan') is True
                        and [o['state'] for o in r.get('outcomes', [])] == ['applied']
                        and r['outcomes'][0]['readback'] == {'status': 'observed', 'value': 'S04'}
                        and r['audit_after']['coverage']['audit_complete'] is True
                        and r['audit_after']['counts']['findings'] == 1)
            result = await gate.call('selected_apply_readback', 'rule_based_edit', request, valid_apply)
            pointer['state'] = 'completed'
            persist(path, pointer)
            await gate.call('same_id_read_only_replay', 'rule_based_edit', request, lambda r:
                r.get('read_only') is True and r.get('replayed') is True
                and r.get('execution_id') == request['execution_id'] and r.get('outcomes') == result['outcomes'])
            await journal(gate, 'journal_after', pointer)
            await selected_audit(gate, 'audit_after', 1)
            await gate.fields('snapshot_only_c04_changed', expected)
            await gate.health('health_after', session)
            report.update(state='ready_for_ui_observation',
                          message='Observe C04=S04, excluded C02=S02 and unchanged other columns. '
                          'One native Undo restores C04; then run M3 Selected Mark Undo Check.cmd. Do not repeat Apply.')
    except Exception as exc:
        rejected = pointer is not None and pointer.get('state') == 'rejected'
        if pointer is not None and sent and not rejected and pointer['state'] == 'apply_pending':
            pointer['state'] = 'unknown'
            persist(path, pointer)
        if gate:
            gate.failure(exc, 'rejected' if rejected else 'unknown' if sent else 'blocked', before_apply=not sent)
            if rejected:
                report.update(native_setters_started=False,
                              message=str(exc) + '. Apply rejected before setters. No Undo or Recover needed for this request; keep reports.')
        else:
            report.update(state='blocked', native_setters_started=False, message=str(exc) + '. No Apply sent.')
    finally:
        save(path, report)
    return report


async def inspect_selected_mark(url, path, execution_path, after_undo=False):
    report = {'state': 'inspection', 'steps': [], 'read_only': True, 'allplan_acceptance': 'not_run'}
    gate = None
    try:
        pointer = json.loads(execution_path.read_text(encoding='utf-8'))
        report['execution_id'] = pointer['execution_id']
        if pointer.get('state') == 'rejected' and pointer.get('native_setters_started') is False:
            report.update(state='rejected', native_setters_started=False, message='Rejected before setters; no Recover sent.')
            return report
        async with Client(url, timeout=90) as client:
            gate = Gate(client, path, report)
            session = await gate.health('health_inspection')
            request = {'action': 'recover', 'execution_id': pointer['execution_id']}
            def valid(r):
                observations = r.get('recovery', {}).get('observations', [])
                return (r.get('read_only') is True and r.get('action') == 'recover'
                        and r.get('execution_id') == pointer['execution_id'] and len(observations) == 1
                        and observations[0]['state'] in (
                            {'old_value_observed'} if after_undo else {'old_value_observed', 'new_value_observed'}))
            response = await gate.call('recover_original_id', 'fix_model_issues', request, valid)
            old = response['recovery']['observations'][0]['state'] == 'old_value_observed'
            await selected_audit(gate, 'audit_inspection', 3 if old else 1)
            await gate.fields('snapshot_inspection', pointer['baseline'] if old else pointer['expected'])
            await gate.call('journal_inspection', 'fix_model_issues', {'action': 'inspect_journal'}, lambda r:
                r.get('read_only') is True and r.get('complete') is True
                and any(item.get('execution_id') == pointer['execution_id'] and item.get('integrity') == 'verified'
                        and item.get('requires_recovery') is False for item in r['records']))
            await gate.health('health_after_inspection', session)
            pointer['state'] = 'undo_checked' if after_undo else 'inspected_old' if old else 'inspected_new'
            persist(path, pointer)
            report.update(state='ready_for_ui_observation', message=(
                'Full original snapshot observed. Leave/save the same copy after Undo and preserve journal/logs.' if old else
                'C04=S04 observed; no Apply replay/resume. Check UI, then one Undo and Selected Mark Undo Check.'))
    except Exception as exc:
        if gate:
            gate.failure(exc, 'blocked', before_apply=True)
        else:
            report.update(state='blocked', message=str(exc) + '. No Apply sent; preserve identity/logs.')
    finally:
        save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'recover', 'undo-check', 'journal'])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--execution', type=Path, default=Path('logs/m3-last-selected-mark-execution.json'))
    args = parser.parse_args()
    path = args.output or Path('logs') / ('m3-selected-mark-' + args.action + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    url = os.getenv('MCP_URL', 'http://127.0.0.1:8888/mcp')
    async def collect_journal():
        report = {'state': 'inspection', 'steps': [], 'read_only': True}
        try:
            async with Client(url, timeout=90) as client:
                result = (await client.call_tool('fix_model_issues', {'request': {'action': 'inspect_journal'}})).data
                report.update(state=result['state'], message=result['report_text'])
                report['steps'].append({'name': 'journal', 'ok': result['complete'], 'response': result})
        except Exception as exc:
            report.update(state='blocked', message=str(exc) + '. No model operation requested.')
        finally:
            save(path, report)
        return report
    if args.action == 'journal':
        report = asyncio.run(collect_journal())
    elif args.action == 'check':
        report = asyncio.run(collect_selected_mark(url, path))
    else:
        report = asyncio.run(inspect_selected_mark(url, path, args.execution, after_undo=args.action == 'undo-check'))
    print('M3 selected mark: ' + report['state'] + '. JSON/TXT: ' + str(path.resolve()))
    print(report.get('message', ''))
    if report['state'] not in {'available', 'ready_for_ui_observation', 'cancelled', 'rejected'}:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
