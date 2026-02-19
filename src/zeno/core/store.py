# src/zeno/core/store.py

from __future__ import annotations

from typing import Dict
from uuid import UUID

from zeno.core.node import Node
from zeno.core.types import NodeType


class IRStore:
    def __init__(self) -> None:
        self._nodes: Dict[UUID, Node] = {}
        self._root_id: UUID | None = None

    @property
    def root_id(self) -> UUID:
        if self._root_id is None:
            raise RuntimeError("Root node not set.")
        return self._root_id

    def create_root(self, node_type: NodeType) -> UUID:
        if self._root_id is not None:
            raise RuntimeError("Root already exists.")

        node = Node.create(node_type)
        self._nodes[node.id] = node
        self._root_id = node.id
        return node.id

    def add_unlinked_node(self, node: Node) -> None:
        if node.id in self._nodes:
            raise ValueError("Node with this ID already exists.")
        if node.parent_id is not None:
            raise ValueError("Unlinked node must not have parent_id set.")
        if node.children:
            raise ValueError("Unlinked node must not have children.")
        self._nodes[node.id] = node

    def link_child(
        self,
        *,
        parent_id: UUID,
        child_id: UUID,
        key: str | None = None,
        index: int | None = None,
    ) -> None:
        parent = self.get_node(parent_id)
        child = self.get_node(child_id)

        if child_id == self.root_id:
            raise ValueError("Root node cannot be linked as a child.")

        if child.parent_id is not None:
            raise ValueError("Child already has a parent.")

        if parent.type == NodeType.SCALAR:
            raise ValueError("Scalar nodes cannot have children.")

        if parent.type == NodeType.OBJECT:
            if key is None:
                raise ValueError("Object child link requires key.")
            if self._object_key_exists(parent, key):
                raise ValueError(f"Duplicate object key: {key}")
            child.key = key

        if parent.type == NodeType.LIST:
            if key is not None:
                raise ValueError("List child link does not allow key.")
            child.key = None

        child.parent_id = parent_id

        if index is None:
            parent.children.append(child_id)
        else:
            if index < 0 or index > len(parent.children):
                raise ValueError("Index out of bounds.")
            parent.children.insert(index, child_id)

    def unlink_child(self, *, child_id: UUID) -> None:
        child = self.get_node(child_id)

        if child_id == self.root_id:
            raise ValueError("Root node cannot be unlinked.")

        if child.parent_id is None:
            raise ValueError("Child has no parent to unlink from.")

        parent = self.get_node(child.parent_id)

        try:
            parent.children.remove(child_id)
        except ValueError:
            raise RuntimeError("Structural corruption: parent missing child link.")

        child.parent_id = None
        child.key = None

    def delete_subtree(self, *, node_id: UUID) -> None:
        if node_id == self.root_id:
            raise ValueError("Root node cannot be deleted.")

        node = self.get_node(node_id)

        # Must be unlinked before delete.
        if node.parent_id is not None:
            raise ValueError("Node must be unlinked before deletion.")

        # Depth-first delete.
        for cid in list(node.children):
            self._delete_subtree_internal(cid)

        del self._nodes[node_id]

    def _delete_subtree_internal(self, node_id: UUID) -> None:
        node = self.get_node(node_id)

        for cid in list(node.children):
            self._delete_subtree_internal(cid)

        del self._nodes[node_id]

    def get_node(self, node_id: UUID) -> Node:
        try:
            return self._nodes[node_id]
        except KeyError:
            raise KeyError(f"Node {node_id} does not exist.")

    def has_node(self, node_id: UUID) -> bool:
        return node_id in self._nodes

    def _object_key_exists(self, parent: Node, key: str) -> bool:
        for cid in parent.children:
            c = self.get_node(cid)
            if c.key == key:
                return True
        return False
