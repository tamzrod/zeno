#!/usr/bin/env python3
"""
Test YAML Adapter bidirectionality (Conflict 3 validation).

Tests that:
1. serialize(Node tree) → YAML string
2. parse(YAML string) → Node tree
3. Round-trip: original tree == parse(serialize(original tree))
"""

from zeno.core.node import Node
from zeno.core.types import NodeType
from zeno.core.store import IRStore
from zeno.adapters.yaml_adapter import serialize, parse


def test_serialize_scalar():
    """Test serializing a scalar root node."""
    store = IRStore()
    root_id = store.create_root(NodeType.SCALAR)
    root = store.get_node(root_id)
    root.value = 42
    
    yaml_str = serialize(root, store)
    assert "42" in yaml_str
    print("✓ Scalar serialization: PASSED")


def test_serialize_object():
    """Test serializing an object with properties."""
    store = IRStore()
    root_id = store.create_root(NodeType.OBJECT)
    root = store.get_node(root_id)
    
    # Add property: name = "Alice"
    name_node = Node.create(NodeType.SCALAR)
    name_node.value = "Alice"
    store.add_unlinked_node(name_node)
    store.link_child(parent_id=root.id, child_id=name_node.id, key="name")
    
    # Add property: age = 30
    age_node = Node.create(NodeType.SCALAR)
    age_node.value = 30
    store.add_unlinked_node(age_node)
    store.link_child(parent_id=root.id, child_id=age_node.id, key="age")
    
    yaml_str = serialize(root, store)
    print(f"Object serialization:\n{yaml_str}")
    assert "name: Alice" in yaml_str
    assert "age: 30" in yaml_str
    print("✓ Object serialization: PASSED")


def test_parse_object():
    """Test parsing an object from YAML."""
    store = IRStore()
    root_id = store.create_root(NodeType.OBJECT)
    root = store.get_node(root_id)
    
    yaml_text = """
    name: Alice
    age: 30
    """
    
    parse(yaml_text, store)
    
    # Verify structure
    assert len(root.children) == 2
    
    # Get children by key
    child_ids = {store.get_node(cid).key: cid for cid in root.children}
    assert "name" in child_ids
    assert "age" in child_ids
    
    name_node = store.get_node(child_ids["name"])
    assert name_node.value == "Alice"
    
    age_node = store.get_node(child_ids["age"])
    assert age_node.value == 30
    
    print("✓ Object parsing: PASSED")


def test_parse_nested_object():
    """Test parsing nested objects."""
    store = IRStore()
    root_id = store.create_root(NodeType.OBJECT)
    root = store.get_node(root_id)
    
    yaml_text = """
    person:
      name: Alice
      age: 30
    """
    
    parse(yaml_text, store)
    
    # Verify structure
    assert len(root.children) == 1
    person_id = root.children[0]
    person_node = store.get_node(person_id)
    
    assert person_node.type == NodeType.OBJECT
    assert person_node.key == "person"
    assert len(person_node.children) == 2
    
    # Get nested children by key
    nested_ids = {store.get_node(cid).key: cid for cid in person_node.children}
    assert "name" in nested_ids
    assert "age" in nested_ids
    
    name_node = store.get_node(nested_ids["name"])
    assert name_node.value == "Alice"
    
    age_node = store.get_node(nested_ids["age"])
    assert age_node.value == 30
    
    print("✓ Nested object parsing: PASSED")


def test_roundtrip_object():
    """Test roundtrip: serialize → parse."""
    # Create original
    store1 = IRStore()
    root_id1 = store1.create_root(NodeType.OBJECT)
    root1 = store1.get_node(root_id1)
    
    name_node = Node.create(NodeType.SCALAR)
    name_node.value = "Alice"
    store1.add_unlinked_node(name_node)
    store1.link_child(parent_id=root1.id, child_id=name_node.id, key="name")
    
    age_node = Node.create(NodeType.SCALAR)
    age_node.value = 30
    store1.add_unlinked_node(age_node)
    store1.link_child(parent_id=root1.id, child_id=age_node.id, key="age")
    
    # Serialize
    yaml_str = serialize(root1, store1)
    
    # Parse into new store
    store2 = IRStore()
    root_id2 = store2.create_root(NodeType.OBJECT)
    root2 = store2.get_node(root_id2)
    parse(yaml_str, store2)
    
    # Verify both stores have same structure
    assert len(root2.children) == 2
    child_ids_2 = {store2.get_node(cid).key: cid for cid in root2.children}
    
    assert store2.get_node(child_ids_2["name"]).value == "Alice"
    assert store2.get_node(child_ids_2["age"]).value == 30
    
    # Serialize again and compare
    yaml_str2 = serialize(root2, store2)
    assert yaml_str.strip() == yaml_str2.strip()
    
    print("✓ Roundtrip object: PASSED")


def test_roundtrip_nested():
    """Test roundtrip with nested structure."""
    # Create original
    store1 = IRStore()
    root_id1 = store1.create_root(NodeType.OBJECT)
    root1 = store1.get_node(root_id1)
    
    person_node = Node.create(NodeType.OBJECT)
    store1.add_unlinked_node(person_node)
    store1.link_child(parent_id=root1.id, child_id=person_node.id, key="person")
    
    name_node = Node.create(NodeType.SCALAR)
    name_node.value = "Alice"
    store1.add_unlinked_node(name_node)
    store1.link_child(parent_id=person_node.id, child_id=name_node.id, key="name")
    
    # Serialize
    yaml_str = serialize(root1, store1)
    
    # Parse into new store
    store2 = IRStore()
    root_id2 = store2.create_root(NodeType.OBJECT)
    root2 = store2.get_node(root_id2)
    parse(yaml_str, store2)
    
    # Verify
    assert len(root2.children) == 1
    person_id_2 = root2.children[0]
    person_node_2 = store2.get_node(person_id_2)
    
    assert person_node_2.key == "person"
    assert len(person_node_2.children) == 1
    
    name_node_2 = store2.get_node(person_node_2.children[0])
    assert name_node_2.value == "Alice"
    
    print("✓ Roundtrip nested: PASSED")


if __name__ == "__main__":
    test_serialize_scalar()
    test_serialize_object()
    test_parse_object()
    test_parse_nested_object()
    test_roundtrip_object()
    test_roundtrip_nested()
    print("\n✅ All adapter tests PASSED!")
