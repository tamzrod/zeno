# ZENO -- Configuration Editing Behavior

Version: 2.1
Status: ALIGNED WITH DOCUMENT-CENTRIC ARCHITECTURE

------------------------------------------------------------------------

## Scope

This document defines the deterministic configuration editing behavior in ZENO.

ZENO is document-centric.

There are no manual modes.

Editing behavior is derived strictly from:
- Active Schema
- Active Document

------------------------------------------------------------------------

## Core Principles

1. IRStore is the single source of truth.
2. Schema defines structure, not runtime behavior.
3. No hardcoded UI rules.
4. All editing capabilities derive from schema definition.
5. No partial generation.
6. No implicit node creation.
7. Deterministic structure only.

------------------------------------------------------------------------

## Schema → IR Expansion Rules

When creating a new configuration from a loaded schema:

- Root is OBJECT.
- For each schema property:
  - type: object → create OBJECT node.
  - type: array → create LIST node (empty).
  - scalar types (string, integer, number, boolean) → create SCALAR node with value = null.
- Arrays do not auto-create items.
- Expansion is recursive for objects only.
- No schema-defined property may be skipped.
- No implicit defaults unless explicitly defined in schema metadata.

------------------------------------------------------------------------

## Context Menu Behavior (Schema-Driven)

### OBJECT Node

Allowed actions:
- Add child property defined in schema.
- Remove node (except root).

Rules:
- No duplicate object keys.
- Only properties defined in schema are allowed.
- No arbitrary fields.
- Removal must unlink before deletion.

### LIST Node

Allowed actions:
- Add list item (type derived from schema.items.type).
- Remove item.
- Move item up.
- Move item down.

Rules:
- LIST items do not have object keys.
- Order is significant and preserved.
- Reordering changes priority intentionally.
- No implicit sorting.

### SCALAR Node

Allowed actions:
- Edit value only.

Rules:
- Type enforcement based on schema.
- No children allowed.
- No implicit coercion beyond schema-declared type.

------------------------------------------------------------------------

## Write Lifecycle Boundary (ABSOLUTE)

Edits occur in the editor workspace and are staged until Write is pressed.

Rules:
- Editing does not mutate IR immediately.
- Write is the only operation that mutates IR.
- On Write failure, IR remains unchanged.

------------------------------------------------------------------------

## Schema Linkage Requirement

Each IR node must be resolvable to its schema definition.

This may be achieved by:
- Attaching schema reference metadata during expansion, OR
- Resolving schema path dynamically based on IR path.

UI must never guess allowed structure.

All structural decisions must be schema-derived.

------------------------------------------------------------------------

## Determinism Guarantees

- Tree rendering reflects IR structure exactly.
- All operations go through OperationProcessor.
- No direct mutation of IR nodes from UI.
- Root cannot be deleted.
- Arrays never auto-expand.
- No structural mutation occurs outside Write lifecycle.

------------------------------------------------------------------------

## Out of Scope

- Validation beyond structural integrity (handled by Validation Engine).
- Runtime export behavior.
- Wizard-specific flow logic.
- Theming or styling rules.
- Schema authoring mechanics (covered elsewhere).

------------------------------------------------------------------------

## Alignment Statement

This document is aligned with:
- Architecture Lock
- Operation Model v2.1
- UI Architecture v2.4
- Schema Specification
- Validation Engine Specification

ZENO editing behavior is schema-driven, deterministic, and mode-free.

------------------------------------------------------------------------

Generated on: 2026-02-28T11:53:23Z
End of Document.
