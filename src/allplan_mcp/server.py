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
    fields are not_checked; units/offset conversion still needs runtime checks.
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

    Query requires explicit positive drawing_files, include_passive and
    visibility=api_select_all. Use observed type GUID/name, layer ID or
    attribute:<ID> predicates with all/any/not. Missing/failed reads are distinct.
    Pages and summaries revalidate query fields; stale selections are rejected.
    Selections expire after five minutes or host restart, count model UUIDs rather
    than components by default, and cannot authorize writes. Explicit
    component_kind=top_level_component resolves parent chains for ordinary
    columns/beams/walls/slabs. Geometry uses mm, model_local or project_global
    (local plus project offset once), with size_*_mm axis-aligned extents.
    spatial_box is a declared inclusive/exclusive AABB intersects/contained test,
    not exact solid intersection. These new native readers need Allplan acceptance.
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
    Optional finding_ids restrict targets to those exact fresh findings.
    Returns old/new values, exclusions, locators, plan ID/hash and a five-minute
    lifetime. Revalidate requires that exact ID/hash and rereads the full scope.
    Changed evidence conflicts; restart/expiry/eviction require a new preview.
    Evaluation apply supports only the two retained file-101 Column repairs,
    with exact plan ID/hash, persistent execution_id and acknowledgement
    disposable_copy_reviewed_two_repairs. It checks native eligibility, stops on
    failure and reads back results. Repeated execution IDs never repeat setters.
    Recover reads persisted execution/current values without resuming writes.
    General apply and native Undo acceptance remain unavailable.
    """
    payload = request.model_dump(exclude_unset=True, exclude_none=True)
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
