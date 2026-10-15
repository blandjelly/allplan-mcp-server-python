# Offline analysis of an M4 wall report

`wall_report_analysis` interprets one saved 0.18.0 wall-probe report. It is an
offline evidence check, not an executable `ChangePlan`: it cannot authorize a
material write, establish native property support, or filter all walls in a
model. Use it only after saving a report as described in the
[0.18.0 wall guide](m4-wall-properties-0.18.0.pl.md).

From a source checkout, run:

```bash
uv run --frozen python -m allplan_mcp.wall_report_analysis path/to/wall-properties.json
```

The analyzer is **not included in the frozen 0.18.0 evaluation ZIP**. It reads
the input report and prints a JSON analysis to stdout. It has no output-file
option, does not overwrite the input, and makes no network or native Allplan
calls.

Exit code 0 means the report yielded a conditional conclusion, an exclusion, or
an unsupported-tier result. Code 1 means evidence could not be checked; code 2
means invalid input, file/JSON failure or invalid options. None establishes a
native PASS or write eligibility.

By default, the target material label is the exact string `C35`. To compare a
different label, pass `--target-material LABEL`. The comparison does not trim,
change case, or convert classes: `C35/45`, `c35`, and ` C35 ` differ from `C35`.
An exact label match is reported as `same_native_label_assuming_mm`; this is a
conditional comparison, not proof that the project material is bound or that a
native write would be a no-op.

One exact reference can be excluded with `--exclude drawing_file:canonicalUUID`;
repeat the option for more exclusions. The reference includes both the drawing
file and canonical, nonzero model UUID. Exclusions apply only to this saved
report and do not transfer to another project or become a whole-model selection.

## How to read the result

The analyzer accepts only a complete `m4-wall-owner-1` report containing exactly
`health_before`, one `wall_sample`, and `health_after`, all received from the
same reported host session. It checks the read-only flags, one sampled wall,
complete foreground-file scope, request/reference agreement and the sampled
Wall root. It requires a single tier and valid reported thickness and native
material before making a candidate comparison. Missing or inconsistent evidence
stays `not_checked`; a tier count other than one is `unsupported`.

The strict `<240` comparison is recomputed from the reported tier thickness;
any precomputed criterion boolean in the input report is ignored. Results may
include `outside_threshold_assuming_mm`, `same_native_label_assuming_mm`, or
`material_change_candidate_assuming_mm`. They are conditional on the saved
thickness being in native millimetres. Units remain unverified, and the exact
material label does not prove catalog binding.

Every result remains `usable_for_write=false`,
`evaluation_apply_available=false`, `runtime_verified=false`, and
`allplan_acceptance=not_run`; current model values are unknown. It emits no
plan, execution ID, changes, or Apply request. Its canonical JSON SHA-256
identifies the analyzed content only; it is not an authenticity signature,
freshness check, or project-copy identity.

Input is limited to 4 MiB. Duplicate JSON keys, non-finite numbers, and
malformed JSON are rejected rather than interpreted ambiguously. These checks
protect the offline analysis boundary; they do not add crash containment or
acceptance evidence to the native 0.18.0 probe.

## Verification scope

**10 focused tests PASS**, using:

```bash
uv run --frozen python -m unittest discover -s tests -p 'test_wall_report_analysis.py' -v
```

The tests cover strict boundaries, exact labels, exceptions, inconsistent and
partial evidence, forged acceptance flags, malformed/bounded JSON and input
preservation. The CLI test runs with site packages disabled and socket creation
forbidden. This is portable analysis coverage, not a new full-suite result or
native acceptance. No new owner package or archive rebuild is needed for this
source-only addition.

Source **0c3a2987df164254d03cd749bcb72b71a79716ee** also passed the normal
Windows/Ubuntu Python 3.12 CI matrix, **2/2 jobs**, including the full **299-test**
portable suite and the workflow's standard build steps:
[CI 38824865834](https://github.com/blandjelly/allplan-mcp-server-python/actions/runs/38824865834).
These source checks do not replace or expand the separately frozen 0.18.0
package evidence. Later documentation-only commits do not change that source scope.
