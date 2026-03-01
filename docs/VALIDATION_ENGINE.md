# ZENO – Validation Engine Specification

Status: Single-Phase Validation (No Generate, No Preview)

---

## 1. Core Principle

**Validation blocks invalid state transitions.**

**IR must never contain invalid state.**

All validation occurs **before** IR mutation. Invalid input is rejected at the buffer level without affecting IR.

---

## 2. Validation Philosophy

Validation is:
- Deterministic and explicit
- Not optional, not advisory
- Enforced at field-level (per-keystroke)
- Blocking for IR commit
- Silent on success, visible on failure

---

## 3. Single-Phase Validation Lifecycle

```
Edit in buffer → Validate field → Valid? → Yes: Update IR → No: Hold in buffer
```

No Generate phase. No Preview validation gating. No transformation layer.

All edits validated **immediately** before IR is touched.

---

## 4. Live Field Validation

**Trigger:** User modifies scalar field value

**Timing:** Per-keystroke

**Process:**
1. Input received into buffer
2. Type checked
3. Structural constraints checked
4. Schema-defined rules checked
5. Result: valid or invalid

**On Valid:**
- IR updated immediately
- No error state

**On Invalid:**
- Input held in buffer
- IR unchanged (remains valid)
- Inline floating hint displayed
- Save disabled

---

## 5. Validation Scope

### 5.1 Always Validated

- Field type correctness
- Required field presence
- Array `unique_by` constraints (within array scope)
- Structural nesting correctness
- Schema-defined restrictions

### 5.2 Validation Rules

**Type Checking:**
- Scalar type matches schema
- Array/object structure matches
- Enum values match allowed set

**Uniqueness (Arrays):**
- `unique_by: field_name` enforced within array
- Single-field uniqueness only
- Duplicate values block commit

**Required Fields:**
- Non-nullable fields must be set
- Missing values prevented at IR level

---

## 6. Error Object Model

Validators produce structured error objects with:

```
{
  path: "listeners[1].port",
  message: "Duplicate value 502. Already used by listeners[0].",
  severity: "error"
}
```

**Delivered to UI:**
- Fields are highlighted
- Tree nodes marked with error indicator
- Inline floating hint shown
- Status line updated
- Save button disabled

**Validation engine never manipulates UI directly.** UI consumes error objects and renders them.

---

## 7. Mutation Boundary Guarantee

```
Input validation → Pass? → IR updated
              → Fail? → Buffer holds invalid state, IR untouched
```

This ensures:
- IR always contains only valid state
- Workflow remains deterministic
- No partial or inconsistent IR states
- Save always reflects actual valid state

---

## 8. Strict Schema Grammar

Schema validation rejects:
- Unknown schema keywords
- Invalid field types
- Invalid nesting patterns
- Unresolvable type references

Strict grammar reduces ambiguity and surface area for user mistakes.

---

## 9. Save Gating

Save is disabled when:
- Any buffer contains invalid input
- Any validation error is present
- Any structural inconsistency is detected

Save is enabled only when:
- All fields are valid
- All buffers are empty or valid
- IR is complete and correct

Save action serializes IR directly to disk via adapter. No pre-save transformation.

---

## 10. No Generate-Phase Validation

There is no separate "Generate" step with its own validation gate.

All validation is live. All validation blocks IR mutation.

Validation engine is single-phase.

---

Generated: 2026-03-01
End of Document.
