from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QMessageBox,
)

from zeno.schema.loader import load
from zeno.core.store import IRStore
from zeno.core.types import NodeType
from zeno.core.operation import Operation
from zeno.core.operation_processor import OperationProcessor

from zeno.ui.tree_panel import TreePanel
from zeno.ui.right_panel import RightPanel


class ZenoMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Zeno Rebuild Phase")
        self.setMinimumSize(1100, 700)

        self._schema = None
        self._store: IRStore | None = None
        self._processor: OperationProcessor | None = None
        self._root_id: UUID | None = None
        self._in_config_mode: bool = False

        self._build_actions()
        self._build_menus()
        self._build_ui()
        self._wire()

        self._load_schema_file("schema/mma_nested_model.zs")

    # ---------------- Menu ----------------

    def _build_actions(self) -> None:
        self.act_new_config = QAction("New Config", self)
        self.act_new_config.triggered.connect(self._on_new_config)

        self.act_exit = QAction("Exit", self)
        self.act_exit.triggered.connect(self.close)

        self.act_about = QAction("About", self)
        self.act_about.triggered.connect(self._on_about)

    def _build_menus(self) -> None:
        mb = self.menuBar()

        m_file = mb.addMenu("File")
        m_file.addAction(self.act_new_config)
        m_file.addSeparator()
        m_file.addAction(self.act_exit)

        mb.addMenu("Edit")

        m_help = mb.addMenu("Help")
        m_help.addAction(self.act_about)

    # ---------------- UI ----------------

    def _build_ui(self) -> None:
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        self.tree_panel = TreePanel()
        self.right_panel = RightPanel()

        splitter.addWidget(self.tree_panel)
        splitter.addWidget(self.right_panel)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 5)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready.")

    # ---------------- Wire ----------------

    def _wire(self) -> None:
        self.tree_panel.node_selected.connect(self._on_node_selected)

    # ---------------- Schema Load ----------------

    def _load_schema_file(self, path: str) -> None:
        schema_path = Path(path)

        if not schema_path.exists():
            QMessageBox.critical(self, "Error", f"Schema not found: {path}")
            return

        self._schema = load(schema_path)
        self._in_config_mode = False

        root_mapping = self._schema.root
        properties = root_mapping.get("properties", {})

        tree_data = {
            "Schema Root": [
                {"type": "section", "key": key, "label": key}
                for key in properties.keys()
            ]
        }

        self.tree_panel.set_tree(tree_data)
        self.statusBar().showMessage(f"Loaded schema: {schema_path.name}")

    # ---------------- New Config ----------------

    def _on_new_config(self) -> None:
        if not self._schema:
            QMessageBox.warning(self, "Warning", "No schema loaded.")
            return

        self._store = IRStore()
        self._processor = OperationProcessor(self._store)
        self._root_id = self._store.create_root(NodeType.OBJECT)
        self._in_config_mode = True

        # Build full IR tree from schema root
        self._expand_schema_into_ir(parent_id=self._root_id, schema_node=self._schema.root)

        # Render top-level IR nodes in tree
        self._render_ir_tree_top_level()

        # Show a dump of full IR for proof
        dump = self._dump_ir(self._root_id)
        self.right_panel.set_full_preview_text(dump)

        self.statusBar().showMessage("New config created (schema-expanded).")

    def _expand_schema_into_ir(self, *, parent_id: UUID, schema_node: dict) -> None:
        """
        Deterministic schema → IR expansion.

        Rules:
        - object: create children for each property
        - array: create LIST node but DO NOT create items (empty list)
        - scalar (string/integer/bool/...): create SCALAR node with value=None
        """
        if not self._processor or not self._store:
            return

        node_type = schema_node.get("type")

        # Only objects have 'properties' in our schema
        if node_type != "object":
            return

        props = schema_node.get("properties", {})
        if not isinstance(props, dict):
            return

        for prop_key, prop_schema in props.items():
            if not isinstance(prop_schema, dict):
                continue

            t = prop_schema.get("type")

            if t == "object":
                child_type = NodeType.OBJECT
            elif t == "array":
                child_type = NodeType.LIST
            else:
                # string/integer/bool/unknown => scalar node
                child_type = NodeType.SCALAR

            op = Operation.create(
                operation_type="add_node",
                target_node_id=None,
                payload={
                    "parent_id": parent_id,
                    "node_type": child_type,
                    "key": prop_key,
                },
            )
            self._processor.apply(op)

            # Find the newly created child by key (object children enforce unique key)
            child_id = self._find_object_child_id(parent_id, prop_key)
            if child_id is None:
                continue

            # Recurse only for objects; arrays remain empty; scalars stop
            if t == "object":
                self._expand_schema_into_ir(parent_id=child_id, schema_node=prop_schema)

    def _find_object_child_id(self, parent_id: UUID, key: str) -> UUID | None:
        if not self._store:
            return None
        parent = self._store.get_node(parent_id)
        for cid in parent.children:
            c = self._store.get_node(cid)
            if c.key == key:
                return cid
        return None

    # ---------------- IR Tree (top-level only for now) ----------------

    def _render_ir_tree_top_level(self) -> None:
        if not self._store or not self._root_id:
            return

        root = self._store.get_node(self._root_id)
        children = []
        for cid in root.children:
            c = self._store.get_node(cid)
            label = c.key or ""
            children.append(
                {
                    "type": c.type.name,
                    "key": label,
                    "label": label,
                    "node_id": str(cid),
                }
            )

        self.tree_panel.set_tree({"Config Root": children})

    # ---------------- Dump IR for proof ----------------

    def _dump_ir(self, node_id: UUID, indent: int = 0) -> str:
        if not self._store:
            return ""

        node = self._store.get_node(node_id)
        pad = "  " * indent

        if node.type == NodeType.SCALAR:
            k = node.key or ""
            v = node.value
            return f"{pad}{k}: {v}"

        if node.type == NodeType.LIST:
            k = node.key or ""
            lines = [f"{pad}{k}: []  # list"]
            for i, cid in enumerate(node.children):
                lines.append(f"{pad}  - [{i}]")
                lines.append(self._dump_ir(cid, indent + 2))
            return "\n".join(lines)

        # OBJECT
        k = node.key or "root"
        lines = [f"{pad}{k}:  # object"]
        for cid in node.children:
            lines.append(self._dump_ir(cid, indent + 1))
        return "\n".join(lines)

    # ---------------- Node Selection ----------------

    def _on_node_selected(self, meta: dict) -> None:
        key = meta.get("key", "")
        self.statusBar().showMessage(f"Selected: {key}")

        # If in config mode and we have node_id, show IR subtree proof
        if self._in_config_mode and self._store:
            node_id_str = meta.get("node_id")
            if node_id_str:
                try:
                    nid = UUID(node_id_str)
                except Exception:
                    return
                if self._store.has_node(nid):
                    self.right_panel.set_full_preview_text(self._dump_ir(nid))
                    return

        # Otherwise, show schema info like before
        if not self._schema or not key:
            return

        props = self._schema.root.get("properties", {})
        node_schema = props.get(key)
        if not isinstance(node_schema, dict):
            return

        node_type = node_schema.get("type", "unknown")
        lines = [f"# {key}", f"type: {node_type}", ""]

        if node_type == "object":
            p = node_schema.get("properties", {})
            lines.append("properties:")
            if isinstance(p, dict):
                for name in p.keys():
                    lines.append(f"  - {name}")

        elif node_type == "array":
            items = node_schema.get("items", {})
            if isinstance(items, dict):
                lines.append(f"items type: {items.get('type', 'unknown')}")

        self.right_panel.set_full_preview_text("\n".join(lines))

    # ---------------- About ----------------

    def _on_about(self) -> None:
        QMessageBox.information(self, "About", "Zeno Rebuild Phase.")


def main() -> int:
    app = QApplication(sys.argv)
    win = ZenoMainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())