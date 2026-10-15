"""Typed first M4 vertical workflow; IDs come from project names, not guesses."""
from typing import Annotated, Literal
from pydantic import Field
from .query_models import ContractModel


class ColumnLayerPreview(ContractModel):
    action: Literal["preview"]
    drawing_file: int = Field(ge=1, le=2147483647)
    attribute_names: list[Annotated[str, Field(min_length=1, max_length=128)]] = Field(
        default_factory=lambda: ["Klasa odporności ogniowej", "Fire resistance classification"], min_length=1, max_length=4)
    layer_short_name: str = Field(default="W1", min_length=1, max_length=16)
    undefined_values: list[Annotated[str, Field(min_length=1, max_length=128)]] = Field(
        default_factory=lambda: ["<niezdefiniowany>", "<undefined>"], min_length=1, max_length=8)
    exclude_model_uuids: list[Annotated[str, Field(pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")]] = Field(default_factory=list, max_length=100)


class ColumnLayerPlan(ContractModel):
    action: Literal["highlight", "revalidate"]
    plan_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class ColumnLayerApply(ContractModel):
    action: Literal["apply"]
    plan_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    acknowledgement: Literal["disposable_copy_reviewed_plan"]


class ColumnLayerRecover(ContractModel):
    action: Literal["recover"]
    execution_id: str = Field(pattern=r"^[0-9a-f]{32}$")


ColumnLayerRequest = Annotated[ColumnLayerPreview | ColumnLayerPlan | ColumnLayerApply | ColumnLayerRecover, Field(discriminator="action")]
