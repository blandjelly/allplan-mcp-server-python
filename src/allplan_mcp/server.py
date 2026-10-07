from __future__ import annotations

import os
import math
import platform
from importlib.metadata import version
from typing import Annotated, Any

from fastmcp import FastMCP

from allplan_mcp.allplan_client import AllplanHostClient, AllplanHostError
from allplan_mcp.skills import SkillsManager


DEFAULT_ALLPLAN_HOST_URL = "http://127.0.0.1:5679"
DEFAULT_MCP_HOST = "127.0.0.1"
DEFAULT_MCP_PORT = 8888
DEFAULT_MCP_PATH = "/mcp"

mcp = FastMCP("Allplan MCP Server")
skills_manager = SkillsManager()


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
def get_model_context(identity_sample_size: int = 0) -> dict[str, Any]:
    """Read-only M1 probe: project, loaded file states, input units and raw offset.

    Optional 0–20 raw adapters expose model/view UUIDs separately. This sample
    is not a component count, reusable selection or write target. Unavailable
    fields are not_checked; units/offset conversion still needs runtime checks.
    """
    if isinstance(identity_sample_size, bool) or not isinstance(identity_sample_size, int) or not 0 <= identity_sample_size <= 20:
        raise ValueError("identity_sample_size must be from 0 to 20.")
    return _allplan_client().post("/get-model-context", {"identity_sample_size": identity_sample_size})


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
