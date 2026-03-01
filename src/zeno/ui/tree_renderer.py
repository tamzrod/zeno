"""Tree rendering plus deterministic Model projection surface with line bindings."""

from __future__ import annotations

from uuid import UUID

from zeno.core.types import NodeType
from zeno.ui.right_panel import ScalarBinding


class TreeRenderer:
    """Manages tree rendering plus structured Model projection with locked syntax."""

    def __init__(self, store, tree_panel, right_panel, schema_provider):
        """Initialize with required component references."""
        self._store = store
        self._tree_panel = tree_panel
        self._right_panel = right_panel
        self._schema_provider = schema_provider
        self._root_id = None

    def set_root_id(self, root_id: UUID | None) -> None:
        """Set the current IR root node ID."""
        self._root_id = root_id

    def render_ir_tree_top_level(self) -> None:
        """Render the complete IR tree structure."""
        if not self._store or not self._root_id:
            return

        root = self._store.get_node(self._root_id)
        children = []
        for cid in root.children:
            child_data = self._build_tree_node_recursive(cid)
            if child_data:
                children.append(child_data)

        self._tree_panel.set_tree({"Config Root": children})

    def _build_tree_node_recursive(self, node_id: UUID, schema_path: str = "") -> dict:
        """Build tree node data with full recursive structure and schema path."""
        if not self._store:
            return {}

        node = self._store.get_node(node_id)
        label = node.key or f"[{node.type.name}]"

        if node.key and schema_path:
            current_schema_path = f"{schema_path}.{node.key}"
        elif node.key:
            current_schema_path = node.key
        else:
            current_schema_path = schema_path

        node_data = {
            "type": node.type.value,
            "key": label,
            "label": label,
            "node_id": str(node_id),
            "schema_path": current_schema_path,
        }

        if node.children:
            children = []
            for child_id in node.children:
                child_data = self._build_tree_node_recursive(child_id, current_schema_path)
                if child_data:
                    children.append(child_data)
            if children:
                node_data["children"] = children

        return node_data

    def handle_node_selection(self, meta: dict, status_callback) -> None:
        """Render selected node's Model projection (structured, line-numbered view)."""
        key = meta.get("key", "")
        status_callback(f"Selected: {key}")

        node_id_str = meta.get("node_id")
        if not node_id_str or not self._store:
            schema = self._schema_provider()
            if schema and key:
                self._render_schema_surface(key, schema)
            return

        try:
            nid = UUID(node_id_str)
        except Exception:
            return

        if not self._store.has_node(nid):
            return

        node = self._store.get_node(nid)
        schema_path = meta.get("schema_path", "")

        if node.type == NodeType.SCALAR:
            self._render_scalar_surface(nid, node, schema_path)
        elif node.type == NodeType.LIST:
            self._render_list_surface(nid, node, schema_path)
        elif node.type == NodeType.OBJECT:
            self._render_object_surface(nid, node, schema_path)

    def _render_scalar_surface(self, nid: UUID, node, schema_path: str) -> None:
        """Render single scalar value as model projection."""
        lines: list[str] = []
        bindings: list[ScalarBinding] = []
        line_spans: dict[str, tuple[int, int]] = {}

        key = node.key or "value"
        value = node.value if node.value is not None else ""

        node_id_str = str(nid)
        line = f"@@{node_id_str}:{key}: {value}"
        lines.append(line)

        bindings.append(
            ScalarBinding(
                node_id=nid,
                key=key,
                node_type="scalar",
                value=value,
                schema_path=schema_path,
            )
        )
        line_spans[node_id_str] = (0, 0)

        model_text = "\n".join(lines)
        title = f"{key}  (scalar)"
        docs = self._get_schema_docs(schema_path)

        self._right_panel.set_node_content(
            node_title=title,
            schema_path=schema_path,
            docs_md=docs,
            bindings=bindings,
            line_spans=line_spans,
            model_text=model_text,
        )

    def _render_list_surface(self, nid: UUID, node, schema_path: str) -> None:
        """Render LIST node as structured model projection."""
        lines: list[str] = []
        bindings: list[ScalarBinding] = []
        line_spans: dict[str, tuple[int, int]] = {}

        key = node.key or "list"
        lines.append(f"{key}:")

        for idx, child_id in enumerate(node.children):
            child_line_start = len(lines)
            self._append_child_lines(child_id, lines, bindings, line_spans, f"{schema_path}", indent=1, index=idx)
            child_line_end = len(lines) - 1
            # Store span for list item container if object
            child_node = self._store.get_node(child_id)
            if child_node.type == NodeType.OBJECT:
                line_spans[str(child_id)] = (child_line_start, child_line_end)

        model_text = "\n".join(lines)
        title = f"{key}  (list)"
        docs = self._get_schema_docs(schema_path)

        self._right_panel.set_node_content(
            node_title=title,
            schema_path=schema_path,
            docs_md=docs,
            bindings=bindings,
            line_spans=line_spans,
            model_text=model_text,
        )

    def _render_object_surface(self, nid: UUID, node, schema_path: str) -> None:
        """Render OBJECT node as structured model projection."""
        lines: list[str] = []
        bindings: list[ScalarBinding] = []
        line_spans: dict[str, tuple[int, int]] = {}

        key = node.key or "object"
        lines.append(f"{key}:")

        for child_id in node.children:
            child_line_start = len(lines)
            self._append_child_lines(child_id, lines, bindings, line_spans, schema_path, indent=1)
            child_line_end = len(lines) - 1
            line_spans[str(child_id)] = (child_line_start, child_line_end)

        model_text = "\n".join(lines)
        title = f"{key}  (object)"
        docs = self._get_schema_docs(schema_path)

        self._right_panel.set_node_content(
            node_title=title,
            schema_path=schema_path,
            docs_md=docs,
            bindings=bindings,
            line_spans=line_spans,
            model_text=model_text,
        )

    def _append_child_lines(
        self,
        child_id: UUID,
        lines: list[str],
        bindings: list[ScalarBinding],
        line_spans: dict[str, tuple[int, int]],
        parent_schema_path: str,
        indent: int = 0,
        index: int | None = None,
    ) -> None:
        """Recursively append lines for child nodes."""
        pad = "  " * indent
        child_node = self._store.get_node(child_id)
        node_id_str = str(child_id)

        child_schema_path = f"{parent_schema_path}.{child_node.key}" if child_node.key else parent_schema_path

        if child_node.type == NodeType.SCALAR:
            key = child_node.key or "value"
            value = child_node.value if child_node.value is not None else ""

            prefix = f"{pad}- " if index is not None else f"{pad}"
            line = f"@@{node_id_str}:{prefix}{key}: {value}"
            line_number = len(lines)
            lines.append(line)

            bindings.append(
                ScalarBinding(
                    node_id=child_id,
                    key=key,
                    node_type="scalar",
                    value=value,
                    schema_path=child_schema_path,
                )
            )
            line_spans[node_id_str] = (line_number, line_number)

        elif child_node.type == NodeType.LIST:
            key = child_node.key or "list"
            prefix = f"{pad}- " if index is not None else f"{pad}"
            lines.append(f"{prefix}{key}:")

            for idx, grandchild_id in enumerate(child_node.children):
                grandchild_start = len(lines)
                self._append_child_lines(grandchild_id, lines, bindings, line_spans, child_schema_path, indent + 1, idx)
                grandchild_end = len(lines) - 1
                grandchild_node = self._store.get_node(grandchild_id)
                if grandchild_node.type == NodeType.OBJECT:
                    line_spans[str(grandchild_id)] = (grandchild_start, grandchild_end)

        elif child_node.type == NodeType.OBJECT:
            key = child_node.key or "object"
            prefix = f"{pad}- " if index is not None else f"{pad}"
            object_line_start = len(lines)
            lines.append(f"{prefix}{key}:")

            for grandchild_id in child_node.children:
                self._append_child_lines(grandchild_id, lines, bindings, line_spans, child_schema_path, indent + 1)

            object_line_end = len(lines) - 1
            line_spans[node_id_str] = (object_line_start, object_line_end)

    def _render_schema_surface(self, key: str, schema) -> None:
        """Render schema info when no IR document is loaded."""
        props = schema.root.get("properties", {})
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

        model_text = "\n".join(lines)
        self._right_panel.set_node_content(
            node_title=f"{key}  (schema)",
            schema_path=key,
            docs_md="",
            bindings=[],
            line_spans={},
            model_text=model_text,
        )

    def _get_schema_docs(self, schema_path: str) -> str:
        """Placeholder for schema doc resolution."""
        return ""
