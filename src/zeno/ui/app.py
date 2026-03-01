from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QMessageBox,
)

from zeno.ui.tree_panel import TreePanel
from zeno.ui.right_panel import RightPanel
from zeno.ui.schema_manager import SchemaManager
from zeno.ui.ir_builder import IRBuilder
from zeno.ui.tree_renderer import TreeRenderer
from zeno.ui.document_manager import DocumentManager
from zeno.ui.node_add_operations import NodeAddOperations
from zeno.ui.node_edit_operations import NodeEditOperations


class ZenoMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setMinimumSize(1100, 700)

        # UI Components
        self.tree_panel = TreePanel()
        self.right_panel = RightPanel()

        # Validation and edit state
        self._has_invalid_buffers = False
        self._has_validation_errors = False

        # Schema & IR utilities
        self.schema_manager = SchemaManager()
        self.ir_builder = IRBuilder(None, None)  # Will be updated on document creation
        self.tree_renderer = TreeRenderer(None, self.tree_panel, self.right_panel, self._get_schema)

        # Document lifecycle manager
        self.document_manager = DocumentManager(
            self.tree_panel,
            self.right_panel,
            self.ir_builder,
            self.tree_renderer,
            self,
        )
        self.document_manager.set_title_callback(self._update_title)
        self.document_manager.set_menu_state_callback(self._update_menu_state)
        self.document_manager.set_status_callback(self._update_status)

        # Node operation handlers
        self.node_add_operations = NodeAddOperations(
            None,  # store (will be set on document creation)
            None,  # processor (will be set on document creation)
            self.schema_manager,
            self.ir_builder,
            self.tree_renderer,
            self,
        )
        self.node_add_operations.set_dirty_callback(self._set_document_dirty)
        self.node_add_operations.set_status_callback(self._update_status)

        self.node_edit_operations = NodeEditOperations(
            None,  # store (will be set on document creation)
            None,  # processor (will be set on document creation)
            self.schema_manager,
            self.tree_renderer,
            self,
        )
        self.node_edit_operations.set_dirty_callback(self._set_document_dirty)
        self.node_edit_operations.set_status_callback(self._update_status)

        self._build_actions()
        self._build_menus()
        self._build_ui()
        self._wire()

        # Start with no schema loaded
        self._update_title()
        self._update_menu_state()
        self._update_status("Ready.")

    # ---------------- Menu ----------------

    def _build_actions(self) -> None:
        self.act_new_config = QAction("New Config...", self)
        self.act_new_config.triggered.connect(self._on_new_config)

        self.act_open_config = QAction("Open Config...", self)
        self.act_open_config.triggered.connect(self._on_open_config)

        self.act_save = QAction("Save", self)
        self.act_save.triggered.connect(self._on_save)

        self.act_save_as = QAction("Save As...", self)
        self.act_save_as.triggered.connect(self._on_save_as)

        self.act_config_wizard = QAction("Config Wizard...", self)
        self.act_config_wizard.triggered.connect(self._on_config_wizard)

        self.act_load_schema = QAction("Load Schema...", self)
        self.act_load_schema.triggered.connect(self._on_load_schema)

        self.act_exit = QAction("Exit", self)
        self.act_exit.triggered.connect(self.close)

        self.act_about = QAction("About", self)
        self.act_about.triggered.connect(self._on_about)

    def _build_menus(self) -> None:
        mb = self.menuBar()

        m_file = mb.addMenu("File")
        m_file.addAction(self.act_new_config)
        m_file.addAction(self.act_open_config)
        m_file.addAction(self.act_save)
        m_file.addAction(self.act_save_as)
        m_file.addSeparator()
        m_file.addAction(self.act_config_wizard)
        m_file.addAction(self.act_load_schema)
        m_file.addSeparator()
        m_file.addAction(self.act_exit)

        mb.addMenu("Edit")

        m_help = mb.addMenu("Help")
        m_help.addAction(self.act_about)

    # ---------------- UI ----------------

    def _build_ui(self) -> None:
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        splitter.addWidget(self.tree_panel)
        splitter.addWidget(self.right_panel)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready.")

    # ---------------- Wire ----------------

    def _wire(self) -> None:
        self.tree_panel.node_selected.connect(self._on_node_selected)
        self.tree_panel.add_node_requested.connect(self._on_add_node_requested)
        self.tree_panel.remove_node_requested.connect(self._on_remove_node_requested)
        self.tree_panel.move_node_requested.connect(self._on_move_node_requested)
        self.tree_panel.edit_value_requested.connect(self._on_edit_value_requested)
        self.tree_panel.new_config_requested.connect(self._on_new_config)

        # Right panel: live scalar edits and validation
        self.right_panel.scalar_value_edited.connect(self._on_scalar_value_edited)
        self.right_panel.invalid_buffers_changed.connect(self._on_invalid_buffers_changed)

    # ---------------- State Management ----------------

    def _get_schema(self):
        """Get current schema for tree rendering."""
        return self.document_manager.get_schema()

    def _update_status(self, message: str) -> None:
        """Update status bar message."""
        self.statusBar().showMessage(message)

    def _set_document_dirty(self, dirty: bool = True) -> None:
        """Mark document as dirty via document manager."""
        self.document_manager.set_dirty(dirty)

    def _sync_operation_context(self) -> None:
        """Sync schema/store/processor references used by node operation handlers."""
        schema = self.document_manager.get_schema()
        store = self.document_manager.get_store()
        processor = self.document_manager.get_processor()
        root_id = self.document_manager.get_root_id()

        self.schema_manager.set_schema(schema)

        self.node_add_operations._store = store
        self.node_add_operations._processor = processor

        self.node_edit_operations._store = store
        self.node_edit_operations._processor = processor
        self.node_edit_operations.set_root_id(root_id)

    def _update_title(self) -> None:
        """Update window title based on document state."""
        schema = self.document_manager.get_schema()
        store = self.document_manager.get_store()
        doc_path = self.document_manager.get_document_path()
        is_dirty = self.document_manager.is_dirty()

        if not schema:
            self.setWindowTitle("ZENO -- No Schema")
        elif doc_path:
            doc_name = doc_path.name
            dirty_marker = "*" if is_dirty else ""
            self.setWindowTitle(f"ZENO -- {doc_name}{dirty_marker}")
        elif store:
            dirty_marker = "*" if is_dirty else ""
            self.setWindowTitle(f"ZENO -- Untitled{dirty_marker}")
        else:
            self.setWindowTitle("ZENO -- Schema Loaded")

    def _update_menu_state(self) -> None:
        """Enable/disable menu items based on document and validation state."""
        has_schema = self.document_manager.get_schema() is not None
        has_document = self.document_manager.get_store() is not None

        # New Config, Config Wizard require schema
        self.act_new_config.setEnabled(has_schema)
        self.act_open_config.setEnabled(has_schema)
        self.act_config_wizard.setEnabled(has_schema)

        # Save/Save As require active document AND no invalid buffers AND no validation errors
        can_save = has_document and not self._has_invalid_buffers and not self._has_validation_errors
        self.act_save.setEnabled(can_save)
        self.act_save_as.setEnabled(can_save)

    # ---------------- Schema Load ----------------

    def _on_load_schema(self) -> None:
        """Handle Load Schema menu action."""
        self.document_manager.handle_load_schema()
        self._sync_operation_context()

    # ---------------- Document Lifecycle ----------------

    def _on_new_config(self) -> None:
        """Handle New Config menu action."""
        self.document_manager.handle_new_config()
        self._sync_operation_context()

    def _on_open_config(self) -> None:
        """Handle Open Config menu action."""
        self.document_manager.handle_open_config()
        self._sync_operation_context()

    def _on_save(self) -> None:
        """Handle Save menu action."""
        self.document_manager.handle_save()

    def _on_save_as(self) -> None:
        """Handle Save As menu action."""
        self.document_manager.handle_save_as()

    def _on_config_wizard(self) -> None:
        """Handle Config Wizard menu action."""
        self.document_manager.handle_config_wizard()

    # ---------------- Node Selection ----------------

    def _on_node_selected(self, meta: dict) -> None:
        """Handle node selection from tree panels."""
        self.tree_renderer.handle_node_selection(meta, self._update_status)

    # ---------------- Node Operations ----------------

    def _on_add_node_requested(self, parent_meta: dict) -> None:
        """Handle request to add a child node."""
        self.node_add_operations.handle_add_node(parent_meta)

    def _on_remove_node_requested(self, node_meta: dict) -> None:
        """Handle request to remove a node."""
        self.node_edit_operations.handle_remove_node(node_meta)

    def _on_move_node_requested(self, move_data: dict) -> None:
        """Handle request to move a node (LIST reordering)."""
        self.node_edit_operations.handle_move_node(move_data)

    def _on_edit_value_requested(self, meta: dict) -> None:
        """Handle request to edit a scalar value (legacy flow from tree context menu)."""
        self.node_edit_operations.handle_edit_value(meta)

    def _on_scalar_value_edited(self, node_id_str: str, raw_value: str) -> None:
        """Handle live scalar value edit from Model projection editor.
        
        Performs type-based validation and commits to IR only when valid.
        Invalid input remains in buffer with inline hint, IR stays valid.
        """
        if not self.document_manager.get_store():
            return

        from uuid import UUID
        from zeno.core.operation import Operation
        from zeno.core.types import NodeType

        try:
            node_id = UUID(node_id_str)
        except Exception:
            return

        store = self.document_manager.get_store()
        if not store or not store.has_node(node_id):
            return

        node = store.get_node(node_id)
        if node.type != NodeType.SCALAR:
            return

        # Type-based validation (currently passthrough, schema-type checking to be added)
        typed_value = raw_value

        # Apply update operation
        processor = self.document_manager.get_processor()
        if not processor:
            return

        op = Operation.create(
            operation_type="update_scalar",
            target_node_id=None,
            payload={
                "node_id": node_id,
                "value": typed_value,
            },
        )

        try:
            processor.apply(op)
            self.right_panel.mark_buffer_valid(node_id_str)
            self._set_document_dirty(True)
            self.tree_renderer.render_ir_tree_top_level()
            self._update_status(f"Updated {node.key or 'value'}")
        except Exception as e:
            # Validation or constraint failure - keep in buffer
            self.right_panel.mark_buffer_invalid(node_id_str, str(e))
            self._update_status(f"Validation error: {e}")

    def _on_invalid_buffers_changed(self, has_invalid: bool) -> None:
        """Update Save gating when buffer validity changes."""
        self._has_invalid_buffers = has_invalid
        self._update_menu_state()

    # ---------------- About ----------------

    def _on_about(self) -> None:
        QMessageBox.information(self, "About", "Zeno Rebuild Phase.")

    # -------- Close Event --------

    def closeEvent(self, event) -> None:
        """Override close event to check for unsaved changes."""
        if not self.document_manager.is_dirty():
            event.accept()
            return

        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "Do you want to save your changes before exiting?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save
        )

        if reply == QMessageBox.Save:
            self._on_save()
            if not self.document_manager.is_dirty():  # Save succeeded
                event.accept()
            else:
                event.ignore()  # Save failed or was cancelled
        elif reply == QMessageBox.Discard:
            event.accept()
        else:  # Cancel
            event.ignore()


def main() -> int:
    app = QApplication(sys.argv)
    win = ZenoMainWindow()
    win.show()
    return app.exec()


def run() -> int:
    return main()


if __name__ == "__main__":
    raise SystemExit(main())