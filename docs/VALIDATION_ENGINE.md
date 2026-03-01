# ZENO -- Validation Engine Specification

## 1. Purpose

This document defines the validation architecture of Zeno.

Zeno uses live validation to enforce correctness while preserving a
clean separation between:

-   Structural integrity
-   Configuration integrity

Validation is deterministic and explicit.

------------------------------------------------------------------------

## 2. Validation Philosophy

> Make it hard for the user to make a mistake.

Validation is not optional. Validation is not cosmetic. Validation is
not advisory.

Validation blocks invalid state transitions.

------------------------------------------------------------------------

## 3. Single-Phase Validation Model

Zeno validates all edits before committing to IR.

There is no Generate phase. There is no separate second validation pass.

All validation now occurs before IR mutation.

IR must never contain invalid state.

------------------------------------------------------------------------

## 4. Live Validation

Triggered by: Model tab → per-keystroke edit

### 4.1 Purpose

Ensure IR always contains only valid state.

### 4.2 What Is Validated

-   Structural correctness
-   Required field presence
-   Field type correctness
-   Array `unique_by` constraints
-   Schema-defined restrictions

### 4.3 What Is NOT Validated

-   (Future extension placeholder)

### 4.4 Behavior on Failure

-   Input remains in buffer
-   IR is NOT updated
-   Inline floating hint displays error
-   Save is disabled
-   No popup dialogs

------------------------------------------------------------------------

## 5. Uniqueness Enforcement

Schema may declare:

``` yaml
type: array
unique_by: field_name
```

Rules:

-   Applies only to arrays
-   Applies within array scope
-   Enforced before IR commit
-   Single-field uniqueness only
-   Duplicate values block commit

Example error:

    Duplicate value detected.
    listeners[1].port = 502
    Port is already used by listeners[0].

------------------------------------------------------------------------

## 6. Error Object Model

Validators return structured errors.

Minimum fields:

    path: listeners[1].port
    message: Duplicate value 502
    severity: error

UI consumes these errors to:

-   Highlight tree nodes
-   Highlight model lines
-   Show inline floating hint
-   Update status line
-   Disable Save

Validation engine must never manipulate UI directly.

------------------------------------------------------------------------

## 7. Strict Mode

Schema grammar is strict.

-   Unknown schema keywords → validation error
-   Invalid node types → error
-   Invalid nesting → error

Strict grammar reduces ambiguity and mistake surface.

------------------------------------------------------------------------

## 8. Mutation Boundary

All validation occurs before IR mutation.

This ensures:

-   Internal state remains consistent
-   User workflow remains deterministic
-   IR is always valid

------------------------------------------------------------------------

## 9. Design Evolution Notes

Initial design:
- Structural validation only

Evolved design (v2):
- Strict schema grammar
- Array-local `unique_by`
- Two-phase validation model (Write/Generate)
- Explicit mutation vs projection boundary

Current design (v3):
- Single-phase live validation
- Valid-only IR guarantee
- Removed Generate phase
- Save gating on validation errors


Validation engine is central to Zeno's safety model.
