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
        elif operation.operation_type == "move_node":
            self._apply_move_node(operation)
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

    def _apply_move_node(self, operation: Operation) -> None:
        """Move a node within its parent's children list (for LIST reordering)."""
        payload = operation.payload

        node_id: UUID = payload["node_id"]
        direction: str = payload["direction"]  # "up" or "down"

        if not self._store.has_node(node_id):
            raise ValueError("Target node does not exist.")

        node = self._store.get_node(node_id)

        if node.parent_id is None:
            raise ValueError("Cannot move root node.")

        parent = self._store.get_node(node.parent_id)

        if parent.type != NodeType.LIST:
            raise ValueError("Move operation only allowed for LIST children.")

        try:
            current_index = parent.children.index(node_id)
        except ValueError:
            raise RuntimeError("Structural corruption: node not in parent's children.")

        if direction == "up":
            if current_index == 0:
                raise ValueError("Cannot move first item up.")
            new_index = current_index - 1
        elif direction == "down":
            if current_index == len(parent.children) - 1:
                raise ValueError("Cannot move last item down.")
            new_index = current_index + 1
        else:
            raise ValueError(f"Invalid direction: {direction}")

        # Remove from current position and insert at new position
        parent.children.pop(current_index)
        parent.children.insert(new_index, node_id)
