# src/zeno/ui/app.py

from __future__ import annotations

import sys
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QMenu,
)

from zeno.core.store import IRStore
from zeno.core.types import NodeType
from zeno.core.operation import Operation
from zeno.core.operation_processor import OperationProcessor


class ZenoWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Zeno  Phase 2")

        self._store = IRStore()
        self._processor = OperationProcessor(self._store)
        self._root_id = self._store.create_root(NodeType.OBJECT)

        self._setup_ui()
        self._refresh_tree()

    def _setup_ui(self) -> None:
        container = QWidget()
        layout = QVBoxLayout()

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Key", "Value"])
        self._tree.setIndentation(20)
        self._tree.setAlternatingRowColors(True)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._open_context_menu)
        self._tree.itemChanged.connect(self._on_item_changed)

        layout.addWidget(self._tree)

        container.setLayout(layout)
        self.setCentralWidget(container)

    # ---------- TREE RENDER ----------

    def _refresh_tree(self) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()

        root_item = QTreeWidgetItem(["root", ""])
        root_item.setData(0, Qt.UserRole, str(self._root_id))
        root_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

        self._tree.addTopLevelItem(root_item)
        self._populate_children(root_item, self._root_id)

        self._tree.expandAll()
        self._tree.blockSignals(False)

    def _populate_children(self, parent_item: QTreeWidgetItem, parent_id: UUID) -> None:
        parent_node = self._store.get_node(parent_id)

        for index, child_id in enumerate(parent_node.children):
            child_node = self._store.get_node(child_id)

            if parent_node.type == NodeType.LIST:
                display_key = f"[{index}]"
            else:
                display_key = child_node.key or ""

            value = (
                str(child_node.value)
                if child_node.type == NodeType.SCALAR and child_node.value is not None
                else ""
            )

            item = QTreeWidgetItem([display_key, value])
            item.setData(0, Qt.UserRole, str(child_id))

            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

            if child_node.type != NodeType.LIST:
                flags |= Qt.ItemIsEditable

            if child_node.type == NodeType.SCALAR:
                flags |= Qt.ItemIsEditable

            item.setFlags(flags)

            parent_item.addChild(item)

            if child_node.children:
                self._populate_children(item, child_id)

    # ---------- CONTEXT MENU ----------

    def _open_context_menu(self, position) -> None:
        item = self._tree.itemAt(position)
        menu = QMenu()

        if item:
            node_id = UUID(item.data(0, Qt.UserRole))
            node = self._store.get_node(node_id)

            if node.type in (NodeType.OBJECT, NodeType.LIST):
                menu.addAction("Add Scalar", lambda: self._add_node(node_id, NodeType.SCALAR))
                menu.addAction("Add Object", lambda: self._add_node(node_id, NodeType.OBJECT))
                menu.addAction("Add List", lambda: self._add_node(node_id, NodeType.LIST))

            if node_id != self._root_id:
                menu.addSeparator()
                menu.addAction("Remove", lambda: self._remove_node(node_id))

        menu.exec(self._tree.viewport().mapToGlobal(position))

    # ---------- OPERATIONS ----------

    def _add_node(self, parent_id: UUID, node_type: NodeType) -> None:
        parent_node = self._store.get_node(parent_id)
        child_count = len(parent_node.children)

        if parent_node.type == NodeType.OBJECT:
            key = f"{node_type.name.lower()}_{child_count}"
        else:
            key = None

        op = Operation.create(
            operation_type="add_node",
            target_node_id=None,
            payload={
                "parent_id": parent_id,
                "node_type": node_type,
                "key": key,
            },
        )

        self._processor.apply(op)
        self._refresh_tree()

    def _remove_node(self, node_id: UUID) -> None:
        op = Operation.create(
            operation_type="remove_node",
            target_node_id=None,
            payload={
                "node_id": node_id,
            },
        )

        self._processor.apply(op)
        self._refresh_tree()

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        node_id = UUID(item.data(0, Qt.UserRole))
        node = self._store.get_node(node_id)

        if column == 0 and node.parent_id:
            # Rename key (only valid for object children)
            parent = self._store.get_node(node.parent_id)
            if parent.type == NodeType.OBJECT:
                node.key = item.text(0)

        if column == 1 and node.type == NodeType.SCALAR:
            op = Operation.create(
                operation_type="update_scalar",
                target_node_id=None,
                payload={
                    "node_id": node_id,
                    "value": item.text(1),
                },
            )
            self._processor.apply(op)


def run() -> None:
    app = QApplication(sys.argv)
    window = ZenoWindow()
    window.resize(800, 500)
    window.show()
    sys.exit(app.exec())
