"""Offline interpretation of one saved Wall probe. Never an executable plan."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

MAX_REPORT_BYTES = 4 * 1024 * 1024
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")


class EvidenceError(ValueError):
    pass


def _require(condition, reason):
    if not condition:
        raise EvidenceError(reason)


def _object(value, label):
    _require(isinstance(value, dict), label + "_not_an_object")
    return value


def _uuid(value):
    return isinstance(value, str) and UUID.fullmatch(value) is not None and value != "00000000-0000-0000-0000-000000000000"


def _file(value):
    return type(value) is int and 1 <= value <= 2147483647


def _no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("Nonfinite JSON constant: " + value)


def _finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("JSON number exceeds finite range.")
    return value


def load_report(path):
    """Bounded read only. Input paths are never opened for writing."""
    with Path(path).open('rb') as stream:
        data = stream.read(MAX_REPORT_BYTES + 1)
    if len(data) > MAX_REPORT_BYTES:
        raise ValueError("Saved report exceeds the 4 MiB limit.")
    return json.loads(data.decode('utf-8'), object_pairs_hook=_no_duplicates,
                      parse_constant=_invalid_constant, parse_float=_finite_float)


def analyze_report(report, *, target_material='C35', excluded_refs=()):
    """Analyze reported values conditionally; input flags can never authorize writes.

    Exceptions are (drawing_file, model_uuid) pairs. Label equality never proves
    that a project catalog material or native modification adapter is bound.
    """
    if (not isinstance(target_material, str) or not target_material.strip() or len(target_material) > 128
            or any(ord(c) < 32 for c in target_material)):
        raise ValueError("Use a bounded, nonempty material label without control characters.")
    excluded = set()
    for ref in excluded_refs:
        if not isinstance(ref, (list, tuple)) or len(ref) != 2 or not _file(ref[0]) or not _uuid(ref[1]):
            raise ValueError("Exceptions must be (drawing_file, canonical model_uuid) pairs.")
        excluded.add(tuple(ref))
    if len(excluded) > 100:
        raise ValueError("At most 100 exact reference exceptions are supported.")
    result = {'schema_version': 'm4-wall-report-analysis-1', 'decision': 'not_checked',
              'read_only': True, 'native_model_access': False, 'model_data_changed': False,
              'usable_for_write': False, 'evaluation_apply_available': False, 'runtime_verified': False,
              'allplan_acceptance': 'not_run', 'is_full_wall_filter': False,
              'target_material_intent': target_material, 'threshold_mm': 240.0,
              'units': 'assumed_native_mm_not_verified', 'material_binding': 'not_checked',
              'current_model_values': 'not_checked', 'source_authenticity': 'not_verified',
              'write_blockers': ['saved_report_is_not_a_live_plan', 'native_wall_read_acceptance_pending',
                                 'native_units_not_verified', 'wall_geometry_not_verified',
                                 'project_material_binding_missing', 'native_material_write_adapter_unavailable']}
    try:
        wrapper = _object(report, 'report')
        _require(wrapper.get('schema_version') == 'm4-wall-owner-1', 'unsupported_report_schema')
        _require(wrapper.get('model_setters_requested') is False, 'source_wrapper_setter_flags_inconsistent')
        steps = wrapper.get('steps')
        _require(isinstance(steps, list) and len(steps) == 3, 'incomplete_or_repeated_probe_steps')
        expected = [('health_before', 'allplan_health'), ('one_wall_sample', 'model_property_probe'),
                    ('health_after', 'allplan_health')]
        responses = []
        for step, (name, tool) in zip(steps, expected):
            step = _object(step, 'step')
            _require(step.get('name') == name and step.get('tool') == tool
                     and step.get('state') == 'response_received', 'incomplete_or_unexpected_probe_step')
            responses.append(_object(step.get('response'), name))
        sessions = []
        for health in (responses[0], responses[2]):
            runtime = _object(health.get('runtime'), 'health_runtime')
            session = runtime.get('host_session_id')
            _require(health.get('ok') is True and isinstance(session, str) and bool(session), 'health_unavailable')
            sessions.append(session)
        _require(sessions[0] == sessions[1], 'host_session_changed')
        result['reported_host_session_id'] = sessions[0]
        request = _object(steps[1].get('request'), 'wall_request')
        _require(request.get('phase') == 'wall_sample' and _file(request.get('drawing_file'))
                 and set(request) <= {'phase', 'drawing_file', 'model_uuid'}, 'unexpected_wall_request')
        if 'model_uuid' in request:
            _require(_uuid(request['model_uuid']), 'invalid_requested_model_uuid')
        probe = responses[1]
        _require(probe.get('host_session_id') == sessions[0], 'probe_host_session_changed')
        _require(probe.get('schema_version') == 'm4-property-probe-1' and probe.get('phase') == 'wall_sample', 'unsupported_probe_schema')
        _require(probe.get('read_only') is True and probe.get('usable_for_write') is False
                 and probe.get('model_data_changed') is False, 'source_probe_flags_inconsistent')
        counts = _object(probe.get('counts'), 'probe_counts')
        _require(type(counts.get('sampled_walls')) is int and counts['sampled_walls'] == 1, 'expected_one_sampled_wall')
        scope = _object(probe.get('scope'), 'probe_scope')
        _require(scope.get('included_files') == [{'drawing_file': request['drawing_file'],
                    'state': 'active_foreground', 'write_eligibility': 'not_checked'}], 'foreground_scope_not_checked')
        coverage = _object(probe.get('coverage'), 'probe_coverage')
        _require(coverage.get('requested_scope_complete') is True
                 and coverage.get('returned_fields_complete') is True, 'probe_scope_incomplete')
        sample = _object(probe.get('sample'), 'wall_sample')
        ref = _object(sample.get('ref'), 'wall_ref')
        _require(_file(ref.get('drawing_file')) and _uuid(ref.get('model_uuid'))
                 and ref['drawing_file'] == request['drawing_file']
                 and ('model_uuid' not in request or ref['model_uuid'] == request['model_uuid']), 'request_ref_mismatch')
        fields = _object(sample.get('fields'), 'sample_fields')
        _require(ref.get('component_kind') == 'top_level_component'
                 and fields.get('type_name') == {'status': 'observed', 'value': 'Wall_TypeUUID'}, 'wall_root_not_checked')
        result['ref'] = {'drawing_file': ref['drawing_file'], 'model_uuid': ref['model_uuid']}
        if (ref['drawing_file'], ref['model_uuid']) in excluded:
            result['decision'] = 'excluded'
            return result
        count = sample.get('tier_count')
        _require(type(count) is int, 'tier_count_not_checked')
        if count != 1:
            result.update(decision='unsupported', reason='requires_one_wall_tier', reported_tier_count=count)
            return result
        _require(probe.get('state') == 'observed' and wrapper.get('state') == 'awaiting_owner_observation', 'native_read_incomplete')
        thickness = _object(sample.get('total_thickness_mm'), 'thickness')
        _require(thickness.get('status') == 'observed' and thickness.get('unit') == 'mm'
                 and thickness.get('source') == 'single_tier_native_Thickness', 'native_thickness_source_not_checked')
        value = thickness.get('value')
        _require(type(value) in (int, float) and 0 < value <= 1_000_000 and math.isfinite(value), 'invalid_native_thickness')
        material = _object(sample.get('native_material'), 'native_material')
        _require(material.get('status') == 'observed' and material.get('source') == 'WallTierProperties.Material', 'native_material_source_not_checked')
        label = material.get('value')
        _require(isinstance(label, str) and len(label) <= 8192, 'invalid_native_material')
        match = value < 240.0  # Never trust a saved criterion's precomputed result.
        same_label = label == target_material  # No aliases, trimming or class conversion.
        result.update(reported_thickness_mm=float(value), reported_native_material=label,
                      criterion_matches_assuming_mm=match, native_label_equals_requested=same_label,
                      decision=('outside_threshold_assuming_mm' if not match else
                                'same_native_label_assuming_mm' if same_label else 'material_change_candidate_assuming_mm'))
    except EvidenceError as exc:
        result['reason'] = str(exc)
    return result


def _exception(value):
    try:
        file_text, model_uuid = value.split(':', 1)
        ref = (int(file_text), model_uuid)
        if not _file(ref[0]) or not _uuid(ref[1]):
            raise ValueError
        return ref
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Use drawing_file:canonical-model-uuid.') from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--target-material', default='C35')
    parser.add_argument('--exclude', action='append', type=_exception, default=[])
    args = parser.parse_args(argv)
    try:
        report = load_report(args.report)
        result = analyze_report(report, target_material=args.target_material, excluded_refs=args.exclude)
        # A digest identifies the analyzed JSON; it does not authenticate it.
        result['source_json_sha256'] = hashlib.sha256(json.dumps(report, sort_keys=True, ensure_ascii=False,
                                                               allow_nan=False, separators=(',', ':')).encode()).hexdigest()
    except (OSError, ValueError, RecursionError) as exc:
        print('Cannot analyze saved report: ' + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 1 if result['decision'] == 'not_checked' else 0


if __name__ == '__main__':
    raise SystemExit(main())
