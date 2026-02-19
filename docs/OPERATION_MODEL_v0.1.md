# ZENO --- Operation Model Specification

Version: v0.1 (Architecture Lock)

------------------------------------------------------------------------

# 1. Purpose

This document defines the only legal way IR may be modified.

All structural mutations must occur through Operations.

Direct mutation of IR nodes is forbidden.

------------------------------------------------------------------------

# 2. Core Principle

User Action → Operation Proposed → Schema Pre-Validation → Operation
Applied → Full Validation Re-Run

If schema pre-validation fails, operation is rejected.

------------------------------------------------------------------------

# 3. Operation Definition

An Operation is a structured command that modifies IR.

Each Operation must contain:

-   operation_id (UUID)
-   target_node_id (UUID)
-   operation_type
-   payload (operation-specific data)

Operations are immutable once created.

------------------------------------------------------------------------

# 4. Supported Operation Types (v0.1)

## 4.1 AddNode

Adds a new child node.

Payload: - parent_node_id - key (for object nodes) - index (for list
nodes) - node_definition (initial type/value)

------------------------------------------------------------------------

## 4.2 RemoveNode

Removes a node from its parent.

Payload: - target_node_id

Root node removal is forbidden.

------------------------------------------------------------------------

## 4.3 UpdateScalar

Updates value of a scalar node.

Payload: - target_node_id - new_value

Only valid for scalar nodes.

------------------------------------------------------------------------

## 4.4 MoveNode

Reorders or re-parents a node.

Payload: - target_node_id - new_parent_id - new_index (optional)

Move must preserve schema structural rules.

------------------------------------------------------------------------

# 5. Pre-Validation Rule

Before applying an operation:

-   Schema rules must be checked for structural legality
-   Operation must not create illegal state

Example:

Cannot add property not allowed by schema. Cannot exceed max_items.
Cannot remove required property.

------------------------------------------------------------------------

# 6. Atomicity Rule

Operations are atomic.

If any part fails, IR must remain unchanged.

Partial mutation is forbidden.

------------------------------------------------------------------------

# 7. Identity Rule

Operations reference nodes by UUID only.

Path-based operations are forbidden.

------------------------------------------------------------------------

# 8. Revision Model

Each successful operation:

-   Produces a new revision state
-   Increments document revision counter

Undo/Redo support will operate by replaying operations.

------------------------------------------------------------------------

# 9. No Direct Mutation Rule

The following are architectural violations:

-   Direct attribute changes on nodes
-   Manual child list manipulation
-   External modification of IR structures

All changes must flow through Operation Processor.

------------------------------------------------------------------------

# 10. Scope Boundary

Operation Model does NOT:

-   Perform validation itself
-   Interpret schema logic
-   Trigger UI logic
-   Serialize text

Operation Model only mutates IR safely.

------------------------------------------------------------------------

END OF OPERATION_MODEL.md v0.1
