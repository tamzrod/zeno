"""Node edit operations (remove, move, edit value)."""

from __future__ import annotations

from uuid import UUID

from PySide6.QtWidgets import QMessageBox, QInputDialog

from zeno.core.types import NodeType
from zeno.core.operation import Operation


class NodeEditOperations:
    """Handles node editing operations (remove, move, update)."""

    def __init__(
        self,
        store,
        processor,
        schema_manager,
        tree_renderer,
        parent_window,
    ):
        """Initialize with required component references."""
        self._store = store
        self._processor = processor
        self._schema_manager = schema_manager
        self._tree_renderer = tree_renderer
        self._parent = parent_window
        self._root_id = None
        self._dirty_callback = None
        self._status_callback = None

    def set_root_id(self, root_id: UUID | None) -> None:
        """Set the current IR root node ID."""
        self._root_id = root_id

    def set_dirty_callback(self, callback) -> None:
        """Set callback for marking document dirty."""
        self._dirty_callback = callback

    def set_status_callback(self, callback) -> None:
        """Set callback for status bar updates."""
        self._status_callback = callback

    def handle_remove_node(self, node_meta: dict) -> None:
        """Handle request to remove a node."""
        if not self._store or not self._processor:
            QMessageBox.warning(self._parent, "Warning", "No active configuration.")
            return

        node_id_str = node_meta.get("node_id")
        if not node_id_str:
            return

        try:
            node_id = UUID(node_id_str)
        except Exception:
            return

        # Safety check: don't allow removing top-level children of root
        node = self._store.get_node(node_id)
        if node.parent_id == self._root_id:
            QMessageBox.warning(
                self._parent, 
                "Cannot Remove", 
                "Top-level schema properties cannot be removed."
            )
            return

        # Check if removing would violate required constraint
        if node.parent_id:
            parent = self._store.get_node(node.parent_id)
            
            # If parent is OBJECT and this property is required, block removal
            if parent.type == NodeType.OBJECT:
                parent_schema_path = node_meta.get("schema_path", "")
                # Get parent's schema path by removing the last segment
                parent_schema_parts = parent_schema_path.split(".")
                if parent_schema_parts and parent_schema_parts[-1]:
                    parent_schema_parts = parent_schema_parts[:-1]
                parent_schema_path = ".".join(parent_schema_parts)
                
                prop_name = node.key
                if prop_name and self._schema_manager.is_property_required(parent_schema_path, prop_name):
                    QMessageBox.warning(
                        self._parent, 
                        "Cannot Remove", 
                        f"Property '{prop_name}' is required."
                    )
                    return
            
            # If parent is LIST, check min_items constraint
            elif parent.type == NodeType.LIST:
                parent_schema_path = node_meta.get("schema_path", "")
                # Get parent's schema path by removing the last segment
                parent_schema_parts = parent_schema_path.split(".")
                if parent_schema_parts and parent_schema_parts[-1]:
                    parent_schema_parts = parent_schema_parts[:-1]
                parent_schema_path = ".".join(parent_schema_parts)
                
                constraints = self._schema_manager.get_array_constraints(parent_schema_path)
                min_items = constraints.get("min_items")
                current_count = len(parent.children)
                
                if min_items is not None and current_count <= min_items:
                    QMessageBox.warning(
                        self._parent, 
                        "Cannot Remove Item", 
                        f"Minimum items ({min_items}) reached."
                    )
                    return

        # Confirm removal
        key = node_meta.get("key", "node")
        reply = QMessageBox.question(
            self._parent,
            "Confirm Removal",
            f"Remove '{key}' and all its children?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return

        op = Operation.create(
            operation_type="remove_node",
            target_node_id=node_id,
            payload={},
        )
        
        try:
            self._processor.apply(op)
            if self._dirty_callback:
                self._dirty_callback(True)
            self._tree_renderer.render_ir_tree_top_level()
            if self._status_callback:
                self._status_callback(f"Removed node: {key}")
        except Exception as e:
            QMessageBox.critical(self._parent, "Error", f"Failed to remove node: {e}")

    def handle_move_node(self, move_data: dict) -> None:
        """Handle request to move a node (LIST reordering)."""
        if not self._store or not self._processor:
            QMessageBox.warning(self._parent, "Warning", "No active configuration.")
            return

        meta = move_data.get("meta", {})
        direction = move_data.get("direction")
        
        node_id_str = meta.get("node_id")
        if not node_id_str or not direction:
            return

        try:
            node_id = UUID(node_id_str)
        except Exception:
            return

        op = Operation.create(
            operation_type="move_node",
            target_node_id=node_id,
            payload={
                "node_id": node_id,
                "direction": direction,
            },
        )
        
        try:
            self._processor.apply(op)
            if self._dirty_callback:
                self._dirty_callback(True)
            self._tree_renderer.render_ir_tree_top_level()
            if self._status_callback:
                self._status_callback(f"Moved item {direction}")
        except ValueError as e:
            # Expected errors like "Cannot move first item up"
            if self._status_callback:
                self._status_callback(str(e))
        except Exception as e:
            QMessageBox.critical(self._parent, "Error", f"Failed to move node: {e}")

    def handle_edit_value(self, meta: dict) -> None:
        """Handle request to edit a scalar value."""
        if not self._store or not self._processor:
            QMessageBox.warning(self._parent, "Warning", "No active configuration.")
            return

        node_id_str = meta.get("node_id")
        if not node_id_str:
            return

        try:
            node_id = UUID(node_id_str)
        except Exception:
            return

        node = self._store.get_node(node_id)
        key = meta.get("key", "value")
        
        # Simple input dialog for now
        # TODO: Type-specific editors based on schema
        current_value = str(node.value) if node.value is not None else ""
        new_value, ok = QInputDialog.getText(
            self._parent,
            "Edit Value",
            f"Enter new value for '{key}':",
            text=current_value
        )
        
        if not ok:
            return

        op = Operation.create(
            operation_type="update_scalar",
            target_node_id=node_id,
            payload={
                "node_id": node_id,
                "value": new_value,
            },
        )
        
        try:
            self._processor.apply(op)
            if self._dirty_callback:
                self._dirty_callback(True)
            self._tree_renderer.render_ir_tree_top_level()
            if self._status_callback:
                self._status_callback(f"Updated {key} = {new_value}")
        except Exception as e:
            QMessageBox.critical(self._parent, "Error", f"Failed to update value: {e}")
