# ZENO – UI Behavior Specification v2.3

Status: Single-Phase Lifecycle (No Generate, No Preview)

---

## 1. Purpose

This document defines user interface behavior for ZENO.

ZENO is document-centric. Behavior is schema-driven. IR is always valid.

---

## 2. Core UI Principles

1. **Live validation per keystroke** – All edits validated before IR commit
2. **Invalid input never mutates IR** – Buffer holds invalid state only
3. **IR updates only when field becomes valid** – Atomic validity guarantee
4. **Save disabled on any validation error** – No invalid state persisted
5. **No raw text editing** – Model tab is structured projection only
6. **No implicit structural mutation** – All changes explicit and validated

---

## 3. Top-Level Layout

```
File   Edit   Help

+--------------------+--------------------------------------+
| Tree               | Tabs: [ Model | Docs ]               |
| (Structure)        |                                      |
|                    | Model: structured projection         |
|                    | (line numbered, scalars editable)    |
+-----------------------------------------------------------+
| Status: ✔ Ready                                          |
+-----------------------------------------------------------+
```

**No Preview tab.**

---

## 4. Document-Centric Model

Active state defined by:
- **Active Schema** – Governs structure and validation
- **Active Document** – Config or schema being edited (optional)

**No manual mode switching.**
**No Schema Mode vs Config Mode.**

Behavior entirely schema-driven.

---

## 5. Tree Panel (Left)

### Purpose
Navigate and visualize document structure.

### Behavior
- Fully derived from IR
- Structure permitted by Active Schema only
- Context menu schema-driven (Add/Remove/Edit)
- Invalid nodes highlighted in red
- Parent nodes indicate child errors
- Root node cannot be removed

### Rules
- No arbitrary key insertion
- Add/Remove allowed only if schema permits
- All mutations validated before IR commit
- No implicit structural changes

---

## 6. Model Tab (Right Workspace)

### Purpose
Structured projection surface for editing scalar values.

### Rendering
- IR rendered as code-like text
- Line numbers displayed
- Keys, punctuation, structure: **read-only**
- Scalar values: **editable**

### Live Validation Flow

```
User types keystroke
    ↓
Validation runs immediately
    ↓
Valid? ──→ Yes ──→ Update IR, clear error
    ↓
   No ──→ Hold in buffer, show inline hint, IR unchanged
```

### On Validation Success
- IR updated atomically
- No error displayed
- Save remains enabled (if no other errors)

### On Validation Failure
- Input held in buffer
- IR unchanged (remains valid)
- Inline floating hint displays error
- Line/field highlighted
- Save disabled

### Guarantees
- IR never contains invalid state
- No race conditions between validation and commit
- All mutations through OperationProcessor
- No direct IR manipulation from UI

---

## 7. Docs Tab (Right Workspace)

### Purpose
Display schema-driven documentation.

### Content
- Field descriptions
- Type constraints
- Validation rules
- Intent notes

### Rules
- Read-only
- Derived from schema metadata only
- Never mutates IR

---

## 8. Inline Floating Hint

### Trigger
Validation error on field edit.

### Display
- Positioned near edited field
- Contains error message
- Links to schema constraint if available
- Dismisses when field becomes valid

### Examples
```
Error: Value must be between 1 and 65535
Type: integer, required

Duplicate value detected.
Port 502 already used by listeners[0].
```

### Rules
- No popup dialogs
- Context-specific
- Schema-driven content

---

## 9. File Menu

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
**No Close or Unload Schema.**

### Save Behavior

**Enabled when:**
- All fields valid
- No validation errors
- No invalid buffers

**Disabled when:**
- Any validation error exists
- Any buffer contains invalid input
- Structural inconsistency detected

**Action:**
- Serializes IR directly to disk via adapter
- No transformation layer
- No Generate step

---

## 10. Edit Menu

```
Edit
 ├── Undo
 └── Redo
```

(Undo/Redo to be defined in future specification)

**Rules:**
- Must not bypass validation
- Must maintain IR validity guarantee

---

## 11. Help Menu

```
Help
 ├── About
 └── Documentation
```

---

## 12. Status Line

Single-line feedback at bottom of window.

### Examples
```
✔ Ready
✔ Saved: config.yaml
❌ Validation error: Duplicate port 502
Schema loaded: mma_config
```

### Rules
- No modal dialogs
- Persistent until state change
- Clear and concise

---

## 13. Error Visualization

When validation fails:

1. **Model Tab:**
   - Line/span highlighted
   - Inline floating hint appears

2. **Tree Panel:**
   - Node marked with error indicator (red)
   - Parent nodes show child error indicator

3. **Status Line:**
   - Error summary displayed

4. **Save Button:**
   - Disabled/grayed out

Error persists until user corrects invalid input.

---

## 14. Context Menu (Tree Panel)

Schema-driven operations:

- **Add Child** – If schema allows array/object expansion
- **Remove Item** – If schema allows and not required
- **Edit Value** – Opens field editor or focuses Model tab
- **Duplicate Item** – If array element

**Rules:**
- All operations validated before commit
- No operation bypasses validation
- Disabled items grayed out
- Root node cannot be removed

---

## 15. Keyboard Shortcuts

(To be defined)

Suggested:
- Ctrl+S: Save
- Ctrl+Z: Undo
- Ctrl+Y: Redo
- F2: Rename/Edit selected node

---

## 16. Drag and Drop (Optional)

If implemented:

**Rules:**
- Must respect schema constraints
- Must validate before committing reorder
- Must not violate uniqueness rules
- Must not violate structural rules
- Invalid drag operations rejected with hint

---

## 17. Field Editing Widgets

Based on schema type:

- **String:** Text input
- **Integer:** Numeric input (spinner optional)
- **Boolean:** Checkbox or dropdown
- **Enum:** Dropdown with allowed values
- **Object:** Not directly editable (edit children)
- **Array:** Not directly editable (add/remove children)

All widgets validate input before IR commit.

---

## 18. Schema-Driven Constraints Display

When field selected or hovered:

Display:
- Type
- Required/optional status
- Allowed values (enum)
- Min/max constraints
- Uniqueness requirements

Location: Inline hint or Docs tab

---

## 19. No Generate Behavior

There is no Generate button.
There is no Generate phase.
There is no Generated state.

All edits commit to IR immediately when valid.

---

## 20. No Preview Behavior

There is no Preview tab.
There is no Preview surface.
There is no Preview blocking.

Model tab is the editing surface.
Save writes IR directly to disk.

---

## 21. Alignment Verification

This specification aligns with:
- Operation Model v2.0 (single-phase lifecycle)
- Validation Engine (live validation, valid-only IR)
- UI Architecture v2.3 (Model/Docs tabs only)
- File Menu Spec (no Generate/Export)

**Core guarantee: IR is always valid.**

---

Generated: 2026-03-01
End of Document.
