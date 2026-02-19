# src/zeno/core/types.py

from enum import Enum


class NodeType(Enum):
    OBJECT = "object"
    LIST = "list"
    SCALAR = "scalar"
