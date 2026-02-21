# ZENO -- Validation Engine Specification

## 1. Purpose

This document defines the validation architecture of Zeno.

Zeno uses layered validation to enforce correctness while preserving a
clean separation between:

-   Structural integrity
-   Configuration integrity
-   Runtime correctness

Validation is deterministic and explicit.

------------------------------------------------------------------------

## 2. Validation Philosophy

> Make it hard for the user to make a mistake.

Validation is not optional. Validation is not cosmetic. Validation is
not advisory.

Validation blocks invalid state transitions.

------------------------------------------------------------------------

## 3. Two-Phase Validation Model

Zeno uses two validation phases:

1.  Write Phase Validation
2.  Generate Phase Validation

Each phase protects a different boundary.

------------------------------------------------------------------------

## 4. Write Phase Validation

Triggered by: Modify Tab → Write button

### 4.1 Purpose

Protect internal IR integrity.

Prevent invalid configuration state from being stored.

### 4.2 What Is Validated

-   Structural correctness
-   Required field presence
-   Field type correctness
-   Array `unique_by` constraints
-   Schema-defined restrictions

### 4.3 What Is NOT Validated

-   Runtime export constraints
-   Cross-field semantic logic (unless schema declares it)
-   Deployment environment checks

### 4.4 Behavior on Failure

-   IR is NOT updated
-   Errors are attached to node paths
-   Tree nodes are highlighted
-   Status line displays error summary
-   No popup dialogs

------------------------------------------------------------------------

## 5. Generate Phase Validation

Triggered by: Preview Tab → Generate button

### 5.1 Purpose

Protect runtime export correctness.

Prevent invalid configuration from being generated.

### 5.2 What Is Validated

-   Structural correctness (re-check)
-   Semantic rules
-   Cross-field constraints
-   Domain-specific rules
-   Runtime export constraints

### 5.3 Behavior on Failure

-   Preview is NOT updated
-   Errors are highlighted
-   Status line displays summary
-   Previous valid preview remains intact

------------------------------------------------------------------------

## 6. Uniqueness Enforcement

Schema may declare:

``` yaml
type: array
unique_by: field_name
```

Rules:

-   Applies only to arrays
-   Applies within array scope
-   Enforced during Write phase
-   Single-field uniqueness only
-   Duplicate values block Write operation

Example error:

    Duplicate value detected.
    listeners[1].port = 502
    Port is already used by listeners[0].

------------------------------------------------------------------------

## 7. Error Object Model

Validators return structured errors.

Minimum fields:

    path: listeners[1].port
    message: Duplicate value 502
    phase: write | generate
    severity: error

UI consumes these errors to:

-   Highlight tree nodes
-   Highlight fields
-   Update status line

Validation engine must never manipulate UI directly.

------------------------------------------------------------------------

## 8. Strict Mode

Schema grammar is strict.

-   Unknown schema keywords → validation error
-   Invalid node types → error
-   Invalid nesting → error

Strict grammar reduces ambiguity and mistake surface.

------------------------------------------------------------------------

## 9. Mutation vs Projection Separation

Write Phase protects mutation.

Generate Phase protects projection.

This separation ensures:

-   Internal state remains consistent
-   Runtime export is safe
-   User workflow remains deterministic

------------------------------------------------------------------------

## 10. Design Evolution Notes

Initial design: - Structural validation only

Evolved design: - Strict schema grammar - Array-local `unique_by` -
Two-phase validation model - Explicit mutation vs projection boundary -
Highlight-based error reporting (no popups)

Validation engine is central to Zeno's safety model.
