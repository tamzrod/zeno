# ZENO -- UI Behavior Specification

Version: 3.0
Status: Updated (Single-Phase Lifecycle)

------------------------------------------------------------------------

## 1. Purpose

This document defines the behavior of the Zeno user interface.

Zeno is a controlled configuration instrument.

Zeno is document-centric.

There are no manual modes.

UI behavior is determined entirely by:

- Active Schema
- Active Document (optional)

------------------------------------------------------------------------

## 2. Top-Level Layout

    File   Edit   Help

    +--------------------+--------------------------------------+
    | Tree               | Tabs: [ Model | Docs ]               |
    | (Structure)        |                                      |
    |                    | Model: structured projection         |
    |                    | (line numbered, scalars editable)    |
    +-----------------------------------------------------------+
    | Status: ✔ Ready                                          |
    +-----------------------------------------------------------+

------------------------------------------------------------------------

## 3. Document-Centric Model

ZENO operates without manual mode switching.

Definitions:

- Active Schema: The schema currently governing structure and validation.
- Active Document: The structured document currently being edited (optional).

Rules:

- Behavior is governed entirely by the Active Schema.
- A schema itself is also a structured document.
- No UI layout or logic may depend on file extension.
- There is no Schema Mode or Config Mode.

------------------------------------------------------------------------

## 4. Left Panel -- Structure Tree

The tree is authoritative.

Rules:

- Fully derived from IR.
- Structure allowed strictly by Active Schema.
- No arbitrary key insertion.
- Context menu is schema-driven.
- Add / Remove / Reorder allowed only if schema permits.
- Root cannot be removed.
- Invalid nodes highlighted in red.
- Parent nodes indicate child errors.

The tree prevents structural mistakes.

------------------------------------------------------------------------

## 5. Right Panel: Model + Docs Tabs

Tabs:
- Model
- Docs

There is NO Preview tab.

------------------------------------------------------------------------

### 5.1 Model Tab

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

On Validation Failure:
- Input remains in buffer
- IR unchanged
- Inline hint displays error
- Save disabled

------------------------------------------------------------------------

### 5.2 Docs Tab

Purpose:
Provide contextual help.

Rules:
- Read-only.
- Displays schema-derived documentation.
- May include:
  - Field description
  - Intent notes
  - Constraints

Docs tab never mutates state.

------------------------------------------------------------------------

## 6. File Menu

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

Rules:
- No Close operation.
- No Unload Schema operation.
- No Mode switch.
- No Export Config.
- No additional items unless formally documented.
- Invalid buffers and validation errors must be checked before Save.

------------------------------------------------------------------------

## 7. Edit Menu

    Edit
     ├── Undo
     └── Redo

Rules:
- Applies only to Model tab edits (to be defined).
- Must not bypass validation.

------------------------------------------------------------------------

## 8. Help Menu

    Help
  ├── About
  └── Documentation

Rules:
- Documentation links are optional and local.
- No tutorial overlays.
- No runtime dependency on internet.

------------------------------------------------------------------------

## 9. Status Line

Single-line feedback mechanism.

Examples:

✔ Ready
✔ Saved: config.yaml
❌ Duplicate port 502
Validation error: ...

Rules:
- No popup validation dialogs.
- Persistent until next state change.
- Clear and concise only.

------------------------------------------------------------------------

## 10. Error Visualization

When validation fails:
- Line/span highlighted in Model tab.
- Inline floating hint displays error message.
- Tree node marked with error indicator.
- Parent nodes indicate child error.
- Status line displays summary.
- Save disabled.

Errors persist until corrected.

------------------------------------------------------------------------

## 11. Drag and Drop (Optional)

If implemented:
- Must respect schema constraints.
- Must validate before committing reorder.
- Must not violate uniqueness or structural rules.

------------------------------------------------------------------------

## 12. Alignment Statement

This UI behavior is fully aligned with:
- Architecture Lock
- UI Architecture v3.0
- File Menu Specification
- Single-phase Live Validation Model

ZENO is document-centric.
Structure is schema-governed.
IR is always valid.

------------------------------------------------------------------------

Generated on: 2026-03-01T00:00:00Z
End of Document.

