"""M3 plans, bounded disposable-copy execution and read-only recovery."""
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .audit_models import AuditRequest
from .query_models import ContractModel, Predicate


class RepairSelection(ContractModel):
    where: Predicate
    exclude_model_uuids: list[Annotated[str, Field(pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")]] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def distinct_exceptions(self):
        if len(set(self.exclude_model_uuids)) != len(self.exclude_model_uuids):
            raise ValueError("Duplicate exception model UUIDs are not allowed.")
        return self


class RepairChoice(ContractModel):
    rule_id: str = Field(pattern=r"^[A-Z][A-Z0-9-]{0,31}$")
    value: str = Field(min_length=1, max_length=128)
    model_uuid: Annotated[str, Field(pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")] | None = None


class RepairPreview(ContractModel):
    action: Literal["preview"]
    audit: AuditRequest
    repairs: list[RepairChoice] = Field(min_length=1, max_length=32)
    selection: RepairSelection | None = None
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
        keys = [(r.rule_id, r.model_uuid) for r in self.repairs]
        if len(set(keys)) != len(keys) or not set(ids) <= set(rules):
            raise ValueError("Repair choices must reference distinct selected rule/target pairs.")
        mark_targets = set()
        for choice in self.repairs:
            rule = rules[choice.rule_id]
            if rule["kind"] in {"required_attribute", "unique_attribute"} and rule["attribute"] == "mark":
                if choice.model_uuid is None or choice.model_uuid in mark_targets:
                    raise ValueError("Each mark repair requires one distinct explicit model UUID.")
                mark_targets.add(choice.model_uuid)
                if not {"required_attribute", "unique_attribute"} <= {
                        r["kind"] for r in rules.values() if r.get("attribute") == "mark"}:
                    raise ValueError("Mark repairs require selected required-mark and unique-mark rules.")
                policy = profile["string_policies"]["mark"]
                value = choice.value.strip() if policy["trim"] else choice.value
                norm = lambda v: v if policy["case_sensitive"] else v.casefold()
                missing = policy["missing"]
                if (not value.strip() or any(ord(c) < 32 or ord(c) == 127 for c in choice.value)
                        or norm(value) in {norm(v.strip() if policy["trim"] else v) for v in missing["literals"]}):
                    raise ValueError("Mark repairs require a nonmissing string without control characters.")
            elif "model_uuid" in choice.model_fields_set:
                raise ValueError("Explicit model UUID choices are supported only for mark repairs.")
            elif rule["kind"] == "required_layer":
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
                raise ValueError("Supported previews are required-layer, allowed-status and explicit mark repairs.")
        if self.finding_ids is not None and len(set(self.finding_ids)) != len(self.finding_ids):
            raise ValueError("Duplicate finding IDs are not allowed.")
        return self


class RepairRevalidate(ContractModel):
    action: Literal["revalidate"]
    plan_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class RepairApply(RepairRevalidate):
    action: Literal["apply"]
    execution_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    acknowledgement: Literal["disposable_copy_reviewed_two_repairs"]


class RepairRecover(ContractModel):
    action: Literal["recover"]
    execution_id: str = Field(pattern=r"^[0-9a-f]{32}$")


RepairRequest = Annotated[RepairPreview | RepairRevalidate | RepairApply | RepairRecover, Field(discriminator="action")]
