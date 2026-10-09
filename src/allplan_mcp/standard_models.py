"""Read-only entry points over the shared versioned repair planner."""
from typing import Literal

from pydantic import Field

from .query_models import ContractModel, QueryScope
from .repair_models import RepairPreview, RepairSelection


class OfficeStandardPreview(ContractModel):
    action: Literal["preview"]
    standard_id: Literal["native-model-qa-demo-layer-status"]
    standard_version: Literal["1.0.0"]
    scope: QueryScope
    selection: RepairSelection | None = None


class RuleBasedPreview(RepairPreview):
    selection: RepairSelection = Field()
