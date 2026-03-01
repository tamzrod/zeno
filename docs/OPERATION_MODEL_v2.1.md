# ZENO -- Operation Model Specification

Version: 3.0
Status: ALIGNED WITH ARCHITECTURE LOCK (Simplified Lifecycle)

------------------------------------------------------------------------

## 1. Purpose

This document defines the operational lifecycle of ZENO.

ZENO now uses a single-phase deterministic lifecycle.

There is no Generate phase. There is no Preview tab. There is no Export.

Save writes IR directly to disk via adapter serialization, and is allowed only when:
  - No validation errors exist
  - No invalid buffers exist

------------------------------------------------------------------------

## 2. Core Operational Principle

> IR must never contain invalid state.

All edits are validated live.

Invalid input remains in buffer without committing to IR.

Save is direct serialization.

------------------------------------------------------------------------

## 3. Operational States

ZENO operates through explicit document states:

1. No Schema Loaded
2. Schema Loaded
3. Document Loaded

There is no "Dirty" state in the old sense. Invalid buffers block Save.

------------------------------------------------------------------------

## 4. Lifecycle Flow

### 4.1 Load Schema

Action: File → Load Schema...

Result:
- Schema validated structurally
- Active Schema updated
- Active Document cleared
- Undo history cleared
- Title updated

Failure:
- Schema rejected
- Status line displays error
- Previous state preserved

There is NO Unload Schema operation.

------------------------------------------------------------------------

### 4.2 New Config

Precondition:
- Schema must be loaded

Result:
- Deterministic config created via schema expansion rules
- Arrays empty
- Scalars null
- Title updated

------------------------------------------------------------------------

### 4.3 Open Config

Precondition:
- Schema must be loaded

Result:
- Config parsed into IR via adapter
- Structural validation performed
- Errors highlighted if present

Failure:
- Config rejected
- No partial state retained

------------------------------------------------------------------------

### 4.4 Live Edit

User modifies scalar values in Model projection surface.

Validation:
- Per-keystroke type checking
- Structural correctness
- Required fields
- Type correctness
- `unique_by` constraints

Success:
- IR updated immediately

Failure:
- Input remains in buffer
- Inline floating hint shown
- IR unchanged

IR contains only valid state.

------------------------------------------------------------------------

### 4.5 Save / Save As

Action: File → Save (or Save As)

Precondition:
- No validation errors
- No invalid buffers

Result:
- IR serialized directly via adapter
- Written to disk

Disabled when:
- Any buffer contains invalid input
- Any validation error exists

------------------------------------------------------------------------

## 5. Undo / Redo Model

Not yet defined in single-phase lifecycle. Placeholder for future spec.

------------------------------------------------------------------------

## 6. Error Handling Across Lifecycle

Errors include:
- Type mismatch
- Uniqueness violations
- Semantic rule violations

Error handling rules:
- No popup validation dialogs
- Highlight affected nodes
- Display inline floating hint
- Block Save transition

Validation engine produces structured error objects. UI consumes them.

------------------------------------------------------------------------

## 7. Document-Centric Guarantees

- Active Schema defines editing universe
- Active Document conforms to Active Schema
- No implicit schema switching
- No overlapping operational states
- No direct IR mutation from UI
- All mutations go through OperationProcessor

------------------------------------------------------------------------

Generated on: 2026-03-01T00:00:00Z
End of Document.

