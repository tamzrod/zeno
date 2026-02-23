# src/zeno/core/ir_validator.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from zeno.core.ir_node import IRNode
from zeno.core.ir_types import IRType, ObjectType, ArrayType, ScalarType


# ==========================================================
# Validation Structures
# ==========================================================

@dataclass(frozen=True, slots=True)
class IRValidationIssue:
    path: str
    message: str


class IRValidationError(Exception):
    def __init__(self, issues: List[IRValidationIssue]) -> None:
        self.issues = issues
        super().__init__("\n".join(f"{i.path}: {i.message}" for i in issues))


# ==========================================================
# Public Entry
# ==========================================================

def validate(root: IRNode) -> None:
    issues: List[IRValidationIssue] = []
    _validate_node(root, path="$", issues=issues)
    if issues:
        raise IRValidationError(issues)


# ==========================================================
# Core Dispatcher
# ==========================================================

def _validate_node(node: IRNode, *, path: str, issues: List[IRValidationIssue]) -> None:
    t = node.type_def

    if isinstance(t, ScalarType):
        _validate_scalar(t, node.value, path=path, issues=issues)
        return

    if isinstance(t, ObjectType):
        _validate_object(t, node.value, path=path, issues=issues)
        return

    if isinstance(t, ArrayType):
        _validate_array(t, node.value, path=path, issues=issues)
        return

    issues.append(IRValidationIssue(path, f"Unknown IRType: {type(t).__name__}"))


# ==========================================================
# Scalar Validation
# ==========================================================

def _validate_scalar(t: ScalarType, value: Any, *, path: str, issues: List[IRValidationIssue]) -> None:
    if value is None:
        if t.required:
            issues.append(IRValidationIssue(path, "Value is required."))
        return

    if not _matches_scalar_type(t.name, value):
        issues.append(IRValidationIssue(path, f"Expected {t.name}, got {type(value).__name__}."))
        return

    if t.enum is not None and value not in t.enum:
        issues.append(IRValidationIssue(path, f"Value {value!r} not in enum {t.enum!r}."))


# ==========================================================
# Object Validation
# ==========================================================

def _validate_object(t: ObjectType, value: Any, *, path: str, issues: List[IRValidationIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(IRValidationIssue(path, f"Expected object (dict), got {type(value).__name__}."))
        return

    # Required fields
    for req in t.required:
        if req not in value:
            issues.append(IRValidationIssue(f"{path}.{req}", "Field is required (missing)."))
            continue

        child = value[req]
        if not isinstance(child, IRNode):
            issues.append(IRValidationIssue(f"{path}.{req}", "Internal error: not IRNode."))
            continue

        if child.value is None:
            issues.append(IRValidationIssue(f"{path}.{req}", "Field is required (value is null)."))

    # Validate properties
    for name, child_type in t.properties.items():
        child_node = value.get(name)
        if child_node is None:
            continue

        if not isinstance(child_node, IRNode):
            issues.append(IRValidationIssue(f"{path}.{name}", "Internal error: property is not IRNode."))
            continue

        _validate_node(child_node, path=f"{path}.{name}", issues=issues)


# ==========================================================
# Array Validation
# ==========================================================

def _validate_array(t: ArrayType, value: Any, *, path: str, issues: List[IRValidationIssue]) -> None:
    if not isinstance(value, list):
        issues.append(IRValidationIssue(path, f"Expected array (list), got {type(value).__name__}."))
        return

    length = len(value)

    # minItems
    if t.min_items is not None and length < t.min_items:
        issues.append(
            IRValidationIssue(
                path,
                f"Expected at least {t.min_items} items (minItems), got {length}.",
            )
        )

    # maxItems
    if t.max_items is not None and length > t.max_items:
        issues.append(
            IRValidationIssue(
                path,
                f"Expected at most {t.max_items} items (maxItems), got {length}.",
            )
        )

    # Validate items
    for idx, item in enumerate(value):
        if not isinstance(item, IRNode):
            issues.append(IRValidationIssue(f"{path}[{idx}]", "Internal error: array item is not IRNode."))
            continue

        _validate_node(item, path=f"{path}[{idx}]", issues=issues)

    # Unique sibling enforcement (only for object arrays)
    if isinstance(t.items, ObjectType):
        _validate_unique_sibling_fields(t.items, value, path=path, issues=issues)


# ==========================================================
# Unique Sibling Enforcement
# ==========================================================

def _validate_unique_sibling_fields(
    obj_type: ObjectType,
    items: List[IRNode],
    *,
    path: str,
    issues: List[IRValidationIssue],
) -> None:

    unique_fields: List[str] = []

    for field_name, field_type in obj_type.properties.items():
        if isinstance(field_type, ScalarType) and field_type.unique == "sibling":
            unique_fields.append(field_name)

    if not unique_fields:
        return

    for field_name in unique_fields:
        seen: Dict[Any, int] = {}

        for idx, item in enumerate(items):
            if not isinstance(item.value, dict):
                continue

            node = item.value.get(field_name)
            if node is None or not isinstance(node, IRNode):
                continue

            v = node.value
            if v is None:
                continue  # ignore null/unset

            if v in seen:
                first_idx = seen[v]
                issues.append(
                    IRValidationIssue(
                        f"{path}[{idx}].{field_name}",
                        f"Duplicate value {v!r}; already used at {path}[{first_idx}].{field_name}.",
                    )
                )
            else:
                seen[v] = idx


# ==========================================================
# Type Matching
# ==========================================================

def _matches_scalar_type(type_name: str, value: Any) -> bool:
    if type_name == "boolean":
        return isinstance(value, bool)

    if type_name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)

    if type_name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    if type_name == "string":
        return isinstance(value, str)

    return False