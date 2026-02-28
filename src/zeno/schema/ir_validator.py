# src/zeno/schema/ir_validator.py

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, List, Tuple
from uuid import UUID

from zeno.core.node import Node
from zeno.core.types import NodeType
from zeno.core.store import IRStore


# ============================================================
# Protocol for tree traversal
# ============================================================

class IRNodeView(ABC):
    """Abstract protocol for reading IR nodes."""

    @abstractmethod
    def node_type(self) -> str:
        """Return: 'object', 'list', or 'scalar'"""
        pass

    @abstractmethod
    def scalar_value(self) -> Any:
        """Return scalar value"""
        pass

    @abstractmethod
    def object_items(self) -> Iterable[Tuple[str, IRNodeView]]:
        """Return: (key, child_view) pairs"""
        pass

    @abstractmethod
    def list_items(self) -> Iterable[IRNodeView]:
        """Return: child views"""
        pass


# ============================================================
# Adapter: IRStore + Node → IRNodeView
# ============================================================

class IRStoreView(IRNodeView):
    """Bridge IRStore + Node tree to protocol."""

    def __init__(self, store: IRStore, node_id: UUID) -> None:
        self._store = store
        self._node_id = node_id

    def node_type(self) -> str:
        node = self._store.get_node(self._node_id)
        if node.type == NodeType.OBJECT:
            return "object"
        if node.type == NodeType.LIST:
            return "list"
        return "scalar"

    def scalar_value(self) -> Any:
        node = self._store.get_node(self._node_id)
        return node.value

    def object_items(self) -> Iterable[Tuple[str, IRNodeView]]:
        node = self._store.get_node(self._node_id)
        for child_id in node.children:
            child = self._store.get_node(child_id)
            yield child.key or "", IRStoreView(self._store, child_id)

    def list_items(self) -> Iterable[IRNodeView]:
        node = self._store.get_node(self._node_id)
        for child_id in node.children:
            yield IRStoreView(self._store, child_id)


# ============================================================
# Error Types
# ============================================================

@dataclass(frozen=True, slots=True)
class ValidationIssue:
    path: str
    message: str


class ValidationError(Exception):
    def __init__(self, issues: List[ValidationIssue]) -> None:
        self.issues = issues
        super().__init__("\n".join(f"{i.path}: {i.message}" for i in issues))


# ============================================================
# Validation Entry
# ============================================================

def validate(root_view: IRNodeView) -> None:
    """Validate an IR node tree structure."""
    issues: List[ValidationIssue] = []
    _validate_node(root_view, path="$", issues=issues)
    if issues:
        raise ValidationError(issues)


# ============================================================
# Recursive Validator
# ============================================================

def _validate_node(view: IRNodeView, *, path: str, issues: List[ValidationIssue]) -> None:
    t = view.node_type()

    if t == "scalar":
        return

    if t == "object":
        _validate_object(view, path=path, issues=issues)
        return

    if t == "list":
        _validate_list(view, path=path, issues=issues)
        return

    issues.append(ValidationIssue(path, f"Unknown node type: {t}"))


def _validate_object(view: IRNodeView, *, path: str, issues: List[ValidationIssue]) -> None:
    seen_keys = set()

    for key, child_view in view.object_items():
        if key in seen_keys:
            issues.append(ValidationIssue(f"{path}.{key}", f"Duplicate key: {key}"))
        seen_keys.add(key)

        _validate_node(child_view, path=f"{path}.{key}", issues=issues)


def _validate_list(view: IRNodeView, *, path: str, issues: List[ValidationIssue]) -> None:
    for idx, child_view in enumerate(view.list_items()):
        _validate_node(child_view, path=f"{path}[{idx}]", issues=issues)
