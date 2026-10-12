"""Owner gate for two separately reviewed single-target standard/selected writes."""
import argparse
import asyncio
from datetime import datetime, timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
from uuid import uuid4

from fastmcp import Client

from .repair_diagnostics import save


async def collect_workflow_apply(mcp_url, path, confirm=input):
    report = {'state': 'preflight', 'steps': [], 'allplan_acceptance': 'not_run', 'executions': []}
    step = 'health_preflight'
    pending = False
    rejected = False
    try:
        async with Client(mcp_url, timeout=90) as client:
            async def call(tool, request=None):
                result = await client.call_tool(tool, {'request': request} if request is not None else {})
                return result.data, [{'type': block.type, 'text': block.text}
                                     for block in result.content if block.type == 'text']

            def record(name, ok, response, content, request=None):
                item = {'name': name, 'ok': bool(ok), 'response': response, 'mcp_content': content}
                if request is not None:
                    item['request'] = request
                report['steps'].append(item)
                save(path, report)
                if not ok:
                    raise ValueError(name + ' did not satisfy the declared gate')

            health, content = await call('allplan_health')
            expected = version('allplan-mcp-server')
            runtime = health['runtime']
            record(step, health.get('ok') is True and health.get('mcp_package_version') == expected
                   and runtime.get('bridge_package', {}).get('version') == expected
                   and runtime.get('installed_bridge_integrity', {}).get('status') == 'verified', health, content)
            session = runtime['host_session_id']
            scope = {'drawing_files': [101], 'include_passive': False, 'visibility': 'api_select_all'}
            audit_request = {'profile_id': 'native-model-qa-demo', 'scope': scope}
            step = 'audit_before'
            before, content = await call('model_audit', audit_request)
            record(step, before['coverage']['audit_complete'] and before['counts']['elements'] == 6
                   and before['counts']['findings'] == 5 and before['counts']['not_checked'] == 0
                   and sorted(f['rule_id'] for f in before['findings']) == ['QA-001', 'QA-002', 'QA-002', 'QA-003', 'QA-004'],
                   before, content, audit_request)
            targets = {}
            for rule, mark, center in [('QA-003', 'S05', [6000, 6000, 1500]),
                                       ('QA-004', 'S06', [12000, 6000, 1500])]:
                candidates = [f for f in before['findings'] if f['rule_id'] == rule
                              and f['locator']['mark'].get('value') == mark
                              and f['locator']['center_mm']['status'] == 'observed'
                              and all(abs(a - b) <= 1 for a, b in zip(f['locator']['center_mm']['value'], center))]
                if len(candidates) != 1:
                    raise ValueError('Expected the retained S05 layer and S06 NWE defects; no write requested')
                targets[rule] = candidates[0]
            if targets['QA-004']['evidence']['raw'].get('value') != 'NWE':
                raise ValueError('S06 must have reviewed old status NWE; no write requested')
            s05 = targets['QA-003']['ref']['model_uuid']
            s06 = targets['QA-004']['ref']['model_uuid']
            scenarios = [
                ('standard', 'apply_office_standard', {'action': 'preview',
                 'standard_id': 'native-model-qa-demo-layer-status', 'standard_version': '1.0.0',
                 'scope': scope, 'selection': {'where': {'field': 'layer_id', 'op': 'exists'},
                                             'exclude_model_uuids': [s06]}}, 'QA-003', s05, 'NAPRAW STANDARD', 4),
                ('selected', 'rule_based_edit', {'action': 'preview', 'audit': audit_request,
                 'repairs': [{'rule_id': 'QA-004', 'value': 'NEW'}],
                 'selection': {'where': {'field': 'status', 'op': 'eq', 'value': 'NWE'},
                               'exclude_model_uuids': [s05]}}, 'QA-004', s06, 'NAPRAW REGULE', 3),
            ]
            for name, tool, preview_request, rule, target, phrase, findings in scenarios:
                step = name + '_preview'
                plan, content = await call(tool, preview_request)
                changes = plan.get('changes', [])
                record(step, plan.get('state') == 'preview_ready' and plan.get('read_only') is True
                       and plan.get('evaluation_apply_available') is True and len(changes) == 1
                       and changes[0]['rule_id'] == rule and changes[0]['ref']['model_uuid'] == target
                       and plan['selection_result']['excluded_elements'] == 1,
                       plan, content, preview_request)
                print(plan['report_text'])
                print('Tylko sprawdzona jednorazowa kopia projektu. Ten krok zapisze jedna wyswietlona zmiane.')
                if confirm('Wpisz ' + phrase + ' po sprawdzeniu celu i kopii projektu: ').strip() != phrase:
                    report.update(state='cancelled' if not report['executions'] else 'stopped',
                                  message='Owner stopped the gate. Earlier completed writes remain; no automatic rollback or retry.')
                    return report
                execution_id = uuid4().hex
                request = {'action': 'apply', 'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash'],
                           'execution_id': execution_id, 'acknowledgement': 'disposable_copy_reviewed_plan'}
                pointer = {'state': 'apply_pending', 'execution_id': execution_id, 'tool': tool,
                           'apply_request': request, 'expected_changes': 1, 'steps': []}
                def persist_pointer():
                    save(path.parent / ('m3-workflow-execution-' + execution_id + '.json'), pointer)
                    save(path.parent / 'm3-last-workflow-execution.json', pointer)
                report['executions'].append(pointer)
                report.update(state='apply_pending', execution_id=execution_id)
                save(path, report)
                persist_pointer()
                step = name + '_apply'
                pending = True
                response, content = await call(tool, request)
                if response.get('state') == 'rejected' and response.get('native_setters_started') is False:
                    pending = False
                    rejected = True
                    pointer.update(state='rejected', native_setters_started=False)
                    persist_pointer()
                    record(step, False, response, content, request)
                pending = any(o.get('state') == 'unknown' for o in response.get('outcomes', []))
                pointer.update(state=response.get('state', 'unknown'))
                persist_pointer()
                record(step, response.get('state') == 'completed' and response.get('execution_id') == execution_id
                       and response.get('audited_fields_match_plan') is True
                       and [o['state'] for o in response.get('outcomes', [])] == ['applied']
                       and response.get('audit_after', {}).get('counts', {}).get('findings') == findings,
                       response, content, request)
                step = name + '_replay'
                replay, content = await call(tool, request)
                record(step, replay.get('replayed') is True and replay.get('read_only') is True
                       and replay.get('outcomes') == response['outcomes'], replay, content, request)
            step = 'audit_after'
            after, content = await call('model_audit', audit_request)
            record(step, after['coverage']['audit_complete'] and after['counts']['elements'] == 6
                   and after['counts']['findings'] == 3 and after['counts']['not_checked'] == 0
                   and sorted(f['rule_id'] for f in after['findings']) == ['QA-001', 'QA-002', 'QA-002'],
                   after, content, audit_request)
            step = 'health_after'
            last, content = await call('allplan_health')
            record(step, last.get('ok') is True and last['runtime']['host_session_id'] == session
                   and last.get('mcp_package_version') == expected
                   and last['runtime']['bridge_package']['version'] == expected
                   and last['runtime']['installed_bridge_integrity']['status'] == 'verified', last, content)
            report.update(state='ready_for_ui_observation',
                          message='Observe S05 structure layer, S06 NEW, unchanged marks/other elements and uninterrupted host. No Undo or repeated gate requested.')
    except Exception as exc:
        if not report['steps'] or report['steps'][-1]['name'] != step:
            report['steps'].append({'name': step, 'ok': False, 'message': str(exc)})
        report.update(state='rejected' if rejected else 'unknown' if pending else 'stopped' if report['executions'] else 'blocked',
                      message=str(exc) + '. No automatic retry. Preserve logs; use workflow recover only if a write has an uncertain outcome.')
    finally:
        save(path, report)
    return report


async def recover_workflow(mcp_url, path, previous):
    report = {'state': 'recovery_pending', 'read_only': True, 'steps': [],
              'execution_id': previous['execution_id'], 'allplan_acceptance': 'not_run'}
    try:
        if previous.get('state') == 'rejected' and previous.get('native_setters_started') is False:
            report.update(state='rejected', message='This request was rejected before setters; no recovery call sent.')
            return report
        async with Client(mcp_url, timeout=90) as client:
            request = {'action': 'recover', 'execution_id': previous['execution_id']}
            result = await client.call_tool('fix_model_issues', {'request': request})
            response = result.data
            observations = response.get('recovery', {}).get('observations', [])
            ok = response.get('read_only') is True and len(observations) == previous['expected_changes']
            report['steps'].append({'name': 'recover_read_only', 'ok': ok, 'request': request,
                                    'response': response, 'mcp_content': [{'type': b.type, 'text': b.text}
                                     for b in result.content if b.type == 'text']})
            resolved = ok and all(o['state'] in {'old_value_observed', 'new_value_observed'} for o in observations)
            report.update(state='ready_for_ui_observation' if resolved else 'stopped',
                          message='Recovery reads current values only. It does not replay Apply, resume skipped writes or request Undo.')
    except Exception as exc:
        report.update(state='blocked', message=str(exc) + '. No write or retry requested.')
    finally:
        save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['apply', 'recover'])
    parser.add_argument('--output', type=Path)
    parser.add_argument('--execution', type=Path, default=Path('logs/m3-last-workflow-execution.json'))
    args = parser.parse_args()
    path = args.output or Path('logs') / ('m3-workflow-' + args.action + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    url = os.getenv('MCP_URL', 'http://127.0.0.1:8888/mcp')
    if args.action == 'apply':
        report = asyncio.run(collect_workflow_apply(url, path))
    else:
        report = asyncio.run(recover_workflow(url, path, json.loads(args.execution.read_text(encoding='utf-8'))))
    print('M3 workflow: ' + report['state'] + '. JSON/TXT: ' + str(path.resolve()))
    print(report.get('message', ''))
    if report['state'] not in {'ready_for_ui_observation', 'cancelled', 'rejected'}:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
