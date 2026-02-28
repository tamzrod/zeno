# src/zeno/ui/right_panel.py
from __future__ import annotations

from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QFormLayout,
    QTextEdit,
    QPushButton,
)

from zeno.ui.right_panel_widgets import NodeSpec, CollapsibleSection, SchemaFormRenderer


class RightPanel(QWidget):
    write_clicked = Signal()
    generate_node_clicked = Signal()
    generate_full_clicked = Signal()
    export_full_clicked = Signal()
    dirty_changed = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._dirty = False
        self._has_generated = False
        self._current_key: Optional[str] = None
        self._current_type: Optional[str] = None
        self._schema: Dict[str, NodeSpec] = {}
        self._model: Dict[str, Dict[str, Any]] = {}

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # -------------------------
        # Model tab
        # -------------------------
        model_tab = QWidget()
        model_l = QVBoxLayout(model_tab)
        model_l.setContentsMargins(10, 10, 10, 10)
        model_l.setSpacing(10)

        self.node_title = QLabel("Select an item from the tree.")
        f = QFont()
        f.setPointSize(11)
        f.setBold(True)
        self.node_title.setFont(f)

        self.form_host = QWidget()
        self.form = QFormLayout(self.form_host)
        self.form.setHorizontalSpacing(16)
        self.form.setVerticalSpacing(10)
        self._form_renderer = SchemaFormRenderer(self.form)

        btn_row = QWidget()
        br = QHBoxLayout(btn_row)
        br.setContentsMargins(0, 0, 0, 0)
        br.setSpacing(8)

        self.btn_write = QPushButton("Write")
        self.btn_generate_node = QPushButton("Preview Node Output")
        self.btn_write.setEnabled(False)
        self.btn_generate_node.setEnabled(False)

        self.badge_dirty = QLabel("")
        self.badge_dirty.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        br.addWidget(self.btn_write)
        br.addWidget(self.btn_generate_node)
        br.addStretch(1)
        br.addWidget(self.badge_dirty)

        preview_body = QWidget()
        pbl = QVBoxLayout(preview_body)
        pbl.setContentsMargins(0, 0, 0, 0)
        pbl.setSpacing(6)

        self.preview_node = QTextEdit()
        self.preview_node.setReadOnly(True)
        self.preview_node.setPlaceholderText("Node output appears here.")
        pbl.addWidget(self.preview_node)

        self.preview_section = CollapsibleSection("Output Preview", preview_body, collapsed=True)

        model_l.addWidget(self.node_title)
        model_l.addWidget(self.form_host)
        model_l.addWidget(btn_row)
        model_l.addWidget(self.preview_section)

        # -------------------------
        # Docs tab
        # -------------------------
        docs_tab = QWidget()
        docs_l = QVBoxLayout(docs_tab)
        docs_l.setContentsMargins(10, 10, 10, 10)

        self.docs = QTextEdit()
        self.docs.setReadOnly(True)
        self.docs.setPlaceholderText("Schema docs will appear here.")
        docs_l.addWidget(self.docs)

        # -------------------------
        # Preview tab
        # -------------------------
        full_tab = QWidget()
        full_l = QVBoxLayout(full_tab)
        full_l.setContentsMargins(10, 10, 10, 10)
        full_l.setSpacing(10)

        full_header = QWidget()
        fhl = QHBoxLayout(full_header)
        fhl.setContentsMargins(0, 0, 0, 0)
        fhl.setSpacing(8)

        self.btn_generate_full = QPushButton("Generate Full Config")
        self.btn_export_full = QPushButton("Export Config")

        self.btn_generate_full.setEnabled(False)
        self.btn_export_full.setEnabled(False)

        fhl.addWidget(self.btn_generate_full)
        fhl.addWidget(self.btn_export_full)
        fhl.addStretch(1)

        self.preview_full = QTextEdit()
        self.preview_full.setReadOnly(True)
        self.preview_full.setPlaceholderText("Full config output appears here after Generate.")

        full_l.addWidget(full_header)
        full_l.addWidget(self.preview_full)

        self.tabs.addTab(model_tab, "Model")
        self.tabs.addTab(docs_tab, "Docs")
        self.tabs.addTab(full_tab, "Preview")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.tabs)

        # Wiring
        self.btn_write.clicked.connect(self.write_clicked.emit)
        self.btn_generate_node.clicked.connect(self.generate_node_clicked.emit)
        self.btn_generate_full.clicked.connect(self.generate_full_clicked.emit)
        self.btn_export_full.clicked.connect(self.export_full_clicked.emit)

    # ---------------- Public API ----------------

    def set_data_sources(self, schema: Dict[str, NodeSpec], model: Dict[str, Dict[str, Any]]) -> None:
        self._schema = schema
        self._model = model
        self._update_buttons()

    def select_node(self, key: str, node_type: str) -> None:
        self._current_key = key
        self._current_type = node_type
        self._dirty = False
        self._update_dirty_ui()

        node = self._model.get(key) or {}
        spec = self._schema.get(node_type)

        self.node_title.setText(f"{key}  ({node_type})")
        self.docs.setMarkdown(spec.docs_md if spec else "")
        self._form_renderer.render(spec, node, on_dirty=self._set_dirty)

        self.btn_write.setEnabled(True)
        self._update_buttons()

    def clear_selection(self) -> None:
        self._current_key = None
        self._current_type = None
        self._dirty = False
        self._update_dirty_ui()

        self.node_title.setText("Select an item from the tree.")
        self.docs.setPlainText("")
        self._form_renderer.clear()

        self.btn_write.setEnabled(False)
        self.btn_generate_node.setEnabled(False)
        self._update_buttons()

    def collect_form_updates(self) -> Dict[str, Any]:
        spec = self._schema.get(self._current_type or "")
        return self._form_renderer.collect_updates(spec)

    def mark_clean(self) -> None:
        if self._dirty:
            self._dirty = False
            self._update_dirty_ui()
            self.dirty_changed.emit(False)

    def set_node_preview_text(self, text: str) -> None:
        self.preview_node.setPlainText(text)
        self.preview_section.ensure_expanded()

    def set_full_preview_text(self, text: str) -> None:
        self.preview_full.setPlainText(text)
        self._has_generated = True
        self._update_buttons()

    def current_key(self) -> Optional[str]:
        return self._current_key

    def is_dirty(self) -> bool:
        return self._dirty

    # ---------------- Internal ----------------

    def _set_dirty(self) -> None:
        if not self._current_key:
            return
        if not self._dirty:
            self._dirty = True
            self._update_dirty_ui()
            self.dirty_changed.emit(True)
        self._update_buttons()

    def _update_dirty_ui(self) -> None:
        self.badge_dirty.setText("● Dirty" if self._dirty else "")
        self._update_buttons()

    def _update_buttons(self) -> None:
        # Full generate allowed only when not dirty
        self.btn_generate_full.setEnabled(not self._dirty)

        # Node generate requires selection + not dirty
        node_ok = bool(self._current_key) and (not self._dirty)
        self.btn_generate_node.setEnabled(node_ok)

        # Export allowed only after successful generate + not dirty
        self.btn_export_full.setEnabled(self._has_generated and (not self._dirty))