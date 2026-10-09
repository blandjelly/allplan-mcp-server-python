"""Public MCP schemas. The dependency-free host validates the same JSON contract."""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Scalar = str | int | float | bool | None
QueryField = Literal["display_name", "type_name", "type_uuid", "layer_id", "drawing_file", "file_state",
                     "bounding_box_mm", "size_x_mm", "size_y_mm", "size_z_mm", "center_x_mm", "center_y_mm",
                     "center_z_mm", "min_z_mm", "max_z_mm", "hierarchy", "mark", "status"]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class QueryScope(ContractModel):
    drawing_files: list[Annotated[int, Field(ge=1, le=2147483647)]] = Field(min_length=1, max_length=100)
    include_passive: bool
    visibility: Literal["api_select_all"]


class Predicate(ContractModel):
    """Exactly one group (all/any/not), or field/op with operator-specific options."""

    all: list[Predicate] | None = None
    any: list[Predicate] | None = None
    not_: Predicate | None = Field(default=None, alias="not")
    field: str | None = None
    op: Literal["eq", "ne", "lt", "lte", "gt", "gte", "in", "contains", "exists", "is_null"] | None = None
    value: Scalar | list[Scalar] = None
    tolerance: float = Field(default=0, ge=0, allow_inf_nan=False)
    case_sensitive: bool = True
    trim: bool = False


class SpatialBox(ContractModel):
    min: list[Annotated[float, Field(allow_inf_nan=False)]] = Field(min_length=3, max_length=3)
    max: list[Annotated[float, Field(allow_inf_nan=False)]] = Field(min_length=3, max_length=3)
    relation: Literal["intersects", "contained"]
    boundary: Literal["inclusive", "exclusive"]
    frame: Literal["model_local", "project_global"]
    tolerance_mm: float = Field(default=0, ge=0, allow_inf_nan=False)


class QueryInput(ContractModel):
    action: Literal["query"]
    scope: QueryScope
    predicate: Predicate | None = None
    fields: list[QueryField] = Field(default_factory=lambda: ["display_name", "layer_id"])
    attribute_ids: list[Annotated[int, Field(ge=1, le=2147483647)]] = Field(default_factory=list, max_length=32)
    page_size: int = Field(default=100, ge=1, le=200)
    max_adapters: int = Field(default=5000, ge=1, le=10000)
    component_kind: Literal["model_identity", "top_level_component"] = "model_identity"
    coordinate_frame: Literal["model_local", "project_global"] = "model_local"
    spatial_box: SpatialBox | None = None
    profile_id: Literal["native-model-qa-demo"] | None = None


class PageInput(ContractModel):
    action: Literal["page"]
    selection_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    cursor: str | None = Field(default=None, pattern=r"^[0-9a-f]{32}$")
    page_size: int = Field(default=100, ge=1, le=200)


class SummaryInput(ContractModel):
    action: Literal["summary"]
    selection_id: str = Field(pattern=r"^[0-9a-f]{32}$")


class InspectInput(ContractModel):
    action: Literal["inspect"]
    scope: QueryScope
    attribute_ids: list[Annotated[int, Field(ge=1, le=2147483647)]] = Field(max_length=32)
    sample_limit: int = Field(default=10, ge=1, le=20)
    max_adapters: int = Field(default=5000, ge=1, le=10000)


class ProfileInput(ContractModel):
    action: Literal["profile"]
    profile_id: Literal["native-model-qa-demo"]


QueryRequest = Annotated[QueryInput | PageInput | SummaryInput | InspectInput | ProfileInput, Field(discriminator="action")]
