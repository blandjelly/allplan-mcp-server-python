# Allplan attribute trial log

## Run scope

- Project: `Kopia MCP_QA_DEMO`; active drawing only: 101.
- Allplan: 2026.1; bridge/MCP package: 0.30.0; installed bridge integrity: verified.
- No missing elements, attributes, or layers were created.
- Previously accepted Beam layer writes and the Column W1 no-op were not repeated.
- Four approved attribute trials ran sequentially. Each had preview, highlight, revalidation, one Apply, fresh read, one user-confirmed Undo, and a fresh restoration read.
- Apply requests were persisted before sending in [allplan-attribute-trial-apply-requests.jsonl](allplan-attribute-trial-apply-requests.jsonl).
- Apply was evaluation mode (`production_apply_available=false`); native acceptance remained pending.

## Results

| Result | Element / identity | Attribute | Type | Before → test value → after Undo | Plan / execution |
|---|---|---|---|---|---|
| PASS | Column; drawing 101; model UUID `51db6258-4f95-4fab-ac80-8948e13bfd21`; view UUID `6e934ac8-ce2f-47c1-8c85-f19ae086301a` | `MCP_QA_MARK`, ID 5001 | String/text (SDK type 67) | `"5" → "QA-TEST-01" → "5"` | plan `c9ce1bde5f0a4224bb54e5b361f96b04`; hash `e1b1805c974ad6d888ce2b934de944f233553cc4be2bf06b2266c63de004a36d`; execution `235901f7cec546fda34e74a2ba0e4424` |
| PASS | Column; drawing 101; model UUID `51db6258-4f95-4fab-ac80-8948e13bfd21`; view UUID `6e934ac8-ce2f-47c1-8c85-f19ae086301a` | `Priorytet`, ID 110 | Integer (SDK type 73) | `100 → 101 → 100` | plan `d79d6a9449d1447aab912cec699f6e06`; hash `159d018cfb42a97e1534b5ed14f4c231c79577b7c6fcc10bc8cce1b07c5073b6`; execution `124bafb4785d4d4d85f8c4e9e4ff7b2d` |
| PASS | Column; drawing 101; model UUID `51db6258-4f95-4fab-ac80-8948e13bfd21`; view UUID `6e934ac8-ce2f-47c1-8c85-f19ae086301a` | `Współczynnik`, ID 230 | Double/real (SDK type 82) | `1 → 1.05 → 1` | plan `1bf00330003a41b491c9ad6a6ef4cc50`; hash `79facd5eb43312af1e5cd35e88a44edb7fb80bccc39e8a30177c8892603f4cb9`; execution `2fdc64148e344db9a98ec106f467f45d` |
| PASS | Wall; drawing 101; model UUID `06d71e4d-193b-483e-8a32-344ade3d612c`; view UUID `2d33e5a6-b4e8-444b-94e8-d4d0ae75d622` | `Nazwa`, ID 507 | String/text (SDK type 67) | `"" → "QA-TEST-WALL" → ""` | plan `4829b07ad9f64c168048196b594db417`; hash `2758d2bc2e0bdbaa6690938582e3892bcbec4ab157afde3395c912145a7eedf8`; execution `7351e2af31e246b5a5cd969944b0a4cb` |

## Raw MCP evidence

The following are the relevant unmodified structured fields from MCP responses. Request IDs are included where returned and captured.

### Connection and scope

```json
{
  "health": {"ok": true, "allplan_version": "2026.1", "bridge_version": "0.30.0", "bridge_integrity": "verified", "request_id": "b035628a-b993-4674-ab87-52ba24cc29d8"},
  "context": {"active_drawing_file": 101, "loaded_drawing_files": [{"number": 101, "state": "active_foreground"}], "document_id": 0, "project": "Kopia MCP_QA_DEMO", "runtime_verified": false, "request_id": "1b3d3c19-fa8d-4914-8f83-62f05c9dae53"}
}
```

### Apply and fresh value/type reads

```json
[
  {
    "execution_id": "235901f7cec546fda34e74a2ba0e4424",
    "apply_request_id": "6e43c54d-cbc5-4407-bbd0-cd87db2f6ebc",
    "state": "completed",
    "outcome": {"state": "applied", "reason": "readback_matches", "readback": {"status": "observed", "value": "QA-TEST-01"}, "representation_consensus": {"complete": true, "agreed": true}},
    "fresh_read": {"phase": "element_attributes", "id": 5001, "name": "MCP_QA_MARK", "value": "QA-TEST-01", "type": 67, "supported_scalar_value_types": ["text"], "metadata_complete": true, "adapter_attribute_consistency": "consistent", "probe_fingerprint": "6b86b33ff1a241d0ee79622fa05ef2d976fa752bdb8f092ceb63fc737a416b35"}
  },
  {
    "execution_id": "124bafb4785d4d4d85f8c4e9e4ff7b2d",
    "apply_request_id": "a8fa050c-c689-4b34-bca4-d1b1563fc135",
    "state": "completed",
    "outcome": {"state": "applied", "reason": "readback_matches", "readback": {"status": "observed", "value": 101}, "representation_consensus": {"complete": true, "agreed": true}},
    "fresh_read": {"phase": "element_attributes", "id": 110, "name": "Priorytet", "value": 101, "type": 73, "supported_scalar_value_types": ["integer"], "metadata_complete": true, "adapter_attribute_consistency": "consistent", "probe_fingerprint": "41d4d526db368afb9b3d885e30463be022d755f43b34fa57aaed9152eb02b473"}
  },
  {
    "execution_id": "2fdc64148e344db9a98ec106f467f45d",
    "apply_request_id": "8fe34744-927b-469e-90b2-50f180846ae9",
    "state": "completed",
    "outcome": {"state": "applied", "reason": "readback_matches", "readback": {"status": "observed", "value": 1.05}, "representation_consensus": {"complete": true, "agreed": true}},
    "fresh_read": {"phase": "element_attributes", "id": 230, "name": "Współczynnik", "value": 1.05, "type": 82, "supported_scalar_value_types": ["real"], "metadata_complete": true, "adapter_attribute_consistency": "consistent", "probe_fingerprint": "bb8bedfaf11ae2174a18569bf1eed2763c70de67a3870ce9a1468d7921afe4d3"}
  },
  {
    "execution_id": "7351e2af31e246b5a5cd969944b0a4cb",
    "apply_request_id": "932ea876-c860-498f-a65b-b976182fd2ef",
    "state": "completed",
    "outcome": {"state": "applied", "reason": "readback_matches", "readback": {"status": "observed", "value": "QA-TEST-WALL"}, "representation_consensus": {"complete": true, "agreed": true}},
    "fresh_read": {"phase": "element_attributes", "id": 507, "name": "Nazwa", "value": "QA-TEST-WALL", "type": 67, "supported_scalar_value_types": ["text"], "metadata_complete": true, "adapter_attribute_consistency": "consistent", "probe_fingerprint": "7449b8e3743672bf321a8a6cd7e31340d9cbcf3b81364caa8de9947edac3b4a5"}
  }
]
```

### Undo restoration reads

```json
[
  {"id": 5001, "name": "MCP_QA_MARK", "value": "5", "type": 67, "probe_fingerprint": "abb9a932f3eb6f32afa032ec2b59951c"},
  {"id": 110, "name": "Priorytet", "value": 100, "type": 73, "probe_fingerprint": "554f389316fd98292e5dce8c99880faea643e18851cbbedbacf8c8a949f7a79b"},
  {"id": 230, "name": "Współczynnik", "value": 1, "type": 82, "probe_fingerprint": "62001e81740f2975540e30ec2b59951c"},
  {"id": 507, "name": "Nazwa", "value": "", "type": 67, "probe_fingerprint": "d377dca886b683871cbabb93c32f1149788611032b9de15fe7803e255709a877"}
]
```

Undo responses were user confirmations rather than MCP calls. Each was followed by the fresh read above. After the real-number Undo, one read attempt returned `host_absent`; the health check then succeeded (`request_id=e9a7bd6e-6337-4b33-b891-f58f7a5d9ba4`) and the next read confirmed restoration. No write was retried.

## Other discovered cases

| Case | Result | Evidence |
|---|---|---|
| Enum | BLOCKED | Column `Status`, ID 49, has SDK type Enum (69), but its stored value was `<niezdefiniowany>`; no valid Enum label was confirmed, so no test value was guessed. |
| Boolean | fixture_missing | No boolean-valued attribute was observed in the inspected Column and Wall attribute listings. Integer 0/1 fields were not treated as Boolean. |
| Beam | BLOCKED | `SkeletonBeam_TypeUUID` attribute read returned `probe_scope_unavailable`: ambiguous root adapter representations; no attribute was read. Previous accepted beam layer cases were not repeated. |
| Standalone slab | fixture_missing | The only `Slab_TypeUUID` was observed as a child of `MultiSlab_TypeUUID`; neither MultiSlab nor the unresolved Slab child was written. |
| Door opening | BLOCKED | Door identity was observed under a Wall, but the isolated attribute-list read failed; no opening write was attempted. |

## Plan lifecycle

All four plans followed preview → highlight → revalidate (`state=unchanged`) → one Apply. All Apply outcomes were `applied/readback_matches`; each fresh read matched the requested value and SDK scalar type. One user-confirmed Undo per trial was followed by restoration of the original value. No Apply was run for Enum, Boolean, beam, standalone slab, or opening cases.
