# ZENO – Error Model Specification

Status: Single-Phase Validation

---

## 1. Purpose

This document defines how errors are represented, categorized, propagated, and displayed in ZENO.

Errors must be:
- Deterministic
- Structured
- Machine-readable
- UI-agnostic

The validation engine produces errors. The UI consumes errors.

---

## 2. Single Validation Phase

All validation occurs before IR mutation.

IR must never contain invalid state.

ZENO has one validation phase only:

```text
Live field edit -> Validate -> Valid: commit to IR / Invalid: hold in buffer
```

There is no Generate phase.
There is no Preview phase.
There is no Write vs Generate lifecycle distinction.

---

## 3. Core Rules

1. Validators never manipulate UI.
2. Errors are data, not side effects.
3. Errors include precise node location.
4. Validation errors persist until corrected.
5. Invalid input never mutates IR.
6. Save is blocked when any validation error exists.

---

## 4. Error Object Structure

All errors use a structured format.

Minimum required fields:

```json
{
  "path": "listeners[1].port",
  "message": "Duplicate value 502. Port already used by listeners[0].",
  "category": "field_validation",
  "severity": "error"
}
```

Field contract:
- `path` (string): Node path in IR
- `message` (string): Human-readable description
- `category` (string): Error category
- `severity` (string): `error` (blocking), `warning` (optional/future)

Optional fields:
- `code` (string)
- `details` (string)
- `context` (object)

---

## 5. Error Categories

Allowed category structure:

1. Structural validation errors
2. Schema rule violations
3. Field-level validation errors
4. Persistence errors (optional)

No category is phase-based.

### 5.1 Structural Validation Errors

Definition:
Errors where edited content violates schema-defined structure.

Examples:
- Missing required field
- Invalid nesting shape
- Invalid object/array structure

Category value:
`structural`

### 5.2 Schema Rule Violations

Definition:
Errors where a value violates schema constraints.

Examples:
- Type mismatch
- Enum mismatch
- Range constraint failure
- Pattern constraint failure

Category value:
`schema_rule`

### 5.3 Field-Level Validation Errors

Definition:
Errors detected during per-keystroke field validation.

Examples:
- Required value currently empty
- Invalid field format
- Field-level uniqueness conflict

Category value:
`field_validation`

### 5.4 Persistence Errors (Optional)

Definition:
Errors during file write operations after validation has passed.

Examples:
- Permission denied
- Path unavailable
- Disk write failure

Category value:
`persistence`

Persistence errors are not Generate-related and do not introduce a new validation phase.

---

## 6. Error Timing

Errors occur during live field validation.

Timing sequence:
1. User edits field.
2. Validation executes immediately.
3. If invalid, error object is emitted and IR is unchanged.
4. If valid, IR updates for that field.

Save behavior:
- Save is blocked if any validation error exists.
- Save checks existing error state; it does not create a second validation phase.
- There is no separate post-validation export error stage.

---

## 7. Explicit Exclusions

There is no Generate-phase error category.
There is no Preview-phase error category.

There is no two-phase error model.

---

## 8. Path Representation

Paths uniquely identify one node in IR.

Examples:
`listeners[1].port`
`memory[0].policy.rules[2].allow_fc`

Rules:
- Array indices are explicit.
- Nested properties use dot notation.
- Path must resolve to exactly one node.

---

## 9. Propagation Model

Flow:

```text
Validator -> Error objects -> UI renderer -> Highlights + status + save gating
```

The validator never directly controls UI widgets.

---

## 10. Multiple Error Handling

If multiple errors exist:
- All errors are retained.
- All impacted nodes are highlighted.
- Save remains disabled until all blocking validation errors are resolved.

---

## 11. Severity

Current blocking level:
- `error`

Optional future advisory level:
- `warning`

Warnings do not mutate IR and do not redefine lifecycle behavior.

---

## 12. Deterministic Guarantee

The error model preserves deterministic behavior:
- Same invalid input produces the same error category and location.
- No hidden phase transitions.
- No hidden transformation layers.
- No invalid IR state.

This supports the core philosophy:

Make it hard for the user to commit a mistake.

---

Generated: 2026-03-01
End of Document.
