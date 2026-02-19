# src/zeno/core/operation.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Operation:
    operation_id: UUID
    operation_type: str
    target_node_id: UUID | None
    payload: dict[str, Any]

    @staticmethod
    def create(
        operation_type: str,
        target_node_id: UUID | None,
        payload: dict[str, Any],
    ) -> "Operation":
        return Operation(
            operation_id=uuid4(),
            operation_type=operation_type,
            target_node_id=target_node_id,
            payload=payload,
        )
