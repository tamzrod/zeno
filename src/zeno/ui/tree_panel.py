from __future__ import annotations

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem


class TreePanel(QWidget):
    """
    Left navigation tree.
    Emits node_selected when a real node is selected.
    """
    node_selected = Signal(dict)  # payload: {"key": str, "type": str, ...}

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.tree)

        self.tree.currentItemChanged.connect(self._on_current_item_changed)

    def set_tree(self, tree_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        tree_data example:
        {
          "ZENO Demo": [
            {"type":"listener","key":"listener: mvps01","label":"listener: mvps01"},
            ...
          ]
        }
        """
        self.tree.clear()

        for group_name, children in tree_data.items():
            group_item = QTreeWidgetItem([group_name])
            group_item.setData(0, Qt.UserRole, {"kind": "group"})
            self.tree.addTopLevelItem(group_item)

            for ch in children:
                label = ch.get("label") or ch.get("key") or "node"
                item = QTreeWidgetItem([label])
                meta = {"kind": "node", **ch}
                item.setData(0, Qt.UserRole, meta)
                group_item.addChild(item)

            group_item.setExpanded(True)

        if self.tree.topLevelItemCount() > 0:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def _on_current_item_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem) -> None:
        if current is None:
            return
        meta = current.data(0, Qt.UserRole) or {}
        if meta.get("kind") != "node":
            return
        self.node_selected.emit(meta)