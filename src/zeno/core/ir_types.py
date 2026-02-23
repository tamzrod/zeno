# src/zeno/core/ir_types.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union


# ==========================================================
# Base IR Type
# ==========================================================

class IRType:
    """Base class for all schema-bound IR types."""
    pass


# ==========================================================
# Scalar Type
# ==========================================================

@dataclass(frozen=True, slots=True)
class ScalarType(IRType):
    """
    Represents a scalar field definition.

    Supported:
        - string
        - integer
        - number
        - boolean
    """

    name: str  # string | integer | number | boolean
    enum: Optional[List[Union[str, int, float, bool]]] = None
    default: Optional[Union[str, int, float, bool]] = None
    required: bool = False

    # Constraint rules
    unique: Optional[str] = None  # only allowed value: "sibling"

    # Optional numeric constraints (future-safe, not yet enforced)
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None


# ==========================================================
# Object Type
# ==========================================================

@dataclass(frozen=True, slots=True)
class ObjectType(IRType):
    """
    Represents an object with named properties.
    """

    properties: Dict[str, IRType] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)


# ==========================================================
# Array Type
# ==========================================================

@dataclass(frozen=True, slots=True)
class ArrayType(IRType):
    """
    Represents an array of items.
    """

    items: IRType
    min_items: Optional[int] = None
    max_items: Optional[int] = None


# ==========================================================
# Utility Helpers
# ==========================================================

def is_scalar(t: IRType) -> bool:
    return isinstance(t, ScalarType)


def is_object(t: IRType) -> bool:
    return isinstance(t, ObjectType)


def is_array(t: IRType) -> bool:
    return isinstance(t, ArrayType)