# src/zeno/schema/binder.py
from __future__ import annotations

from typing import Any, Dict, List

from zeno.core.ir_types import (
    IRType,
    ScalarType,
    ObjectType,
    ArrayType,
)


# ==========================================================
# Public Entry
# ==========================================================

def bind(root_schema: Dict[str, Any]) -> IRType:
    """
    Bind a schema root (schema.root) into IRType tree.

    This performs structural interpretation only.
    No IR instance creation.
    No validation execution.
    """
    return _bind_node(root_schema)


# ==========================================================
# Core Binding Dispatcher
# ==========================================================

def _bind_node(node: Dict[str, Any]) -> IRType:
    if "type" not in node:
        raise ValueError("Schema node missing required key: 'type'")

    node_type = node["type"]

    if node_type == "object":
        return _bind_object(node)

    if node_type == "array":
        return _bind_array(node)

    if node_type in ("string", "integer", "number", "boolean"):
        return _bind_scalar(node)

    raise ValueError(f"Unsupported schema type: {node_type}")


# ==========================================================
# Object Binding
# ==========================================================

def _bind_object(node: Dict[str, Any]) -> ObjectType:
    properties = node.get("properties", {})
    required = node.get("required", [])

    if not isinstance(properties, dict):
        raise ValueError("Object 'properties' must be a mapping")

    if not isinstance(required, list):
        raise ValueError("Object 'required' must be a list")

    bound_props: Dict[str, IRType] = {}

    for name, child_schema in properties.items():
        if not isinstance(child_schema, dict):
            raise ValueError(f"Invalid schema for property '{name}'")
        bound_props[name] = _bind_node(child_schema)

    return ObjectType(
        properties=bound_props,
        required=list(required),
    )


# ==========================================================
# Array Binding
# ==========================================================

def _bind_array(node: Dict[str, Any]) -> ArrayType:
    if "items" not in node:
        raise ValueError("Array schema missing 'items'")

    items_schema = node["items"]
    if not isinstance(items_schema, dict):
        raise ValueError("Array 'items' must be a schema object")

    min_items = node.get("minItems")
    max_items = node.get("maxItems")

    return ArrayType(
        items=_bind_node(items_schema),
        min_items=min_items,
        max_items=max_items,
    )


# ==========================================================
# Scalar Binding
# ==========================================================

def _bind_scalar(node: Dict[str, Any]) -> ScalarType:
    name = node["type"]

    enum = node.get("enum")
    default = node.get("default")
    required = bool(node.get("required", False))
    unique = node.get("unique")
    minimum = node.get("minimum")
    maximum = node.get("maximum")

    # ------------------------------------------
    # Validate unique rule
    # ------------------------------------------
    if unique is not None:
        if unique != "sibling":
            raise ValueError(
                f"Unsupported unique scope '{unique}'. Only 'sibling' is allowed."
            )

    # ------------------------------------------
    # Validate enum
    # ------------------------------------------
    if enum is not None:
        if not isinstance(enum, list):
            raise ValueError("Scalar 'enum' must be a list")

    # ------------------------------------------
    # Validate numeric constraints
    # ------------------------------------------
    if minimum is not None and not isinstance(minimum, (int, float)):
        raise ValueError("Scalar 'minimum' must be numeric")

    if maximum is not None and not isinstance(maximum, (int, float)):
        raise ValueError("Scalar 'maximum' must be numeric")

    return ScalarType(
        name=name,
        enum=enum,
        default=default,
        required=required,
        unique=unique,
        minimum=minimum,
        maximum=maximum,
    )