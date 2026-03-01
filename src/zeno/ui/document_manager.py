"""Document lifecycle management (new, open, save, schema load)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QMessageBox, QFileDialog

from zeno.schema.loader import load
from zeno.core.store import IRStore
from zeno.core.types import NodeType
from zeno.core.operation_processor import OperationProcessor


class DocumentManager:
    """Manages document and schema lifecycle operations."""

    def __init__(
        self,
        tree_panel,
        right_panel,
        ir_builder,
        tree_renderer,
        parent_window,
    ):
        """Initialize with required component references."""
        self._tree_panel = tree_panel
        self._right_panel = right_panel
        self._ir_builder = ir_builder
        self._tree_renderer = tree_renderer
        self._parent = parent_window
        
        # State
        self._schema = None
        self._schema_path: Path | None = None
        self._store: IRStore | None = None
        self._processor: OperationProcessor | None = None
        self._root_id = None
        self._document_path: Path | None = None
        self._is_dirty: bool = False
        
        # Callbacks
        self._title_callback = None
        self._menu_state_callback = None
        self._status_callback = None

    def set_title_callback(self, callback) -> None:
        """Set callback for updating window title."""
        self._title_callback = callback

    def set_menu_state_callback(self, callback) -> None:
        """Set callback for updating menu state."""
        self._menu_state_callback = callback

    def set_status_callback(self, callback) -> None:
        """Set callback for status bar updates."""
        self._status_callback = callback

    def get_schema(self):
        """Get current schema."""
        return self._schema

    def get_store(self):
        """Get current IR store."""
        return self._store

    def get_processor(self):
        """Get current operation processor."""
        return self._processor

    def get_root_id(self):
        """Get current root node ID."""
        return self._root_id

    def get_document_path(self) -> Path | None:
        """Get current document path."""
        return self._document_path

    def is_dirty(self) -> bool:
        """Check if document has unsaved changes."""
        return self._is_dirty

    def set_dirty(self, dirty: bool = True) -> None:
        """Mark document as dirty."""
        if self._is_dirty != dirty:
            self._is_dirty = dirty
            if self._title_callback:
                self._title_callback()

    def check_dirty_and_proceed(self, callback) -> bool:
        """Check for unsaved changes before proceeding with document transition.
        
        Returns True if we should proceed, False if cancelled.
        """
        if not self._is_dirty:
            callback()
            return True

        reply = QMessageBox.question(
            self._parent,
            "Unsaved Changes",
            "Do you want to save your changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )

        if reply == QMessageBox.Save:
            self.handle_save()
            if not self._is_dirty:  # Save succeeded
                callback()
                return True
            return False  # Save failed or was cancelled
        elif reply == QMessageBox.Discard:
            callback()
            return True
        else:  # Cancel
            return False

    def handle_load_schema(self) -> None:
        """Handle Load Schema menu action."""
        # Check for dirty document before loading new schema
        def proceed_with_load():
            file_path, _ = QFileDialog.getOpenFileName(
                self._parent,
                "Load Schema",
                "schema",
                "Zeno Schema Files (*.zs);;All Files (*)"
            )

            if not file_path:
                return

            self._load_schema_file(Path(file_path))

        if self._store:  # Document is open
            self.check_dirty_and_proceed(proceed_with_load)
        else:
            proceed_with_load()

    def _load_schema_file(self, schema_path: Path) -> None:
        """Load a schema file and update UI."""
        if not schema_path.exists():
            QMessageBox.critical(self._parent, "Error", f"Schema not found: {schema_path}")
            return

        try:
            self._schema = load(schema_path)
            self._schema_path = schema_path
        except Exception as e:
            QMessageBox.critical(self._parent, "Error", f"Failed to load schema: {e}")
            return

        # Clear any active document
        self._store = None
        self._processor = None
        self._root_id = None
        self._document_path = None
        self._is_dirty = False

        # Show schema structure in tree
        root_mapping = self._schema.root
        properties = root_mapping.get("properties", {})

        tree_data = {
            "Schema Root": [
                {"type": "section", "key": key, "label": key}
                for key in properties.keys()
            ]
        }

        self._tree_panel.set_tree(tree_data)
        self._right_panel.clear_selection()
        
        if self._title_callback:
            self._title_callback()
        if self._menu_state_callback:
            self._menu_state_callback()
        if self._status_callback:
            self._status_callback(f"Loaded schema: {schema_path.name}")

    def handle_new_config(self) -> None:
        """Handle New Config menu action."""
        if not self._schema:
            QMessageBox.warning(self._parent, "Warning", "No schema loaded.")
            return

        # Check for dirty document before creating new
        def create_new():
            self._store = IRStore()
            self._processor = OperationProcessor(self._store)
            self._root_id = self._store.create_root(NodeType.OBJECT)
            self._document_path = None
            self._is_dirty = False

            # Update components with new state
            self._ir_builder._store = self._store
            self._ir_builder._processor = self._processor
            self._tree_renderer._store = self._store
            self._tree_renderer.set_root_id(self._root_id)

            # Build full IR tree from schema root
            self._ir_builder.expand_schema_into_ir(parent_id=self._root_id, schema_node=self._schema.root)

            # Render top-level IR nodes in tree
            self._tree_renderer.render_ir_tree_top_level()

            if self._title_callback:
                self._title_callback()
            if self._menu_state_callback:
                self._menu_state_callback()
            if self._status_callback:
                self._status_callback("New config created (schema-expanded).")

        if self._store:  # Document already open
            self.check_dirty_and_proceed(create_new)
        else:
            create_new()

    def handle_open_config(self) -> None:
        """Handle Open Config menu action."""
        if not self._schema:
            QMessageBox.warning(self._parent, "Warning", "No schema loaded.")
            return

        # Check for dirty document before opening
        def proceed_with_open():
            file_path, _ = QFileDialog.getOpenFileName(
                self._parent,
                "Open Config",
                "",
                "YAML Files (*.yaml *.yml);;All Files (*)"
            )

            if not file_path:
                return

            # TODO: Load config via adapter and populate IR
            QMessageBox.information(self._parent, "Not Implemented", "Config loading not yet implemented.")

        if self._store:  # Document already open
            self.check_dirty_and_proceed(proceed_with_open)
        else:
            proceed_with_open()

    def handle_save(self) -> None:
        """Handle Save menu action - direct IR serialization when valid."""
        if not self._store:
            return

        # If first save, redirect to Save As
        if not self._document_path:
            self.handle_save_as()
            return

        # Save IR to file via YAML adapter
        from zeno.adapters.yaml_adapter import serialize
        root = self._store.get_node(self._root_id)
        yaml_text = serialize(root, self._store)
        
        try:
            self._document_path.write_text(yaml_text, encoding="utf-8")
            self._is_dirty = False
            if self._title_callback:
                self._title_callback()
            if self._status_callback:
                self._status_callback(f"Saved: {self._document_path.name}")
        except Exception as e:
            QMessageBox.critical(self._parent, "Save Error", f"Failed to save: {e}")

    def handle_save_as(self) -> None:
        """Handle Save As menu action - direct IR serialization when valid."""
        if not self._store:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self._parent,
            "Save Config As",
            "",
            "YAML Files (*.yaml *.yml);;All Files (*)"
        )

        if not file_path:
            return

        # Save IR to file via YAML adapter
        from zeno.adapters.yaml_adapter import serialize
        root = self._store.get_node(self._root_id)
        yaml_text = serialize(root, self._store)
        
        try:
            Path(file_path).write_text(yaml_text, encoding="utf-8")
            self._document_path = Path(file_path)
            self._is_dirty = False
            if self._title_callback:
                self._title_callback()
            if self._menu_state_callback:
                self._menu_state_callback()
            if self._status_callback:
                self._status_callback(f"Saved as: {self._document_path.name}")
        except Exception as e:
            QMessageBox.critical(self._parent, "Save Error", f"Failed to save: {e}")

    def handle_config_wizard(self) -> None:
        """Handle Config Wizard menu action."""
        if not self._schema:
            QMessageBox.warning(self._parent, "Warning", "No schema loaded.")
            return

        # Check for dirty document before starting wizard
        def start_wizard():
            QMessageBox.information(self._parent, "Not Implemented", "Config Wizard not yet implemented.")

        if self._store:  # Document already open
            self.check_dirty_and_proceed(start_wizard)
        else:
            start_wizard()
