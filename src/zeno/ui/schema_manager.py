"""Schema resolution and constraint query utilities."""

from __future__ import annotations


class SchemaManager:
    """Manages schema resolution and constraint queries."""

    def __init__(self, schema=None):
        """Initialize with optional schema."""
        self._schema = schema

    def set_schema(self, schema) -> None:
        """Update the active schema."""
        self._schema = schema

    def resolve_object_schema(self, schema_path: str) -> dict:
        """Resolve schema definition for an object at given path."""
        if not self._schema:
            return {}
        
        if not schema_path:
            return self._schema.root
        
        schema_node = self._schema.root
        parts = schema_path.split(".")
        
        for part in parts:
            if not isinstance(schema_node, dict):
                return {}
            
            # Navigate through properties
            props = schema_node.get("properties", {})
            if part not in props:
                # Might be array item, check items
                items = schema_node.get("items", {})
                if isinstance(items, dict):
                    schema_node = items
                    continue
                return {}
            
            schema_node = props[part]
        
        return schema_node if isinstance(schema_node, dict) else {}

    def resolve_list_item_schema(self, schema_path: str) -> dict:
        """Resolve schema definition for items in a list at given path."""
        object_schema = self.resolve_object_schema(schema_path)
        return object_schema.get("items", {})

    def get_array_constraints(self, schema_path: str) -> dict:
        """Get min_items and max_items for an array at given path."""
        schema = self.resolve_object_schema(schema_path)
        return {
            "min_items": schema.get("min_items"),
            "max_items": schema.get("max_items"),
        }

    def get_required_properties(self, schema_path: str) -> set:
        """Get set of required property names for an object at given path."""
        schema = self.resolve_object_schema(schema_path)
        # Some schemas may use 'required' field listing required property names
        return set(schema.get("required", []))

    def is_property_required(self, object_schema_path: str, property_name: str) -> bool:
        """Check if a specific property is marked as required."""
        if not self._schema:
            return False
        
        schema = self.resolve_object_schema(object_schema_path)
        props = schema.get("properties", {})
        prop_schema = props.get(property_name, {})
        
        # Check per-property required flag
        if prop_schema.get("required") is True:
            return True
        
        # Or check if it's in the object's required list
        required_list = schema.get("required", [])
        return property_name in required_list
