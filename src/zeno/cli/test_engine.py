# src/zeno/cli/test_engine.py

from __future__ import annotations

import sys
from pathlib import Path

from zeno.schema.loader import load as load_schema
from zeno.core.store import IRStore
from zeno.core.types import NodeType
from zeno.core.operation import Operation
from zeno.core.operation_processor import OperationProcessor
from zeno.adapters.yaml_adapter import serialize


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m zeno.cli.test_engine <schema.zs>")
        return 1

    schema_path = Path(sys.argv[1])

    print(f"[1] Loading schema: {schema_path}")
    schema = load_schema(schema_path)

    print("[2] Creating empty IR from schema")
    store = IRStore()
    root_id = store.create_root(NodeType.OBJECT)
    processor = OperationProcessor(store)

    print("[3] Expanding schema into IR")
    _expand_schema_into_ir(
        store=store,
        processor=processor,
        parent_id=root_id,
        schema_node=schema.root,
    )

    print("[4] Serializing via YAML adapter")
    root = store.get_node(root_id)
    output = serialize(root, store)

    print("\n----- GENERATED OUTPUT -----\n")
    print(output)

    print("Engine test completed successfully.")
    return 0


def _expand_schema_into_ir(*, store, processor, parent_id, schema_node: dict) -> None:
    """Deterministic schema → IR expansion."""
    
    node_type = schema_node.get("type")
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
        processor.apply(op)

        # Find newly created child
        parent = store.get_node(parent_id)
        child_id = None
        for cid in parent.children:
            c = store.get_node(cid)
            if c.key == prop_key:
                child_id = cid
                break

        if child_id is None:
            continue

        # Recurse for objects
        if t == "object":
            _expand_schema_into_ir(
                store=store,
                processor=processor,
                parent_id=child_id,
                schema_node=prop_schema,
            )


if __name__ == "__main__":
    raise SystemExit(main())