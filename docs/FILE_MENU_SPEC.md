# ZENO – File Menu Specification v2.3

Status: Single-Phase Lifecycle (No Generate, No Preview)

---

## 1. Purpose

This document defines the authoritative behavior of the File menu.

The File menu controls:
- Schema loading
- Document lifecycle
- Save operations

All operations respect single-phase validation and valid-only IR guarantee.

---

## 2. Menu Structure

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
**No Export operation.**
**No Close or Unload Schema.**

This structure is locked.

---

## 3. Startup State

On application launch:
- No schema loaded
- No document loaded
- Save: disabled
- Save As: disabled
- New Config: disabled
- Open Config: disabled

Title: `ZENO – No Schema`

**First action must be Load Schema.**

---

## 4. Load Schema...

### Preconditions
None (available at any time)

### Behavior

**If document currently open:**
- Check for invalid buffers
- If invalid buffers exist: prompt "Discard Changes / Cancel"
- If no invalid buffers: prompt "Continue / Cancel" (optional)

**On user confirmation:**
1. Load and validate schema file
2. Clear Active Document
3. Clear undo history
4. Update title to schema name
5. Persist schema path for next session

**On failure:**
- Schema rejected
- Previous state preserved
- Error displayed in status line

**Result State:**
- Schema loaded
- No document active
- New Config / Open Config enabled

---

## 5. New Config...

### Preconditions
- Schema must be loaded

### Behavior

**If document currently open:**
- Check for invalid buffers
- If invalid: prompt "Discard Changes / Cancel"
- If valid: prompt "Continue / Cancel" (optional)

**On user confirmation:**
1. Create deterministic document via schema expansion
2. Arrays initialized empty
3. Scalars initialized null (or schema defaults)
4. Set as Active Document
5. Update title

**Result State:**
- Document loaded
- IR valid
- Save enabled

---

## 6. Open Config...

### Preconditions
- Schema must be loaded

### Behavior

**If document currently open:**
- Check for invalid buffers
- If invalid: prompt "Discard Changes / Cancel"
- If valid: prompt "Continue / Cancel" (optional)

**On user confirmation:**
1. Select file via dialog
2. Parse file via adapter into IR
3. Run structural validation
4. If errors: load anyway, highlight errors in UI
5. Set as Active Document
6. Update title

**On parse failure:**
- File rejected
- Previous state preserved
- Error displayed

**Result State:**
- Document loaded
- IR valid (or error-marked but structurally sound)
- Save enabled if no validation errors

---

## 7. Save

### Preconditions
- Document must be active
- No invalid buffers
- No validation errors

### When Disabled
- No document active
- Invalid buffers exist
- Validation errors exist

### Behavior

**If no file path set (first save):**
- Redirect to Save As

**Otherwise:**
1. Serialize IR directly via adapter
2. Write to current file path
3. Update status: "Saved: filename.yaml"

**Critical Rules:**
- **Save does NOT mutate IR**
- **Save does NOT run validation** (only checks error state)
- **Save does NOT transform IR** (direct serialization only)
- **Save does NOT trigger Generate step** (no such step exists)

**On write failure:**
- Error displayed
- IR unchanged
- File unchanged

---

## 8. Save As...

### Preconditions
- Document must be active
- No invalid buffers
- No validation errors

### When Disabled
- No document active
- Invalid buffers exist
- Validation errors exist

### Behavior

1. Prompt for new file path via dialog
2. Serialize IR directly via adapter
3. Write to selected path
4. Update Active Document path
5. Update title with new filename
6. Update status: "Saved: filename.yaml"

**Critical Rules:**
- Same as Save
- No Generate, no transformation
- Direct IR serialization only

**On write failure:**
- Error displayed
- IR unchanged
- Active Document path unchanged

---

## 9. Config Wizard...

### Preconditions
- Schema must be loaded

### Behavior

**If document currently open:**
- Check for invalid buffers
- If invalid: prompt "Discard Changes / Cancel"
- If valid: prompt "Continue / Cancel"

**Wizard flow:**
1. Guided step-by-step configuration creation
2. Each field validated before accept
3. Wizard commits only valid state to IR
4. Final document must pass all validation

**Rules:**
- Wizard uses same validation as Model tab
- Wizard respects OperationProcessor
- Wizard cannot bypass IR valid-only rule
- Wizard creates valid document or is cancelled

**Result State:**
- Valid document loaded
- Save enabled

---

## 10. Exit

### Behavior

**If invalid buffers exist:**
- Prompt: "Discard Changes / Cancel"
- Save option shown but disabled (cannot save invalid state)

**If no invalid buffers:**
- Exit immediately (IR auto-saved to session, schema path persisted)

**On Cancel:**
- Return to editor

---

## 11. Disabled State Rules

When **no document active:**
- Save: disabled
- Save As: disabled

When **invalid buffers or validation errors exist:**
- Save: disabled
- Save As: disabled

When **no schema loaded:**
- New Config: disabled
- Open Config: disabled
- Config Wizard: disabled

**Preventive disabling preferred over runtime errors.**

---

## 12. Save Behavior Summary

Save is NOT a validation trigger.
Save is NOT a transformation step.
Save is NOT a Generate phase.

Save is:
- **Condition check:** Are buffers valid? Are validation errors present?
- **Direct serialization:** IR → Adapter → File
- **Status update:** Display save confirmation

Save **assumes IR is already valid** (guaranteed by live validation).

---

## 13. Title Bar Updates

| State | Title |
|-------|-------|
| No schema | `ZENO – No Schema` |
| Schema loaded only | `ZENO – <SchemaName>` |
| Document loaded | `ZENO – <SchemaName> – <DocumentName>` |

Title updates:
- On Load Schema
- On New Config / Open Config
- On Save As (document name changes)

Title does NOT update:
- During editing
- On Save (unless path changes)

---

## 14. Design Principles

1. **No silent state loss** – Always prompt before discard
2. **No implicit mutation** – All changes explicit
3. **Schema defines universe** – No operations without schema
4. **Invalid state blocks Save** – Preventive architecture
5. **IR always valid** – Guaranteed by live validation
6. **Save is serialization only** – No hidden workflows

The File menu reflects ZENO's safety philosophy:

**Make it hard for the user to commit a mistake.**

---

Generated: 2026-03-01
End of Document.

