"""First M3 slice: explicit, read-only repair plans and revalidation."""
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .audit_models import AuditRequest
from .query_models import ContractModel


class RepairChoice(ContractModel):
    rule_id: str = Field(pattern=r"^[A-Z][A-Z0-9-]{0,31}$")
    value: str = Field(min_length=1, max_length=128)


class RepairPreview(ContractModel):
    action: Literal["preview"]
    audit: AuditRequest
    repairs: list[RepairChoice] = Field(min_length=1, max_length=32)
    finding_ids: list[Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]] | None = Field(
        default=None, min_length=1, max_length=100)

    @model_validator(mode="after")
    def explicit_choices(self):
        from .demo_profile import load_audit_profile
        if self.audit.scope.include_passive or len(self.audit.scope.drawing_files) != 1:
            raise ValueError("Repair preview requires one explicit drawing file and include_passive=false.")
        profile = self.audit.profile.model_dump() if self.audit.profile else load_audit_profile()
        rules = {r["rule_id"]: r for r in profile["rules"]
                 if self.audit.rule_ids is None or r["rule_id"] in self.audit.rule_ids}
        ids = [r.rule_id for r in self.repairs]
        if len(set(ids)) != len(ids) or not set(ids) <= set(rules):
            raise ValueError("Repair choices must reference distinct selected rule IDs.")
        for choice in self.repairs:
            rule = rules[choice.rule_id]
            if rule["kind"] == "required_layer":
                if choice.value != rule["expected_layer"]:
                    raise ValueError("Layer repair must use the rule's explicit expected layer role.")
            elif rule["kind"] == "allowed_attribute_values" and rule["attribute"] == "status":
                if "status" not in profile["string_policies"]:
                    raise ValueError("A status string policy is required for status repairs.")
                policy = profile["string_policies"]["status"]
                def normalized(value):
                    value = value.strip() if policy["trim"] else value
                    return value if policy["case_sensitive"] else value.casefold()
                if normalized(choice.value) not in {normalized(v) for v in rule["allowed_values"]}:
                    raise ValueError("Status repair value must satisfy the selected rule.")
            else:
                raise ValueError("This slice supports required-layer and allowed-status repair previews only.")
        if self.finding_ids is not None and len(set(self.finding_ids)) != len(self.finding_ids):
            raise ValueError("Duplicate finding IDs are not allowed.")
        return self


class RepairRevalidate(ContractModel):
    action: Literal["revalidate"]
    plan_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


RepairRequest = Annotated[RepairPreview | RepairRevalidate, Field(discriminator="action")]
