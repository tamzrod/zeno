# src/zeno/schema/loader.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


class SchemaError(Exception):
    """Base class for schema loader errors."""


class SchemaLoadError(SchemaError):
    """Raised when a schema file cannot be read or parsed."""


class SchemaValidationError(SchemaError):
    """Raised when a schema file is syntactically valid YAML but structurally invalid."""


@dataclass(frozen=True, slots=True)
class SchemaHeader:
    zeno_schema: str
    application: str
    format: str


@dataclass(frozen=True, slots=True)
class Schema:
    header: SchemaHeader
    root: Mapping[str, Any]
    raw: Mapping[str, Any]
    source_path: str


def load(path: str | Path) -> Schema:
    """
    Load a .zs schema file (YAML transport), perform minimal structural validation,
    and return a structured Schema object.

    Phase 1 scope:
      - Parse YAML safely
      - Validate presence of: zeno_schema, application, format, root
      - No recursive validation
      - No cross-field validation
      - No UI binding
    """
    p = Path(path)

    _require_file_exists(p)
    _require_zs_extension(p)

    text = _read_text(p)
    data = _parse_yaml(text, source_path=str(p))

    header = _extract_header(data)
    root = _extract_root(data)

    return Schema(
        header=header,
        root=root,
        raw=data,
        source_path=str(p),
    )


def _require_file_exists(p: Path) -> None:
    if not p.exists():
        raise SchemaLoadError(f"Schema file not found: {p}")
    if not p.is_file():
        raise SchemaLoadError(f"Schema path is not a file: {p}")


def _require_zs_extension(p: Path) -> None:
    # Locked strategy: schema extension is .zs (YAML transport).
    if p.suffix.lower() != ".zs":
        raise SchemaLoadError(f"Invalid schema extension (expected .zs): {p.name}")


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError as e:
        raise SchemaLoadError(f"Failed to read schema file: {p} ({e})") from e


def _parse_yaml(text: str, *, source_path: str) -> Mapping[str, Any]:
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise SchemaLoadError(f"YAML parse error in schema: {source_path} ({e})") from e

    if parsed is None:
        raise SchemaValidationError(f"Schema is empty: {source_path}")

    if not isinstance(parsed, dict):
        raise SchemaValidationError(
            f"Schema root must be a mapping/object: {source_path} (got {type(parsed).__name__})"
        )

    # Treat as read-only mapping from here.
    return parsed


def _extract_header(data: Mapping[str, Any]) -> SchemaHeader:
    zeno_schema = _require_str_field(data, "zeno_schema")
    application = _require_str_field(data, "application")
    fmt = _require_str_field(data, "format")

    return SchemaHeader(
        zeno_schema=zeno_schema,
        application=application,
        format=fmt,
    )


def _extract_root(data: Mapping[str, Any]) -> Mapping[str, Any]:
    if "root" not in data:
        raise SchemaValidationError("Missing required top-level field: root")

    root = data["root"]
    if not isinstance(root, dict):
        raise SchemaValidationError(f"Field 'root' must be a mapping/object (got {type(root).__name__})")

    return root


def _require_str_field(data: Mapping[str, Any], key: str) -> str:
    if key not in data:
        raise SchemaValidationError(f"Missing required top-level field: {key}")

    value = data[key]
    if not isinstance(value, str) or value.strip() == "":
        raise SchemaValidationError(f"Field '{key}' must be a non-empty string")

    return value.strip()