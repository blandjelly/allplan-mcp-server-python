"""Typed public inputs for the bounded, read-only M2 audit."""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from .query_models import ContractModel, QueryScope


class MissingValues(ContractModel):
    absent: bool
    null: bool
    empty: bool
    literals: list[str] = Field(max_length=20)


class StringPolicy(ContractModel):
    trim: bool
    case_sensitive: bool
    missing: MissingValues


class RuleBase(ContractModel):
    rule_id: str = Field(pattern=r"^[A-Z][A-Z0-9-]{0,31}$")
    severity: Literal["info", "warning", "error"]
    remedy: str = Field(min_length=1, max_length=512)


class RequiredAttribute(RuleBase):
    kind: Literal["required_attribute"]
    attribute: Literal["mark", "status"]


class UniqueAttribute(RuleBase):
    kind: Literal["unique_attribute"]
    attribute: Literal["mark", "status"]
    ignore_missing: bool
    uniqueness_scope: list[Literal["drawing_file", "element_family"]]


class RequiredLayer(RuleBase):
    kind: Literal["required_layer"]
    expected_layer: Literal["structure", "review"]


class AllowedValues(RuleBase):
    kind: Literal["allowed_attribute_values"]
    attribute: Literal["mark", "status"]
    allowed_values: list[str] = Field(min_length=1, max_length=100)


class DimensionRange(RuleBase):
    kind: Literal["dimension_range"]
    field: Literal["size_x_mm", "size_y_mm", "size_z_mm"]
    min_mm: float = Field(allow_inf_nan=False, ge=0)
    max_mm: float = Field(allow_inf_nan=False, ge=0)
    tolerance_mm: float = Field(allow_inf_nan=False, ge=0)


AuditRule = Annotated[RequiredAttribute | UniqueAttribute | RequiredLayer | AllowedValues | DimensionRange,
                      Field(discriminator="kind")]


class AuditProfile(ContractModel):
    schema_version: Literal["m2-profile-1"]
    profile_id: Literal["native-model-qa-demo"]
    profile_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    read_profile: dict
    string_policies: dict[Literal["mark", "status"], StringPolicy]
    rules: list[AuditRule] = Field(min_length=1, max_length=32)


class AuditRequest(ContractModel):
    scope: QueryScope
    profile_id: Literal["native-model-qa-demo"] | None = None
    profile: AuditProfile | None = None
    rule_ids: list[str] | None = Field(default=None, min_length=1, max_length=32)
    max_adapters: int = Field(default=5000, ge=1, le=10000)

    @model_validator(mode="after")
    def one_profile(self):
        if (self.profile_id is None) == (self.profile is None):
            raise ValueError("Supply exactly one profile_id or explicit profile.")
        from .demo_profile import load_audit_profile
        read_profile = self.profile.read_profile if self.profile is not None else load_audit_profile()["read_profile"]
        scope = read_profile.get("scope")
        files = scope.get("drawing_files") if isinstance(scope, dict) else None
        if not isinstance(files, list) or not 1 <= len(files) <= 100 or any(type(v) is not int or v < 1 or v > 2147483647 for v in files):
            raise ValueError("Audit read_profile must declare explicit positive drawing_files.")
        if len(set(files)) != len(files) or len(set(self.scope.drawing_files)) != len(self.scope.drawing_files):
            raise ValueError("Duplicate drawing-file IDs are not allowed.")
        if not set(self.scope.drawing_files) <= set(files):
            raise ValueError("Requested audit files exceed the explicit profile scope.")
        return self
