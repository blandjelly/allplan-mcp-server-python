from __future__ import annotations

import os
import math
import platform
from importlib.metadata import version
from typing import Annotated, Any

from fastmcp import FastMCP

from allplan_mcp.allplan_client import AllplanHostClient, AllplanHostError
from allplan_mcp.skills import SkillsManager
from allplan_mcp.query_models import QueryRequest
from allplan_mcp.demo_profile import load_demo_profile, load_audit_profile
from allplan_mcp.audit_models import AuditRequest
from allplan_mcp.repair_models import RepairRequest
from allplan_mcp.standard_models import OfficeStandardRequest, RuleBasedRequest
from allplan_mcp.office_standard import load_office_standard
from allplan_mcp.column_layer_models import ColumnLayerRequest
from allplan_mcp.property_models import PropertiesRequest, SelectionRequest, PropertyProbeRequest
from allplan_mcp.wall_filter_models import WallFilterRequest
from allplan_mcp.model_edit_models import ModelEditRequest


DEFAULT_ALLPLAN_HOST_URL = "http://127.0.0.1:5679"
DEFAULT_MCP_HOST = "127.0.0.1"
DEFAULT_MCP_PORT = 8888
DEFAULT_MCP_PATH = "/mcp"

mcp = FastMCP("Allplan MCP Server")
skills_manager = SkillsManager()


@mcp.resource("allplan://profiles/native-model-qa-demo", mime_type="application/json")
def native_model_qa_demo_profile() -> str:
    """Versioned demo rules/resource names; project IDs require action=profile."""
    import json
    return json.dumps(load_demo_profile(), ensure_ascii=False, indent=2)


@mcp.resource("allplan://profiles/native-model-qa-demo/audit", mime_type="application/json")
def native_model_qa_audit_profile() -> str:
    """M2 rules with explicit missing/normalization policies; read-only remedies."""
    import json
    return json.dumps(load_audit_profile(), ensure_ascii=False, indent=2)


@mcp.resource("allplan://standards/native-model-qa-demo-layer-status", mime_type="application/json")
def native_office_standard() -> str:
    """Versioned evaluation layer/status preset."""
    import json
    return json.dumps(load_office_standard(), ensure_ascii=False, indent=2)


@mcp.resource("allplan://standards/native-model-qa-demo-mark-numbering", mime_type="application/json")
def native_mark_standard() -> str:
    """Versioned preserve-valid-fill-gaps mark numbering; native gate pending."""
    import json
    return json.dumps(load_office_standard("native-model-qa-demo-mark-numbering"), ensure_ascii=False, indent=2)


def _allplan_client() -> AllplanHostClient:
    return AllplanHostClient(
        base_url=os.getenv("ALLPLAN_HOST_URL", DEFAULT_ALLPLAN_HOST_URL),
        timeout=float(os.getenv("ALLPLAN_HOST_TIMEOUT", "30")),
    )


@mcp.resource(
    "allplan://skills",
    name="allplan-skills",
    title="ALLPLAN skills index",
    description="Index of bundled ALLPLAN skills and sample scripts",
    mime_type="text/markdown",
)
def allplan_skills_index() -> str:
    """Read the skills index"""

    return skills_manager.index_text()


@mcp.resource(
    "allplan://skills/{skill_name}",
    name="allplan-skill",
    title="ALLPLAN skill",
    description="Read one bundled ALLPLAN skill",
    mime_type="text/markdown",
)
def allplan_skill(skill_name: Annotated[str, "Skill folder name"]) -> str:
    """Read one skill"""

    return skills_manager.skill_text(skill_name)


@mcp.resource(
    "allplan://skills/{skill_name}/assets/{asset_name}",
    name="allplan-skill-asset",
    title="ALLPLAN skill asset",
    description="Read one bundled ALLPLAN asset note",
    mime_type="text/markdown",
)
def allplan_skill_asset(
    skill_name: Annotated[str, "Skill folder name"],
    asset_name: Annotated[str, "Asset file name"],
) -> str:
    """Read one asset"""

    return skills_manager.asset_text(skill_name, asset_name)


@mcp.resource(
    "allplan://skills/{skill_name}/scripts/{script_name}",
    name="allplan-skill-script",
    title="ALLPLAN skill script",
    description="Read one bundled ALLPLAN sample script",
    mime_type="text/x-python",
)
def allplan_skill_script(
    skill_name: Annotated[str, "Skill folder name"],
    script_name: Annotated[str, "Script file name"],
) -> str:
    """Read one sample script"""

    return skills_manager.script_text(skill_name, script_name)


@mcp.tool
def allplan_health() -> dict[str, Any]:
    """Check that the Allplan Python host is reachable."""

    response = _allplan_client().post("/get-allplan-version")
    return {
        "ok": True,
        "allplan_version": response.get("version"),
        "runtime": response,
        "external_python": platform.python_version(),
        "mcp_package_version": version("allplan-mcp-server"),
        "request_id": response.get("request_id"),
        "allplan_host_url": os.getenv("ALLPLAN_HOST_URL", DEFAULT_ALLPLAN_HOST_URL),
    }


@mcp.tool
def get_allplan_version() -> str:
    """Get the version of the running Allplan instance."""

    response = _allplan_client().post("/get-allplan-version")
    if not response.get("version"):
        raise AllplanHostError("The host could not read the installed Allplan version.", code="version_unavailable", request_id=response.get("request_id"))
    return str(response["version"])


@mcp.tool
def get_model_context(identity_sample_size: int = 0, profile_id: str | None = None) -> dict[str, Any]:
    """Read-only M1 probe: project, loaded file states, input units and raw offset.

    Optional 0–20 raw adapters expose model/view UUIDs separately. This sample
    is not a component count, reusable selection or write target. Unavailable
    fields are not_checked; units/offset here remain raw observations. Canonical
    query geometry has bounded Allplan 2026-1-7 fixture acceptance.
    """
    if isinstance(identity_sample_size, bool) or not isinstance(identity_sample_size, int) or not 0 <= identity_sample_size <= 20:
        raise ValueError("identity_sample_size must be from 0 to 20.")
    payload = {"identity_sample_size": identity_sample_size}
    if profile_id is not None:
        if profile_id != "native-model-qa-demo":
            raise ValueError("Unknown profile_id.")
        payload["profile"] = load_demo_profile()
    return _allplan_client().post("/get-model-context", payload)


@mcp.tool
def model_query(request: QueryRequest) -> dict[str, Any]:
    """Read-only model query, page, summary, metadata inspection or profile binding.

    Query defaults to open_drawings, including passive files for reads. The host
    resolves the loaded inventory on every scan and reports explicit file states
    and omissions. Whole-project scope is unavailable. An explicit scope uses
    positive drawing_files, include_passive and visibility=api_select_all.
    Use observed type GUID/name, layer ID or
    attribute:<ID> predicates with all/any/not. Missing/failed reads are distinct.
    attribute_read_mode=all_and_computable is an opt-in read of requested
    attribute IDs with computed attributes included; it preserves computed_only
    provenance, is read-only, and binds the mode into the source fingerprint.
    The stored ReadAll default and its callers remain unchanged.
    layer_resolution=component with component_kind=semantic_component reads a
    Wall's effective layer from all directly owned WallTier adapters; mixed or
    unreadable tier layers are not_checked. Default adapter resolution preserves
    the raw layer on the queried adapter. Query/highlight can still satisfy the
    independent presentation part of an unsupported native-material request;
    never silently replace native material with a different attribute target.
    wall.total_thickness_mm reads the real single-tier Wall Thickness in native
    mm; it never substitutes axis-aligned bounding-box extents. Unsupported
    multi-tier/unknown representations remain not_checked.
    component_ownership is an optional structural read of exact adapter
    ancestry and direct children. It never merges by bounds, identifies a
    writable property owner, or serves as a predicate field.
    Pages and summaries revalidate query fields; stale selections are rejected.
    Selections expire after five minutes or host restart, count model UUIDs rather
    than components by default, and cannot authorize writes. Explicit
    component_kind=top_level_component resolves parent chains for ordinary
    columns/beams/walls/slabs. Geometry uses mm, model_local or project_global
    (local plus project offset once), with size_*_mm axis-aligned extents.
    spatial_box is a declared inclusive/exclusive AABB intersects/contained test,
    not exact solid intersection. Native fixture reads have bounded acceptance on
    Allplan 2026-1-7; arbitrary scenes/builds remain outside that acceptance.
    Inspect requires explicit scope and attribute_ids (up to 32), returns a
    bounded sample (1..20), raw values and project attribute/layer metadata.
    A missing passive attribute is an API omission, not proof of native absence.
    profile_id=native-model-qa-demo binds named resources freshly; mark/status
    aliases require compatible string attributes and the configured file scope.
    action=profile reports missing resources without creating them. Profile
    binding is read-only; mutation eligibility remains not_checked.
    """
    payload = request.model_dump(by_alias=True, exclude_unset=True)
    profile_id = payload.pop("profile_id", None)
    if profile_id is not None:
        payload["profile"] = load_demo_profile()
    if payload.get("spatial_box") is None:
        payload.pop("spatial_box", None)
    if payload.get("action") == "page" and payload.get("cursor") is None:
        payload.pop("cursor", None)
    payload["schema_version"] = "m1-query-1"
    return _allplan_client().post("/model-query", payload)


@mcp.tool
def column_layer(request: ColumnLayerRequest) -> dict[str, Any]:
    """Find Columns with unset fire resistance classification and assign W1.

    preview resolves exact project field names and the layer with ID/name round
    trips, scans one foreground drawing and reports every Column's value state.
    Defaults use Klasa odporności ogniowej / Fire resistance classification
    (F30/F60), not the separate fire-risk attribute Odporność ogniowa.
    Null, empty/whitespace and the explicit undefined strings match. Read errors,
    unsupported types and omission from ReadAll are unknown and block Apply;
    ReadAll omits computed attributes, so omission never proves native absence.
    Conflicting field names block instead of selecting an arbitrary attribute.
    No metadata type/unit/enum discovery, resource creation or audit findings.

    highlight submits all matching Columns, including those already on W1;
    explicit exceptions remain excluded. highlight_targets and changes are
    separate hash-bound lists. All-no-op plans can highlight without Apply.
    This is highlighting, not native selection. The owner
    accepts highlighting for this workflow; observe visibility in Allplan.
    apply requires the exact highlighted plan/hash, an execution ID and reviewed
    disposable-copy acknowledgement. Shared M3 controls enforce fresh whole-scope
    evidence, 1..32 Column layer changes, writable targets, durable write-ahead
    journal, readback, replay deduplication and read-only recover. Persist the
    exact Apply request before sending; on lost reply recover that ID, never
    generate a new ID or retry a setter. Preview again after model/resource changes.
    The revised highlighting requires native 0.17.2 observation.
    """
    payload = request.model_dump(exclude_unset=True)
    payload["schema_version"] = "m4-column-layer-1"
    try:
        return _allplan_client().post("/column-layer", payload)
    except AllplanHostError as exc:
        before_write = {"target_not_writable", "plan_expired", "plan_hash_mismatch", "presentation_required",
                        "repair_scope_unavailable", "repair_conflict", "repair_journal_full",
                        "execution_id_conflict", "repair_recovery_required", "property_binding_unavailable"}
        if payload["action"] != "apply" or exc.code not in before_write:
            raise
        return {"schema_version": "m3-execution-1", "action": "apply", "state": "rejected",
                "read_only": True, "native_setters_started": False, "execution_id": payload["execution_id"],
                "error": {"code": exc.code, "message": str(exc)}}


@mcp.tool
def model_edit(request: ModelEditRequest) -> dict[str, Any]:
    """Find components and plan typed attributes, layers, native material or deletion.

    Use exact project attribute names/IDs, never guessed IDs. Preview defaults to
    open_drawings and binds the whole family scope, predicate, explicit exclusions,
    old/new values and resources. Choose native_types or a family predicate and
    component owners are resolved without redirecting doors/windows to their wall.
    Attribute targets accept text/integer/real/boolean values with replace/add/upsert;
    value_type=auto infers loaded-SDK scalar types and exact SDK Enum labels.
    JSON booleans for Integer attributes require the loaded SDK CheckBox control;
    the reviewed resource binds true/false to native 1/0. Other integers never
    silently accept booleans. Explicit enum labels use
    targeted label/key roundtrips and a runtime-bound Enum/Integer/String type;
    no enum catalog is enumerated. Dates remain unsupported. Layer targets accept
    an existing short_name or name. Search both full and short layer names;
    model_property_probe layer_catalog paginates Allplan 2026's layer IDs when
    direct lookup is insufficient. Follow its continuation and confirmation hints.
    If a name is ambiguous or a catalog match is uncertain, show the actual full
    and short names and ask the user to confirm the target before using its exact
    confirmed_targets entry in a new preview, including expected_layer_id and
    expected_name. This keeps the user's choice bound to the same ID and names.
    Never translate or invent a layer short name.
    Attribute material is distinct from native material and surface.
    Native material uses changes=[{target:{kind:native_material,tier_index:1},value:EXACT_STRING}]
    as the only edit. It requires a standalone single-tier Wall without openings,
    readable native scalar properties and serialized Polyhedron3D tier geometry.
    The exact string is a native property value, without catalog validation or
    catalog creation. Geometry and explicit non-material evidence must remain
    unchanged at preflight and fresh readback; unsupported variants are blocked.
    Complex property representations provide bounded drift evidence only.
    Delete with changes=[{target:{kind:delete}}] as the only edit. This binds
    exact terminal component roots and their full bounded owned subtrees, or a
    WindowDoor opening directly owned by a Wall; it never uses the current UI
    selection or redirects an opening to its wall. Other children cannot be
    deleted independently. A root
    and matching child become one root deletion; excluded descendants block it.
    Review the complete cascade scope in resource.delete_ownership before Apply.
    DeleteElements return values are not success: a complete fresh identity scan
    must prove every reviewed model identity absent. Partial/unreadable absence
    stays unknown and blocks further writes. Recovery never repeats deletion.
    is_unset matches observed null/blank. Combine explicit undefined values with any.
    Stored ReadAll omissions are unknown, never absence. The new opt-in
    attribute_read_mode=all_and_computable establishes absence only after a complete
    documented read; is_unset then includes absent and not exists matches absence.
    No broad definition/enum discovery. all_and_computable explicitly includes
    computed values in targeted reads; computed_only values remain marked and
    cannot be edited. model_query stays read-only; model_edit applies only under
    its separate safeguards. Stored remains default; existing ReadAll routes
    are unchanged.
    Metadata-bound numeric/boolean attributes can replace exact old undefined
    strings <niezdefiniowany> or <undefined>, with their raw old value preserved.
    Arbitrary old strings are never parsed/coerced. Wall layer edits bind all
    directly owned tiers and use their agreed layer, rather than a root-only
    setter/readback. Mixed tier layers or unknown ownership block the plan.
    Use wall.total_thickness_mm < 240 for walls thinner than 24 cm: the native
    criterion and the complete Wall peer set are bound/revalidated in the plan,
    including changes into or out of the match, without a separate UUID handoff.

    highlight presents all matches including no-ops; native select stays unsupported.
    Apply is experimental, limited to 32 setters in one foreground drawing, with
    exact highlighted plan/hash, execution_id and disposable_copy_reviewed_plan.
    The public apply_available reports this offered evaluation Apply;
    evaluation_apply_available is its compatibility alias, while
    production_apply_available remains false. Pending native acceptance does
    not disable an otherwise eligible evaluation Apply. Never claim that
    experimental Apply has native acceptance. Continue only when the user has
    authorized the write and the exact plan, acknowledgement and safety checks
    are satisfied. Preview/highlight responses expose write_mode, blockers,
    required_steps and next_action; follow the returned exact model_edit request.
    Before apply, persist the new UUID4 hex execution_id named by
    next_action.required_request_fields.
    Persist the exact Apply request before sending. Use a 32-character lowercase
    hexadecimal execution_id (uuid.uuid4().hex). Lost replies require recover
    with that same execution ID; never create a new ID or automatically retry writes.
    Shared journal, fresh scope/resource checks, native writability and readback
    remain enforced. Recover M4 executions by exact journal targets in the original
    project/document, without requiring a new global criterion scan. Recovery
    never repeats setters. Follow its journal blockers and next action; if the
    outcome remains unreadable, preserve the journal and do not create a new
    execution ID to bypass it. Native acceptance of this new path is pending.
    If a trace/journal fills, follow next_action to fix_model_issues
    preview_journal_cleanup. Ask for user confirmation before cleanup_journal;
    no shell deletion or automatic retry of Apply. Cleanup preserves unresolved
    executions and the archived execution-ID replay guard.
    """
    payload = request.model_dump(by_alias=True, exclude_unset=True)
    payload["schema_version"] = "m4-model-edit-1"
    try:
        return _allplan_client().post("/model-edit", payload)
    except AllplanHostError as exc:
        if exc.code not in {"repair_journal_full", "probe_trace_unavailable"}:
            raise
        target = "repair_records" if exc.code == "repair_journal_full" else "native_trace"
        # A trace error can occur after native work. Do not infer that retrying
        # an Apply is safe merely because maintenance is available.
        return {"action": payload["action"], "state": "journal_maintenance_required",
                "error": {"code": exc.code, "message": str(exc)}, "request_id": exc.request_id,
                "execution_id": payload.get("execution_id"), "automatic_retry": False,
                "outcome": "not_established", "user_confirmation_required": True,
                "next_action": {"tool": "fix_model_issues", "request": {
                    "action": "preview_journal_cleanup", "target": target}},
                "report_text": "Show the cleanup preview and ask the user before archival. "
                    "After an attempted Apply, inspect/recover its original execution ID; never repeat setters automatically."}


@mcp.tool
def model_properties(request: PropertiesRequest) -> dict[str, Any]:
    """Property discovery is suspended after the native 0.16.0 crash.

    Valid requests return native_probe_blocked before native API/document access.
    Preserve bridge.log; do not repeat the broad discovery experiment. The
    following contract describes the suspended implementation, not native support.

    Defaults to open_drawings, including passive files for reads. Optional exact
    attribute_names/layer_short_names resolve through native ID/name round trips;
    no IDs or semantic aliases are guessed. Reports raw types, units, enum labels,
    sampled adapter ownership and a build-bound support registry. This catalog
    covers sampled attributes and requested names, not every project definition.
    A read or API symbol never establishes replace/add/native-update support.
    native.material, attribute material, visual.surface and organizational.layer
    remain separate. C35 requires the actual catalog; wall thickness has no AABB
    substitute. No resources are created and no writes are enabled by this probe.
    This discovery gate failed natively; it is not ready_for_owner_test.
    """
    payload = request.model_dump(exclude_unset=True)
    payload["schema_version"] = "m4-properties-1"
    return _allplan_client().post("/model-properties", payload)


@mcp.tool
def model_property_probe(request: PropertyProbeRequest) -> dict[str, Any]:
    """Run exactly one isolated native property-read phase after the M4 crash.

    Begin with column_sample in foreground file 101 of the retained test copy;
    it reads one Column root's raw attributes, without metadata, enums or UI.
    wall_sample independently reads one Wall root's native properties in one
    foreground drawing, optionally by model_uuid (otherwise first by model UUID).
    Only a single-tier Wall is read: native Thickness and Material, no attribute
    or surface substitution. Multi-tier/invalid/failed reads stop without fallback.
    component_identity reads one explicit drawing/model/view adapter's ancestry,
    direct children and represented native Python type. Use it to distinguish
    Slab tiers, MultiSlab owners and opening/inserted adapters. It never merges
    identities by bounds or establishes which adapter owns a writable property.
    drawing_identity explicitly inventories direct model/view identities in one
    foreground drawing, including children and unsupported families. It returns
    at most 32 views per page (offset/limit), with per-view hierarchy/native-type
    observations and explicit unreadable/conflicting results. Each page is a
    fresh scan; compare source_fingerprint before combining pages.
    The <240 mm comparison is informational pending native units/value observation;
    it neither finds all thin walls nor binds C35 or authorizes material writes.
    Other phases resolve one exact attribute/layer name or read one observed
    attribute ID's metadata. Every new native call is preceded by a flushed/fsynced
    Local/.allplan-mcp/logs/m4-native-probe.jsonl entry. Unwritable/full tracing blocks
    calls. M1 scan is logged as one existing service phase, not an individual API
    trace. Review one phase's evidence before requesting another; no automatic
    implicit batch, retries, GetEnumValues, highlighting, writes or resource creation.
    element_attributes requires one exact foreground drawing/model UUID/view UUID;
    it pages ReadAll values and targeted name/ID roundtrip and SDK type metadata
    for that root adapter across supported semantic families. Name search is
    case-insensitive. Incomplete name/type metadata makes total_matches unknown
    and suppresses next_offset. This is not a project definition catalog, does
    not prove omissions, applicability or writability, and never probes
    enum/control/unit metadata.
    layer_name accepts layer_name for a full or short name, or the legacy
    layer_short_name. If the SDK cannot resolve the full name, follow the returned
    layer_catalog continuation. That read-only phase scans bounded ID pages and
    searches full and short names without removing Polish diacritics. Its page
    trace records the batch before native reads. Ask the user to confirm the
    returned full name and short_name whenever confirmation_required is returned;
    preserve the returned confirmed_targets entry, including expected ID/name,
    for a new model_edit preview. Continue searching with continue_search when
    the user needs more candidates. An incomplete
    scan or an API error never proves a layer absent or authorizes a write.
    The broad model_properties route stays blocked. Native acceptance is pending.
    """
    payload = request.model_dump(exclude_unset=True)
    payload["schema_version"] = "m4-property-probe-1"
    return _allplan_client().post("/model-property-probe", payload)


@mcp.tool
def model_wall_filter(request: WallFilterRequest) -> dict[str, Any]:
    """Find and optionally highlight Walls by native total thickness, strictly less than a threshold.

    Supply one explicit active foreground drawing. The default threshold is
    24 cm (240 mm); exactly 240 mm does not match. Only single-tier native Walls
    are supported, using tier Thickness rather than an axis-aligned bounding box.
    mm/cm/m convert to native mm; runtime units still require owner observation.
    Every nonexcluded Wall must be resolved and read within the bounded budget;
    incomplete scope, unsupported multi-tier Walls or a failed read block all UI
    calls. Results include all Walls up to max_walls (default 20, maximum 100),
    without paging. UUID exceptions must name members of that drawing's Wall set.

    query reads only. highlight evaluates a fresh full scope in one UI dispatch
    and replaces document highlights, also clearing stale highlights for zero
    matches. It reports submitted adapters, with visibility/counts pending owner
    observation. This is highlighting; native selection remains unsupported.
    No material/attribute reads, setters, resources, edit plans or Apply IDs.
    Preserve the pending request before sending; never retry a lost native reply.
    This new Wall filter/highlight requires a bounded native Allplan test.
    """
    payload = request.model_dump(exclude_unset=True)
    payload["schema_version"] = "m4-wall-filter-1"
    return _allplan_client().post("/model-wall-filter", payload)


@mcp.tool
def model_selection(request: SelectionRequest) -> dict[str, Any]:
    """Present the full revalidated model_query selection through explicit UI actions.

    highlight re-resolves every match across all pages, with optional model-UUID
    exceptions. It replaces all highlights in the current document, including
    other sources. clear_highlight has the same document-wide clear scope.
    Native visibility/highlight count requires owner observation; submitted counts
    are not proof of highlighted or selected elements. select returns unsupported
    in the current interactor and never substitutes highlighting. Stale/expired
    selections fail before UI calls. No model data is written, no files activated,
    and UI presentation never authorizes a repair. UI failures return unknown;
    inspect the view and clear explicitly, without automatic retry.
    """
    payload = request.model_dump(exclude_unset=True)
    payload["schema_version"] = "m4-selection-1"
    return _allplan_client().post("/model-selection", payload)


@mcp.tool
def model_audit(request: AuditRequest) -> dict[str, Any]:
    """Audit a fresh full explicit scope without changing or highlighting elements.

    Supply profile_id=native-model-qa-demo or a complete m2-profile-1 profile.
    The demo checks marks, per-file/family uniqueness, layers and allowed status.
    Its literal <niezdefiniowany> means missing only by declared policy; raw
    evidence is retained. Optional dimension_range checks axis-aligned mm extents.
    Unknown reads stay not_checked; empty applicability stays not_applicable.
    Report includes severity, raw evidence, session/snapshot refs and file/mark/
    model_local locations. Missing resources reject the audit before enumeration.
    Each call rereads the model; findings are read evidence and authorize no writes.
    """
    payload = request.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)
    if payload.pop("profile_id", None) is not None:
        payload["profile"] = load_audit_profile()
    payload["schema_version"] = "m2-audit-1"
    return _allplan_client().post("/model-audit", payload)


@mcp.tool
def fix_model_issues(request: RepairRequest) -> dict[str, Any]:
    """Preview/revalidate repairs, apply the bounded disposable-copy gate, or recover.

    Preview takes a fresh audit request and explicit rule_id/value choices.
    Mark choices additionally require exact model_uuid targets; their final
    values are collision-checked in the full scope before evaluation Apply.
    Optional finding_ids restrict targets to those exact fresh findings.
    Returns old/new values, exclusions, locators, plan ID/hash and a five-minute
    lifetime. Revalidate requires that exact ID/hash and rereads the full scope.
    Changed evidence conflicts; restart/expiry/eviction require a new preview.
    Evaluation apply supports 1..32 reviewed existing string mark/status or layer changes on
    Column roots in one foreground file, including selected/standard plans,
    with exact plan ID/hash, persistent execution_id and acknowledgement
    disposable_copy_reviewed_plan. The old two-repair acknowledgement is retained
    only for its accepted fixture. It checks native eligibility, stops on
    failure and reads back results. Repeated execution IDs never repeat setters.
    Recover reads persisted execution/current values without resuming writes.
    inspect_journal returns verified historical record summaries, capacity and
    unresolved/invalid record blockers without reading or changing the model.
    It neither reconciles records nor establishes current values after Undo.
    For a full diagnostic trace or execution journal, use preview_journal_cleanup
    with target=native_trace or repair_records. Show the returned scope/counts and
    ask the user whether to clean it. Only after their confirmation send
    cleanup_journal with that exact snapshot_hash and acknowledgement
    confirmed_journal_cleanup. It archives bytes, never deletes unresolved,
    corrupt or oversized execution records, and preserves archived execution IDs
    for setter-free replay. Trace rotation and record archival do not edit Allplan.
    Changed snapshots require a fresh preview and confirmation. Cleanup is never
    automatic without user consent and never retries the interrupted model edit.
    The retained mark-numbering gate has bounded native acceptance. The diagnostic
    evaluation_stop control requires disposable_copy_reviewed_recovery_test and
    only the retained unselected two-mark numbering fixture. It stops after the
    first setter before readback; normal recovery never resumes the second target.
    Other native-property writes remain unavailable. Native UI Undo requires
    two separate steps for the accepted retained fixture; no automatic rollback.
    """
    payload = request.model_dump(exclude_unset=True, exclude_none=True, by_alias=True)
    if getattr(request, "selection", None) is not None:
        payload["selection"] = request.selection.model_dump(exclude_unset=True, by_alias=True)
    return _send_repair(payload)


@mcp.tool
def apply_office_standard(request: OfficeStandardRequest) -> dict[str, Any]:
    """Preview and execute an explicit versioned layer/status or numbering standard.

    Requires standard ID/version and one active drawing file. Optional query
    predicate/model-UUID exceptions filter fresh audit findings on the same scan.
    Apply requires exact reviewed plan ID/hash, a saved execution ID and
    disposable_copy_reviewed_plan. It must reference an office-standard plan.
    The mark-numbering standard preserves valid marks, retains a deterministic
    duplicate keeper and fills free S numbers in center Y/X/Z/UUID order.
    Excluded peers retain their marks and reserve numbers. Revalidate/recover
    reuse the shared service. Mark writes have bounded fixture acceptance; file moves
    remain unavailable.
    """
    if request.action != "preview":
        payload = request.model_dump(exclude_unset=True, exclude_none=True, by_alias=True)
        if request.action == "apply":
            payload["workflow_kind"] = "office_standard_preview"
        return _send_repair(payload)
    standard = load_office_standard(request.standard_id)
    payload = {"action": "preview", "audit": {"profile_id": standard["audit_profile_id"],
               "scope": request.scope.model_dump()}, "repairs": standard["repairs"],
               "workflow": {k: standard[k] for k in ("standard_id", "standard_version", "standard_fingerprint")}}
    payload["workflow"]["kind"] = "office_standard_preview"
    if "numbering" in standard:
        payload["numbering"] = standard["numbering"]
    if request.selection is not None:
        payload["selection"] = request.selection.model_dump(exclude_unset=True, by_alias=True)
    return _send_repair(payload)


@mcp.tool
def rule_based_edit(request: RuleBasedRequest) -> dict[str, Any]:
    """Preview and execute selected mark/status/layer repairs with query/UUID exceptions.

    Selection uses audited mark/status/layer_id/file_state or selected dimension
    fields from one full fresh scan. Unknown predicates block readiness. Excluded
    elements still participate in full source revalidation. Apply requires exact
    reviewed plan ID/hash, saved execution ID and disposable_copy_reviewed_plan;
    it must reference a rule-based plan. Mark choices require exact
    model_uuid targets and selected required/unique mark rules; final mark values
    are checked for collisions against the full scope, including excluded peers,
    before evaluation Apply. Mark writes have bounded fixture acceptance.
    Revalidate/recover reuse the shared service.
    """
    if request.action != "preview":
        payload = request.model_dump(exclude_unset=True, exclude_none=True, by_alias=True)
        if request.action == "apply":
            payload["workflow_kind"] = "rule_based_edit_preview"
        return _send_repair(payload)
    payload = request.model_dump(exclude_unset=True, exclude_none=True, by_alias=True)
    payload["selection"] = request.selection.model_dump(exclude_unset=True, by_alias=True)
    payload["workflow"] = {"kind": "rule_based_edit_preview"}
    return _send_repair(payload)


def _send_repair(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["action"] == "preview":
        audit = payload["audit"]
        if audit.pop("profile_id", None) is not None:
            audit["profile"] = load_audit_profile()
        audit["schema_version"] = "m2-audit-1"
    payload["schema_version"] = "m3-repair-1"
    try:
        return _allplan_client().post("/fix-model-issues", payload)
    except AllplanHostError as exc:
        # These apply errors originate before any setter in the current request.
        # Journal/transport/unexpected failures may occur after a write and must
        # remain errors with unknown outcomes; never infer safety from text.
        before_write = {"target_not_writable", "plan_expired", "plan_hash_mismatch",
                        "repair_scope_unavailable", "repair_conflict", "repair_journal_full",
                        "execution_id_conflict", "repair_recovery_required"}
        if payload["action"] != "apply" or exc.code not in before_write:
            raise
        return {"schema_version": "m3-execution-1", "action": "apply", "state": "rejected",
                "read_only": True, "native_setters_started": False,
                "execution_id": payload["execution_id"], "request_id": exc.request_id,
                "error": {"code": exc.code, "message": str(exc)},
                "report_text": "Apply rejected before native setters: " + str(exc)}


@mcp.tool
def get_all_object_names() -> list[str]:
    """Get display names for all elements in the current Allplan document."""

    response = _allplan_client().post("/get-all-object-names")
    names = response.get("names", [])
    if not isinstance(names, list):
        raise ValueError(f"Unexpected Allplan response for names: {response!r}")

    return [str(name) for name in names]


@mcp.tool
def create_cube(size: float) -> dict[str, Any]:
    """Submit one cube in the current Allplan document; size is in mm. Inspect the result before retrying."""

    if not math.isfinite(size) or size <= 0:
        raise ValueError("size must be greater than zero.")

    response = _allplan_client().post(
        "/create-box",
        {
            "length": size,
            "width": size,
            "height": size,
        },
    )
    return {
        "submitted": True,
        "readback_verified": False,
        "request_id": response.get("request_id"),
        "type": "cube",
        "dimensions": {
            "length": size,
            "width": size,
            "height": size,
        },
    }


@mcp.tool
def create_box(length: float, width: float, height: float) -> dict[str, Any]:
    """Submit one cuboid in the current Allplan document; dimensions are in mm. Inspect before retrying."""

    if any(not math.isfinite(v) or v <= 0 for v in (length, width, height)):
        raise ValueError("length, width, and height must be greater than zero.")

    response = _allplan_client().post(
        "/create-box",
        {
            "length": length,
            "width": width,
            "height": height,
        },
    )
    return {
        "submitted": True,
        "readback_verified": False,
        "request_id": response.get("request_id"),
        "type": "cuboid",
        "dimensions": {
            "length": length,
            "width": width,
            "height": height,
        },
    }


def execute_python(
    code: str,
    result_expression: str | None = None,
) -> dict[str, Any]:
    """Development only: execute AST-filtered Python inside Allplan; not an isolation boundary."""

    if not code.strip():
        raise ValueError("code must be a non-empty string.")

    payload: dict[str, Any] = {"code": code}
    if result_expression is not None:
        payload["result_expression"] = result_expression

    return _allplan_client().post("/execute-python", payload)


if os.getenv("ALLPLAN_MCP_ENABLE_PYTHON_EXEC") == "1":
    mcp.tool(execute_python)


def main() -> None:
    host = os.getenv("MCP_HOST", DEFAULT_MCP_HOST)
    port = int(os.getenv("MCP_PORT", str(DEFAULT_MCP_PORT)))
    path = os.getenv("MCP_PATH", DEFAULT_MCP_PATH)

    mcp.run(transport="http", host=host, port=port, path=path)


if __name__ == "__main__":
    main()
