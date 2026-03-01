"""Right-side panel with Model/Docs tabs and deterministic live validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QTextEdit,
)


@dataclass
class ScalarBinding:
    """Editable scalar binding for model projection rendering."""

    node_id: UUID
    key: str
    node_type: str
    value: Any
    schema_path: str


class RightPanel(QWidget):
    """Model projection editor + docs surface without Preview/Generate phase."""

    scalar_value_edited = Signal(str, str)  # node_id, raw_text
    invalid_buffers_changed = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._active_node_id: Optional[str] = None
        self._active_schema_path: str = ""
        self._bindings: dict[str, ScalarBinding] = {}
        self._buffer_values: dict[str, str] = {}
        self._buffer_errors: dict[str, str] = {}
        self._node_line_spans: dict[str, tuple[int, int]] = {}
        self._line_tokens: list[tuple[str, str]] = []
        self._is_programmatic_model_update = False

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 8, 10, 0)

        self.node_title = QLabel("Select an item from the tree.")
        self.validation_badge = QLabel("")
        self.validation_badge.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header_layout.addWidget(self.node_title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.validation_badge)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        model_tab = QWidget()
        model_layout = QVBoxLayout(model_tab)
        model_layout.setContentsMargins(10, 8, 10, 10)
        model_layout.setSpacing(8)

        model_hint = QLabel("Model projection is structured: edit scalar values only.")
        model_hint.setObjectName("modelHint")
        model_layout.addWidget(model_hint)

        self.model_view = QTextEdit()
        self.model_view.setAcceptRichText(False)
        self.model_view.setLineWrapMode(QTextEdit.NoWrap)
        self.model_view.setPlaceholderText("Model projection appears here.")
        self.model_view.textChanged.connect(self._on_model_text_changed)
        model_layout.addWidget(self.model_view)

        self.inline_hint = QLabel("")
        self.inline_hint.setWordWrap(True)
        self.inline_hint.setVisible(False)
        model_layout.addWidget(self.inline_hint)

        docs_tab = QWidget()
        docs_layout = QVBoxLayout(docs_tab)
        docs_layout.setContentsMargins(10, 8, 10, 10)

        self.docs = QTextEdit()
        self.docs.setReadOnly(True)
        self.docs.setPlaceholderText("Schema docs will appear here.")
        docs_layout.addWidget(self.docs)

        self.tabs.addTab(model_tab, "Model")
        self.tabs.addTab(docs_tab, "Docs")

        root_layout.addWidget(header)
        root_layout.addWidget(self.tabs)

    # ---------------- Public API ----------------

    def set_node_content(
        self,
        *,
        node_title: str,
        schema_path: str,
        docs_md: str,
        bindings: list[ScalarBinding],
        line_spans: dict[str, tuple[int, int]],
        model_text: str,
    ) -> None:
        """Set current node content rendered by tree renderer."""
        self._active_schema_path = schema_path
        self.node_title.setText(node_title)
        self.docs.setMarkdown(docs_md or "")

        self._bindings = {str(binding.node_id): binding for binding in bindings}
        self._node_line_spans = dict(line_spans)

        self._line_tokens = []
        self._buffer_values = {}
        for line in model_text.splitlines():
            token = ""
            rendered = line
            if line.startswith("@@"):
                head, _, tail = line.partition(":")
                token = head[2:]
                rendered = tail.lstrip()
                if token in self._bindings:
                    self._line_tokens.append((token, rendered))
                    self._buffer_values[token] = rendered.split(":", 1)[1].strip() if ":" in rendered else ""
                    continue
            self._line_tokens.append((token, rendered))

        self._is_programmatic_model_update = True
        try:
            self.model_view.setPlainText("\n".join(rendered for _, rendered in self._line_tokens))
        finally:
            self._is_programmatic_model_update = False

        self._active_node_id = None
        self._clear_inline_hint()
        self._refresh_error_highlights()
        self._emit_invalid_state_if_changed()

    def clear_selection(self) -> None:
        """Clear active selection surfaces."""
        self._active_node_id = None
        self._active_schema_path = ""
        self._bindings = {}
        self._buffer_values = {}
        self._buffer_errors = {}
        self._line_tokens = []
        self._node_line_spans = {}

        self.node_title.setText("Select an item from the tree.")
        self.docs.setPlainText("")
        self._is_programmatic_model_update = True
        try:
            self.model_view.setPlainText("")
        finally:
            self._is_programmatic_model_update = False
        self._clear_inline_hint()
        self._emit_invalid_state_if_changed(force=True)

    def mark_buffer_valid(self, node_id: str) -> None:
        """Mark a scalar buffer as valid after successful commit to IR."""
        if node_id in self._buffer_errors:
            del self._buffer_errors[node_id]
            self._refresh_error_highlights()
            self._emit_invalid_state_if_changed()

    def mark_buffer_invalid(self, node_id: str, message: str) -> None:
        """Keep invalid input in buffer without committing to IR."""
        self._buffer_errors[node_id] = message
        self._refresh_error_highlights()
        if self._active_node_id == node_id:
            self._show_inline_hint(message)
        self._emit_invalid_state_if_changed()

    def set_active_scalar(self, node_id: str) -> None:
        """Set currently selected scalar for inline hints."""
        self._active_node_id = node_id
        if node_id in self._buffer_errors:
            self._show_inline_hint(self._buffer_errors[node_id])
        else:
            self._clear_inline_hint()

    def has_invalid_buffers(self) -> bool:
        return bool(self._buffer_errors)

    def active_schema_path(self) -> str:
        return self._active_schema_path

    # ---------------- Internal ----------------

    def _on_model_text_changed(self) -> None:
        if self._is_programmatic_model_update:
            return

        current_lines = self.model_view.toPlainText().splitlines()
        if len(current_lines) != len(self._line_tokens):
            self._revert_model_surface()
            return

        next_lines: list[tuple[str, str]] = []
        pending_changes: list[tuple[str, str]] = []

        for index, (token, previous_rendered) in enumerate(self._line_tokens):
            current_rendered = current_lines[index]
            if not token:
                if current_rendered != previous_rendered:
                    self._revert_model_surface()
                    return
                next_lines.append((token, previous_rendered))
                continue

            if ":" not in current_rendered:
                self._revert_model_surface()
                return

            expected_key = previous_rendered.split(":", 1)[0]
            current_key = current_rendered.split(":", 1)[0]
            if expected_key != current_key:
                self._revert_model_surface()
                return

            new_value = current_rendered.split(":", 1)[1].strip()
            old_value = self._buffer_values.get(token, "")
            if new_value != old_value:
                self._buffer_values[token] = new_value
                pending_changes.append((token, new_value))
            next_lines.append((token, current_rendered))

        self._line_tokens = next_lines

        for node_id, raw_value in pending_changes:
            self.scalar_value_edited.emit(node_id, raw_value)

    def _revert_model_surface(self) -> None:
        self._is_programmatic_model_update = True
        try:
            self.model_view.setPlainText("\n".join(rendered for _, rendered in self._line_tokens))
        finally:
            self._is_programmatic_model_update = False

    def _refresh_error_highlights(self) -> None:
        cursor = self.model_view.textCursor()
        selections = []

        for node_id, message in self._buffer_errors.items():
            span = self._node_line_spans.get(node_id)
            if not span:
                continue
            start_line, end_line = span
            start_pos = self._line_start_position(start_line)
            end_pos = self._line_end_position(end_line)
            if start_pos < 0 or end_pos < start_pos:
                continue

            selection = QTextEdit.ExtraSelection()
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#ffe5e5"))
            fmt.setToolTip(message)
            selection.format = fmt
            selection.cursor = QTextCursor(self.model_view.document())
            selection.cursor.setPosition(start_pos)
            selection.cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            selections.append(selection)

        self.model_view.setExtraSelections(selections)

        self.validation_badge.setText("● Invalid" if self._buffer_errors else "")

    def _line_start_position(self, line_index: int) -> int:
        if line_index < 0:
            return -1
        doc = self.model_view.document()
        block = doc.findBlockByLineNumber(line_index)
        if not block.isValid():
            return -1
        return block.position()

    def _line_end_position(self, line_index: int) -> int:
        doc = self.model_view.document()
        block = doc.findBlockByLineNumber(line_index)
        if not block.isValid():
            return -1
        return block.position() + block.length() - 1

    def _show_inline_hint(self, message: str) -> None:
        self.inline_hint.setText(message)
        self.inline_hint.setVisible(True)

    def _clear_inline_hint(self) -> None:
        self.inline_hint.setVisible(False)
        self.inline_hint.setText("")

    def _emit_invalid_state_if_changed(self, force: bool = False) -> None:
        has_invalid = bool(self._buffer_errors)
        if force:
            self.invalid_buffers_changed.emit(has_invalid)
            return
        self.invalid_buffers_changed.emit(has_invalid)
