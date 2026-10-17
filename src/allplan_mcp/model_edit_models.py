"""Public request contract for typed, criterion-based model edits."""
from typing import Annotated, Literal
import re

from pydantic import Field, model_validator

from .query_models import ContractModel, Predicate, QueryScope


class AttributeEditTarget(ContractModel):
    kind: Literal["attribute"]
    attribute_id: Annotated[int, Field(ge=1, le=2147483647)] | None = None
    name: Annotated[str, Field(min_length=1, max_length=128)] | None = None

    @model_validator(mode="after")
    def has_binding(self):
        if self.attribute_id is None and self.name is None:
            raise ValueError("Attribute edits require an attribute_id or exact name.")
        return self


class LayerEditTarget(ContractModel):
    kind: Literal["layer"]
    short_name: Annotated[str, Field(min_length=1, max_length=16)]


EditTarget = Annotated[AttributeEditTarget | LayerEditTarget, Field(discriminator="kind")]


class AttributeEdit(ContractModel):
    target: AttributeEditTarget
    value_type: Literal["text", "integer", "real", "boolean"]
    value: str | int | float | bool
    mode: Literal["replace", "upsert", "add"] = "replace"

    @model_validator(mode="after")
    def value_matches_type(self):
        valid = {
            "text": isinstance(self.value, str),
            "integer": isinstance(self.value, int) and not isinstance(self.value, bool),
            "real": isinstance(self.value, (int, float)) and not isinstance(self.value, bool),
            "boolean": isinstance(self.value, bool),
        }[self.value_type]
        if not valid:
            raise ValueError("value must match value_type.")
        if isinstance(self.value, float) and not __import__("math").isfinite(self.value):
            raise ValueError("value must be finite.")
        if self.target.kind != "attribute":
            raise ValueError("Typed attribute edits require an attribute target.")
        return self


class LayerEdit(ContractModel):
    target: LayerEditTarget


Edit = AttributeEdit | LayerEdit

_QUERY_FIELDS = {"display_name", "type_name", "type_uuid", "layer_id", "drawing_file", "file_state",
                 "bounding_box_mm", "size_x_mm", "size_y_mm", "size_z_mm", "center_x_mm", "center_y_mm",
                 "center_z_mm", "min_z_mm", "max_z_mm", "hierarchy", "family", "opening_kind", "wall.total_thickness_mm"}
_QUERY_OPS = {"eq", "ne", "lt", "lte", "gt", "gte", "in", "contains", "exists", "is_null", "is_unset"}


def _validate_predicate(node, depth=0, budget=None):
    if node is None:
        return
    budget = [0] if budget is None else budget
    budget[0] += 1
    if depth > 8 or budget[0] > 64:
        raise ValueError("Predicate exceeds the model_query size limit.")
    if not isinstance(node, dict):
        raise ValueError("Predicate must be an object.")
    groups = [key for key in ("all", "any", "not") if key in node]
    if groups:
        if len(groups) != 1 or set(node) != {groups[0]}:
            raise ValueError("Predicate group must contain exactly one group.")
        key = groups[0]
        children = [node[key]] if key == "not" else node[key]
        if not isinstance(children, list) or not 1 <= len(children) <= 64:
            raise ValueError("Predicate group must contain 1 to 64 children.")
        for child in children:
            _validate_predicate(child, depth + 1, budget)
        return
    field, op = node.get("field"), node.get("op")
    if not (field in _QUERY_FIELDS if isinstance(field, str) else False) and not (
            isinstance(field, str) and re.fullmatch(r"attribute:[1-9][0-9]{0,9}", field)):
        raise ValueError("Unknown model_query predicate field.")
    if op not in _QUERY_OPS:
        raise ValueError("Unknown model_query predicate operator.")


class ModelEditPreview(ContractModel):
    schema_version: Literal["m4-model-edit-1"] = "m4-model-edit-1"
    action: Literal["preview"]
    scope: QueryScope | Literal["open_drawings"] = "open_drawings"
    # A native type list may be combined with predicate as an additional filter.
    # With no native types, predicate must identify the intended family.
    native_types: list[Annotated[str, Field(min_length=1, max_length=128)]] = Field(
        default_factory=lambda: ["Column_TypeUUID", "Beam_TypeUUID", "SkeletonBeam_TypeUUID",
                                 "Wall_TypeUUID", "Slab_TypeUUID", "MultiSlab_TypeUUID", "WindowDoor_TypeUUID"], max_length=16)
    attribute_ids: list[Annotated[int, Field(ge=1, le=2147483647)]] = Field(default_factory=list, max_length=32)
    attribute_read_mode: Literal["stored", "all_and_computable"] = "stored"
    predicate: Predicate | None = None
    changes: list[Edit] = Field(min_length=1, max_length=16)
    exclude_model_uuids: list[Annotated[str, Field(pattern=r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")]] = Field(default_factory=list, max_length=100)
    max_adapters: int = Field(default=5000, ge=1, le=10000)

    @model_validator(mode="after")
    def distinct_and_scoped(self):
        _validate_predicate(self.predicate.model_dump(by_alias=True, exclude_unset=True) if self.predicate else None)
        if len(set(self.native_types)) != len(self.native_types):
            raise ValueError("native_types must be distinct.")
        if len(set(self.attribute_ids)) != len(self.attribute_ids):
            raise ValueError("attribute_ids must be distinct.")
        if len(set(self.exclude_model_uuids)) != len(self.exclude_model_uuids):
            raise ValueError("exclude_model_uuids must be distinct.")
        return self


class ModelEditPlan(ContractModel):
    schema_version: Literal["m4-model-edit-1"] = "m4-model-edit-1"
    action: Literal["highlight", "revalidate"]
    plan_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


class ModelEditApply(ContractModel):
    schema_version: Literal["m4-model-edit-1"] = "m4-model-edit-1"
    action: Literal["apply"]
    plan_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    execution_id: str = Field(pattern=r"^[0-9a-f]{32}$")
    acknowledgement: Literal["disposable_copy_reviewed_plan"]


class ModelEditRecover(ContractModel):
    schema_version: Literal["m4-model-edit-1"] = "m4-model-edit-1"
    action: Literal["recover"]
    execution_id: str = Field(pattern=r"^[0-9a-f]{32}$")


ModelEditRequest = Annotated[ModelEditPreview | ModelEditPlan | ModelEditApply | ModelEditRecover,
                             Field(discriminator="action")]
