# src/zeno/ui/right_panel_widgets.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QTextEdit,
    QToolButton,
)


@dataclass
class FieldSpec:
    key: str
    label: str
    kind: str  # "str" | "int" | "bool" | "enum"
    editable: bool = True
    enum_values: Optional[List[str]] = None
    min_value: int = 0
    max_value: int = 65535
    help_text: str = ""


@dataclass
class NodeSpec:
    type_name: str
    fields: List[FieldSpec]
    docs_md: str = ""


class CollapsibleSection(QWidget):
    def __init__(self, title: str, body: QWidget, collapsed: bool = True, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._body = body

        self._btn = QToolButton()
        self._btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._btn.setText(title)
        self._btn.setCheckable(True)
        self._btn.setChecked(not collapsed)
        self._btn.setArrowType(Qt.RightArrow if collapsed else Qt.DownArrow)
        self._btn.clicked.connect(self._toggle)

        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.addWidget(self._btn)
        hl.addStretch(1)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)
        root.addWidget(header)
        root.addWidget(self._body)

        self._body.setVisible(not collapsed)

    def _toggle(self) -> None:
        expanded = self._btn.isChecked()
        self._btn.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow)
        self._body.setVisible(expanded)

    def ensure_expanded(self) -> None:
        if not self._btn.isChecked():
            self._btn.click()


class SchemaFormRenderer:
    def __init__(self, form: QFormLayout) -> None:
        self._form = form

    def clear(self) -> None:
        while self._form.rowCount():
            self._form.removeRow(0)

    def render(self, spec: Optional[NodeSpec], node: Dict[str, Any], on_dirty: Optional[callable] = None) -> None:
        self.clear()
        if not spec:
            self._form.addRow(QLabel("No schema spec found."), QLabel(""))
            return

        for field in spec.fields:
            w = self._make_widget(field, node.get(field.key))
            w.setEnabled(field.editable)

            label = QLabel(field.label)
            label.setToolTip(field.help_text or "")
            w.setToolTip(field.help_text or "")

            self._form.addRow(label, w)

            if field.editable and on_dirty is not None:
                self._attach_dirty(field.kind, w, on_dirty)

    def collect_updates(self, spec: Optional[NodeSpec]) -> Dict[str, Any]:
        if not spec:
            return {}

        updates: Dict[str, Any] = {}
        for row_idx, field in enumerate(spec.fields):
            item = self._form.itemAt(row_idx, QFormLayout.FieldRole)
            w = item.widget() if item else None
            if w is None:
                continue

            if field.kind == "str" and isinstance(w, QLineEdit):
                updates[field.key] = w.text()
            elif field.kind == "int" and isinstance(w, QSpinBox):
                updates[field.key] = int(w.value())
            elif field.kind == "bool" and isinstance(w, QCheckBox):
                updates[field.key] = bool(w.isChecked())
            elif field.kind == "enum" and isinstance(w, QComboBox):
                updates[field.key] = w.currentText()
            else:
                if isinstance(w, QLineEdit):
                    updates[field.key] = w.text()

        return updates

    def _make_widget(self, field: FieldSpec, value: Any) -> QWidget:
        if field.kind == "str":
            w = QLineEdit()
            w.setText("" if value is None else str(value))
            return w

        if field.kind == "int":
            w = QSpinBox()
            w.setRange(field.min_value, field.max_value)
            w.setValue(int(value) if value is not None else field.min_value)
            return w

        if field.kind == "bool":
            w = QCheckBox()
            w.setChecked(bool(value))
            return w

        if field.kind == "enum":
            w = QComboBox()
            w.addItems(field.enum_values or [])
            if value in (field.enum_values or []):
                w.setCurrentText(str(value))
            return w

        w = QLineEdit()
        w.setText("" if value is None else str(value))
        return w

    def _attach_dirty(self, kind: str, w: QWidget, on_dirty: callable) -> None:
        if kind == "str" and isinstance(w, QLineEdit):
            w.textEdited.connect(lambda _t: on_dirty())
        elif kind == "int" and isinstance(w, QSpinBox):
            w.valueChanged.connect(lambda _v: on_dirty())
        elif kind == "bool" and isinstance(w, QCheckBox):
            w.stateChanged.connect(lambda _s: on_dirty())
        elif kind == "enum" and isinstance(w, QComboBox):
            w.currentIndexChanged.connect(lambda _i: on_dirty())
        else:
            if isinstance(w, QLineEdit):
                w.textEdited.connect(lambda _t: on_dirty())