# M1 metadata portable evidence — 0.4.0

Date: 2026-10-07. Linux, external Python 3.12.14, FastMCP 3.2.4.
**12 targeted checks PASS**: seven new metadata/fake-resource checks, one new
MCP/diagnostic capture check, and four relevant existing contract, transport,
package/registration and version checks. Existing checks are selected because
the action discriminator, host contract and package payload changed. No accepted
owner Allplan batch or full historical developer suite was repeated.

```bash
PYTHONPATH=tests .venv/bin/python -m unittest \
  test_model_metadata \
  test_mcp_smoke.MCPSmokeTests.test_metadata_inspect_diagnostics_capture_and_invalid_request_no_native_call \
  test_mcp_smoke.MCPSmokeTests.test_model_query_schema_transport_predicates_pages_and_summary \
  test_model_query.QueryTests.test_invalid_requests_never_enumerate_and_unknown_geometry_is_rejected \
  test_package.PackageTests.test_deterministic_archive_integrity_and_fresh_install_from_extracted_payload \
  test_package.PackageTests.test_version_and_lock_agree -v
```

The ten non-socket checks passed first; the new transport check initially could
not open a loopback socket in the restricted sandbox (PermissionError). It
passed after granting network capability. This is environment recovery, not
an Allplan test. The existing transport check was then run for the changed
public discriminator. No other passing checks were repeated unnecessarily.

Covered: exact native read signatures, document adapter versus integer document
ID, passive missing/raw observed distinction, per-field exceptions and bounded
strings, bounded sorted sample and sampled-layer coverage, rejected contracts
before reads, resource-sensitive probe fingerprint, cooperative total budget
failure with no selection, unloaded-scope omission, full request/response capture
with correlation ID, malformed public input, and deterministic archive/install
integrity with the new host module and Explorer entry point.

Wheel/sdist and evaluation ZIP build successfully. The package's embedded
manifest identifies its exact source commit and hashes. Original accepted ZIPs
and raw owner evidence remain unchanged. Windows execution/CI is not claimed.

2026 API documentation establishes signature feasibility only:
[AttributeService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/AttributeService/),
[LayerService](https://pythonparts.allplan.com/2026/api_reference/InterfaceStubs/NemAll_Python_BaseElements/LayerService/).
Fake-resource tests cannot confirm those APIs or passive attribute behavior in
Allplan. [New owner card](../m1-metadata-batch.md) is **pending**; geometry,
offset/units, hierarchy and profile activation are unverified.
