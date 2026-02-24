# CONFIG_MODE_BEHAVIOR.md

## Scope

This document defines the behavior of **Config Mode** in Zeno.

Config Mode is responsible for deterministic configuration editing based
strictly on schema design.

Schema Mode is out of scope.

------------------------------------------------------------------------

## Core Principles

1.  IRStore is the single source of truth.
2.  Schema defines structure, not runtime behavior.
3.  No hardcoded UI rules.
4.  All editing capabilities derive from schema definition.
5.  No partial generation.
6.  No implicit node creation.
7.  Deterministic structure only.

------------------------------------------------------------------------

## Schema → IR Expansion Rules

When creating a new configuration:

-   Root is OBJECT.
-   For each schema property:
    -   type: object → create OBJECT node.
    -   type: array → create LIST node (empty).
    -   scalar types (string, integer, boolean, etc.) → create SCALAR
        node with value=None.
-   Arrays do not auto-create items.
-   Expansion is recursive for objects only.

------------------------------------------------------------------------

## Context Menu Behavior (Schema-Driven)

### OBJECT Node

Allowed actions: - Add child property defined in schema. - Remove node
(except root).

Rules: - No duplicate object keys. - Only properties defined in schema
are allowed. - No arbitrary fields.

### LIST Node

Allowed actions: - Add list item (type derived from
schema.items.type). - Remove item. - Move item up. - Move item down.

Rules: - LIST items do not have object keys. - Order is significant and
preserved. - Reordering changes priority.

### SCALAR Node

Allowed actions: - Edit value only.

Rules: - Type enforcement based on schema. - No children allowed.

------------------------------------------------------------------------

## Schema Linkage Requirement

Each IR node must be resolvable to its schema definition.

This can be achieved by: - Attaching schema reference metadata during
expansion, or - Resolving schema path dynamically based on IR path.

UI must never guess allowed structure.

------------------------------------------------------------------------

## Determinism Guarantees

-   Tree rendering reflects IR structure exactly.
-   All operations go through OperationProcessor.
-   No direct mutation of IR nodes from UI.
-   Removal must unlink before deletion.
-   Root cannot be deleted.

------------------------------------------------------------------------

## Out of Scope

-   Validation expansion beyond structural integrity.
-   Excel import/export.
-   Schema editing.
-   Conditional formatting.
-   Styling rules.

------------------------------------------------------------------------

End of document.
