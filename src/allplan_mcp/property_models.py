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


class ColumnProbeInput(ContractModel):
    phase: Literal["column_sample"]
    drawing_file: int = Field(ge=1, le=2147483647)


class AttributeNameProbeInput(ContractModel):
    phase: Literal["attribute_name"]
    attribute_name: str = Field(min_length=1, max_length=128)


class AttributeDefinitionProbeInput(ContractModel):
    phase: Literal["attribute_definition"]
    attribute_id: int = Field(ge=1, le=2147483647)


class LayerNameProbeInput(ContractModel):
    phase: Literal["layer_name"]
    layer_short_name: str = Field(min_length=1, max_length=16)


PropertyProbeRequest = Annotated[ColumnProbeInput | AttributeNameProbeInput | AttributeDefinitionProbeInput | LayerNameProbeInput, Field(discriminator="phase")]
