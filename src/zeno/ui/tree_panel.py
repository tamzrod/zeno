from __future__ import annotations
from typing import Any, Dict, List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem


class TreePanel(QWidget):
    node_selected = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

        self.tree.currentItemChanged.connect(self._on_current_item_changed)

    def set_tree(self, tree_data: Dict[str, List[Dict[str, Any]]]) -> None:
        self.tree.clear()

        for group_name, children in tree_data.items():
            group_item = QTreeWidgetItem([group_name])
            group_item.setData(0, Qt.UserRole, {"kind": "group"})
            self.tree.addTopLevelItem(group_item)

            for child in children:
                self._add_node_recursive(group_item, child)

            group_item.setExpanded(True)

        if self.tree.topLevelItemCount() > 0:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def _add_node_recursive(self, parent_item: QTreeWidgetItem, node_data: Dict[str, Any]) -> None:
        label = node_data.get("label") or node_data.get("key") or "node"

        item = QTreeWidgetItem([label])
        meta = {"kind": "node", **node_data}
        item.setData(0, Qt.UserRole, meta)

        parent_item.addChild(item)

        children = node_data.get("children")
        if isinstance(children, list):
            for child in children:
                self._add_node_recursive(item, child)

    def _on_current_item_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem) -> None:
        if current is None:
            return

        meta = current.data(0, Qt.UserRole) or {}
        if meta.get("kind") != "node":
            return

        self.node_selected.emit(meta)
