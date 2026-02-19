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
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
)

from zeno.core.store import IRStore
from zeno.core.types import NodeType
from zeno.core.operation import Operation
from zeno.core.operation_processor import OperationProcessor


class ZenoWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Zeno  Phase 0")

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
        self._tree.itemChanged.connect(self._on_item_changed)

        self._add_button = QPushButton("Add Scalar")
        self._add_button.clicked.connect(self._on_add_scalar)

        layout.addWidget(self._tree)
        layout.addWidget(self._add_button)

        container.setLayout(layout)
        self.setCentralWidget(container)

    def _refresh_tree(self) -> None:
        self._tree.blockSignals(True)
        self._tree.clear()

        root_item = QTreeWidgetItem(["root", ""])
        root_item.setFlags(Qt.ItemIsEnabled)
        self._tree.addTopLevelItem(root_item)

        self._populate_children(root_item, self._root_id)

        self._tree.expandAll()
        self._tree.blockSignals(False)

    def _populate_children(self, parent_item: QTreeWidgetItem, parent_id: UUID) -> None:
        parent_node = self._store.get_node(parent_id)

        for child_id in parent_node.children:
            child_node = self._store.get_node(child_id)

            key = child_node.key or ""
            value = str(child_node.value) if child_node.value is not None else ""

            item = QTreeWidgetItem([key, value])
            item.setData(0, Qt.UserRole, str(child_id))

            if child_node.type == NodeType.SCALAR:
                item.setFlags(
                    Qt.ItemIsEnabled
                    | Qt.ItemIsSelectable
                    | Qt.ItemIsEditable
                )
            else:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            parent_item.addChild(item)

            if child_node.children:
                self._populate_children(item, child_id)

    def _on_add_scalar(self) -> None:
        op = Operation.create(
            operation_type="add_node",
            target_node_id=None,
            payload={
                "parent_id": self._root_id,
                "node_type": NodeType.SCALAR,
                "key": f"field_{len(self._store.get_node(self._root_id).children)}",
            },
        )

        self._processor.apply(op)
        self._refresh_tree()

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 1:
            return

        node_id_str = item.data(0, Qt.UserRole)
        if not node_id_str:
            return

        node_id = UUID(node_id_str)
        new_value = item.text(1)

        op = Operation.create(
            operation_type="update_scalar",
            target_node_id=None,
            payload={
                "node_id": node_id,
                "value": new_value,
            },
        )

        self._processor.apply(op)


def run() -> None:
    app = QApplication(sys.argv)
    window = ZenoWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())
