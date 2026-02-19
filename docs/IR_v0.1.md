# ZENO --- IR Specification Document

Version: v0.1 (Architecture Lock)

------------------------------------------------------------------------

# 1. Purpose

This document formally defines the Intermediate Representation (IR) used
by Zeno.

IR is the internal, format-agnostic tree model that represents
structured documents in memory.

Zeno edits IR --- never raw text.

Adapters translate between text formats (YAML, JSON, INI, etc.) and IR.

------------------------------------------------------------------------

# 2. Core Definition

IR is defined as:

> A rooted, ordered, hierarchical tree of typed nodes.

IR is:

-   Format-agnostic
-   Domain-agnostic
-   Schema-agnostic
-   In-memory only

IR does NOT understand YAML, JSON, Kubernetes, MMA, or any
domain-specific rule.

------------------------------------------------------------------------

# 3. Node Model

Every document is represented as a single Root Node.

Each node in IR must contain:

-   `id` (stable unique identifier, UUID)
-   `type` (object \| list \| scalar)
-   `parent_id` (nullable for root)
-   `children` (ordered, for object/list)
-   `value` (for scalar nodes only)
-   `metadata` (optional container for non-structural information)

------------------------------------------------------------------------

# 4. Node Types

## 4.1 Object Node

Represents a mapping/dictionary structure.

Characteristics: - Ordered key-value children - Keys are stored
explicitly - Child order must be preserved

------------------------------------------------------------------------

## 4.2 List Node

Represents an ordered sequence.

Characteristics: - Ordered indexed children - Order must be preserved

------------------------------------------------------------------------

## 4.3 Scalar Node

Represents a leaf value.

Characteristics: - Stores raw typed value - Supported base types: -
string - int - float - bool - null

No domain validation exists at IR level.

------------------------------------------------------------------------

# 5. Ordering Rule

Child ordering is preserved strictly.

IR must never reorder nodes automatically.

Adapters are responsible for preserving original order when parsing and
serializing.

------------------------------------------------------------------------

# 6. Identity Rule

Each node must have a stable UUID.

Operations must reference nodes by UUID, not by path.

Paths are derived views, not identity.

------------------------------------------------------------------------

# 7. Metadata

Metadata is optional and may include:

-   Validation results
-   UI state hints
-   Source line references
-   Comments (if later supported)

Metadata must NOT affect structural equality of IR.

------------------------------------------------------------------------

# 8. Mutability Model

IR is mutable.

All mutations must occur through the Operation Processor.

Direct mutation of node structures is forbidden outside the Core Engine.

------------------------------------------------------------------------

# 9. Structural Invariants

1.  Exactly one root node per document.
2.  Object children must have unique keys.
3.  List children are ordered by index.
4.  Scalar nodes may not have children.
5.  No node may reference multiple parents.
6.  IR contains no schema rules.

------------------------------------------------------------------------

# 10. Scope Boundary

IR does NOT:

-   Validate domain constraints
-   Enforce required fields
-   Interpret formats (email, ip, port, etc.)
-   Contain adapter logic
-   Contain UI logic

IR only represents structure.

------------------------------------------------------------------------

END OF IR.md v0.1
