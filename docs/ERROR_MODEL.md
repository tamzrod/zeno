# ZENO -- Error Model Specification

## 1. Purpose

This document defines how errors are represented, propagated, and
displayed in Zeno.

Errors must be:

-   Deterministic
-   Structured
-   Machine-readable
-   UI-agnostic

The validation engine produces errors. The UI consumes errors.

Separation of concerns is mandatory.

------------------------------------------------------------------------

## 2. Core Principles

1.  Validators never manipulate UI.
2.  Errors are data, not side effects.
3.  Errors must include precise location information.
4.  No popup dialogs for validation errors.
5.  Errors persist until corrected.

------------------------------------------------------------------------

## 3. Error Object Structure

All validation errors must conform to a structured format.

Minimum required fields:

    path: string
    message: string
    phase: "write" | "generate"
    severity: "error"

Optional fields (future-safe):

    code: string
    details: string
    context: object

------------------------------------------------------------------------

## 4. Path Representation

Paths must uniquely identify a node inside IR.

Example:

    listeners[1].port
    memory[0].policy.rules[2].allow_fc

Rules:

-   Array indices must be explicit.
-   Nested properties separated by dot (`.`).
-   Path must always resolve to a single node.

Paths are consumed by UI to highlight exact node.

------------------------------------------------------------------------

## 5. Error Phases

### 5.1 Write Phase Errors

Triggered during: Modify → Write

Examples:

-   Structural violation
-   Missing required field
-   Invalid type
-   Duplicate value (`unique_by` violation)

Behavior:

-   Write blocked
-   IR unchanged
-   Node highlighted
-   Status updated

------------------------------------------------------------------------

### 5.2 Generate Phase Errors

Triggered during: Preview → Generate

Examples:

-   Cross-field violation
-   Runtime constraint failure
-   Export transformation error

Behavior:

-   Preview unchanged
-   Node highlighted
-   Status updated

------------------------------------------------------------------------

## 6. Uniqueness Error Example

If duplicate port detected:

    path: listeners[1].port
    message: Duplicate value 502. Port already used by listeners[0].
    phase: write
    severity: error

------------------------------------------------------------------------

## 7. Error Propagation Flow

    Validator
       ↓
    Error Objects (list)
       ↓
    UI Layer
       ↓
    Tree Highlight
    Field Highlight
    Status Line Update

No direct coupling between validator and UI.

------------------------------------------------------------------------

## 8. Status Line Behavior

Status line displays summary message.

Examples:

✔ Write successful\
❌ Duplicate port 502\
❌ 3 validation errors detected

Rules:

-   Single-line only
-   No scrolling log
-   Cleared on next successful operation

------------------------------------------------------------------------

## 9. Multiple Errors Handling

If multiple errors exist:

-   All errors stored internally
-   First error summarized in status line
-   All affected nodes highlighted
-   Optional future: expandable error panel

System must never stop at first error silently.

------------------------------------------------------------------------

## 10. Severity Levels

Currently supported:

-   error (blocking)

Future possibility:

-   warning (non-blocking)

Warnings must never silently auto-correct state.

------------------------------------------------------------------------

## 11. Design Evolution Notes

Initial concept: - Simple exception-based error handling

Evolved design: - Structured error objects - Phase-aware validation -
UI-agnostic error propagation - No popup dialogs - Highlight-based
visualization

The error model enforces deterministic and visible failure handling.

It supports the core philosophy:

Make it hard for the user to make a mistake.
