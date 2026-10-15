"""No-code Column -> W1 workflow, durable pending requests and read-only recovery."""
from __future__ import annotations
import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4
from fastmcp import Client


def save(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    if os.name != 'nt':
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    path.with_suffix('.txt').write_text(
        'M4 Column -> W1: ' + report['state'] + '\n' + report.get('message', '') + '\n' +
        '\n'.join(s['name'] + ': ' + s['state'] for s in report['steps']) + '\n', encoding='utf-8')


def health(response, session=None):
    runtime = response.get('runtime', {})
    current = runtime.get('host_session_id')
    expected = version('allplan-mcp-server')
    if (response.get('ok') is not True or response.get('mcp_package_version') != expected
            or runtime.get('bridge_package', {}).get('version') != expected
            or runtime.get('installed_bridge_integrity', {}).get('status') != 'verified'
            or runtime.get('compatibility', {}).get('major_matches') is not True
            or not current or (session and current != session)):
        raise ValueError('Wersja/integralnosc hosta lub sesja rozni sie od zainstalowanego pakietu. Uruchom ponownie host.')
    return current


async def run(url, path, *, drawing_file=101, attribute_names=None, confirm=None, recover_from=None):
    report = {'schema_version': 'm4-column-layer-owner-1', 'state': 'collecting', 'steps': [],
              'allplan_acceptance': 'not_run', 'native_selection': 'highlight_only', 'model_setters_requested': False}
    sent = False
    async def call(client, name, tool, request=None):
        step = {'name': name, 'tool': tool, 'request': request, 'state': 'request_pending'}
        report['steps'].append(step)
        save(path, report)
        result = (await client.call_tool(tool, {'request': request} if request is not None else {})).data
        step.update(state='response_received', response=result)
        save(path, report)
        return result
    try:
        async with Client(url, timeout=90) as client:
            session = health(await call(client, 'health_before', 'allplan_health'))
            if recover_from is not None:
                previous = json.loads(Path(recover_from).read_text(encoding='utf-8'))
                request = previous['apply_request']
                report['apply_request'] = request  # carry identity across recovery/Undo inspection
                if previous.get('state') == 'rejected':
                    report.update(state='rejected', message='Poprzednia proba zostala odrzucona przed zapisem. Nie wymaga Recover.')
                    return report
                result = await call(client, 'recover_original_id', 'column_layer', {'action': 'recover', 'execution_id': request['execution_id']})
                report['state'] = 'recovered' if result.get('read_only') is True else 'unknown'
            else:
                journal = await call(client, 'journal_before', 'fix_model_issues', {'action': 'inspect_journal'})
                if journal.get('state') != 'available':
                    raise ValueError('Dziennik blokuje nowe zmiany. Zachowaj logi i wykonaj Recover wskazanej operacji.')
                request = {'action': 'preview', 'drawing_file': drawing_file}
                if attribute_names:
                    request['attribute_names'] = attribute_names
                plan = await call(client, 'preview', 'column_layer', request)
                if (plan.get('evaluation_highlight_available') is not True
                        or (plan.get('state') != 'no_op' and plan.get('evaluation_apply_available') is not True)):
                    criteria = plan.get('criteria', {})
                    attribute = criteria.get('binding', {}).get('attribute', {})
                    states = {}
                    for check in criteria.get('checks', []):
                        if check.get('decision') == 'unknown':
                            state = check.get('value_state', 'unknown')
                            states[state] = states.get(state, 0) + 1
                    raise ValueError(
                        f"Plan niekompletny lub poza zakresem zapisu. Pole: {attribute.get('name', '?')} "
                        f"(ID {attribute.get('attribute_id', '?')}); nierozstrzygniete odczyty: {states}. "
                        'Oczekiwane pole to Klasa odporności ogniowej (np. F30/F60). '
                        'Brak pola w odczycie nie dowodzi pustej wartosci. Sprawdz criteria w raporcie; nic nie zmieniono.')
                refs = {'plan_id': plan['plan_id'], 'plan_hash': plan['plan_hash']}
                shown = await call(client, 'highlight_exact_targets', 'column_layer', {'action': 'highlight', **refs})
                if (shown.get('state') != 'submitted'
                        or shown.get('counts', {}).get('submitted_model_identities') != len(plan['highlight_targets'])):
                    raise ValueError('Wynik podswietlenia niepewny; nie wyslano Apply.')
                if plan.get('state') == 'no_op':
                    report.update(state='no_op', message=(
                        f"Dopasowane slupy do podswietlenia: {len(plan['highlight_targets'])}; zmian: 0. "
                        'Sa juz na W1 albo nie ma dopasowan. Nie wyslano Apply.'))
                else:
                    if confirm is None or not confirm(plan):
                        report.update(state='preview_only', message='Plan i podswietlenie gotowe; nie wyslano Apply.')
                    else:
                        request = {'action': 'apply', **refs, 'execution_id': uuid4().hex,
                                   'acknowledgement': 'disposable_copy_reviewed_plan'}
                        report.update(apply_request=request, model_setters_requested=True, state='apply_pending')
                        save(path, report)  # exact identity survives a lost response/process exit
                        sent = True
                        result = await call(client, 'apply', 'column_layer', request)
                        report['state'] = result.get('state', 'unknown')
                        if result.get('state') == 'completed':
                            if (result.get('audited_fields_match_plan') is not True
                                    or len(result.get('outcomes', [])) != len(plan['changes'])
                                    or not all(o['state'] == 'applied' for o in result['outcomes'])):
                                report['state'] = 'verification_failed'
                        if report['state'] not in {'completed', 'rejected'}:
                            report['message'] = 'Wynik wymaga Recover tego samego execution_id. Nie ponawiaj Apply.'
            health(await call(client, 'health_after', 'allplan_health'), session)
    except Exception as exc:
        report.update(state='unknown' if sent or recover_from is not None else 'blocked', message=str(exc))
    finally:
        save(path, report)
    return report


def confirm_plan(plan):
    binding = plan['criteria']['binding']
    print('Pole:', binding['attribute']['name'], '(ID', str(binding['attribute']['attribute_id']) + ')',
          '; warstwa:', binding['layer']['short_name'])
    print('Do podswietlenia:', len(plan['highlight_targets']), '; zmiany warstwy:', len(plan['changes']),
          '; juz na W1:', plan['criteria']['counts'].get('no_op', 0))
    for ref in plan['highlight_targets']:
        print('Dopasowany slup:', ref['model_uuid'])
    for change in plan['changes']:
        print('Rysunek', change['ref']['drawing_file'], 'slup', change['ref']['model_uuid'],
              'warstwa', change['old_value']['value'], '->', change['new_value'])
    print('Sprawdz podswietlone slupy w Allplanie. Slupy juz na W1 pozostaja podswietlone bez zapisu.')
    print('Testuj na kopii projektu. Zmiana warstwy dotyczy tylko powyzszej listy zmian.')
    return input('Wpisz ZMIEN, aby przypisac W1 (Enter pozostawia sam podglad): ').strip() == 'ZMIEN'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'recover'])
    parser.add_argument('--drawing-file', type=int, default=101)
    parser.add_argument('--attribute-name', action='append')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--url', default='http://127.0.0.1:8888/mcp')
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = Path('logs') / f'm4-column-layer-{args.action}-{stamp}.json'
    previous = args.report
    if args.action == 'recover' and previous is None:
        # Select the newest report with an Apply identity, never invent a new ID.
        reports = sorted(Path('logs').glob('m4-column-layer-*.json'), reverse=True)
        candidates = []
        for candidate in reports:
            try:
                if 'apply_request' in json.loads(candidate.read_text(encoding='utf-8')):
                    candidates.append(candidate)
            except (OSError, ValueError):
                print('Nieczytelny raport:', candidate, '; wskaz --report.'); return 1
        if not candidates:
            print('Brak raportu z execution_id do Recover.'); return 1
        previous = max(candidates, key=lambda p: p.stat().st_mtime_ns)
    report = asyncio.run(run(args.url, path, drawing_file=args.drawing_file, attribute_names=args.attribute_name,
                             confirm=confirm_plan, recover_from=previous if args.action == 'recover' else None))
    print(report['state'], report.get('message', ''), '\nRaport:', path.resolve())
    return 0 if report['state'] in {'completed', 'no_op', 'preview_only', 'recovered'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
