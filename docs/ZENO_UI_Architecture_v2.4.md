# ZENO -- UI Architecture

Version: 3.0
Status: LOCKED (Single-Phase Lifecycle)

------------------------------------------------------------------------

# 0. Scope

This document defines the authoritative UI surface contract for ZENO post-refactor.

Superseded elements:
- Preview tab (removed)
- Generate button (removed)
- Two-phase lifecycle Write → Generate → Export
- Dirty state (supplanted by invalid buffer gating)

Core architecture layers (Schema, IR, Store, Validators, OperationProcessor)
remain unchanged.

------------------------------------------------------------------------

# 1. Document-Centric Architecture (LOCKED)

ZENO is document-centric.

There is no manual Mode switch.

The UI state is defined by:

- Active Schema
- Active Document (optional)

Important:
- A Schema is also a structured document.
- ZENO may edit schemas via a meta-schema.
- Behavior is governed entirely by the Active Schema.
- No UI behavior may depend on file extension.

Definitions:

Active Schema:
  The schema currently loaded and used for rendering and validation.

Active Document:
  The structured document currently being edited (configuration file or schema file).

------------------------------------------------------------------------

# 2. Right Workspace Layout (LOCKED)

The right workspace SHALL contain exactly two tabs:

1. Model
2. Docs

There is NO Preview tab.

Editing now occurs in the Model tab as a structured projection surface, not free text.

Rationale:
- ZENO edits IR, never raw text.
- The Model tab renders a code-like projection with line numbers.
- Structural editing: user edits scalar values only.
- No Generate phase.

------------------------------------------------------------------------

# 3. Workspace Responsibilities

## 3.1 Model Tab

Purpose:
Structured projection surface for editing Active Document scalars.

Rules:
- Renders IR as code-like text with line numbers.
- Keys, punctuation, and structure are read-only.
- Only schema-permitted scalars are editable.
- Live per-keystroke validation before IR commit.
- Invalid input remains in buffer; IR is never invalid.
- Inline floating hint box shows schema-driven help and errors.
- Sync selection with tree.

No Write button required; commits happen live when valid.

------------------------------------------------------------------------

## 3.2 Docs Tab

Purpose:
Display documentation and field help from the Active Schema.

Rules:
- Read-only.
- Derived strictly from schema metadata.
- Must not mutate IR.

------------------------------------------------------------------------

# 4. Operation Lifecycle (LOCKED)

Canonical lifecycle:

Edit (buffer) → Live validation → Commit to IR (only when valid) → Save / Save As

There is no Generate phase. There is no Export.

Edit:
- User modifies scalar values in Model tab.
- Validation runs immediately.
- Valid input commits to IR.
- Invalid input remains in buffer and blocks Save.

Save:
- Allowed only when:
    - No validation errors anywhere
    - No invalid buffers
- Serializes IR directly to disk via adapter.

------------------------------------------------------------------------

# 5. Save Gating Rules (ABSOLUTE)

Save is disabled if:
- Any validation error exists
- Any buffer contains invalid input

IR must never contain invalid state.

------------------------------------------------------------------------

# 6. Menu Bar Structure (LOCKED)

Top-level menus SHALL be:

1. File
2. Edit
3. Help

A Mode menu SHALL NOT exist.

------------------------------------------------------------------------

## 6.1 File Menu (Authoritative)

The File menu SHALL contain exactly:

    File
     ├── New Config...
     ├── Open Config...
     ├── Save
     ├── Save As...
     ├── ----------------
     ├── Config Wizard...
     ├── Load Schema...
     └── Exit

There is NO:
- Close
- Unload Schema
- Mode switch
- Export Config

All transitions must respect invalid buffer and validation gating rules.

------------------------------------------------------------------------

## 6.2 Edit Menu

- Undo
- Redo

Undo/Redo applies to Model tab edits only (to be defined).

------------------------------------------------------------------------

## 6.3 Help Menu

- About
- Documentation (optional local links)

No runtime dependency on internet required.

------------------------------------------------------------------------

# 7. Title Bar Contract (LOCKED)

The title bar SHALL reflect the Active Schema.

Primary format:

ZENO -- <ActiveSchemaName>

Extended format (if document loaded):

ZENO -- <ActiveSchemaName> -- <ActiveDocumentName>

Rules:
- Title changes when schema loads.
- Title changes when document opens.
- Title does NOT change during Edit or Save.
- Schema name should come from schema metadata (application field).
- If metadata not available, fallback to schema filename.
- No mode indicator appended.

------------------------------------------------------------------------

# 8. Enforcement Checklist

Before implementation:

- Tabs match: Model / Docs
- No Preview tab exists
- No Generate button exists
- Model tab renders structured projection with line numbers
- Model tab allows editing scalar values only
- Live validation enforced before IR commit
- Save gated on validation errors and invalid buffers
- No Mode menu exists
- File/Edit/Help menus present
- File menu matches authoritative structure exactly
- Title bar follows contract
- IR is always valid

------------------------------------------------------------------------

Generated on: 2026-03-01T00:00:00Z
End of Document.

