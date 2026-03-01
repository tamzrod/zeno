"""IR tree building and expansion utilities."""

from __future__ import annotations

from uuid import UUID

from zeno.core.types import NodeType
from zeno.core.operation import Operation


class IRBuilder:
    """Builds and expands IR trees from schema definitions."""

    def __init__(self, store, processor):
        """Initialize with store and processor references."""
        self._store = store
        self._processor = processor

    def expand_schema_into_ir(self, *, parent_id: UUID, schema_node: dict) -> None:
        """
        Deterministic schema → IR expansion.

        Rules:
        - object: create children for each property
        - array: create LIST node but DO NOT create items (empty list)
        - scalar (string/integer/bool/...): create SCALAR node with value=None
        """
        if not self._processor or not self._store:
            return

        node_type = schema_node.get("type")

        # Only objects have 'properties' in our schema
        if node_type != "object":
            return

        props = schema_node.get("properties", {})
        if not isinstance(props, dict):
            return

        for prop_key, prop_schema in props.items():
            if not isinstance(prop_schema, dict):
                continue

            t = prop_schema.get("type")

            if t == "object":
                child_type = NodeType.OBJECT
            elif t == "array":
                child_type = NodeType.LIST
            else:
                # string/integer/bool/unknown => scalar node
                child_type = NodeType.SCALAR

            op = Operation.create(
                operation_type="add_node",
                target_node_id=None,
                payload={
                    "parent_id": parent_id,
                    "node_type": child_type,
                    "key": prop_key,
                },
            )
            self._processor.apply(op)

            # Find the newly created child by key (object children enforce unique key)
            child_id = self.find_object_child_id(parent_id, prop_key)
            if child_id is None:
                continue

            # Recurse only for objects; arrays remain empty; scalars stop
            if t == "object":
                self.expand_schema_into_ir(parent_id=child_id, schema_node=prop_schema)

    def find_object_child_id(self, parent_id: UUID, key: str) -> UUID | None:
        """Find child node ID by key in an OBJECT node."""
        if not self._store:
            return None
        parent = self._store.get_node(parent_id)
        for cid in parent.children:
            c = self._store.get_node(cid)
            if c.key == key:
                return cid
        return None

    def get_array_item_count(self, node_id: UUID) -> int:
        """Get current number of items in a LIST node."""
        if not self._store:
            return 0
        node = self._store.get_node(node_id)
        if node.type == NodeType.LIST:
            return len(node.children)
        return 0

    def get_object_property_count(self, node_id: UUID) -> int:
        """Get current number of properties in an OBJECT node."""
        if not self._store:
            return 0
        node = self._store.get_node(node_id)
        if node.type == NodeType.OBJECT:
            return len(node.children)
        return 0
