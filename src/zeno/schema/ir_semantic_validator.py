# src/zeno/schema/ir_semantic_validator.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .loader import Schema
from .ir_validator import IRNodeView


@dataclass(frozen=True, slots=True)
class IRSemanticError:
    path: str
    message: str


def validate_ir_semantics(schema: Schema, ir_root: IRNodeView) -> list[IRSemanticError]:
    """
    Semantic validation layer.

    Scope (current phase):
      - array.unique_by (array-local duplicate detection)

    Assumptions:
      - Structural validation has already succeeded.
      - IR shape matches schema shape.
    """

    errors: list[IRSemanticError] = []

    if schema.root.get("type") != "object":
        # Structural validator should have already blocked this.
        return errors

    _validate_node(
        schema_node=schema.root,
        ir_node=ir_root,
        path="$",
        errors=errors,
    )

    return errors


def _validate_node(
    *,
    schema_node: Mapping[str, Any],
    ir_node: IRNodeView,
    path: str,
    errors: list[IRSemanticError],
) -> None:
    schema_type = schema_node.get("type")
    if not isinstance(schema_type, str):
        return

    if schema_type == "object":
        _validate_object(schema_node=schema_node, ir_node=ir_node, path=path, errors=errors)
        return

    if schema_type == "array":
        _validate_array(schema_node=schema_node, ir_node=ir_node, path=path, errors=errors)
        return

    # Primitive: no semantic rules yet.


def _validate_object(
    *,
    schema_node: Mapping[str, Any],
    ir_node: IRNodeView,
    path: str,
    errors: list[IRSemanticError],
) -> None:
    props = schema_node.get("properties")
    if not isinstance(props, Mapping):
        return

    ir_map = {k: child for (k, child) in ir_node.object_items()}

    for key, child_schema in props.items():
        if not isinstance(key, str):
            continue
        if not isinstance(child_schema, Mapping):
            continue

        child_ir = ir_map.get(key)
        if child_ir is None:
            continue

        _validate_node(
            schema_node=child_schema,
            ir_node=child_ir,
            path=f"{path}.{key}",
            errors=errors,
        )


def _validate_array(
    *,
    schema_node: Mapping[str, Any],
    ir_node: IRNodeView,
    path: str,
    errors: list[IRSemanticError],
) -> None:
    # --- Enforce unique_by ---
    unique_by = schema_node.get("unique_by")

    if isinstance(unique_by, str) and unique_by:
        _enforce_unique_by(
            ir_node=ir_node,
            field_name=unique_by,
            path=path,
            errors=errors,
        )

    # --- Recurse into items ---
    items_schema = schema_node.get("items")
    if not isinstance(items_schema, Mapping):
        return

    for idx, child in enumerate(ir_node.list_items()):
        _validate_node(
            schema_node=items_schema,
            ir_node=child,
            path=f"{path}[{idx}]",
            errors=errors,
        )


def _enforce_unique_by(
    *,
    ir_node: IRNodeView,
    field_name: str,
    path: str,
    errors: list[IRSemanticError],
) -> None:
    seen: dict[Any, int] = {}

    for idx, item in enumerate(ir_node.list_items()):
        if item.node_type() != "object":
            errors.append(
                IRSemanticError(
                    path=f"{path}[{idx}]",
                    message="unique_by requires array items of type 'object'",
                )
            )
            continue

        field_node = _ir_object_get(item, field_name)
        field_path = f"{path}[{idx}].{field_name}"

        if field_node is None:
            errors.append(
                IRSemanticError(
                    path=field_path,
                    message="missing field required by unique_by",
                )
            )
            continue

        if field_node.node_type() != "scalar":
            errors.append(
                IRSemanticError(
                    path=field_path,
                    message="unique_by field must be scalar",
                )
            )
            continue

        value = field_node.scalar_value()

        if value in seen:
            first_idx = seen[value]
            errors.append(
                IRSemanticError(
                    path=field_path,
                    message=f"duplicate value {value!r} (already used at {path}[{first_idx}].{field_name})",
                )
            )
            continue

        seen[value] = idx


def _ir_object_get(obj_node: IRNodeView, key: str) -> IRNodeView | None:
    for k, child in obj_node.object_items():
        if k == key:
            return child
    return None