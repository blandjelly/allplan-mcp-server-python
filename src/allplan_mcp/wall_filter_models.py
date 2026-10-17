"""Bounded single-drawing semantic Wall thickness query and presentation."""
from typing import Annotated, Literal

from pydantic import Field

from .query_models import ContractModel


class WallThicknessThreshold(ContractModel):
    value: float = Field(gt=0, le=1_000_000, allow_inf_nan=False)
    unit: Literal["mm", "cm", "m"]


class WallFilterRequest(ContractModel):
    action: Literal["query", "highlight"]
    drawing_file: int = Field(ge=1, le=2147483647)
    threshold: WallThicknessThreshold = Field(default_factory=lambda: WallThicknessThreshold(value=24, unit="cm"))
    exclude_model_uuids: list[Annotated[str, Field(pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")]] = Field(default_factory=list, max_length=100)
    max_walls: int = Field(default=20, ge=1, le=100)
