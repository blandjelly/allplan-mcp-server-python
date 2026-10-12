"""Same-session excluded-peer conflict gate using one separately reviewed write."""
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
from .workflow_diagnostics import recover_workflow


async def collect_conflict(mcp_url, path, confirm=input):
    report = {'state': 'preflight', 'steps': [], 'allplan_acceptance': 'not_run'}
    step, pending, pointer = 'health_preflight', False, None
    pointer_path = path.parent / 'm3-last-conflict-execution.json'

    def persist_pointer():
        save(path.parent / ('m3-conflict-execution-' + pointer['execution_id'] + '.json'), pointer)
        save(pointer_path, pointer)

    try:
        if pointer_path.exists():
            previous = json.loads(pointer_path.read_text(encoding='utf-8'))
            if (previous.get('state') not in {'completed', 'rejected'}
                    or previous.get('uncertain_stale_execution_id')):
                raise ValueError('Previous conflict execution needs read-only recovery before another test')
        async with Client(mcp_url, timeout=90) as client:
            async def call(tool, request=None):
                result = await client.call_tool(tool, {'request': request} if request is not None else {})
                return result.data, [{'type': b.type, 'text': b.text} for b in result.content if b.type == 'text']

            def record(name, ok, response, content, request=None):
                report['steps'].append({'name': name, 'ok': bool(ok), 'response': response,
                                        'mcp_content': content, 'request': copy.deepcopy(request)})
                save(path, report)
                if not ok:
                    raise ValueError(name + ' differs from the same-session conflict contract')

            health, content = await call('allplan_health')
            runtime, expected = health['runtime'], version('allplan-mcp-server')
            record(step, health.get('ok') is True and health.get('mcp_package_version') == expected
                   and runtime.get('bridge_package', {}).get('version') == expected
                   and runtime.get('installed_bridge_integrity', {}).get('status') == 'verified', health, content)
            session = runtime['host_session_id']
            step = 'context_before'
            context, content = await call('get_model_context')
            record(step, context.get('read_only') is True, context, content)
            scope = {'drawing_files': [101], 'include_passive': False, 'visibility': 'api_select_all'}
            audit_request = {'profile_id': 'native-model-qa-demo', 'scope': scope}
            step = 'audit_before'
            before, content = await call('model_audit', audit_request)
            findings = [f for f in before['findings'] if f['rule_id'] in {'QA-001', 'QA-002'}]
            record(step, before['coverage']['audit_complete'] is True and before['counts']['elements'] == 6
                   and before['counts']['not_checked'] == 0
                   and sorted(f['rule_id'] for f in findings) == ['QA-001', 'QA-002', 'QA-002'],
                   before, content, audit_request)
            targets = []
            for rule, old, center in [('QA-001', '<niezdefiniowany>', [12000, 0, 1500]),
                                      ('QA-002', 'S02', [0, 6000, 1500])]:
                matches = [f for f in findings if f['rule_id'] == rule
                           and f['evidence']['raw'].get('value') == old
                           and f['locator']['center_mm']['status'] == 'observed'
                           and len(f['locator']['center_mm']['value']) == 3
                           and all(abs(a - b) <= 1 for a, b in zip(f['locator']['center_mm']['value'], center))]
                if len(matches) != 1:
                    raise ValueError('Expected retained C03 undefined and C04=S02; no write requested')
                targets.append(matches[0]['ref']['model_uuid'])
            c03, c04 = targets
            resource = before['profile_binding']['attributes']['mark']['value']

            async def preview(name, target, old):
                request = {'action': 'preview', 'standard_id': 'native-model-qa-demo-mark-numbering',
                           'standard_version': '1.0.0', 'scope': scope,
                           'selection': {'where': {'field': 'layer_id', 'op': 'exists'},
                                         'exclude_model_uuids': sorted({c['ref']['model_uuid']
                                             for c in before['checks']} - {target})}}
                plan, content = await call('apply_office_standard', request)
                changes = plan.get('changes', [])
                record(name, plan.get('state') == 'preview_ready' and plan.get('read_only') is True
                       and plan.get('evaluation_apply_available') is True and len(changes) == 1
                       and changes[0]['ref']['model_uuid'] == target
                       and changes[0]['old_value'].get('value') == old and changes[0]['new_value'] == 'S03'
                       and changes[0]['operation'] == 'set_attribute' and changes[0]['property_role'] == 'mark'
                       and changes[0]['resource'] == resource and plan['mark_validation']['state'] == 'validated'
                       and plan['mark_validation']['uses_full_snapshot'] is True
                       and plan['selection_result']['excluded_elements'] == 5
                       and plan['source_fingerprint'] == before['source_fingerprint']
                       and plan['audit_report_fingerprint'] == before['report_fingerprint'], plan, content, request)
                return plan

            step = 'older_c04_preview'
            older = await preview(step, c04, 'S02')
            step = 'c03_write_preview'
            plan = await preview(step, c03, '<niezdefiniowany>')
            step = 'unchanged_preview_audit'
            unchanged, content = await call('model_audit', audit_request)
            record(step, unchanged['source_fingerprint'] == before['source_fingerprint']
                   and unchanged['report_fingerprint'] == before['report_fingerprint'], unchanged, content, audit_request)
            print(plan['report_text'])
            print('Zapiszemy tylko C03 (12000,0): niezdefiniowany -> S03. C04 pozostanie S02.')
            print('Starszy plan C04 -> S03 ma zostac odrzucony. Nie edytuj modelu ani nie koncz hosta podczas testu.')
            if confirm('Wpisz SPRAWDZ KONFLIKT po sprawdzeniu kopii i jednej zmiany C03: ').strip() != 'SPRAWDZ KONFLIKT':
                report.update(state='cancelled', message='Owner cancelled. No Apply requested.')
                return report
            step = 'c03_revalidate'
            review = {'action': 'revalidate', 'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash']}
            check, content = await call('apply_office_standard', review)
            record(step, check.get('state') == 'unchanged' and check.get('evaluation_apply_available') is True,
                   check, content, review)
            request = {**review, 'action': 'apply', 'execution_id': uuid4().hex,
                       'acknowledgement': 'disposable_copy_reviewed_plan'}
            pointer = {'state': 'apply_pending', 'execution_id': request['execution_id'],
                       'tool': 'apply_office_standard', 'apply_request': request, 'expected_changes': 1, 'steps': []}
            report.update(execution_id=request['execution_id'], apply_request=copy.deepcopy(request))
            save(path, report)
            persist_pointer()
            step, pending = 'c03_apply_readback', True
            result, content = await call('apply_office_standard', request)
            pointer['state'] = result.get('state', 'unknown')
            if result.get('state') == 'rejected' and result.get('native_setters_started') is False:
                pending = False
                pointer['native_setters_started'] = False
                persist_pointer()
                report.update(state='rejected', native_setters_started=False, message=result['report_text'])
                report['steps'].append({'name': step, 'ok': False, 'response': result, 'mcp_content': content})
                return report
            persist_pointer()
            record(step, result.get('state') == 'completed' and result.get('execution_id') == request['execution_id']
                   and result.get('audited_fields_match_plan') is True
                   and [o['state'] for o in result.get('outcomes', [])] == ['applied']
                   and result['outcomes'][0]['readback'] == {'status': 'observed', 'value': 'S03'}
                   and result['audit_after']['coverage']['audit_complete'] is True
                   and result['audit_after']['counts']['findings'] == before['counts']['findings'] - 1,
                   result, content, request)
            pending = False
            # New identity for the deliberately rejected stale request; the C03
            # recovery pointer remains untouched and identifies the only write.
            stale = {'action': 'apply', 'plan_id': older['plan_id'], 'plan_hash': older['plan_hash'],
                     'execution_id': uuid4().hex, 'acknowledgement': 'disposable_copy_reviewed_plan'}
            report['stale_apply_request'] = copy.deepcopy(stale)
            save(path, report)
            step, pending = 'older_c04_apply_rejected', True
            rejection, content = await call('apply_office_standard', stale)
            record(step, rejection.get('state') == 'rejected' and rejection.get('native_setters_started') is False
                   and rejection.get('error', {}).get('code') == 'plan_expired', rejection, content, stale)
            pending = False
            step = 'excluded_peer_source_conflict'
            inspect = {'action': 'revalidate', 'plan_id': older['plan_id'], 'plan_hash': older['plan_hash']}
            conflict, content = await call('apply_office_standard', inspect)
            record(step, conflict.get('state') == 'conflict' and conflict.get('read_only') is True
                   and conflict.get('source_unchanged') is False and conflict.get('plan_invalidated') is True
                   and conflict.get('invalidation_reason') == 'execution_started'
                   and conflict.get('evaluation_apply_available') is False
                   and conflict['current_source_fingerprint'] != older['source_fingerprint']
                   and conflict['current_source_fingerprint'] == result['audit_after']['source_fingerprint']
                   and conflict['current_audit_report_fingerprint'] != older['audit_report_fingerprint']
                   and conflict['current_audit_report_fingerprint'] == result['audit_after']['report_fingerprint'],
                   conflict, content, inspect)
            step = 'audit_after_rejection'
            after, content = await call('model_audit', audit_request)
            c04_marks = [c['evidence']['raw'] for c in after['checks']
                         if c['rule_id'] == 'QA-001' and c['ref']['model_uuid'] == c04]
            record(step, after['coverage']['audit_complete'] is True
                   and after['source_fingerprint'] == result['audit_after']['source_fingerprint']
                   and after['report_fingerprint'] == result['audit_after']['report_fingerprint']
                   and c04_marks == [{'status': 'observed', 'value': 'S02'}], after, content, audit_request)
            step = 'health_after'
            last, content = await call('allplan_health')
            record(step, last.get('ok') is True and last['runtime']['host_session_id'] == session
                   and last.get('mcp_package_version') == expected
                   and last['runtime']['bridge_package']['version'] == expected
                   and last['runtime']['installed_bridge_integrity']['status'] == 'verified', last, content)
            report.update(state='ready_for_ui_observation', message='Observe C03=S03, C04/C02=S02 and unchanged other elements. '
                          'Then one native Undo restores C03; use M3 Conflict Recover only. Partial/unknown native outcomes remain a separate gate.')
    except Exception as exc:
        report.update(state='unknown' if pending else 'stopped' if report.get('execution_id') else 'blocked',
                      message=str(exc) + '. Preserve logs. If Apply was sent, use M3 Conflict Recover only; do not rerun this launcher.')
        if pointer is not None and pending:
            # The stale probe has its own ID in the report; never misidentify it
            # as the C03 execution or silently retry either request.
            if step == 'older_c04_apply_rejected':
                report['uncertain_stale_execution_id'] = report['stale_apply_request']['execution_id']
                pointer['uncertain_stale_execution_id'] = report['uncertain_stale_execution_id']
                persist_pointer()
                report['message'] += ' Inspect the separately saved stale execution ID with local Codex before any further write.'
            else:
                pointer['state'] = 'unknown'
                persist_pointer()
        if not report['steps'] or report['steps'][-1]['name'] != step:
            report['steps'].append({'name': step, 'ok': False})
    finally:
        save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'recover'])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--execution', type=Path, default=Path('logs/m3-last-conflict-execution.json'))
    args = parser.parse_args()
    path = args.output or Path('logs') / ('m3-conflict-' + args.action + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    url = os.getenv('MCP_URL', 'http://127.0.0.1:8888/mcp')
    if args.action == 'check':
        report = asyncio.run(collect_conflict(url, path))
    else:
        report = asyncio.run(recover_workflow(url, path, json.loads(args.execution.read_text(encoding='utf-8'))))
    print('M3 conflict: ' + report['state'] + '. JSON/TXT: ' + str(path.resolve()))
    print(report.get('message', ''))
    if report['state'] not in {'ready_for_ui_observation', 'cancelled', 'rejected'}:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
