# src/zeno/schema/ir_validator.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol, runtime_checkable

from .loader import Schema, SchemaValidationError


@runtime_checkable
class IRNodeView(Protocol):
    """
    Minimal read-only view of an IR node for schema structural validation.

    This avoids coupling schema logic to the core IR implementation.
    Core remains dumb; schema layer consumes a view.

    Required semantics:
      - node_type: "object" | "list" | "scalar"
      - object_items(): yields (key, child_node_view) in order
      - list_items(): yields child_node_view in order
      - scalar_value(): returns scalar payload (only used to detect scalar-ness; NOT validated by type)
    """

    def node_type(self) -> str: ...
    def object_items(self) -> Iterable[tuple[str, "IRNodeView"]]: ...
    def list_items(self) -> Iterable["IRNodeView"]: ...
    def scalar_value(self) -> Any: ...


@dataclass(frozen=True, slots=True)
class IRStructuralError:
    path: str
    message: str


def validate_ir_structure(schema: Schema, ir_root: IRNodeView) -> None:
    """
    Structural validation binding: compare schema.root (object/array/primitives)
    to an IR tree (object/list/scalar).

    Scope:
      - Validate node kind matches (object/list/scalar)
      - Validate object keys: only allowed keys + required-by-schema keys presence
      - Validate array items shape (per 'items')
      - NO value/type constraints (string vs integer etc.) in this phase
      - Unknown schema keys ignored (forward compatible)

    Raises:
      - SchemaValidationError (single, clear message)
    """
    # Ensure schema itself is structurally valid (Phase 2).
    _require_schema_root_object(schema)

    errors: list[IRStructuralError] = []
    _validate_node(schema_node=schema.root, ir_node=ir_root, path="$", errors=errors)

    if errors:
        # Keep it clear: show first error (minimal) + count
        first = errors[0]
        if len(errors) == 1:
            raise SchemaValidationError(f"IR structure invalid at {first.path}: {first.message}")
        raise SchemaValidationError(
            f"IR structure invalid at {first.path}: {first.message} "
            f"(and {len(errors) - 1} more)"
        )


def _require_schema_root_object(schema: Schema) -> None:
    t = schema.root.get("type")
    if t != "object":
        raise SchemaValidationError("Schema root.type must be 'object' for IR binding")


def _validate_node(
    *,
    schema_node: Mapping[str, Any],
    ir_node: IRNodeView,
    path: str,
    errors: list[IRStructuralError],
) -> None:
    schema_type = schema_node.get("type")
    if not isinstance(schema_type, str) or not schema_type:
        errors.append(IRStructuralError(path=path, message="schema node missing/invalid 'type'"))
        return

    expected_ir_kind = _schema_type_to_ir_kind(schema_type)
    actual_ir_kind = ir_node.node_type()

    if actual_ir_kind != expected_ir_kind:
        errors.append(
            IRStructuralError(
                path=path,
                message=f"expected IR '{expected_ir_kind}' from schema type '{schema_type}', got '{actual_ir_kind}'",
            )
        )
        return

    if schema_type == "object":
        _validate_object(schema_node=schema_node, ir_node=ir_node, path=path, errors=errors)
        return

    if schema_type == "array":
        _validate_array(schema_node=schema_node, ir_node=ir_node, path=path, errors=errors)
        return

    # Primitive: only require scalar (already matched by kind check).
    # No value checks in this phase.


def _validate_object(
    *,
    schema_node: Mapping[str, Any],
    ir_node: IRNodeView,
    path: str,
    errors: list[IRStructuralError],
) -> None:
    props = schema_node.get("properties")
    if props is None:
        # Object with no properties means "no defined keys" — treat as allow-any object?
        # To avoid future traps, we choose: allow any keys if properties is absent.
        return

    if not isinstance(props, Mapping):
        errors.append(IRStructuralError(path=path, message="schema object 'properties' must be a mapping"))
        return

    # Collect IR keys (ordered), but we only need membership + traversal.
    ir_items = list(ir_node.object_items())
    ir_keys = [k for (k, _) in ir_items]
    ir_map = {k: child for (k, child) in ir_items}

    # Required keys by schema = all properties listed (strict shape)
    # This is the "make it hard to make mistake" behavior.
    # If later you want optional keys, we add 'optional: true' or 'required: []' in a later phase.
    missing = [k for k in props.keys() if isinstance(k, str) and k not in ir_map]
    if missing:
        errors.append(IRStructuralError(path=path, message=f"missing required keys: {missing}"))
        # Don’t return; still report other issues if possible.

    # Disallow unknown keys (hard-to-mistake). This is structural strictness.
    unknown = [k for k in ir_keys if k not in props]
    if unknown:
        errors.append(IRStructuralError(path=path, message=f"unknown keys not allowed by schema: {unknown}"))

    # Validate children shapes for keys that exist in both.
    for key, child_schema in props.items():
        if not isinstance(key, str):
            errors.append(IRStructuralError(path=path, message="schema properties contains non-string key"))
            continue
        if key not in ir_map:
            continue
        if not isinstance(child_schema, Mapping):
            errors.append(IRStructuralError(path=f"{path}.{key}", message="schema property must be a mapping node"))
            continue

        _validate_node(
            schema_node=child_schema,
            ir_node=ir_map[key],
            path=f"{path}.{key}",
            errors=errors,
        )


def _validate_array(
    *,
    schema_node: Mapping[str, Any],
    ir_node: IRNodeView,
    path: str,
    errors: list[IRStructuralError],
) -> None:
    if "items" not in schema_node:
        errors.append(IRStructuralError(path=path, message="schema array requires 'items'"))
        return

    items_schema = schema_node.get("items")
    if not isinstance(items_schema, Mapping):
        errors.append(IRStructuralError(path=f"{path}[]", message="schema array 'items' must be a mapping node"))
        return

    for idx, child in enumerate(ir_node.list_items()):
        _validate_node(
            schema_node=items_schema,
            ir_node=child,
            path=f"{path}[{idx}]",
            errors=errors,
        )


def _schema_type_to_ir_kind(schema_type: str) -> str:
    if schema_type == "object":
        return "object"
    if schema_type == "array":
        return "list"
    # primitives map to scalar
    return "scalar"