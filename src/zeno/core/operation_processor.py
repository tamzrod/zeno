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
        elif operation.operation_type == "update_scalar":
            self._apply_update_scalar(operation)
        elif operation.operation_type == "remove_node":
            self._apply_remove_node(operation)
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

        self._store.add_unlinked_node(new_node)

        self._store.link_child(
            parent_id=parent_id,
            child_id=new_node.id,
            key=key,
        )

    def _apply_update_scalar(self, operation: Operation) -> None:
        payload = operation.payload

        node_id: UUID = payload["node_id"]
        new_value = payload["value"]

        if not self._store.has_node(node_id):
            raise ValueError("Target node does not exist.")

        node = self._store.get_node(node_id)

        if node.type != NodeType.SCALAR:
            raise ValueError("Only scalar nodes can be updated.")

        node.value = new_value

    def _apply_remove_node(self, operation: Operation) -> None:
        payload = operation.payload

        node_id: UUID = payload["node_id"]

        if not self._store.has_node(node_id):
            raise ValueError("Target node does not exist.")

        if node_id == self._store.root_id:
            raise ValueError("Root node cannot be removed.")

        # Must unlink first
        self._store.unlink_child(child_id=node_id)

        # Then delete subtree
        self._store.delete_subtree(node_id=node_id)
