"""Portable rules over one fresh full M1 snapshot; no native mutations."""
from __future__ import annotations

import copy
import json
import math
from collections import Counter, defaultdict

from .audit_contracts import SCHEMA, is_missing_string, normalized, query_request, selected_rules, validate_audit_request
from .query_contracts import fingerprint
from .transport import BridgeError

STATES = ("pass", "fail", "not_checked", "not_applicable")


def attribute_value(element, binding, role, policy):
    ident = binding["attributes"][role]["value"]["attribute_id"]
    raw = element["fields"][f"attribute:{ident}"]
    status, value = raw["status"], raw.get("value")
    if status == "not_checked":
        return raw, "not_checked", None
    if status == "missing":
        if element["fields"]["file_state"].get("value") == "passive_background":
            return raw, "not_checked", None
        return raw, "missing" if policy["missing"]["absent"] else "not_checked", None
    if value is None:
        return raw, "missing" if policy["missing"]["null"] else "not_checked", None
    if not isinstance(value, str):
        return raw, "not_checked", None
    if is_missing_string(value, policy):
        return raw, "missing", None
    return raw, "present", normalized(value, policy)


def locator(element, binding):
    fields = element["fields"]
    ident = binding["attributes"]["mark"]["value"]["attribute_id"]
    box = fields["bounding_box_mm"]
    return {"method": "drawing_file_mark_location", "drawing_file": element["ref"]["drawing_file"],
            "model_uuid": element["ref"]["model_uuid"],
            "mark": copy.deepcopy(fields[f"attribute:{ident}"]),
            "layer_id": copy.deepcopy(fields["layer_id"]), "bounding_box_mm": copy.deepcopy(box),
            "center_mm": ({"status": "observed", "value": [(a + b) / 2 for a, b in zip(box["value"]["min"], box["value"]["max"])],
                           "frame": "model_local"} if box["status"] == "observed"
                          else {"status": "not_checked", "value": None}),
            "highlight": "not_requested", "usable_for_write": False}


def evaluate_rule(rule, elements, binding, profile, complete, check_budget):
    """One check per rule/element, retaining raw observations and comparisons."""
    kind = rule["kind"]
    values, groups = {}, defaultdict(list)
    if "attribute" in rule:
        role = rule["attribute"]
        policy = profile["string_policies"][role]
        for index, element in enumerate(elements):
            check_budget()
            values[index] = attribute_value(element, binding, role, policy)
            if kind == "unique_attribute" and values[index][1] == "present":
                key = (element["ref"]["drawing_file"], element["ref"]["type_uuid"], values[index][2])
                groups[key].append(element["ref"])
    unresolved_files = {elements[i]["ref"]["drawing_file"] for i, value in values.items() if value[1] == "not_checked"}
    for index, element in enumerate(elements):
        check_budget()
        evidence, state, reason = {}, "not_checked", "input_unavailable"
        if kind in {"required_attribute", "allowed_attribute_values", "unique_attribute"}:
            raw, observed, value = values[index]
            evidence = {"field": rule["attribute"], "raw": copy.deepcopy(raw),
                        "value_state": observed, "normalized_value": value,
                        "policy": copy.deepcopy(policy)}
            if observed == "missing":
                state = "not_applicable" if kind == "unique_attribute" and rule["ignore_missing"] else "fail"
                reason = "missing_value_ignored" if state == "not_applicable" else "required_value_missing"
            elif observed == "present":
                if kind == "required_attribute":
                    state, reason = "pass", "value_present"
                elif kind == "allowed_attribute_values":
                    evidence["allowed_values"] = copy.deepcopy(rule["allowed_values"])
                    state = "pass" if value in {normalized(v, policy) for v in rule["allowed_values"]} else "fail"
                    reason = "allowed_value" if state == "pass" else "value_not_allowed"
                else:
                    key = (element["ref"]["drawing_file"], element["ref"]["type_uuid"], value)
                    members = groups[key]
                    evidence.update({"uniqueness_scope": rule["uniqueness_scope"],
                                     "observed_group_size": len(members), "members": copy.deepcopy(members),
                                     "group_id": fingerprint({"profile": fingerprint(profile), "rule_id": rule["rule_id"],
                                                              "project": element["ref"]["project_key"], "key": key}),
                                     "scope_complete": complete})
                    if len(members) > 1:
                        state, reason = "fail", "duplicate_value"
                    elif not complete or element["ref"]["drawing_file"] in unresolved_files:
                        state, reason = "not_checked", "uniqueness_scope_incomplete"
                    else:
                        state, reason = "pass", "unique_value"
        elif kind == "required_layer":
            raw = element["fields"]["layer_id"]
            expected = binding["layers"][rule["expected_layer"]]["value"]
            evidence = {"field": "layer_id", "raw": copy.deepcopy(raw), "expected": copy.deepcopy(expected)}
            if raw["status"] == "observed":
                state = "pass" if raw["value"] == expected["layer_id"] else "fail"
                reason = "expected_layer" if state == "pass" else "unexpected_layer"
        else:
            raw = element["fields"][rule["field"]]
            evidence = {"field": rule["field"], "raw": copy.deepcopy(raw), "units": "mm",
                        "measurement": "axis_aligned_bounding_box_extent", "min_mm": rule["min_mm"],
                        "max_mm": rule["max_mm"], "tolerance_mm": rule["tolerance_mm"]}
            if raw["status"] == "observed" and type(raw["value"]) in (int, float) and math.isfinite(raw["value"]):
                state = "pass" if rule["min_mm"] - rule["tolerance_mm"] <= raw["value"] <= rule["max_mm"] + rule["tolerance_mm"] else "fail"
                reason = "dimension_in_range" if state == "pass" else "dimension_out_of_range"
        yield {"rule_id": rule["rule_id"], "severity": rule["severity"], "state": state, "reason": reason,
                       "ref": copy.deepcopy(element["ref"]), "evidence": evidence,
                       "source_fingerprint": element["source_fingerprint"], "usable_for_write": False}


def run_audit(queries, doc, base, settings, request, *, with_snapshot=False):
    validate_audit_request(request)
    started = queries.clock()
    def check_budget():
        if queries.clock() - started >= queries.SCAN_SECONDS:
            raise BridgeError("scan_limit_exceeded", "Audit exceeded its read/report time budget; no partial report is returned.", 409)
    snapshot = queries._scan(doc, base, settings, query_request(request))
    check_budget()
    profile = request["profile"]
    binding = snapshot["profile_binding"]
    complete = snapshot["coverage"]["requested_scope_complete"]
    elements = snapshot["elements"]
    rules, checks, findings = [], [], []
    locations = {fingerprint(e["ref"]): locator(e, binding) for e in elements}
    result_bytes = 0
    for rule in selected_rules(request):
        counts = Counter()
        for check in evaluate_rule(rule, elements, binding, profile, complete, check_budget):
            check_budget()
            counts[check["state"]] += 1
            checks.append(check)
            result_bytes += len(json.dumps(check, ensure_ascii=False, allow_nan=False).encode())
            if check["state"] == "fail":
                finding = {**copy.deepcopy(check),
                           "finding_id": fingerprint({"profile": fingerprint(profile), "rule_id": rule["rule_id"], "ref": check["ref"]}),
                           "locator": copy.deepcopy(locations[fingerprint(check["ref"])]),
                           "remedy": rule["remedy"], "remedy_applied": False}
                findings.append(finding)
                result_bytes += len(json.dumps(finding, ensure_ascii=False, allow_nan=False).encode())
            if result_bytes > queries.MAX_SNAPSHOT_BYTES:
                raise BridgeError("scan_limit_exceeded", "Audit exceeds the 4 MiB report budget. Narrow the scope/rules; no partial report is returned.", 409)
        state = ("fail" if counts["fail"] else "not_checked" if counts["not_checked"] or not complete
                 else "pass" if counts["pass"] else "not_applicable")
        rules.append({"rule_id": rule["rule_id"], "kind": rule["kind"], "severity": rule["severity"],
                      "state": state, "counts": {s: counts[s] for s in STATES}, "scope_complete": complete,
                      "reason": "no_applicable_elements" if state == "not_applicable" else "rule_evaluated" if complete else "scope_incomplete"})
    counts = Counter(c["state"] for c in checks)
    total = {s: counts[s] for s in STATES}
    total.update({"elements": len(elements), "rules": len(rules), "findings": len(findings),
                  "affected_elements": len({fingerprint(f["ref"]) for f in findings}),
                  "duplicate_groups": len({f["evidence"]["group_id"] for f in findings if "group_id" in f["evidence"]}),
                  "severity": dict(Counter(f["severity"] for f in findings))})
    status = "fail" if findings else "not_checked" if not complete or counts["not_checked"] else "pass" if counts["pass"] else "not_applicable"
    coverage = {**copy.deepcopy(snapshot["coverage"]), "rule_inputs_complete": not counts["not_checked"],
                "audit_complete": complete and not counts["not_checked"], "uses_full_snapshot": True,
                "durable_identity_verified": False}
    lines = [f"Audit {profile['profile_id']} {profile['profile_version']}: {status}.",
             f"{len(elements)} elements; {len(findings)} findings on {total['affected_elements']} elements; {total['not_checked']} unchecked checks.",
             f"Requested scope complete: {complete}; audit complete: {coverage['audit_complete']}."]
    lines.extend(f"{r['rule_id']} ({r['severity']}): {r['state']} {r['counts']}" for r in rules)
    for f in findings:
        location = f["locator"]
        lines.append(f"{f['rule_id']}: file {location['drawing_file']}, mark {location['mark'].get('value')!r}, model {location['model_uuid']}, center {location['center_mm'].get('value')} mm (model_local): {f['reason']}. {f['remedy']}")
    report = {"schema_version": SCHEMA, "read_only": True, "runtime_verified": False,
              "allplan_acceptance": "not_run", "state": status, "profile_id": profile["profile_id"],
              "profile_version": profile["profile_version"], "profile_fingerprint": fingerprint(profile),
              "query_session_id": queries.session_id, "source_fingerprint": snapshot["source_fingerprint"],
              "profile_binding": copy.deepcopy(binding), "scope": copy.deepcopy(snapshot["scope"]),
              "coverage": coverage, "scan_counts": copy.deepcopy(snapshot["counts"]),
              "omissions": copy.deepcopy(snapshot["omissions"]),
              "not_checked_samples": copy.deepcopy(snapshot["not_checked_samples"]),
              "counts": total, "rules": rules, "checks": checks, "findings": findings,
              "report_text": "\n".join(lines), "usable_for_write": False,
              "reference_lifetime": "host_session_project_document_snapshot; rerun after model changes or restart"}
    report["report_fingerprint"] = fingerprint(report)
    check_budget()
    if len(json.dumps(report, ensure_ascii=False, allow_nan=False).encode()) > queries.MAX_SNAPSHOT_BYTES:
        raise BridgeError("scan_limit_exceeded", "Audit exceeds the 4 MiB report budget; no partial report is returned.", 409)
    check_budget()
    return (report, snapshot) if with_snapshot else report
