#!/usr/bin/env python3
"""
Test schema/ir_validator.py works with Node+IRStore (Conflict 4 validation).

Verifies that the protocol-based validator can validate Node trees.
"""

from zeno.core.node import Node
from zeno.core.types import NodeType
from zeno.core.store import IRStore
from zeno.schema.ir_validator import IRStoreView, validate, ValidationError


def test_validate_valid_object():
    """Test validator accepts valid object structure."""
    store = IRStore()
    root_id = store.create_root(NodeType.OBJECT)
    root = store.get_node(root_id)
    
    # Add properties
    name_node = Node.create(NodeType.SCALAR)
    name_node.value = "Alice"
    store.add_unlinked_node(name_node)
    store.link_child(parent_id=root.id, child_id=name_node.id, key="name")
    
    # Create validator view and validate
    root_view = IRStoreView(store, root_id)
    
    try:
        validate(root_view)
        print("✓ Valid object passes validation: PASSED")
    except ValidationError as e:
        print(f"✗ Unexpected validation error: {e}")
        raise


def test_validate_valid_nested():
    """Test validator accepts valid nested structure."""
    store = IRStore()
    root_id = store.create_root(NodeType.OBJECT)
    root = store.get_node(root_id)
    
    # Add nested object
    person_node = Node.create(NodeType.OBJECT)
    store.add_unlinked_node(person_node)
    store.link_child(parent_id=root.id, child_id=person_node.id, key="person")
    
    # Add nested scalar
    name_node = Node.create(NodeType.SCALAR)
    name_node.value = "Alice"
    store.add_unlinked_node(name_node)
    store.link_child(parent_id=person_node.id, child_id=name_node.id, key="name")
    
    # Validate
    root_view = IRStoreView(store, root_id)
    
    try:
        validate(root_view)
        print("✓ Valid nested object passes validation: PASSED")
    except ValidationError as e:
        print(f"✗ Unexpected validation error: {e}")
        raise


def test_validate_valid_array():
    """Test validator accepts valid array structure."""
    store = IRStore()
    root_id = store.create_root(NodeType.LIST)
    root = store.get_node(root_id)
    
    # Add array elements
    for value in ["apple", "banana", 42]:
        elem_node = Node.create(NodeType.SCALAR)
        elem_node.value = value
        store.add_unlinked_node(elem_node)
        store.link_child(parent_id=root.id, child_id=elem_node.id)
    
    # Validate
    root_view = IRStoreView(store, root_id)
    
    try:
        validate(root_view)
        print("✓ Valid array passes validation: PASSED")
    except ValidationError as e:
        print(f"✗ Unexpected validation error: {e}")
        raise


def test_validate_duplicate_keys():
    """Test that IRStore prevents duplicate object keys (validated at store level)."""
    store = IRStore()
    root_id = store.create_root(NodeType.OBJECT)
    root = store.get_node(root_id)
    
    # Add first key
    node1 = Node.create(NodeType.SCALAR)
    node1.value = 1
    store.add_unlinked_node(node1)
    store.link_child(parent_id=root.id, child_id=node1.id, key="duplicate")
    
    # Try to add same key - should fail at store level
    node2 = Node.create(NodeType.SCALAR)
    node2.value = 2
    store.add_unlinked_node(node2)
    
    try:
        store.link_child(parent_id=root.id, child_id=node2.id, key="duplicate")
        print("✗ Should have rejected duplicate keys")
        raise AssertionError("Store allowed duplicate keys")
    except ValueError as e:
        assert "Duplicate object key" in str(e)
        print("✓ Duplicate key rejection at store level: PASSED")


def test_validator_works_with_store():
    """Integration test: validator works with Node+IRStore directly."""
    store = IRStore()
    root_id = store.create_root(NodeType.OBJECT)
    root = store.get_node(root_id)
    
    # Build complex structure
    config_node = Node.create(NodeType.OBJECT)
    store.add_unlinked_node(config_node)
    store.link_child(parent_id=root.id, child_id=config_node.id, key="settings")
    
    debug_node = Node.create(NodeType.SCALAR)
    debug_node.value = True
    store.add_unlinked_node(debug_node)
    store.link_child(parent_id=config_node.id, child_id=debug_node.id, key="debug")
    
    items_array = Node.create(NodeType.LIST)
    store.add_unlinked_node(items_array)
    store.link_child(parent_id=config_node.id, child_id=items_array.id, key="items")
    
    for item_val in ["a", "b", "c"]:
        item = Node.create(NodeType.SCALAR)
        item.value = item_val
        store.add_unlinked_node(item)
        store.link_child(parent_id=items_array.id, child_id=item.id)
    
    # Validate via adapter
    view = IRStoreView(store, root_id)
    
    try:
        validate(view)
        print("✓ Complex structure validation: PASSED")
    except ValidationError as e:
        print(f"✗ Unexpected validation error: {e}")
        raise


if __name__ == "__main__":
    test_validate_valid_object()
    test_validate_valid_nested()
    test_validate_valid_array()
    test_validate_duplicate_keys()
    test_validator_works_with_store()
    print("\n✅ All validator tests PASSED!")
