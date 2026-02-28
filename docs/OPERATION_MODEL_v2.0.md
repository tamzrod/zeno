# ZENO -- Operation Model Specification

Version: 2.0\
Status: ALIGNED WITH ARCHITECTURE LOCK

------------------------------------------------------------------------

## 1. Purpose

This document defines the operational lifecycle of ZENO.

ZENO separates configuration mutation from runtime projection.

This separation is intentional, explicit, and foundational.

ZENO is document-centric.

There are no manual modes.

UI state is defined only by:

-   Active Schema
-   Active Document (optional)

------------------------------------------------------------------------

## 2. Core Operational Principle

> Mutation and projection must never be implicit.

All state transitions must be explicit and user-triggered.

There is: - No background auto-generation - No implicit mutation - No
hidden state transitions

------------------------------------------------------------------------

## 3. Operational States

ZENO operates through explicit document states:

1.  No Schema Loaded
2.  Schema Loaded
3.  Document Loaded
4.  Editing (Dirty State)
5.  Written (Validated Internal State)
6.  Generated (Validated Runtime Projection)

Each transition requires explicit action.

There is no Schema Mode or Config Mode.

------------------------------------------------------------------------

## 4. Lifecycle Flow

### 4.1 Load Schema

Action: File → Load Schema...

Result: - Schema validated structurally - Active Schema updated - Active
Document cleared - Undo history cleared - Preview cleared - Dirty
reset - Title updated

Failure: - Schema rejected - Status line displays error - Previous state
preserved

There is NO Unload Schema operation.

------------------------------------------------------------------------

### 4.2 New Config

Precondition: - Schema must be loaded

Result: - Deterministic config created via schema expansion rules -
Arrays empty - Scalars null - Dirty = false - Title updated

------------------------------------------------------------------------

### 4.3 Open Config

Precondition: - Schema must be loaded

Result: - Config parsed into IR via adapter - Structural validation
performed - Errors highlighted if present - Dirty = false

Failure: - Config rejected - No partial state retained

------------------------------------------------------------------------

### 4.4 Edit → Write

Edit: - User modifies fields in Model tab - Dirty = true

Write: Action: Model → Write

Purpose: Commit user changes to internal IR.

Validation: - Structural correctness - Required fields - Type
correctness - `unique_by` constraints

Success: - IR updated - Dirty cleared - Status: ✔ Write successful

Failure: - IR unchanged - Errors highlighted - Status updated

Write protects internal integrity.

------------------------------------------------------------------------

### 4.5 Generate

Action: Preview → Generate

Purpose: Produce runtime configuration projection.

Validation: - Structural re-check - Semantic validation - Cross-field
constraints - Runtime export constraints

Success: - Preview updated - Status: ✔ Preview generated

Failure: - Preview remains unchanged - Errors highlighted - Status
updated

Generate protects deployment correctness.

------------------------------------------------------------------------

### 4.6 Export

Action: Preview → Export Config

Rules: - Exports last successfully generated preview only - Must NOT
call Generate implicitly - Must NOT mutate IR - Disabled while Dirty =
true

Export is projection-only.

------------------------------------------------------------------------

## 5. Dirty State Model (ABSOLUTE)

Editing without Write places system in Dirty State.

Rules: - Dirty blocks Generate - Dirty blocks Export - Dirty must be
intercepted before schema or document transitions - Dirty clears only
after successful Write

This guarantees deterministic workflow.

------------------------------------------------------------------------

## 6. Undo / Redo Model

Undo/Redo operates on Model tab field edits only.

Rules: - Does NOT implicitly trigger Write - Does NOT implicitly trigger
Generate - Does NOT bypass validation

Undo restores previous editable state only.

------------------------------------------------------------------------

## 7. Error Handling Across Lifecycle

Errors include:

-   Structural errors
-   Uniqueness violations
-   Semantic rule violations
-   Runtime export constraints

Error handling rules:

-   No popup validation dialogs
-   Highlight affected nodes
-   Display summary in status line
-   Block illegal transitions

Validation engine produces structured error objects. UI consumes them.

------------------------------------------------------------------------

## 8. Document-Centric Guarantees

-   Active Schema defines editing universe
-   Active Document conforms to Active Schema
-   No implicit schema switching
-   No overlapping operational states
-   No direct IR mutation from UI
-   All mutations go through OperationProcessor

------------------------------------------------------------------------

## 9. Design Evolution Notes

Initial concept: - Two-mode operation (Schema Mode / Config Mode)

Evolved model: - Document-centric architecture - Explicit Write/Generate
separation - Dirty state enforcement - Atomic mutation model -
Deterministic lifecycle transitions

ZENO operates as a controlled instrument, not a live editor.

The operation model reinforces the philosophy:

Make it hard for the user to make a mistake.
