"""Project metadata discovery, separate from property mutation eligibility."""
from typing import Annotated, Literal

from pydantic import Field

from .query_models import ContractModel, QueryScope

NativeFamily = Literal["Column_TypeUUID", "Wall_TypeUUID", "Beam_TypeUUID",
                       "SkeletonBeam_TypeUUID", "Slab_TypeUUID", "MultiSlab_TypeUUID"]


class PropertiesRequest(ContractModel):
    scope: QueryScope | Literal["open_drawings"] = "open_drawings"
    native_types: list[NativeFamily] = Field(default_factory=lambda: ["Column_TypeUUID", "Wall_TypeUUID"], min_length=1, max_length=6)
    attribute_names: list[Annotated[str, Field(min_length=1, max_length=128)]] = Field(default_factory=list, max_length=16)
    layer_short_names: list[Annotated[str, Field(min_length=1, max_length=16)]] = Field(default_factory=list, max_length=16)
    sample_limit: int = Field(default=10, ge=1, le=20)
    metadata_limit: int = Field(default=64, ge=1, le=128)
    max_adapters: int = Field(default=5000, ge=1, le=10000)


class HighlightInput(ContractModel):
    action: Literal["highlight", "select"]
    selection_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    exclude_model_uuids: list[Annotated[str, Field(pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")]] = Field(default_factory=list, max_length=100)


class ClearHighlightInput(ContractModel):
    action: Literal["clear_highlight"]


SelectionRequest = Annotated[HighlightInput | ClearHighlightInput, Field(discriminator="action")]
