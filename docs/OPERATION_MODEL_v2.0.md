# ZENO – Operation Model Specification v2.0

Status: Simplified Lifecycle (No Generate, No Preview)

---

## 1. Core Invariant

**IR must never contain invalid state.**

All mutations are validated before IR commit. Invalid input remains in buffer only.

---

## 2. Operational Principle

ZENO operates through a **single-phase validation lifecycle**:

```
Edit (in buffer) → Live Validate → IR Commit → Save
```

- No Generate phase
- No Preview tab
- No Generated state
- No transformation layer

Save is direct serialization of the IR to disk via adapter.

---

## 3. Document States

ZENO maintains three explicit states:

1. **No Schema Loaded** – Startup state
2. **Schema Loaded** – Schema in memory, no active document
3. **Schema Loaded + Document Loaded** – Working state

Invalid buffers do not change document state.

---

## 4. Lifecycle Operations

### 4.1 Load Schema

**Precondition:** None

**Action:** File → Load Schema...

**Process:**
- Schema file validated structurally
- Schema parsed and stored as Active Schema
- Active Document cleared
- Undo history cleared

**Failure:** Schema rejected, previous state preserved

**Result State:** Schema Loaded

---

### 4.2 New Document

**Precondition:** Schema must be loaded

**Action:** File → New

**Process:**
- Deterministic document created via schema expansion
- Arrays initialized empty
- Scalars initialized null

**Result State:** Schema Loaded + Document Loaded

---

### 4.3 Open Document

**Precondition:** Schema must be loaded

**Action:** File → Open...

**Process:**
- Document file parsed via adapter into IR
- Structural validation performed
- Errors reported if present

**Failure:** Document rejected, no partial state loaded

**Result State:** Schema Loaded + Document Loaded (or unchanged on failure)

---

### 4.4 Live Edit

**Precondition:** Document must be loaded

**User Action:** Modify a field value in Model surface

**Per-Keystroke Validation:**
- Type checking
- Structural correctness
- Required field enforcement
- `unique_by` constraint checking

**Success Path:**
- Input accepted into buffer
- IR updated immediately
- No error state

**Failure Path:**
- Input rejected from IR
- Input held in buffer
- Inline floating error hint displayed
- IR unchanged

**Guarantee:** After each keystroke, IR contains only valid state.

---

### 4.5 Save

**Precondition:**
- Document loaded
- No validation errors exist
- No invalid buffers exist

**Action:** File → Save (or Ctrl+S)

**Process:**
- IR serialized directly via adapter
- Output written to current file path

**Failure:** Save disabled (button/menu grayed out)

**Result:** IR persisted to disk

---

### 4.6 Save As

**Precondition:** Same as Save

**Action:** File → Save As...

**Process:**
- User specifies new file path
- IR serialized and written to new path
- Active document path updated

---

## 5. Validation Engine Contract

Validation runs in two contexts:

1. **Per-keystroke** – Field-level, non-blocking when invalid
2. **Pre-save** – Full document, blocks Save action

Error types:
- Type mismatch
- Required field missing
- Uniqueness violation
- Semantic constraint violation

Error delivery:
- Structured error objects
- UI highlights affected nodes
- Inline hints shown to user
- No popup dialogs

---

## 6. IR Mutation Rules

All IR mutations follow this contract:

1. User edits field in Model surface (buffer)
2. Validation engine validates change
3. If valid → IR updated immediately
4. If invalid → Buffer updated, IR untouched

No implicit mutations. No transformation layer. No multi-step commits.

---

## 7. Guarantees

- **Format Agnostic:** IR model unchanged regardless of adapter
- **Schema Driven:** Active Schema defines all valid structures
- **No Implicit State:** No read-ahead, no background generation
- **No Overlapping States:** Exactly one active schema and document
- **Synchronous UI:** Save always serializes current IR snapshot
- **No Raw Editing:** Model surface is only editing mechanism

---

## 8. Undo/Redo

Not defined in this version. Reserved for future specification.

---

Generated: 2026-03-01
End of Document.
