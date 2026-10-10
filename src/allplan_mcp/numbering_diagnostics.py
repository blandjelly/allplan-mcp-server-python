"""Owner-operated mark numbering gate; the durable identity precedes Apply."""
import copy
from importlib.metadata import version
from uuid import uuid4

from fastmcp import Client

from .repair_diagnostics import save


async def collect_numbering_apply(mcp_url, path, confirm=input):
    report = {'state': 'preflight', 'steps': [], 'allplan_acceptance': 'not_run'}
    step, pending = 'health_preflight', False
    pointer_path = path.parent / 'm3-last-numbering-execution.json'
    pointer = None
    try:
        async with Client(mcp_url, timeout=90) as client:
            async def call(tool, request=None):
                result = await client.call_tool(tool, {'request': request} if request is not None else {})
                return result.data, [{'type': b.type, 'text': b.text} for b in result.content if b.type == 'text']

            def record(name, ok, response, content, request=None):
                report['steps'].append({'name': name, 'ok': bool(ok), 'response': response,
                                        'mcp_content': content, 'request': copy.deepcopy(request)})
                save(path, report)
                if not ok:
                    raise ValueError(name + ' differs from the declared numbering gate')

            health, content = await call('allplan_health')
            runtime, expected = health['runtime'], version('allplan-mcp-server')
            record(step, health.get('ok') is True and health.get('mcp_package_version') == expected
                   and runtime.get('bridge_package', {}).get('version') == expected
                   and runtime.get('installed_bridge_integrity', {}).get('status') == 'verified', health, content)
            session = runtime['host_session_id']
            scope = {'drawing_files': [101], 'include_passive': False, 'visibility': 'api_select_all'}
            audit_request = {'profile_id': 'native-model-qa-demo', 'scope': scope}
            step = 'audit_before'
            before, content = await call('model_audit', audit_request)
            mark_findings = [f for f in before['findings'] if f['rule_id'] in {'QA-001', 'QA-002'}]
            record(step, before['coverage']['audit_complete'] is True and before['counts']['elements'] == 6
                   and before['counts']['not_checked'] == 0
                   and sorted(f['rule_id'] for f in mark_findings) == ['QA-001', 'QA-002', 'QA-002'], before, content, audit_request)
            # Establish actual marks in this project copy; the prior Undo state is irrelevant.
            expected_targets = {}
            for rule, old, new, center in [('QA-001', '<niezdefiniowany>', 'S03', [12000, 0, 1500]),
                                           ('QA-002', 'S02', 'S04', [0, 6000, 1500])]:
                matches = [f for f in mark_findings if f['rule_id'] == rule
                           and f['evidence']['raw'].get('value') == old
                           and f['locator']['center_mm']['status'] == 'observed'
                           and all(abs(a - b) <= 1 for a, b in zip(f['locator']['center_mm']['value'], center))]
                if len(matches) != 1:
                    raise ValueError('Expected retained C03/C04 defects; no write requested')
                expected_targets[matches[0]['ref']['model_uuid']] = (old, new)
            preview_request = {'action': 'preview', 'standard_id': 'native-model-qa-demo-mark-numbering',
                               'standard_version': '1.0.0', 'scope': scope}
            step = 'numbering_preview'
            plan, content = await call('apply_office_standard', preview_request)
            resource = before['profile_binding']['attributes']['mark']['value']
            def valid_plan(candidate):
                return (candidate.get('state') == 'preview_ready' and candidate.get('read_only') is True
                        and candidate.get('evaluation_apply_available') is True and len(candidate['changes']) == 2
                        and {c['ref']['model_uuid']: (c['old_value'].get('value'), c['new_value'])
                             for c in candidate['changes']} == expected_targets
                        and all(c['property_role'] == 'mark' and c['operation'] == 'set_attribute'
                                and c['resource'] == resource for c in candidate['changes'])
                        and candidate['mark_validation']['state'] == 'validated'
                        and candidate['mark_validation']['remaining_duplicate_groups'] == 0
                        and candidate['mark_validation']['remaining_missing_marks'] == 0
                        and candidate['numbering']['state'] == 'validated'
                        and candidate['source_fingerprint'] == before['source_fingerprint'])
            record(step, valid_plan(plan), plan, content, preview_request)
            step = 'deterministic_preview'
            repeated, content = await call('apply_office_standard', preview_request)
            record(step, valid_plan(repeated) and repeated['changes'] == plan['changes']
                   and repeated['numbering'] == plan['numbering'], repeated, content, preview_request)
            step = 'unchanged_preview_audit'
            unchanged, content = await call('model_audit', audit_request)
            record(step, unchanged['report_fingerprint'] == before['report_fingerprint'], unchanged, content, audit_request)
            print(plan['report_text'])
            print('Sprawdz jednorazowa kopie i cele: C03 (12000,0) -> S03, C04 (0,6000) -> S04.')
            print('Zmiana dotyczy danych atrybutu oznaczenia. Sprawdz oba pola w UI po tescie.')
            if confirm('Wpisz NUMERUJ KOPIE po sprawdzeniu tych dwoch zmian: ').strip() != 'NUMERUJ KOPIE':
                report.update(state='cancelled', message='Owner cancelled. No write requested.')
                return report
            step = 'numbering_revalidate'
            review = {'action': 'revalidate', 'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash']}
            check, content = await call('apply_office_standard', review)
            record(step, check.get('state') == 'unchanged' and check.get('evaluation_apply_available') is True,
                   check, content, review)
            execution_id = uuid4().hex
            request = {**review, 'action': 'apply', 'execution_id': execution_id,
                       'acknowledgement': 'disposable_copy_reviewed_plan'}
            pointer = {'state': 'apply_pending', 'execution_id': execution_id, 'tool': 'apply_office_standard',
                       'apply_request': request, 'expected_changes': 2, 'steps': []}
            report.update(execution_id=execution_id, apply_request=copy.deepcopy(request))
            save(path, report)
            save(path.parent / ('m3-numbering-execution-' + execution_id + '.json'), pointer)
            save(pointer_path, pointer)
            step, pending = 'numbering_apply_readback', True
            result, content = await call('apply_office_standard', request)
            if result.get('state') == 'rejected' and result.get('native_setters_started') is False:
                pending = False
                pointer.update(state='rejected', native_setters_started=False)
                report.update(state='rejected', native_setters_started=False, message=result['report_text'])
                report['steps'].append({'name': step, 'ok': False, 'response': result, 'mcp_content': content})
                save(pointer_path, pointer)
                return report
            ok = (result.get('state') == 'completed' and result.get('execution_id') == execution_id
                  and result.get('audited_fields_match_plan') is True
                  and [o['state'] for o in result.get('outcomes', [])] == ['applied', 'applied']
                  and result['audit_after']['coverage']['audit_complete'] is True
                  and result['audit_after']['counts']['findings'] == before['counts']['findings'] - 3
                  and not any(f['rule_id'] in {'QA-001', 'QA-002'} for f in result['audit_after']['findings']))
            if not ok:
                report.update(state='stopped', message='Inspect current values and use M3 Numbering Recover. No new Apply or rollback.')
                pointer['state'] = result.get('state', 'unknown')
                save(pointer_path, pointer)
                report['steps'].append({'name': step, 'ok': False, 'response': result, 'mcp_content': content})
                return report
            pending = False
            pointer['state'] = 'completed'
            save(pointer_path, pointer)
            record(step, ok, result, content, request)
            step = 'same_execution_read_only_replay'
            replay, content = await call('apply_office_standard', request)
            record(step, replay.get('read_only') is True and replay.get('replayed') is True
                   and replay.get('outcomes') == result['outcomes'], replay, content, request)
            step = 'numbering_noop_after'
            noop, content = await call('apply_office_standard', preview_request)
            record(step, noop.get('state') == 'preview_ready' and noop.get('changes') == []
                   and noop.get('evaluation_apply_available') is False, noop, content, preview_request)
            step = 'health_after'
            last, content = await call('allplan_health')
            record(step, last.get('ok') is True and last['runtime']['host_session_id'] == session
                   and last['runtime']['installed_bridge_integrity']['status'] == 'verified', last, content)
            report.update(state='ready_for_ui_observation', message='Inspect S03/S04 and unchanged other elements. '
                          'Then observe two separate native Undo steps on this copy and use M3 Numbering Recover; no automatic rollback.')
    except Exception as exc:
        report.update(state='unknown' if pending else 'stopped' if report.get('execution_id') else 'blocked',
                      message=str(exc) + '. Preserve logs. If Apply was sent, use M3 Numbering Recover only; do not restart this write launcher.')
        if pointer is not None and pending:
            pointer['state'] = 'unknown'
            save(pointer_path, pointer)
        if not report['steps'] or report['steps'][-1]['name'] != step:
            report['steps'].append({'name': step, 'ok': False})
    finally:
        save(path, report)
    return report
