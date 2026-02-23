# src/zeno/core/ir_view.py

from __future__ import annotations

from typing import Iterable, Tuple

from zeno.core.store import IRStore
from zeno.core.node import Node
from zeno.core.types import NodeType
from zeno.schema.ir_validator import IRNodeView


class IRStoreView(IRNodeView):
    """
    Adapter that exposes IRStore + Node tree as IRNodeView
    without modifying core classes.
    """

    def __init__(self, store: IRStore, node_id) -> None:
        self._store = store
        self._node_id = node_id

    # ---------- Protocol Methods ----------

    def node_type(self) -> str:
        node = self._store.get_node(self._node_id)

        if node.type == NodeType.OBJECT:
            return "object"
        if node.type == NodeType.LIST:
            return "list"
        return "scalar"

    def object_items(self) -> Iterable[Tuple[str, IRNodeView]]:
        node = self._store.get_node(self._node_id)

        for child_id in node.children:
            child = self._store.get_node(child_id)
            yield child.key or "", IRStoreView(self._store, child_id)

    def list_items(self) -> Iterable[IRNodeView]:
        node = self._store.get_node(self._node_id)

        for child_id in node.children:
            yield IRStoreView(self._store, child_id)

    def scalar_value(self):
        node = self._store.get_node(self._node_id)
        return node.value