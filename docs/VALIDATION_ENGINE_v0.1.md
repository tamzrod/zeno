# ZENO --- Validation Engine Specification

Version: v0.1 (Architecture Lock)

------------------------------------------------------------------------

# 1. Purpose

This document defines how schema rules are applied to IR.

The Validation Engine:

-   Interprets Schema definitions
-   Evaluates IR nodes
-   Produces validation results
-   Does NOT modify IR structure

Validation is deterministic and side-effect free.

------------------------------------------------------------------------

# 2. Core Principle

Validation reads:

Schema + IR

Validation produces:

ValidationResult objects

Validation must never:

-   Mutate IR structure
-   Inject nodes
-   Auto-correct values
-   Access adapters
-   Access UI layer

------------------------------------------------------------------------

# 3. Validation Phases

Validation occurs in two distinct phases:

## Phase 1 --- Structural Validation

Checks:

-   Node type matches schema type
-   Required properties exist
-   Additional properties rules
-   List cardinality (min_items, max_items)

Structural validation runs top-down from root.

------------------------------------------------------------------------

## Phase 2 --- Scalar Validation

Applies to scalar nodes only.

Checks:

-   Datatype correctness
-   Min / Max constraints
-   Enum membership
-   Regex pattern match
-   Named format validator

Scalar validation runs bottom-up.

------------------------------------------------------------------------

# 4. Validation Output Model

Validation produces a collection of:

ValidationResult

Each result must contain:

-   node_id (UUID of IR node)
-   severity (error \| warning \| info)
-   message (human-readable text)
-   rule_reference (optional reference to schema rule)

Validation results must not modify IR.

------------------------------------------------------------------------

# 5. Determinism Rule

Given:

-   Same IR
-   Same Schema

Validation must always produce identical results.

No randomness. No external state. No time-based behavior.

------------------------------------------------------------------------

# 6. Format Validators

Named format validators (e.g., ipv4, email, port) are:

-   Registered in Validation Engine
-   Referenced by name in Schema
-   Pure functions
-   Side-effect free

Format validators must:

-   Accept scalar value
-   Return pass/fail + message

------------------------------------------------------------------------

# 7. Error Handling Rule

Validation must:

-   Never throw unexpected exceptions
-   Convert internal errors into validation results

Engine crashes are architectural violations.

------------------------------------------------------------------------

# 8. No Auto-Fix Rule

Validation is read-only.

Auto-correction logic (if ever implemented) must be a separate
subsystem.

------------------------------------------------------------------------

# 9. Performance Model

Full validation runs:

-   On document load
-   After each successful operation

Incremental validation optimization may be added later but must preserve
determinism.

------------------------------------------------------------------------

# 10. Scope Boundary

Validation Engine does NOT:

-   Modify IR
-   Modify Schema
-   Trigger UI changes directly
-   Access file system
-   Contain adapter logic

Validation only evaluates.

------------------------------------------------------------------------

END OF VALIDATION_ENGINE.md v0.1
