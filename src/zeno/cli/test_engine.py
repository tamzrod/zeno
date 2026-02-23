# src/zeno/cli/test_engine.py
from __future__ import annotations

import sys
from pathlib import Path

from zeno.schema.loader import load as load_schema
from zeno.schema.binder import bind
from zeno.core.ir_node import IRNode
from zeno.core.ir_validator import validate
from zeno.adapters.yaml_adapter import serialize


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m zeno.cli.test_engine <schema.zs>")
        return 1

    schema_path = Path(sys.argv[1])

    print(f"[1] Loading schema: {schema_path}")
    schema = load_schema(schema_path)

    print("[2] Binding schema.root → IRType")
    root_type = bind(schema.root)

    print("[3] Creating empty IR instance from type")
    root_node = IRNode.create_from_type(root_type)

    print("[4] Validating IR")
    validate(root_node)

    print("[5] Serializing via YAML adapter")
    output = serialize(root_node)

    print("\n----- GENERATED OUTPUT -----\n")
    print(output)

    print("Engine test completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())