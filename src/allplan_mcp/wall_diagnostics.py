"""Read one native Wall; persist the pending request and stop before any edits."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastmcp import Client
from .column_layer_diagnostics import health


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
    lines = ['M4 Wall native properties: ' + report['state'], 'No model setters requested.']
    lines.extend(step['name'] + ': ' + step['state'] for step in report['steps'])
    if report.get('message'):
        lines.append(report['message'])
    path.with_suffix('.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')


async def run(url, path, *, drawing_file=101, model_uuid=None):
    report = {'schema_version': 'm4-wall-owner-1', 'state': 'collecting', 'steps': [],
              'allplan_acceptance': 'not_run', 'model_setters_requested': False,
              'automatic_retry': False, 'native_trace_required': 'Local/.allplan-mcp/logs/m4-native-probe.jsonl'}

    async def call(client, name, tool, request=None):
        step = {'name': name, 'tool': tool, 'request': request, 'state': 'request_pending'}
        report['steps'].append(step)
        save(path, report)
        response = (await client.call_tool(tool, {'request': request} if request is not None else {})).data
        step.update(state='response_received', response=response)
        save(path, report)
        return response

    try:
        async with Client(url, timeout=90) as client:
            session = health(await call(client, 'health_before', 'allplan_health'))
            request = {'phase': 'wall_sample', 'drawing_file': drawing_file}
            if model_uuid is not None:
                request['model_uuid'] = model_uuid
            result = await call(client, 'one_wall_sample', 'model_property_probe', request)
            # A structured unsupported/not_checked reply is still bracketed by
            # health; a lost reply is never followed by another native request.
            health(await call(client, 'health_after', 'allplan_health'), session)
            if (result.get('state') != 'observed' or result.get('read_only') is not True
                    or result.get('usable_for_write') is not False
                    or result.get('counts', {}).get('sampled_walls') != 1
                    or result.get('sample', {}).get('tier_count') != 1):
                report.update(state='blocked', message='Odczyt sciany niepelny lub poza zakresem. Zachowaj raport; nie ponawiaj proby.')
            else:
                sample = result['sample']
                report.update(state='awaiting_owner_observation', message=(
                    f"Sciana {sample['ref']['model_uuid']}: grubosc API {sample['total_thickness_mm']['value']} mm; "
                    f"material natywny: {sample['native_material']['value']!r}. "
                    'Porownaj z UI. Nie zmieniono modelu; zapis C35 pozostaje niedostepny.'))
    except Exception as exc:
        report.update(state='blocked', message=str(exc))
    finally:
        save(path, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--drawing-file', type=int, default=101)
    parser.add_argument('--model-uuid')
    parser.add_argument('--url', default='http://127.0.0.1:8888/mcp')
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = Path('logs') / f'wall-properties-{stamp}.json'
    report = asyncio.run(run(args.url, path, drawing_file=args.drawing_file, model_uuid=args.model_uuid))
    print(report['state'], report.get('message', ''), '\nRaport:', path.resolve())
    return 0 if report['state'] == 'awaiting_owner_observation' else 1


if __name__ == '__main__':
    raise SystemExit(main())
