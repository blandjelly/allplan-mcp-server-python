"""Read-only owner gate for explicit mark repairs and excluded-peer collisions."""
import argparse
import asyncio
import copy
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from fastmcp import Client

from .repair_diagnostics import save


async def collect_mark_preview(mcp_url, path):
    report = {'state': 'preflight', 'read_only': True, 'steps': [], 'allplan_acceptance': 'not_run'}
    step = 'health_preflight'
    try:
        async with Client(mcp_url, timeout=30) as client:
            async def call(tool, request=None):
                result = await client.call_tool(tool, {'request': request} if request is not None else {})
                return result.data, [{'type': block.type, 'text': block.text}
                                     for block in result.content if block.type == 'text']

            def record(name, ok, response, content, request=None):
                item = {'name': name, 'ok': bool(ok), 'response': response, 'mcp_content': content}
                if request is not None:
                    item['request'] = copy.deepcopy(request)
                report['steps'].append(item)
                if not ok:
                    raise ValueError(name + ' differs from the retained-copy read-only contract.')

            health, content = await call('allplan_health')
            expected = version('allplan-mcp-server')
            runtime = health['runtime']
            ok = (health.get('ok') is True and health.get('mcp_package_version') == expected
                  and runtime.get('bridge_package', {}).get('version') == expected
                  and runtime.get('installed_bridge_integrity', {}).get('status') == 'verified'
                  and {'fix_model_issues', 'rule_based_edit'} <= {t.name for t in await client.list_tools()})
            record(step, ok, health, content)
            audit_request = {'profile_id': 'native-model-qa-demo', 'scope': {
                'drawing_files': [101], 'include_passive': False, 'visibility': 'api_select_all'}}
            step = 'audit_before'
            before, content = await call('model_audit', audit_request)
            findings = before['findings']
            ok = (before['coverage']['audit_complete'] is True and before['counts']['elements'] == 6
                  and before['counts']['findings'] == 3 and before['counts']['not_checked'] == 0
                  and sorted(f['rule_id'] for f in findings) == ['QA-001', 'QA-002', 'QA-002'])
            record(step, ok, before, content, audit_request)
            missing = [f for f in findings if f['rule_id'] == 'QA-001'
                       and f['evidence']['raw'].get('value') == '<niezdefiniowany>']
            duplicate = [f for f in findings if f['rule_id'] == 'QA-002'
                         and f['evidence']['raw'].get('value') == 'S02'
                         and f['locator']['center_mm']['status'] == 'observed'
                         and all(abs(a - b) <= 1 for a, b in zip(f['locator']['center_mm']['value'], [0, 6000, 1500]))]
            s06 = [c['ref']['model_uuid'] for c in before['checks'] if c['rule_id'] == 'QA-001'
                   and c['evidence']['raw'].get('value') == 'S06']
            if len(missing) != 1 or len(duplicate) != 1 or len(s06) != 1:
                raise ValueError('Expected the retained missing C03, duplicate C04 at (0,6000) mm and S06; no mark preview requested.')
            if (missing[0]['locator']['center_mm']['status'] != 'observed'
                    or not all(abs(a - b) <= 1 for a, b in zip(missing[0]['locator']['center_mm']['value'], [12000, 0, 1500]))):
                raise ValueError('Missing mark location differs from retained C03; no mark preview requested.')
            assignments = [
                {'rule_id': 'QA-001', 'model_uuid': missing[0]['ref']['model_uuid'], 'value': 'S03'},
                {'rule_id': 'QA-002', 'model_uuid': duplicate[0]['ref']['model_uuid'], 'value': 'S04'},
            ]
            collision = copy.deepcopy(assignments)
            collision[0]['value'] = 'S06'
            selection = {'where': {'field': 'layer_id', 'op': 'exists'}}
            scenarios = [
                ('explicit_marks', 'fix_model_issues', {'action': 'preview', 'audit': audit_request, 'repairs': assignments}),
                ('mark_exception', 'rule_based_edit', {'action': 'preview', 'audit': audit_request, 'repairs': assignments,
                    'selection': {**selection, 'exclude_model_uuids': [assignments[1]['model_uuid']]}}),
                ('excluded_peer_collision', 'rule_based_edit', {'action': 'preview', 'audit': audit_request, 'repairs': collision,
                    'selection': {**selection, 'exclude_model_uuids': s06}}),
            ]
            mark_resource = before['profile_binding']['attributes']['mark']['value']
            for step, tool, request in scenarios:
                plan, content = await call(tool, request)
                mark_check = plan['mark_validation']
                expected_assignments = {c['model_uuid']: c['value'] for c in request['repairs']
                                        if c['model_uuid'] not in request.get('selection', {}).get('exclude_model_uuids', [])}
                actual_assignments = {c['ref']['model_uuid']: c['new_value'] for c in plan['changes']}
                is_collision = step == 'excluded_peer_collision'
                ok = (plan.get('state') == ('conflict' if is_collision else 'preview_ready')
                      and plan.get('read_only') is True and all(plan.get(k) is False
                          for k in ('apply_available', 'evaluation_apply_available', 'usable_for_write'))
                      and actual_assignments == expected_assignments and len(plan['changes']) == len(expected_assignments)
                      and all(c['operation'] == 'set_attribute' and c['resource'] == mark_resource
                              and c['field'] == f"attribute:{mark_resource['attribute_id']}" for c in plan['changes'])
                      and plan['counts'] == {'changes': len(expected_assignments),
                          'excluded_findings': 3 - len(expected_assignments), 'audit_findings': 3}
                      and mark_check['state'] == ('conflict' if is_collision else 'validated')
                      and mark_check['checked_elements'] == 6 and mark_check['not_checked_elements'] == 0
                      and mark_check['collision_groups'] == (1 if is_collision else 0)
                      and mark_check['proposed_marks'] == len(expected_assignments)
                      and mark_check['remaining_missing_marks'] == 0
                      and mark_check['remaining_duplicate_groups'] == (0 if step == 'explicit_marks' else 1)
                      and mark_check['uses_full_snapshot'] is True
                      and plan['source_fingerprint'] == before['source_fingerprint']
                      and plan['audit_report_fingerprint'] == before['report_fingerprint'])
                if step != 'explicit_marks':
                    ok = ok and plan['selection_result'] == {'selected_elements': 5, 'predicate_false': 0,
                                                            'excluded_elements': 1, 'predicate_not_checked': 0}
                if is_collision:
                    collisions = mark_check['collisions']
                    ok = ok and len(collisions) == 1 and collisions[0]['normalized_value'] == 'S06'
                    ok = ok and {ref['model_uuid'] for ref in collisions[0]['refs']} == {assignments[0]['model_uuid'], s06[0]}
                record(step, ok, plan, content, request)
                step += '_revalidate'
                request = {'action': 'revalidate', 'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash']}
                check, content = await call('fix_model_issues', request)
                ok = (check.get('state') == 'unchanged' and check.get('source_unchanged') is True
                      and check.get('read_only') is True and check.get('evaluation_apply_available') is False
                      and check['current_source_fingerprint'] == before['source_fingerprint']
                      and check['current_audit_report_fingerprint'] == before['report_fingerprint'])
                record(step, ok, check, content, request)
            step = 'audit_after'
            after, content = await call('model_audit', audit_request)
            ok = (after['report_fingerprint'] == before['report_fingerprint']
                  and after['source_fingerprint'] == before['source_fingerprint'])
            record(step, ok, after, content, audit_request)
            step = 'health_after'
            last, content = await call('allplan_health')
            ok = (last.get('ok') is True and last['runtime']['host_session_id'] == runtime['host_session_id']
                  and last.get('mcp_package_version') == expected
                  and last['runtime']['bridge_package']['version'] == expected
                  and last['runtime']['installed_bridge_integrity']['status'] == 'verified')
            record(step, ok, last, content)
            report.update(state='ready_for_ui_observation',
                          message='Read-only mark gate: proposed S03/S04, exception and expected S06 collision. Observe unchanged model/host. No Apply, Recover or Undo requested.')
    except Exception as exc:
        report.update(state='blocked', message=str(exc) + '. No mutation or automatic retry requested.')
        if not report['steps'] or report['steps'][-1]['name'] != step:
            report['steps'].append({'name': step, 'ok': False})
    finally:
        save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    path = args.output or Path('logs') / ('m3-marks-preview-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    report = asyncio.run(collect_mark_preview('http://127.0.0.1:8888/mcp', path))
    print(f"M3 marks: {report['state']}. JSON/TXT: {path.resolve()}")
    print(report.get('message', ''))
    if report['state'] != 'ready_for_ui_observation':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
