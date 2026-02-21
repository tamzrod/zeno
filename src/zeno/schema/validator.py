# src/zeno/schema/validator.py

from __future__ import annotations

from typing import Any, Mapping

from .loader import Schema, SchemaValidationError


_ALLOWED_TYPES = {
    "object",
    "array",
    "string",
    "integer",
    "number",
    "boolean",
}


def validate_structure(schema: Schema) -> None:
    """
    Phase 2 – Structural Validation Binding

    Validates only schema SHAPE.
    No cross-field validation.
    No value validation.
    No UI binding.
    No recursion engine abstraction.
    Unknown keys are ignored for forward compatibility.
    """

    root = schema.root

    if not isinstance(root, Mapping):
        raise SchemaValidationError("Schema root must be a mapping/object")

    _validate_node(root, path="root")

    # Enforce root must be object
    if root.get("type") != "object":
        raise SchemaValidationError("Schema root.type must be 'object'")


def _validate_node(node: Mapping[str, Any], *, path: str) -> None:
    if not isinstance(node, Mapping):
        raise SchemaValidationError(f"{path} must be a mapping/object")

    # --- type required ---
    node_type = node.get("type")
    if node_type is None:
        raise SchemaValidationError(f"{path} missing required field: type")

    if not isinstance(node_type, str):
        raise SchemaValidationError(f"{path}.type must be a string")

    if node_type not in _ALLOWED_TYPES:
        raise SchemaValidationError(
            f"{path}.type must be one of {_ALLOWED_TYPES} (got '{node_type}')"
        )

    # --- object rules ---
    if node_type == "object":
        properties = node.get("properties")

        if properties is not None:
            if not isinstance(properties, Mapping):
                raise SchemaValidationError(
                    f"{path}.properties must be a mapping/object"
                )

            for prop_name, prop_schema in properties.items():
                if not isinstance(prop_name, str):
                    raise SchemaValidationError(
                        f"{path}.properties contains non-string key"
                    )

                _validate_node(
                    prop_schema,
                    path=f"{path}.properties.{prop_name}",
                )

    # --- array rules ---
    elif node_type == "array":
        if "items" not in node:
            raise SchemaValidationError(f"{path} of type 'array' requires 'items'")

        items = node.get("items")

        if not isinstance(items, Mapping):
            raise SchemaValidationError(
                f"{path}.items must be a mapping/object"
            )

        _validate_node(items, path=f"{path}.items")

    # --- primitive rules ---
    else:
        # Primitive types must not define structural nesting
        if "properties" in node:
            raise SchemaValidationError(
                f"{path} of primitive type '{node_type}' "
                f"must not define 'properties'"
            )

        if "items" in node:
            raise SchemaValidationError(
                f"{path} of primitive type '{node_type}' "
                f"must not define 'items'"
            )