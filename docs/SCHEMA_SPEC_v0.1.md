# ZENO --- Schema Specification Document

Version: v0.1 (Architecture Lock)

------------------------------------------------------------------------

# 1. Purpose

This document defines the declarative YAML format used to author schemas
in Zeno.

A Schema describes:

-   Structure rules
-   Node types
-   Cardinality rules
-   Scalar constraints
-   Validation behavior
-   Editor behavior hints

Schemas are written in YAML.

Schemas are edited through Zeno using IR.

------------------------------------------------------------------------

# 2. Core Principle

Schema defines rules.

IR stores structure.

Validation Engine applies schema rules to IR.

Schema contains no executable Python logic.

------------------------------------------------------------------------

# 3. Schema File Structure

Every schema YAML must contain:

-   `id` (unique schema identifier)
-   `name` (human-readable name)
-   `version`
-   `root` (root node definition)
-   `definitions` (reusable node definitions)

------------------------------------------------------------------------

# 4. Root Definition

Example:

``` yaml
id: mma_schema
name: MMA Config Schema
version: 1.0
root:
  type: object
  properties:
    notify:
      $ref: notify_block
definitions:
  notify_block:
    type: object
    properties:
      holding_registers:
        type: list
        items:
          $ref: register_block
  register_block:
    type: object
    properties:
      start:
        type: scalar
        datatype: int
        min: 0
      count:
        type: scalar
        datatype: int
        min: 1
```

------------------------------------------------------------------------

# 5. Node Definition Types

Schema supports:

-   object
-   list
-   scalar

------------------------------------------------------------------------

# 6. Object Definition

Object nodes may define:

-   `properties` (named children)
-   `required` (list of required property names)
-   `additional_properties` (true \| false)

Example:

``` yaml
type: object
required: [port]
properties:
  port:
    type: scalar
    datatype: int
    min: 1
    max: 65535
```

------------------------------------------------------------------------

# 7. List Definition

List nodes may define:

-   `items` (node definition or \$ref)
-   `min_items`
-   `max_items`

Example:

``` yaml
type: list
min_items: 1
items:
  type: scalar
  datatype: string
```

------------------------------------------------------------------------

# 8. Scalar Definition

Scalar nodes must define:

-   `datatype`

Supported base datatypes:

-   string
-   int
-   float
-   bool
-   null

Optional constraints:

-   min
-   max
-   pattern (regex)
-   enum (list of allowed values)
-   format (named validator)

Example:

``` yaml
type: scalar
datatype: string
format: ipv4
```

------------------------------------------------------------------------

# 9. \$ref Mechanism

Definitions may reference reusable blocks via:

\$ref: definition_name

References must resolve within `definitions`.

No external file references in v0.1.

------------------------------------------------------------------------

# 10. Validation Model

Validation is applied in two layers:

1.  Structural validation (type, required, cardinality)
2.  Scalar validation (datatype, range, pattern, format)

Schema does not perform validation itself. Validation Engine interprets
schema rules.

------------------------------------------------------------------------

# 11. Editor Behavior Hints (Optional)

Schema may include non-validation hints:

-   description
-   default
-   ui_widget (future use)

These hints must not affect validation logic.

------------------------------------------------------------------------

# 12. Scope Boundary

Schema does NOT:

-   Contain executable code
-   Access filesystem
-   Modify IR directly
-   Contain UI implementation logic

Schema only declares rules.

------------------------------------------------------------------------

END OF SCHEMA_SPEC.md v0.1
