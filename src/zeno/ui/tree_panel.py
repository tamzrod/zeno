from __future__ import annotations
from typing import Any, Dict, List, Optional, Set
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QColor, QBrush, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QMenu


class TreePanel(QWidget):
    node_selected = Signal(dict)
    add_node_requested = Signal(dict)  # parent_meta
    remove_node_requested = Signal(dict)  # node_meta
    move_node_requested = Signal(dict)  # {node_meta, direction: "up" or "down"}
    edit_value_requested = Signal(dict)  # node_meta
    new_config_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)

        # Track nodes with errors
        self._error_nodes: Set[str] = set()
        self._schema_constraints: Dict[str, Any] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

        self.tree.currentItemChanged.connect(self._on_current_item_changed)

    def set_tree(self, tree_data: Dict[str, List[Dict[str, Any]]]) -> None:
        expanded_keys = self._collect_expanded_item_keys()
        selected_key = self._get_selected_item_key()

        self.tree.clear()

        for group_name, children in tree_data.items():
            group_item = QTreeWidgetItem([group_name])
            group_item.setData(0, Qt.UserRole, {"kind": "group"})
            self.tree.addTopLevelItem(group_item)

            for child in children:
                self._add_node_recursive(group_item, child)

        self._restore_expanded_items(expanded_keys)

        if not expanded_keys:
            for i in range(self.tree.topLevelItemCount()):
                self.tree.topLevelItem(i).setExpanded(True)

        # Apply error highlighting after building tree
        self._apply_error_highlighting()

        restored_selection = False
        if selected_key is not None:
            selected_item = self._find_item_by_key(selected_key)
            if selected_item is not None:
                self.tree.setCurrentItem(selected_item)
                restored_selection = True

        if not restored_selection and self.tree.topLevelItemCount() > 0:
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

    def _collect_expanded_item_keys(self) -> Set[tuple[str, str]]:
        """Collect stable keys for currently expanded items."""
        expanded_keys: Set[tuple[str, str]] = set()

        def walk(item: QTreeWidgetItem) -> None:
            key = self._get_item_key(item)
            if key is not None and item.isExpanded():
                expanded_keys.add(key)
            for i in range(item.childCount()):
                walk(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            walk(self.tree.topLevelItem(i))

        return expanded_keys

    def _restore_expanded_items(self, expanded_keys: Set[tuple[str, str]]) -> None:
        """Restore expanded state from previously captured keys."""
        if not expanded_keys:
            return

        def walk(item: QTreeWidgetItem) -> None:
            key = self._get_item_key(item)
            item.setExpanded(key in expanded_keys if key is not None else False)
            for i in range(item.childCount()):
                walk(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            walk(self.tree.topLevelItem(i))

    def _get_selected_item_key(self) -> tuple[str, str] | None:
        """Get stable key for currently selected item."""
        current = self.tree.currentItem()
        if current is None:
            return None
        return self._get_item_key(current)

    def _find_item_by_key(self, target_key: tuple[str, str]) -> QTreeWidgetItem | None:
        """Find first tree item matching a stable key."""
        def walk(item: QTreeWidgetItem) -> QTreeWidgetItem | None:
            if self._get_item_key(item) == target_key:
                return item
            for i in range(item.childCount()):
                found = walk(item.child(i))
                if found is not None:
                    return found
            return None

        for i in range(self.tree.topLevelItemCount()):
            found = walk(self.tree.topLevelItem(i))
            if found is not None:
                return found
        return None

    def _get_item_key(self, item: QTreeWidgetItem) -> tuple[str, str] | None:
        """Build a stable key for preserving UI state across tree rebuilds."""
        meta = item.data(0, Qt.UserRole) or {}
        kind = meta.get("kind")

        if kind == "group":
            return ("group", item.text(0))

        if kind == "node":
            node_id = meta.get("node_id")
            if isinstance(node_id, str) and node_id:
                return ("node_id", node_id)

            schema_path = meta.get("schema_path")
            if isinstance(schema_path, str) and schema_path:
                return ("schema_path", schema_path)

            label = item.text(0)
            parent = item.parent()
            parent_label = parent.text(0) if parent else ""
            return ("label_path", f"{parent_label}/{label}")

        return None

    def _on_current_item_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem) -> None:
        if current is None:
            return

        meta = current.data(0, Qt.UserRole) or {}
        if meta.get("kind") != "node":
            return

        self.node_selected.emit(meta)

    def set_schema_constraints(self, constraints: Dict[str, Any]) -> None:
        """Store schema constraints for validating operations."""
        self._schema_constraints = constraints

    def mark_node_errors(self, error_node_ids: Set[str]) -> None:
        """Highlight nodes with validation errors in red."""
        self._error_nodes = error_node_ids
        self._apply_error_highlighting()

    def _apply_error_highlighting(self) -> None:
        """Apply red highlighting to nodes with errors and their parents."""
        # Reset all colors first
        self._reset_colors(self.tree.invisibleRootItem())
        
        # Mark error nodes and propagate to parents
        self._mark_errors_recursive(self.tree.invisibleRootItem())

    def _reset_colors(self, item: QTreeWidgetItem) -> None:
        """Reset colors for item and all children."""
        for i in range(item.childCount()):
            child = item.child(i)
            child.setForeground(0, QBrush(QColor(0, 0, 0)))  # Black
            self._reset_colors(child)

    def _mark_errors_recursive(self, item: QTreeWidgetItem) -> bool:
        """Mark node with error color and return True if node or any child has error."""
        has_error = False
        
        # Check all children first
        for i in range(item.childCount()):
            child = item.child(i)
            if self._mark_errors_recursive(child):
                has_error = True
        
        # Check if this node itself has an error
        meta = item.data(0, Qt.UserRole) or {}
        node_id = meta.get("node_id", "")
        if node_id in self._error_nodes:
            # Direct error - bright red
            item.setForeground(0, QBrush(QColor(220, 20, 20)))
            has_error = True
        elif has_error:
            # Child has error - darker red/orange
            item.setForeground(0, QBrush(QColor(180, 80, 20)))
        
        return has_error

    def _on_context_menu(self, pos: QPoint) -> None:
        """Show context menu with schema-driven operations."""
        item = self.tree.itemAt(pos)
        if not item:
            return

        meta = item.data(0, Qt.UserRole) or {}
        kind = meta.get("kind")

        menu = QMenu(self)
        
        # === GROUP operations ===
        if kind == "group":
            expand_group_action = QAction("Expand All", self)
            expand_group_action.triggered.connect(lambda: self._expand_group(item))
            menu.addAction(expand_group_action)
            
            collapse_group_action = QAction("Collapse All", self)
            collapse_group_action.triggered.connect(lambda: self._collapse_group(item))
            menu.addAction(collapse_group_action)
            
            menu.exec(self.tree.viewport().mapToGlobal(pos))
            return

        if kind != "node":
            return

        node_type = meta.get("type", "")  # Already lowercase from app.py
        
        # Check if this is root
        is_root = self._is_root_node(item)
        
        # Check if this is a LIST item (parent is LIST)
        parent_item = item.parent()
        is_list_item = False
        if parent_item:
            parent_meta = parent_item.data(0, Qt.UserRole) or {}
            parent_type = parent_meta.get("type", "")
            is_list_item = parent_type == "list"

        # === OBJECT-specific operations ===
        if node_type == "object":
            add_property_action = QAction("Add Property...", self)
            add_property_action.triggered.connect(lambda: self.add_node_requested.emit(meta))
            menu.addAction(add_property_action)

        # === LIST-specific operations ===
        elif node_type == "list":
            add_item_action = QAction("Add Item", self)
            add_item_action.triggered.connect(lambda: self.add_node_requested.emit(meta))
            menu.addAction(add_item_action)

        # === SCALAR-specific operations ===
        elif node_type == "scalar":
            edit_value_action = QAction("Edit Value...", self)
            edit_value_action.triggered.connect(lambda: self.edit_value_requested.emit(meta))
            menu.addAction(edit_value_action)
        
        # === SECTION (schema browsing only) ===
        elif node_type == "section":
            new_config_action = QAction("Create New Config...", self)
            new_config_action.triggered.connect(self.new_config_requested.emit)
            menu.addAction(new_config_action)

        # === LIST ITEM operations (Move Up/Down) ===
        if is_list_item:
            menu.addSeparator()
            
            # Move Up
            move_up_action = QAction("Move Up", self)
            move_up_action.triggered.connect(lambda: self.move_node_requested.emit({"meta": meta, "direction": "up"}))
            
            # Check if this is the first item
            if parent_item:
                item_index = parent_item.indexOfChild(item)
                if item_index == 0:
                    move_up_action.setEnabled(False)
            
            menu.addAction(move_up_action)
            
            # Move Down
            move_down_action = QAction("Move Down", self)
            move_down_action.triggered.connect(lambda: self.move_node_requested.emit({"meta": meta, "direction": "down"}))
            
            # Check if this is the last item
            if parent_item:
                item_index = parent_item.indexOfChild(item)
                if item_index == parent_item.childCount() - 1:
                    move_down_action.setEnabled(False)
            
            menu.addAction(move_down_action)

        # === Remove operation (not for root, not for top-level schema properties) ===
        if not is_root and (is_list_item or self._is_removable_property(item)):
            menu.addSeparator()
            remove_action = QAction("Remove", self)
            remove_action.triggered.connect(lambda: self.remove_node_requested.emit(meta))
            menu.addAction(remove_action)

        # === Expand/Collapse (always available) ===
        menu.addSeparator()
        if item.isExpanded():
            collapse_action = QAction("Collapse", self)
            collapse_action.triggered.connect(lambda: item.setExpanded(False))
            menu.addAction(collapse_action)
        else:
            expand_action = QAction("Expand", self)
            expand_action.triggered.connect(lambda: item.setExpanded(True))
            menu.addAction(expand_action)

        # Show menu if there are actions
        if menu.actions():
            menu.exec(self.tree.viewport().mapToGlobal(pos))

    def _is_root_node(self, item: QTreeWidgetItem) -> bool:
        """Check if item is a root node (direct child of a group)."""
        parent = item.parent()
        if not parent:
            return False
        
        parent_meta = parent.data(0, Qt.UserRole) or {}
        return parent_meta.get("kind") == "group"

    def _expand_group(self, group_item: QTreeWidgetItem) -> None:
        """Recursively expand all items in a group."""
        for i in range(group_item.childCount()):
            child = group_item.child(i)
            child.setExpanded(True)
            self._expand_recursive(child)
    
    def _expand_recursive(self, item: QTreeWidgetItem) -> None:
        """Recursively expand an item and all its children."""
        item.setExpanded(True)
        for i in range(item.childCount()):
            child = item.child(i)
            self._expand_recursive(child)
    
    def _collapse_group(self, group_item: QTreeWidgetItem) -> None:
        """Recursively collapse all items in a group."""
        for i in range(group_item.childCount()):
            child = group_item.child(i)
            self._collapse_recursive(child)
            child.setExpanded(False)
    
    def _collapse_recursive(self, item: QTreeWidgetItem) -> None:
        """Recursively collapse an item and all its children."""
        item.setExpanded(False)
        for i in range(item.childCount()):
            child = item.child(i)
            self._collapse_recursive(child)

    def _is_removable_property(self, item: QTreeWidgetItem) -> bool:
        """Check if this is a removable property (not a top-level schema property)."""
        parent = item.parent()
        if not parent:
            return False
        
        parent_meta = parent.data(0, Qt.UserRole) or {}
        
        # If parent is root config object, this is a top-level schema property (not removable)
        # Otherwise, it's a nested property (removable)
        # For now, allow removal of non-root items
        return not self._is_root_node(item)
