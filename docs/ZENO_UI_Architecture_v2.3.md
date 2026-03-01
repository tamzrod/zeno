# ZENO – UI Architecture v2.3

Status: Single-Phase Lifecycle (No Generate, No Preview)

---

## 1. Document-Centric Architecture

ZENO is document-centric. UI state is defined by:

- **Active Schema** – Currently loaded schema governing UI behavior
- **Active Document** – Configuration or schema file being edited (optional)

No mode system. No manual mode switching. Behavior is entirely schema-driven.

---

## 2. Tab Layout

The right workspace contains **exactly two tabs**:

1. **Model** – Structured projection surface for editing
2. **Docs** – Documentation derived from schema metadata

**There is no Preview tab.**

---

## 3. Model Tab

### Purpose
Structured editing surface for Active Document scalars.

### Behavior
- Renders IR as code-like text with line numbers
- Keys, punctuation, structure are read-only
- Only scalar values are editable
- Live per-keystroke validation before IR commit
- Invalid input held in buffer; IR never contains invalid state
- Inline floating hint displays schema help and validation errors
- Selection synced with tree panel

### Guarantees
- No raw text editing
- No direct IR mutation from UI
- All mutations validated before commit
- IR always valid

---

## 4. Docs Tab

### Purpose
Display schema-driven documentation.

### Behavior
- Read-only
- Content derived from schema metadata
- Field-level help and descriptions
- No IR mutation

---

## 5. Operational Lifecycle

```
Edit (buffer) → Live Validate → IR Commit (when valid) → Save
```

**No Generate phase.**
**No Preview step.**
**No Export operation.**

### Edit
- User modifies scalar values in Model tab
- Validation runs per-keystroke
- Valid input commits to IR immediately
- Invalid input remains in buffer, blocks Save

### Save
- Enabled only when:
  - No validation errors exist
  - No invalid buffers exist
- Serializes IR directly to disk via adapter
- No transformation layer

---

## 6. Save Gating

Save is **disabled** when:
- Any validation error exists
- Any buffer contains invalid input

Save is **enabled** when:
- All fields valid
- All buffers empty or valid
- IR complete and correct

---

## 7. Menu Structure

### File Menu
```
File
 ├── New Config...
 ├── Open Config...
 ├── Save
 ├── Save As...
 ├── ──────────────
 ├── Config Wizard...
 ├── Load Schema...
 └── Exit
```

**No Generate button.**
**No Export option.**
**No Unload Schema.**
**No Close.**

### Edit Menu
```
Edit
 ├── Undo
 └── Redo
```

(Undo/Redo to be defined in future specification)

### Help Menu
```
Help
 ├── About
 └── Documentation
```

**No Mode menu.**

---

## 8. Title Bar

Format when schema loaded:
```
ZENO – <ActiveSchemaName>
```

Format when document loaded:
```
ZENO – <ActiveSchemaName> – <ActiveDocumentName>
```

Rules:
- Title reflects Active Schema
- Updates on schema load
- Updates on document open
- Schema name from schema metadata `application` field
- Fallback to schema filename if metadata unavailable
- No mode indicator

---

## 9. Tree Panel

### Purpose
Visual navigation of document structure.

### Behavior
- Reflects IR structure
- Nodes correspond to objects and arrays
- Selection synced with Model tab
- Highlights validation errors
- Supports Add/Remove/Edit operations via context menu

### Rules
- Tree is read-only representation of IR
- All mutations go through OperationProcessor
- No direct tree manipulation

---

## 10. Right Panel (Details)

### Purpose
Contextual field editing and metadata display.

### Behavior
- Shows selected node details
- Scalar field editing widgets
- Schema-driven constraints displayed
- Live validation feedback

### Rules
- All edits validated before IR commit
- Invalid input remains in widget buffer
- IR never mutated with invalid state

---

## 11. Status Line

Displays:
- Validation errors
- Active schema name
- Active document status
- Save state (enabled/disabled)

---

## 12. Enforcement Checklist

Before implementation, verify:

✅ Two tabs only: Model and Docs
✅ No Preview tab
✅ No Generate button anywhere
✅ Model tab is structured projection (not raw text editor)
✅ Only scalar values editable
✅ Live validation before IR commit
✅ Save gated on validation errors
✅ File/Edit/Help menus only (no Mode menu)
✅ File menu matches specification exactly
✅ Title bar follows contract
✅ IR always valid (no invalid state possible)

---

Generated: 2026-03-01
End of Document.
