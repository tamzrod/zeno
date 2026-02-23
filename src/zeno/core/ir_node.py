# src/zeno/core/ir_node.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from zeno.core.ir_types import IRType, ObjectType, ArrayType, ScalarType


@dataclass(slots=True)
class IRNode:
    type_def: IRType
    value: Any = None

    def to_plain(self) -> Any:
        """
        Convert IR tree to plain Python structure (dict/list/scalar)
        suitable for adapters.
        """
        if isinstance(self.type_def, ScalarType):
            return self.value

        if isinstance(self.type_def, ObjectType):
            result: Dict[str, Any] = {}
            for k, v in (self.value or {}).items():
                result[k] = v.to_plain()
            return result

        if isinstance(self.type_def, ArrayType):
            return [item.to_plain() for item in (self.value or [])]

        raise TypeError("Unknown IRType")

    @staticmethod
    def create_from_type(type_def: IRType) -> "IRNode":
        """
        Create empty node based on type definition.
        """
        if isinstance(type_def, ScalarType):
            return IRNode(type_def=type_def, value=type_def.default)

        if isinstance(type_def, ObjectType):
            obj = {}
            for name, child_type in type_def.properties.items():
                obj[name] = IRNode.create_from_type(child_type)
            return IRNode(type_def=type_def, value=obj)

        if isinstance(type_def, ArrayType):
            return IRNode(type_def=type_def, value=[])

        raise TypeError("Unsupported IRType")