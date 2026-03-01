"""Node add operations (add LIST items and OBJECT properties)."""

from __future__ import annotations

from uuid import UUID

from PySide6.QtWidgets import QMessageBox, QInputDialog

from zeno.core.types import NodeType
from zeno.core.operation import Operation


class NodeAddOperations:
    """Handles adding nodes (list items and object properties)."""

    def __init__(
        self,
        store,
        processor,
        schema_manager,
        ir_builder,
        tree_renderer,
        parent_window,
    ):
        """Initialize with required component references."""
        self._store = store
        self._processor = processor
        self._schema_manager = schema_manager
        self._ir_builder = ir_builder
        self._tree_renderer = tree_renderer
        self._parent = parent_window
        self._dirty_callback = None
        self._status_callback = None

    def set_dirty_callback(self, callback) -> None:
        """Set callback for marking document dirty."""
        self._dirty_callback = callback

    def set_status_callback(self, callback) -> None:
        """Set callback for status bar updates."""
        self._status_callback = callback

    def handle_add_node(self, parent_meta: dict) -> None:
        """Handle request to add a child node."""
        if not self._store or not self._processor:
            QMessageBox.warning(self._parent, "Warning", "No active configuration.")
            return

        parent_id_str = parent_meta.get("node_id")
        if not parent_id_str:
            return

        try:
            parent_id = UUID(parent_id_str)
        except Exception:
            return

        parent = self._store.get_node(parent_id)
        parent_type = parent.type
        
        # For LIST nodes, add an item
        if parent_type == NodeType.LIST:
            self.add_list_item(parent_id, parent_meta)
        # For OBJECT nodes, show available properties
        elif parent_type == NodeType.OBJECT:
            self.add_object_property(parent_id, parent_meta)
        else:
            QMessageBox.warning(self._parent, "Warning", "Cannot add children to scalar nodes.")

    def add_list_item(self, parent_id: UUID, parent_meta: dict) -> None:
        """Add an item to a LIST node based on schema."""
        if not self._processor:
            return
        
        # Check max_items constraint
        schema_path = parent_meta.get("schema_path", "")
        constraints = self._schema_manager.get_array_constraints(schema_path)
        max_items = constraints.get("max_items")
        
        current_count = self._ir_builder.get_array_item_count(parent_id)
        if max_items is not None and current_count >= max_items:
            QMessageBox.warning(
                self._parent, 
                "Cannot Add Item", 
                f"Maximum items ({max_items}) reached."
            )
            return
        
        # Get schema for the list to determine item type
        item_schema = self._schema_manager.resolve_list_item_schema(schema_path)
        
        if not item_schema:
            QMessageBox.warning(self._parent, "Warning", "Cannot determine item type from schema.")
            return
        
        item_type_str = item_schema.get("type", "string")
        
        # Map schema type to NodeType
        if item_type_str == "object":
            item_type = NodeType.OBJECT
        elif item_type_str == "array":
            item_type = NodeType.LIST
        else:
            item_type = NodeType.SCALAR
        
        op = Operation.create(
            operation_type="add_node",
            target_node_id=None,
            payload={
                "parent_id": parent_id,
                "node_type": item_type,
                "key": None,  # LIST items don't have keys
            },
        )
        
        try:
            self._processor.apply(op)
            
            # If it's an object, expand it according to schema
            if item_type == NodeType.OBJECT:
                # Find the newly added child
                parent = self._store.get_node(parent_id)
                new_child_id = parent.children[-1]  # Last added
                self._ir_builder.expand_schema_into_ir(parent_id=new_child_id, schema_node=item_schema)
            
            if self._dirty_callback:
                self._dirty_callback(True)
            self._tree_renderer.render_ir_tree_top_level()
            if self._status_callback:
                self._status_callback("Added list item")
        except Exception as e:
            QMessageBox.critical(self._parent, "Error", f"Failed to add item: {e}")

    def add_object_property(self, parent_id: UUID, parent_meta: dict) -> None:
        """Add a property to an OBJECT node, showing only available schema properties."""
        if not self._processor:
            return
        
        # Get current children keys
        parent = self._store.get_node(parent_id)
        existing_keys = {self._store.get_node(cid).key for cid in parent.children}
        
        # Get schema for this object to determine available properties
        schema_path = parent_meta.get("schema_path", "")
        object_schema = self._schema_manager.resolve_object_schema(schema_path)
        
        if not object_schema:
            QMessageBox.warning(self._parent, "Warning", "Cannot determine properties from schema.")
            return
        
        # Get available properties
        schema_properties = object_schema.get("properties", {})
        available_properties = [key for key in schema_properties.keys() if key not in existing_keys]
        
        if not available_properties:
            QMessageBox.information(
                self._parent, 
                "No Properties Available", 
                "All schema-defined properties have been added."
            )
            return
        
        # Show dialog to select property
        property_key, ok = QInputDialog.getItem(
            self._parent,
            "Add Property",
            "Select property to add:",
            available_properties,
            0,
            False
        )
        
        if not ok or not property_key:
            return
        
        # Get the property schema
        prop_schema = schema_properties[property_key]
        prop_type_str = prop_schema.get("type", "string")
        
        # Map to NodeType
        if prop_type_str == "object":
            node_type = NodeType.OBJECT
        elif prop_type_str == "array":
            node_type = NodeType.LIST
        else:
            node_type = NodeType.SCALAR
        
        op = Operation.create(
            operation_type="add_node",
            target_node_id=None,
            payload={
                "parent_id": parent_id,
                "node_type": node_type,
                "key": property_key,
            },
        )
        
        try:
            self._processor.apply(op)
            
            # Find the newly created child and expand if it's an object
            child_id = self._ir_builder.find_object_child_id(parent_id, property_key)
            if child_id and node_type == NodeType.OBJECT:
                self._ir_builder.expand_schema_into_ir(parent_id=child_id, schema_node=prop_schema)
            
            if self._dirty_callback:
                self._dirty_callback(True)
            self._tree_renderer.render_ir_tree_top_level()
            if self._status_callback:
                self._status_callback(f"Added property: {property_key}")
        except Exception as e:
            QMessageBox.critical(self._parent, "Error", f"Failed to add property: {e}")
