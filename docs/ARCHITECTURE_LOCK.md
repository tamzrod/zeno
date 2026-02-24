# ARCHITECTURE_LOCK.md
Version: 1.0
Status: LOCKED (unless explicitly revised)

This document consolidates the currently-authoritative architecture and UI contracts for **ZENO** into a single master reference.

---

## 0. Core Identity

ZENO is a **schema-driven structured document editor**.

- ZENO edits **IR**, never raw text.
- Adapters translate between **text formats** (YAML/JSON/INI/...) and IR.
- The schema defines **allowed structure**, not runtime behavior.
- The UI derives editing capabilities strictly from schema definitions.

Primary product goal:

> Make it hard for the user to make a mistake.

---

## 1. Canonical Layers

### 1.1 Schema Layer
- Input: `.zs` schema files (YAML transport).
- Defines:
  - allowed node types and nesting
  - allowed object properties
  - array item shape
  - optional array uniqueness (`unique_by`)
  - documentation via comments/metadata only
- Does **not** execute runtime behavior.

### 1.2 IR Layer (Intermediate Representation)
IR is the in-memory tree model.

IR is:
- format-agnostic
- domain-agnostic
- schema-agnostic
- ordered and hierarchical

ZENO edits IR only. Parsing/serialization is done by adapters.

### 1.3 IRStore
- Single source of truth for the active document model.
- UI never mutates IR directly.

### 1.4 OperationProcessor
- The only lawful mutation gateway for IR.
- All changes are operations applied through the processor.

### 1.5 Validation Engine
Layered validation with **two phases**:
- **Write Phase**: protects IR integrity before committing edits.
- **Generate Phase**: protects runtime projection correctness.

Validation produces **structured error objects**.
Validators never manipulate UI.

### 1.6 Adapters
- Translate between formats (YAML/JSON/INI/...) and IR.
- Preserve ordering when parsing and serializing.
- Do not embed domain behavior.

---

## 2. IR Contract (LOCKED)

### 2.1 Node Model
Every node contains:
- `id` (stable UUID)
- `type` (object | list | scalar)
- `parent_id` (null for root)
- `children` (ordered for object/list)
- `value` (scalar only)
- `metadata` (optional; must not affect structural equality)

### 2.2 Node Types
- **Object**: ordered key/value children; keys stored explicitly; unique keys.
- **List**: ordered indexed children; order is significant.
- **Scalar**: leaf value; supported base types: string/int/float/bool/null; no children.

### 2.3 Invariants (Must Always Hold)
1. Exactly one root node per document.
2. Object children must have unique keys.
3. List children are ordered and preserved.
4. Scalar nodes may not have children.
5. No node may reference multiple parents.
6. IR contains no schema rules.

---

## 3. Schema Language Contract (LOCKED)

### 3.1 File Header (Required)
Top-level keys:
- `zeno_schema`
- `application`
- `format`
- `root`

Root must be:
```yaml
root:
  type: object
  properties: ...
```

### 3.2 Allowed Types
- `object`
- `array`
- `string`
- `integer`
- `number`
- `boolean`

Unknown types are rejected.

### 3.3 Objects
```yaml
type: object
properties:
  key_name:
    type: ...
```
Rules:
- Only declared properties are allowed.
- Unknown keys in config are rejected.

### 3.4 Arrays
```yaml
type: array
items:
  type: ...
```
Rules:
- `items` required.
- items must be a schema node.
- Arrays do not auto-create items.

### 3.5 Uniqueness (`unique_by`)
Allowed only on arrays:
```yaml
type: array
unique_by: field_name
items:
  type: object
  properties:
    field_name:
      type: integer
```
Rules:
- single-field uniqueness only
- field must exist in `items.properties`
- uniqueness applies within that array scope
- enforced during **Write Phase**

---

## 4. Config Editing Behavior (LOCKED)

### 4.1 Deterministic Expansion (New Config)
When creating a new configuration from schema:
- Root is OBJECT.
- For each schema property:
  - object → create OBJECT node
  - array → create LIST node (empty)
  - scalar → create SCALAR node with value = null/None
- Expansion is recursive for objects only.
- Arrays never auto-create items.

### 4.2 Context Menu Rules (Schema-Driven)

#### OBJECT node actions
- Add child property defined in schema
- Remove node (except root)

Rules:
- no duplicate keys
- only schema-defined properties
- no arbitrary fields

#### LIST node actions
- Add list item (type derived from schema.items)
- Remove item
- Move item up/down

Rules:
- no keys on list items
- order preserved
- reorder changes priority (by design)

#### SCALAR node actions
- Edit value only

Rules:
- type enforcement based on schema
- no children

### 4.3 Schema Linkage Requirement
Each IR node must be resolvable to its schema definition by either:
- attached schema reference metadata during expansion, OR
- dynamic resolution via IR path → schema path

UI must never guess allowed structure.

---

## 5. Operation Lifecycle (LOCKED)

ZENO is document-centric (no manual Mode switch).
UI state is defined by:
- Active Schema
- Active Document (optional)

Canonical lifecycle:

**Edit → Write → Generate → Export**

### 5.1 Write
- user-triggered only
- runs **Write Phase Validation**
- on success: IR commits, Dirty clears
- on failure: IR unchanged, errors surfaced

### 5.2 Generate
- user-triggered only
- runs **Generate Phase Validation**
- on success: Preview updates
- on failure: Preview remains unchanged

### 5.3 Export
- exports last successfully generated preview only
- must not call Generate implicitly
- must not mutate IR

### 5.4 Dirty State (ABSOLUTE)
If Dirty = true:
- Generate disabled
- Export disabled
Dirty clears only after successful Write.

---

## 6. Validation Contract (LOCKED)

### 6.1 Two Phases
1. **Write Phase** (mutation boundary)
   Validates:
   - structural correctness
   - required fields
   - type correctness
   - `unique_by`
   On failure: IR unchanged.

2. **Generate Phase** (projection boundary)
   Validates:
   - structural re-check
   - semantic rules
   - cross-field constraints
   - runtime export constraints
   On failure: preview unchanged.

### 6.2 Error Object Model
Minimum fields:
- `path: string`
- `message: string`
- `phase: write | generate`
- `severity: error`

Path format:
- arrays use explicit indices: `listeners[1].port`
- dot-separated nesting: `memory[0].policy.rules[2].allow_fc`

No popups for validation. Highlight affected nodes/fields and show a single-line status summary.

---

## 7. UI Surface Contract (LOCKED)

### 7.1 Top-Level Menus
Exactly:
- File
- Edit
- Help

### 7.2 Right Workspace Tabs
Exactly three:
1. **Model**
2. **Docs**
3. **Preview**

No additional tabs unless formally documented.

### 7.3 Tab Responsibilities
- **Model**: schema-governed editing; Write is the only IR mutation operation; Dirty tracked.
- **Docs**: read-only schema-derived help.
- **Preview**: full-document generated output; controls: Generate + Export Config.

Generate belongs exclusively to Preview (full projection).

### 7.4 Title Bar
Reflects Active Schema, optionally Active Document.

Primary:
- `ZENO -- <ActiveSchemaName>`

Extended:
- `ZENO -- <ActiveSchemaName> -- <ActiveDocumentName>`

Title changes only on schema load/unload and document open/close.

---

## 8. Schema-Defined Identity (LOCKED)

Schema may define:
```yaml
zeno_schema: 1.0
application: MMA
version: 2.0
icon: icons/mma.png
```

Behavior:
- Title uses schema metadata when available; fallback to filename.
- Icon resolved relative to schema directory.
- Missing icon file must not crash; fallback to default icon.

Theming (accent color, layout hints, toolbars) is deferred.

---

## 9. Non-Negotiables (Quick Checklist)

- IRStore is the single truth.
- No implicit node creation (especially array items).
- No UI guessing: all structure is schema-derived.
- No direct IR mutation from UI.
- All mutations go through OperationProcessor.
- Write and Generate are separate and explicit.
- Generate does not mutate IR.
- Export does not call Generate.
- Dirty disables Generate and Export.
- Validation errors are structured objects; UI only consumes them.
- No popup validation dialogs.

---

## 10. Appendix: Source Documents (Reference)

This lock consolidates these specs:
- CONFIG_MODE_BEHAVIOR.md
- IR_v0.1.md
- SCHEMA_SPEC.md
- VALIDATION_ENGINE.md
- OPERATION_MODEL.md
- UI_BEHAVIOR.md
- ERROR_MODEL.md
- ADDENDUM.md
- ZENO_UI_Architecture_v2.2.md
- Python_Programming_Guidelines_Universal_v1.1.md
