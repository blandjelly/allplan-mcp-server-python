"""Project metadata discovery, separate from property mutation eligibility."""
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .query_models import ContractModel, QueryScope

NativeFamily = Literal["Column_TypeUUID", "Wall_TypeUUID", "Beam_TypeUUID",
                       "SkeletonBeam_TypeUUID", "Slab_TypeUUID", "MultiSlab_TypeUUID"]


class PropertiesRequest(ContractModel):
    scope: QueryScope | Literal["open_drawings"] = "open_drawings"
    native_types: list[NativeFamily] = Field(default_factory=lambda: ["Column_TypeUUID", "Wall_TypeUUID"], min_length=1, max_length=6)
    attribute_names: list[Annotated[str, Field(min_length=1, max_length=128)]] = Field(default_factory=list, max_length=16)
    layer_short_names: list[Annotated[str, Field(min_length=1, max_length=16)]] = Field(default_factory=list, max_length=16)
    layer_names: list[Annotated[str, Field(min_length=1, max_length=128)]] = Field(default_factory=list, max_length=16)
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


class WallProbeInput(ContractModel):
    phase: Literal["wall_sample"]
    drawing_file: int = Field(ge=1, le=2147483647)
    model_uuid: str = Field(default=None, pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")


class AttributeNameProbeInput(ContractModel):
    phase: Literal["attribute_name"]
    attribute_name: str = Field(min_length=1, max_length=128)


class AttributeDefinitionProbeInput(ContractModel):
    phase: Literal["attribute_definition"]
    attribute_id: int = Field(ge=1, le=2147483647)


class ElementAttributesProbeInput(ContractModel):
    phase: Literal["element_attributes"]
    drawing_file: int = Field(ge=1, le=2147483647)
    model_uuid: str = Field(pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
    view_uuid: str = Field(pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
    name_contains: str = Field(default="", max_length=64)
    offset: int = Field(default=0, ge=0, le=255)
    limit: int = Field(default=32, ge=1, le=32)

    @model_validator(mode="after")
    def nonzero_identities(self):
        # UUID shape is part of the public contract; reject the null sentinel
        # before any host/document call as well as in the dependency-free host.
        if (self.model_uuid == "00000000-0000-0000-0000-000000000000"
                or self.view_uuid == "00000000-0000-0000-0000-000000000000"):
            raise ValueError("model_uuid and view_uuid must be nonzero canonical UUIDs.")
        return self


class ComponentIdentityProbeInput(ContractModel):
    phase: Literal["component_identity"]
    drawing_file: int = Field(ge=1, le=2147483647)
    model_uuid: str = Field(pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
    view_uuid: str = Field(pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")

    @model_validator(mode="after")
    def nonzero_identities(self):
        if "00000000-0000-0000-0000-000000000000" in (self.model_uuid, self.view_uuid):
            raise ValueError("model_uuid and view_uuid must be nonzero canonical UUIDs.")
        return self


class LayerNameProbeInput(ContractModel):
    phase: Literal["layer_name"]
    layer_short_name: str | None = Field(default=None, min_length=1, max_length=16)
    layer_name: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def exactly_one_layer_spelling(self):
        if (self.layer_short_name is None) == (self.layer_name is None):
            raise ValueError("Provide exactly one of layer_short_name or layer_name.")
        return self


class LayerCatalogProbeInput(ContractModel):
    phase: Literal["layer_catalog"]
    layer_name: str = Field(min_length=1, max_length=128)
    offset: int = Field(default=0, ge=0, le=65536)
    limit: int = Field(default=8192, ge=1, le=8192)
    candidate_ids: list[Annotated[int, Field(ge=0, le=65535)]] = Field(default_factory=list, max_length=8192)

    @model_validator(mode="after")
    def distinct_candidate_ids(self):
        if len(set(self.candidate_ids)) != len(self.candidate_ids):
            raise ValueError("candidate_ids must be distinct.")
        return self


PropertyProbeRequest = Annotated[ColumnProbeInput | WallProbeInput | AttributeNameProbeInput | AttributeDefinitionProbeInput | ElementAttributesProbeInput | ComponentIdentityProbeInput | LayerNameProbeInput | LayerCatalogProbeInput, Field(discriminator="phase")]
