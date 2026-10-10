"""Versioned previews and reviewed execution over the shared repair service."""
from typing import Annotated, Literal

from pydantic import Field

from .query_models import ContractModel, QueryScope
from .repair_models import RepairApply, RepairPreview, RepairRecover, RepairRevalidate, RepairSelection


class OfficeStandardPreview(ContractModel):
    action: Literal["preview"]
    standard_id: Literal["native-model-qa-demo-layer-status", "native-model-qa-demo-mark-numbering"]
    standard_version: Literal["1.0.0"]
    scope: QueryScope
    selection: RepairSelection | None = None


class RuleBasedPreview(RepairPreview):
    selection: RepairSelection = Field()


OfficeStandardRequest = Annotated[OfficeStandardPreview | RepairRevalidate | RepairApply | RepairRecover, Field(discriminator="action")]
RuleBasedRequest = Annotated[RuleBasedPreview | RepairRevalidate | RepairApply | RepairRecover, Field(discriminator="action")]
