# ZENO -- Schema Specification

Version: 2.1\
Status: UPDATED (Implements required / min_items / max_items)

------------------------------------------------------------------------

## 1. Purpose

This document defines the schema language used by ZENO (`.zs` files).

The schema describes:

-   Allowed structure
-   Allowed nesting
-   Array uniqueness constraints
-   Structural cardinality constraints
-   Intent documentation

The schema does NOT:

-   Perform runtime export
-   Execute logic
-   Implicitly fix errors

Its purpose is structural authority.

------------------------------------------------------------------------

## 2. Schema File Format

Extension: `.zs`\
Transport: YAML

Root must contain:

``` yaml
zeno_schema: <version>
application: <name>
format: <mode>
root:
  type: object
  properties: ...
```

Required top-level keys:

-   `zeno_schema`
-   `application`
-   `format`
-   `root`

------------------------------------------------------------------------

## 3. Node Types

Every schema node MUST define:

``` yaml
type: <node_type>
```

Allowed types:

-   `object`
-   `array`
-   `string`
-   `integer`
-   `number`
-   `boolean`

Unknown types are rejected.

------------------------------------------------------------------------

## 4. Object Nodes

``` yaml
type: object
properties:
  key_name:
    type: ...
    required: true | false
```

Rules:

-   `properties` must be a mapping.
-   Each property must itself be a schema node.
-   Only defined properties are allowed.
-   Unknown keys in config are rejected.
-   `required` (optional):
    -   Default: false
    -   If true → property must exist.
    -   UI must disable removal of required properties.
    -   Write-phase validation blocks missing required properties.

------------------------------------------------------------------------

## 5. Array Nodes

``` yaml
type: array
min_items: <integer>
max_items: <integer>
unique_by: <field_name>
items:
  type: ...
```

Rules:

-   `items` is required.
-   `min_items` (optional):
    -   Default: 0
    -   Removal disabled if current_count == min_items
-   `max_items` (optional):
    -   If defined → Add disabled when current_count == max_items
-   `unique_by` allowed only on arrays
-   `unique_by` enforced during Write phase
-   Uniqueness applies only within that array scope

Example:

``` yaml
listeners:
  type: array
  unique_by: port
  min_items: 1
```

------------------------------------------------------------------------

## 6. Primitive Nodes

Primitive types:

-   string
-   integer
-   number
-   boolean

Rules:

-   Cannot define `properties`
-   Cannot define `items`
-   Cannot define `min_items` or `max_items`

------------------------------------------------------------------------

## 7. Structural Cardinality Enforcement

### Object Properties

If `required: true`: - Property must exist. - UI removal must be
disabled. - Write-phase validation blocks deletion.

If `required: false` or omitted: - Property may be removed. - Absence is
valid.

### Arrays

If `min_items` defined: - Removal disabled when item_count == min_items.

If `max_items` defined: - Add disabled when item_count == max_items.

If neither defined: - Array unconstrained structurally.

------------------------------------------------------------------------

## 8. Tree Behavior Contract (Structural Layer)

Tree operations must derive strictly from schema:

OBJECT: - Add → Only missing schema-defined properties. - Remove →
Disabled if `required: true`. - No duplicate keys.

ARRAY: - Add → Disabled if `max_items` reached. - Remove → Disabled if
`min_items` boundary reached. - Reorder allowed unless domain rule
prevents.

SCALAR: - Edit value only. - No structural mutation.

------------------------------------------------------------------------

## 9. MMA Example (Applied)

### Required Memory Per Port

``` yaml
memory:
  type: array
  min_items: 1
```

Prevents port without memory blocks.

### Optional State Sealing

``` yaml
state_sealing:
  type: object
  required: false
```

If absent → state sealing disabled.

------------------------------------------------------------------------

## 10. Strict Grammar

Unknown schema keywords → error.\
Invalid nesting → error.\
Invalid cardinality definitions → error.

Schema remains deterministic and explicit.

------------------------------------------------------------------------

## 11. Alignment Statement

This update aligns with:

-   Architecture Lock
-   Operation Model v2.1
-   UI Architecture v2.4
-   Validation Engine Specification

ZENO remains schema-driven and document-centric.

------------------------------------------------------------------------

Generated on: 2026-02-28T08:52:38.073901 UTC
