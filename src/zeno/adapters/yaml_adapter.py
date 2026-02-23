# src/zeno/adapters/yaml_adapter.py
from __future__ import annotations

from typing import Any

import yaml

from zeno.core.ir_node import IRNode


def serialize(node: IRNode) -> str:
    plain = node.to_plain()
    return yaml.safe_dump(
        plain,
        sort_keys=False,
        allow_unicode=True,
    )