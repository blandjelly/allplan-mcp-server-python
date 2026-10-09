# M2 read-only audit contract — 0.6.1

M2.1–M2.3 are implemented and portable-tested. **UAT-04 PASS** on the retained
Allplan 2026-1-7 fixture, package 0.6.1; see
[native acceptance and limits](test-results/m2-acceptance-0.6.1.md). Public tool `model_audit`,
bridge route `/model-audit`, report/request schema `m2-audit-1`, audit profile
schema `m2-profile-1`. No native setter, selection, highlight, resource creation
or repair is called.

## Request and profiles

```json
{
  "scope": {"drawing_files": [101], "include_passive": false, "visibility": "api_select_all"},
  "profile_id": "native-model-qa-demo"
}
```

Exactly one `profile_id` or complete typed `profile` is required. No implicit
current-file/project scope is inferred. Optional `rule_ids` selects 1–32 distinct
configured rules; omitted means all rules. `max_adapters` is 1–10000, default 5000.
Scope must be a subset of the profile's explicit drawing files. Public validation also rejects a scope beyond the declared profile before
contacting the bridge (0.6.1). Host validation
rejects unknown keys, invalid rules, reversed ranges, nonfinite numbers, duplicate
IDs/allowed values, unsupported bindings and ambiguous uniqueness before native
reads. Missing/incompatible project resources return `profile_unbound` before
enumeration; no misleading successful zero-finding report is returned.

[Audit profile 2.0.0](../profiles/examples/native-model-qa.audit.json) embeds the
unchanged accepted M1 read profile 1.0.2. It freshly resolves typed string
attributes MCP_QA_MARK / MCP_QA_STATUS and layer short names SZ_OGÓ01 / SZ_OGÓ02
through the established name/type/ID round trips. The audit resource is
`allplan://profiles/native-model-qa-demo/audit`; the M1 resource remains unchanged.
Binding `active_for_write=false` and `write_eligibility=not_checked` are retained.

The public explicit profile can adjust policies/rules or file scope within these
bounded native column/resource bindings. This is not a general office-profile
registry or an arbitrary-family/property audit. Profile versions and SHA-256
fingerprints identify configuration; the fingerprint includes the complete rules,
policies and read profile. The software does not maintain a global version registry.

## Values and rule states

String policies are explicit per mark/status: trimming, case sensitivity and
whether observed absence, null, empty string or named literals mean missing.
Demo 2.0.0 trims, compares case-sensitively and treats absent/null/empty/whitespace
and literal `<niezdefiniowany>` as missing. This is a demo QA choice, not native
normalization. Raw observation/value always remains in evidence, including the
literal undefined text and null. Numeric/boolean values are never coerced to text.
A failed read, incompatible type or null/absence disabled in policy remains
`not_checked`. Absence from a passive file's GetAttributes response also remains
`not_checked`: it does not prove native absence.

| State | Meaning |
| --- | --- |
| `pass` | Observed rule inputs meet the rule. |
| `fail` | Observed input proves a violation. One finding per rule/element. |
| `not_checked` | Input/coverage is insufficient to decide. No invented violation. |
| `not_applicable` | The rule deliberately ignores a missing value, or a complete scope has no applicable elements. |

Supported rules:

- `required_attribute`: a policy-defined missing value fails.
- `allowed_attribute_values`: a present normalized string must match an explicit allowed value; missing fails; unavailable stays unchecked.
- `unique_attribute`: grouping is explicitly drawing_file + element_family + normalized value. `ignore_missing` is mandatory. Each duplicate member receives a finding; members share one group ID. Outside-scope files/families and duplicate views do not inflate groups. An observed group with two members already proves a failure even if coverage is incomplete. A singleton passes only with complete scope and no unknown peer values in its file; otherwise it remains unchecked.
- `required_layer`: compares observed layer ID to the freshly bound named profile layer.
- `dimension_range`: compares size_x_mm / size_y_mm / size_z_mm with inclusive min/max expanded by finite nonnegative absolute tolerance_mm. These are model-local axis-aligned box extents, not rotated native section dimensions or engineering checks. Failed geometry stays unchecked.

The packaged demo runs QA-001–QA-004 only: 24 checks over six columns give
18 pass, 5 fail and 1 not_applicable. Required/duplicate marks have error severity;
layer/status violations have warning severity. The optional dimension rule is
portable-tested; it is not added to the five-finding UAT gate.

## Full snapshot, coverage and limits

Every audit reads one fresh full M1 snapshot with top-level native component
resolution, representation deduplication and the profile column GUID predicate.
It neither consumes a displayed page nor reuses cached selections. The source
fingerprint includes context, resolved resources and relevant source reads;
profile and report fingerprints identify their separate evidence. It does not
create an audit/selection cache. Rerun after changes; reports are historical
snapshots, not persistent authorization or a live change registry.

The scan retains M1 coverage/omissions/diagnostic samples/counts. Rule summaries
retain all four counts and scope completeness. Aggregate state is fail if a
violation is proven, otherwise not_checked for incomplete inputs/scope, otherwise
pass if any applicable check passed, otherwise not_applicable. Known failures can
coexist with unchecked inputs. Inspect `coverage.audit_complete` as well as state:
zero findings alone does not establish success. `rule_inputs_complete` concerns
checks over returned elements; `requested_scope_complete` separately covers
omitted/conflicting/unknown identities. An empty complete scope is not_applicable;
an unloaded scope is not_checked. Scope is never claimed to cover a whole project.

Uncheckable locator geometry does not turn a supported attribute check into a
failure. `returned_fields_complete` exposes that limitation while
`audit_complete` concerns rule inputs and enumeration. Each locator retains its
own observed/not_checked statuses.

The shared five-second cooperative scan/report budget cannot interrupt a blocked
native call. Enumeration covers the entire current-document adapter list, even
outside scope, under the adapter limit. Scan and complete serialized report are
limited to 4 MiB. Oversize/time/adapter failures return `scan_limit_exceeded` and
no partial successful audit. Duplicate-group evidence is bounded by the same
report limit. Runtime performance in Allplan remains unmeasured.

## Findings and inspection

Structured `rules`, `checks` and `findings` retain rule ID, severity, state,
reason, raw/comparison evidence, relevant element fingerprint and full
session/project/document/file/model/type reference. A deterministic finding ID
identifies a rule+reference+profile within that host context; repeat identical
reads preserve it. Restart/context/profile changes produce different IDs.
`report_fingerprint` additionally binds the full report content.

Each finding provides drawing-file number, raw mark, model UUID, layer ID,
model-local bounding box and box center in mm, plus a readable remedy. Duplicate
marks are disambiguated by location/model UUID. Native highlight is not requested.
References remain session/snapshot evidence with `durable_identity_verified=false`
and `usable_for_write=false`; M1 does not prove durable re-resolution. A changed
model must be reread before future M3 planning; no repair is implemented here.
Remedies are suggestions, never executable operations.

The report includes `report_text`. **M2 Audit.cmd** supplies the prepared request
and saves full `logs/diagnostics-*.json` plus matching `.txt`, including readable
errors. Diagnostic `allplan_acceptance=not_run` is deliberately not an automatic
UAT verdict. [Native acceptance](test-results/m2-acceptance-0.6.1.md) records the owner verification;
[diagnostic commands](diagnostics.md) describe reusable capture procedures.

## Dispatcher exception boundary (0.6.1)

Typed/unexpected host errors are contained inside the WPF callback and returned
as primitive result/error data. HTTP errors are raised on the worker after UI
dispatch returns; Python exception objects do not cross the delegate. Persistent
request/error logs support native diagnosis. See [correction and causal limits](test-results/m2-dispatch-fix-0.6.1.md)
and the [accepted native recovery gate](test-results/m2-acceptance-0.6.1.md).
