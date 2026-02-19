# src/zeno/core/node.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID, uuid4

from zeno.core.types import NodeType


@dataclass
class Node:
    id: UUID
    type: NodeType
    parent_id: Optional[UUID] = None
    key: Optional[str] = None
    value: Optional[Any] = None
    children: list[UUID] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(node_type: NodeType) -> "Node":
        return Node(
            id=uuid4(),
            type=node_type,
        )
