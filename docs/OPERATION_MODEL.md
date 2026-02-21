# ZENO -- Operation Model Specification

## 1. Purpose

This document defines the operational lifecycle of Zeno.

Zeno separates configuration mutation from runtime projection.

This separation is intentional and foundational.

------------------------------------------------------------------------

## 2. Core Operational Principle

> Mutation and projection must never be implicit.

All state transitions must be explicit and user-triggered.

No background magic. No live auto-generation. No hidden state changes.

------------------------------------------------------------------------

## 3. Operational States

Zeno operates through clear state transitions:

1.  Schema Loaded
2.  Config Loaded
3.  Editing (Dirty State)
4.  Written (Validated Internal State)
5.  Generated (Validated Runtime Projection)

Each state transition requires explicit action.

------------------------------------------------------------------------

## 4. Lifecycle Flow

### 4.1 Load Schema

Action: File → Load Schema

Result: - Schema validated structurally - Schema loaded into core - Mode
switches to CONFIG-ready state - Tree prepared for config editing

Failure: - Schema rejected - Status line displays error - Mode remains
unchanged

------------------------------------------------------------------------

### 4.2 Load Config

Action: File → Open Config

Precondition: Schema must be loaded.

Result: - Config parsed into IR - Structural validation performed -
Errors highlighted if present

Failure: - Config rejected - No partial state retained

------------------------------------------------------------------------

### 4.3 Edit → Write

Action: Modify Tab → Write

Purpose: Commit user changes to internal IR.

Validation: - Structural validation - Required fields - Type
correctness - `unique_by` constraints

Success: - IR updated - Dirty flag cleared - Status: ✔ Write successful

Failure: - IR unchanged - Errors highlighted - Status updated

Write protects internal integrity.

------------------------------------------------------------------------

### 4.4 Generate

Action: Preview Tab → Generate

Purpose: Produce runtime configuration projection.

Validation: - Structural re-check - Semantic validation - Cross-field
rules - Runtime export constraints

Success: - Preview updated - Status: ✔ Preview generated

Failure: - Preview remains unchanged - Errors highlighted - Status
updated

Generate protects deployment correctness.

------------------------------------------------------------------------

## 5. Dirty State Model

Editing without Write places system in Dirty State.

Rules: - Dirty state blocks Generate - Status indicates unsaved
changes - Write required before Generate

This ensures deterministic flow.

------------------------------------------------------------------------

## 6. Undo / Redo Model

Undo operates at Write-level granularity.

Meaning: - Each successful Write is one atomic mutation. - Undo restores
previous valid IR state. - Generate is not part of undo history.

This preserves structural safety.

------------------------------------------------------------------------

## 7. Error Handling Across Lifecycle

Errors include:

-   Structural errors
-   Uniqueness violations
-   Semantic rule violations
-   Runtime export constraints

Error handling rules:

-   No popups for validation
-   Highlight affected nodes
-   Display summary in status line
-   Block illegal transitions

------------------------------------------------------------------------

## 8. Mode Transitions

Switching Modes:

Schema Mode → Config Mode: - Requires successful schema load

Config Mode → Schema Mode: - Current config must close or be saved -
Prevents accidental cross-mode corruption

Modes must never overlap implicitly.

------------------------------------------------------------------------

## 9. Export Model

Generate produces runtime projection only.

Exporting to file is separate and explicit.

Rules: - Only generated preview can be exported - Cannot export invalid
configuration - Export does not mutate IR

------------------------------------------------------------------------

## 10. Design Evolution Notes

Initial concept: - Basic structural editing

Evolved model: - Explicit Write/Generate separation - Dirty state
enforcement - Atomic mutation model - Two-mode operation - Deterministic
lifecycle transitions

Zeno operates as a controlled instrument, not a live editor.

Operation model reinforces the philosophy:

Make it hard for the user to make a mistake.
