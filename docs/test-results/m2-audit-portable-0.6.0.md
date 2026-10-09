# M2.1–M2.3 portable evidence — 0.6.0

Historical portable result. Subsequent native captures and the corrected
0.6.1 recovery test are accepted separately in
[the bounded UAT-04 record](m2-acceptance-0.6.1.md). The NOT RUN status below
describes this original portable run.

Date: **2026-10-09**. Package **0.6.0**, audit profile **2.0.0** /
`m2-profile-1`, embedded unchanged M1 profile **1.0.2**. Linux external
Python **3.12.14**, FastMCP **3.2.4**, uv **0.12.19**.

**Portable PASS; native UAT-04 NOT RUN.** No live Allplan instance was available
in this cloud environment. Existing native M1 evidence remains unchanged and does
not establish M2 acceptance. [Owner card](../m2-audit-batch.md) is the next action.

## Verification

`uv sync --frozen` succeeded with a writable temporary uv cache.
`uv run --frozen python -m unittest discover -s tests -v`: **114 tests PASS**
(95 baseline + 17 M2 rule/host checks + 2 M2 MCP/diagnostic checks).
Real loopback HTTP checks require the execution environment's network capability;
these succeeded with it enabled. A sandbox-only run cannot create test sockets
and is not a test result for the code. No external live model is used.

`uv build` builds the 0.6.0 wheel and sdist. The deterministic Windows package
builder, SHA-256 payload verification, extracted-package registration, tamper and
missing/extra-file rejection run in the full test suite. The new M2 launcher,
audit modules and identical source/example profile data are checked there.
The existing Windows/Ubuntu Python 3.11–3.13 CI matrix includes M2 but was not
executed remotely during this local preparation; do not claim a current CI PASS.

## Meaningful cases

| Check | Portable result |
| --- | --- |
| Complete six-column fixture plus outside-file/family adapters | Exactly 5 findings on 5 columns; 1 duplicate group; 18 pass / 5 fail / 1 not_applicable / 0 not_checked. |
| Raw literal, whitespace, null, absent, wrong scalar types and policy override | Explicit missing semantics; literal/null retained; incompatible values remain unchecked. |
| Per-file/family uniqueness; extended profile includes passive 102 | Reference S02 does not join the file-101 duplicate group; missing passive native data stays unchecked. |
| Failed peer attribute read / representation conflict | Scope/input completeness remains false; singleton uniqueness cannot claim pass; proven duplicates still fail. |
| Duplicate views | No additional element/finding/group. |
| Rule subsets | Full snapshot, independent of display pages; unknown/duplicate/empty rule IDs rejected. |
| Empty loaded versus unloaded scope | not_applicable versus not_checked; zero findings alone is not success. |
| Missing/incompatible resource bindings | profile_unbound before enumeration. |
| Invalid profile/rule/scope/type/range/nonfinite/tolerance | invalid_payload before resource/enumeration calls. |
| Axis-aligned dimension range | Inclusive 1 mm tolerance; boundary/violation/unknown geometry distinguished. |
| Missing locator geometry | Attribute findings stay valid; locator/returned-fields coverage explicitly unchecked. |
| Fresh rerun, changed status and host restart | Updated source/report/finding evidence, no cached write authority. |
| Adapter, byte and combined scan/report time limits | No partial successful report or selection cache entry. |
| Actual FastMCP Streamable HTTP → typed bridge → fake native host service | Full five-finding report transported; audit profile resource and strict public input errors verified. |
| Diagnostics CLI | Prepared audit input saves full JSON plus matching readable TXT; errors captured; invalid typed inputs do not connect. |

These tests simulate native adapters/resources/geometry. They do not prove native
highlight, persistent identities, performance, native writable setters or Undo.
M2 uses file/mark/model-local location for inspection and executes no repairs.
The model cannot observe the owner's Allplan UI; UAT-04 must compare the five
findings and their locators with that UI and confirm no model changes.
