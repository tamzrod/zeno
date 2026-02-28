# ZENO -- Schema Specification

## 1. Purpose

This document defines the schema language used by Zeno (`.zs` files).

The schema describes: - Allowed structure - Allowed nesting - Array
uniqueness constraints - Intent documentation

The schema does NOT: - Perform runtime export - Execute logic -
Implicitly fix errors

Its purpose is structural authority.

------------------------------------------------------------------------

## 2. Schema File Format

-   Extension: `.zs`
-   Transport: YAML
-   Root must contain:

``` yaml
zeno_schema: <version>
application: <name>
format: <mode>
root:
  type: object
  properties: ...
```

Required top-level keys: - `zeno_schema` - `application` - `format` -
`root`

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
```

Rules: - `properties` must be a mapping. - Each property value must
itself be a schema node. - Only defined properties are allowed. -
Unknown keys in config are rejected.

------------------------------------------------------------------------

## 5. Array Nodes

``` yaml
type: array
items:
  type: ...
```

Rules: - `items` is required. - `items` must be a schema node. - Array
structure is validated per item.

------------------------------------------------------------------------

## 6. Primitive Nodes

Primitive types: - string - integer - number - boolean

Rules: - Cannot define `properties` - Cannot define `items`

------------------------------------------------------------------------

## 7. Uniqueness Constraint (`unique_by`)

Zeno supports controlled uniqueness enforcement on arrays.

``` yaml
type: array
unique_by: field_name
items:
  type: object
  properties:
    field_name:
      type: integer
```

Rules:

-   `unique_by` allowed only on `type: array`
-   Value must be a single field name (string)
-   Field must exist in `items.properties`
-   Uniqueness applies only within that array scope
-   Enforced during Write phase validation

Example:

``` yaml
listeners:
  type: array
  unique_by: port
```

This prevents duplicate `port` values inside `listeners`.

Composite uniqueness is NOT supported at this stage.

------------------------------------------------------------------------

## 8. Strict Grammar

Schema is strict.

-   Unknown schema keywords → error
-   Undefined node types → error
-   Invalid nesting → error

Schema must be deterministic and explicit.

------------------------------------------------------------------------

## 9. Behavioral Documentation via Comments

Export mappings and semantic notes must be documented in comments only.

Example:

``` yaml
port:
  type: integer
  # Exported as listen: ":<port>"
```

Machine-readable schema must not imply behavior that engine does not
enforce.

------------------------------------------------------------------------

## 10. Domain-Specific Notes (MMA Example)

-   `state_sealing`:
    -   Absence of declaration means state sealing is disabled.
-   `unique_by` is used for:
    -   listeners.port
    -   memory.unit_id (per listener)

------------------------------------------------------------------------

## 11. Design Evolution Notes

Initial design: - Structural validation only - Permissive unknown
keywords

Evolved design: - Strict schema grammar - `unique_by` enforcement -
Array-local uniqueness - Explicit separation of structural and semantic
validation

Schema remains declarative and authoritative.
