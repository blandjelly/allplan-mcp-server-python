"""Read-only owner gate for versioned standards and selected repair previews."""
import argparse
import asyncio
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from fastmcp import Client

from .office_standard import load_office_standard
from .repair_diagnostics import save


async def collect_standard_preview(mcp_url, path):
    report = {'state': 'preflight', 'read_only': True, 'steps': [], 'allplan_acceptance': 'not_run'}
    step = 'health_preflight'
    try:
        async with Client(mcp_url, timeout=30) as client:
            health = (await client.call_tool('allplan_health')).data
            expected = version('allplan-mcp-server')
            runtime = health['runtime']
            ok = (health.get('ok') is True and health.get('mcp_package_version') == expected
                  and runtime.get('bridge_package', {}).get('version') == expected
                  and runtime.get('installed_bridge_integrity', {}).get('status') == 'verified'
                  and {'apply_office_standard', 'rule_based_edit'} <= {t.name for t in await client.list_tools()})
            report['steps'].append({'name': step, 'ok': ok, 'response': health})
            if not ok:
                raise ValueError('Package/integrity/tool preflight differs; no preview requested.')
            audit_request = {'profile_id': 'native-model-qa-demo', 'scope': {
                'drawing_files': [101], 'include_passive': False, 'visibility': 'api_select_all'}}
            step = 'audit_before'
            before = (await client.call_tool('model_audit', {'request': audit_request})).data
            ok = (before['coverage']['audit_complete'] is True and before['counts']['elements'] == 6
                  and before['counts']['findings'] == 3)
            report['steps'].append({'name': step, 'ok': ok, 'response': before})
            if not ok:
                raise ValueError('Use the retained repaired six-column copy; audit must be complete with 3 findings.')
            s06 = [c['ref']['model_uuid'] for c in before['checks'] if c['rule_id'] == 'QA-001'
                   and c['evidence']['raw'].get('value') == 'S06']
            if len(s06) != 1:
                raise ValueError('S06 must identify exactly one audited Column; no selected preview requested.')
            standard = load_office_standard()
            structure_layer = before['profile_binding']['layers']['structure']['value']['layer_id']
            scenarios = [
                ('office_standard', 'apply_office_standard', {
                    'action': 'preview', 'standard_id': standard['standard_id'],
                    'standard_version': standard['standard_version'], 'scope': audit_request['scope']}),
                ('selected_with_exception', 'rule_based_edit', {
                    'action': 'preview', 'audit': audit_request, 'repairs': standard['repairs'],
                    'selection': {'where': {'field': 'layer_id', 'op': 'eq', 'value': structure_layer},
                                  'exclude_model_uuids': s06}}),
                ('empty_selection', 'rule_based_edit', {
                    'action': 'preview', 'audit': audit_request, 'repairs': standard['repairs'],
                    'selection': {'where': {'field': 'layer_id', 'op': 'ne', 'value': structure_layer}}}),
            ]
            for step, tool, request in scenarios:
                plan = (await client.call_tool(tool, {'request': request})).data
                ok = (plan.get('state') == 'preview_ready' and plan.get('read_only') is True
                      and plan.get('apply_available') is False and plan.get('evaluation_apply_available') is False
                      and plan['counts'] == {'changes': 0, 'excluded_findings': 3, 'audit_findings': 3}
                      and plan['source_fingerprint'] == before['source_fingerprint']
                      and plan['audit_report_fingerprint'] == before['report_fingerprint'])
                if step == 'office_standard':
                    ok = ok and plan['workflow']['standard_fingerprint'] == standard['standard_fingerprint']
                else:
                    counts = plan['selection_result']
                    ok = ok and counts == ({'selected_elements': 5, 'predicate_false': 0,
                                           'excluded_elements': 1, 'predicate_not_checked': 0}
                                          if step == 'selected_with_exception' else
                                          {'selected_elements': 0, 'predicate_false': 6,
                                           'excluded_elements': 0, 'predicate_not_checked': 0})
                report['steps'].append({'name': step, 'ok': ok, 'request': request, 'response': plan})
                if not ok:
                    raise ValueError('Standard/selected preview differs; no write requested.')
                step += '_revalidate'
                check = (await client.call_tool('fix_model_issues', {'request': {
                    'action': 'revalidate', 'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash']}})).data
                ok = (check.get('state') == 'unchanged' and check.get('read_only') is True
                      and check.get('source_unchanged') is True and check.get('evaluation_apply_available') is False)
                report['steps'].append({'name': step, 'ok': ok, 'response': check})
                if not ok:
                    raise ValueError('Plan changed/expired; no further preview requested.')
            step = 'audit_after'
            after = (await client.call_tool('model_audit', {'request': audit_request})).data
            ok = (after['report_fingerprint'] == before['report_fingerprint']
                  and after['source_fingerprint'] == before['source_fingerprint'])
            report['steps'].append({'name': step, 'ok': ok, 'response': after})
            step = 'health_after'
            last = (await client.call_tool('allplan_health')).data
            ok = last.get('ok') is True and last['runtime']['host_session_id'] == runtime['host_session_id']
            report['steps'].append({'name': step, 'ok': ok, 'response': last})
            report['state'] = 'ready_for_ui_observation' if all(s['ok'] for s in report['steps']) else 'blocked'
            report['message'] = 'Read-only standard/selection gate. Observe unchanged values and appearance; no Apply, Recover or Undo requested.'
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
    path = args.output or Path('logs') / ('m3-standards-preview-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
    report = asyncio.run(collect_standard_preview('http://127.0.0.1:8888/mcp', path))
    print(f"M3 standards: {report['state']}. JSON/TXT: {path.resolve()}")
    print(report.get('message', ''))
    if report['state'] != 'ready_for_ui_observation':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
