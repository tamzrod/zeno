# src/zeno/adapters/yaml_adapter.py

from __future__ import annotations

from typing import Any

import yaml

from zeno.core.node import Node
from zeno.core.types import NodeType
from zeno.core.store import IRStore


def serialize(node: Node, store: IRStore) -> str:
    """
    Serialize a Node tree to YAML string.
    Preserves ordering and structure exactly.
    """
    plain = _node_to_plain(node, store)
    return yaml.safe_dump(
        plain,
        sort_keys=False,
        allow_unicode=True,
    )


def parse(yaml_text: str, store: IRStore) -> None:
    """
    Parse YAML text and populate an IRStore.
    
    Assumes store already has a root node created.
    Recursively parses YAML structure into Node tree.
    """
    data = yaml.safe_load(yaml_text)
    if data is None:
        return
    
    if not store._nodes or store._root_id is None:
        raise ValueError("Store must have a root node before parsing")
    
    root = store.get_node(store.root_id)
    
    if isinstance(data, dict):
        _parse_object(store, root, data)
    elif isinstance(data, list):
        _parse_array(store, root, data)
    else:
        # Scalar at root level
        root.value = data


# ============================================================
# Serialization (Node → Plain)
# ============================================================

def _node_to_plain(node: Node, store: IRStore) -> Any:
    """Convert Node tree to plain Python structure (dict/list/scalar)."""
    
    if node.type == NodeType.SCALAR:
        return node.value
    
    if node.type == NodeType.OBJECT:
        result = {}
        for child_id in node.children:
            child = store.get_node(child_id)
            key = child.key or ""
            result[key] = _node_to_plain(child, store)
        return result
    
    if node.type == NodeType.LIST:
        result = []
        for child_id in node.children:
            child = store.get_node(child_id)
            result.append(_node_to_plain(child, store))
        return result
    
    return None


# ============================================================
# Parsing (YAML/Plain → Node tree + Store)
# ============================================================

def _parse_object(store: IRStore, obj_node: Node, data: dict) -> None:
    """Parse dict data into object node."""
    
    for key, value in data.items():
        # Create child node
        child = Node.create(NodeType.SCALAR)
        
        if isinstance(value, dict):
            child.type = NodeType.OBJECT
            store.add_unlinked_node(child)
            store.link_child(parent_id=obj_node.id, child_id=child.id, key=key)
            _parse_object(store, child, value)
        
        elif isinstance(value, list):
            child.type = NodeType.LIST
            store.add_unlinked_node(child)
            store.link_child(parent_id=obj_node.id, child_id=child.id, key=key)
            _parse_array(store, child, value)
        
        else:
            # Scalar
            child.value = value
            store.add_unlinked_node(child)
            store.link_child(parent_id=obj_node.id, child_id=child.id, key=key)


def _parse_array(store: IRStore, list_node: Node, data: list) -> None:
    """Parse list data into list node."""
    
    for idx, item in enumerate(data):
        child = Node.create(NodeType.SCALAR)
        
        if isinstance(item, dict):
            child.type = NodeType.OBJECT
            store.add_unlinked_node(child)
            store.link_child(parent_id=list_node.id, child_id=child.id)
            _parse_object(store, child, item)
        
        elif isinstance(item, list):
            child.type = NodeType.LIST
            store.add_unlinked_node(child)
            store.link_child(parent_id=list_node.id, child_id=child.id)
            _parse_array(store, child, item)
        
        else:
            # Scalar
            child.value = item
            store.add_unlinked_node(child)
            store.link_child(parent_id=list_node.id, child_id=child.id)