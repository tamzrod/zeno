# src/zeno/core/operation_processor.py

from __future__ import annotations

from uuid import UUID

from zeno.core.operation import Operation
from zeno.core.store import IRStore
from zeno.core.types import NodeType
from zeno.core.node import Node


class OperationProcessor:
    def __init__(self, store: IRStore) -> None:
        self._store = store

    def apply(self, operation: Operation) -> None:
        if operation.operation_type == "add_node":
            self._apply_add_node(operation)
        else:
            raise NotImplementedError(
                f"Unsupported operation type: {operation.operation_type}"
            )

    def _apply_add_node(self, operation: Operation) -> None:
        payload = operation.payload

        parent_id: UUID = payload["parent_id"]
        node_type: NodeType = payload["node_type"]
        key: str | None = payload.get("key")

        if not self._store.has_node(parent_id):
            raise ValueError("Parent node does not exist.")

        new_node = Node.create(node_type)

        # 1. Register as unlinked
        self._store.add_unlinked_node(new_node)

        # 2. Link to parent safely
        self._store.link_child(
            parent_id=parent_id,
            child_id=new_node.id,
            key=key,
        )
