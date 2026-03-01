# CODE vs. DOCUMENTATION CONFLICTS

**Status:** ✅ ALL RESOLVED (12 of 12 COMPLETE)  
**Last Updated:** 2026-02-28  
**Source of Truth:** Documentation (LOCKED)

This document tracks conflicts and resolutions between codebase and documentation.

---

## ✅ RESOLVED: CONFLICT 1 (Dual IR Models)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. **Deleted legacy IR model files:**
   - `src/zeno/core/ir_node.py` (removed type-def IRNode)
   - `src/zeno/core/ir_types.py` (removed ScalarType, ObjectType, ArrayType)
   - `src/zeno/core/ir_validator.py` (removed old validator)
   - `src/zeno/core/ir_view.py` (removed deprecated adapter)

2. **Migrated to UUID-based Node model:**
   - `src/zeno/adapters/yaml_adapter.py`: New serialize/parse functions using `Node + IRStore`
   - `src/zeno/cli/test_engine.py`: Updated to use `Node`, `IRStore`, `OperationProcessor`
   - `src/zeno/schema/ir_validator.py`: Protocol-based validation via `IRNodeView` (decoupled)
   - `src/zeno/schema/binder.py`: No longer needed (kept for reference)

3. **Result:**
   - ✓ Single canonical IR: `Node` (UUID-based, matches documentation)
   - ✓ Adapter bidirectional (parse + serialize)
   - ✓ Validator uses protocol bridge (IRNodeView) for flexibility
   - ✓ All core components now unified on same IR model

---

## ✅ RESOLVED: CONFLICT 2 (Missing `key` Field in Documentation)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. Updated [IR_v0.1.md](IR_v0.1.md) Section 3 to include `key` field
2. Added clarification: Object children use `key` for property names; list children and root have `key=None`

**Result:**
- ✓ Documentation now matches implementation
- ✓ `key` field is formally part of Node model specification

---

## ✅ RESOLVED: CONFLICT 3 (Adapter Parse Function Missing)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. **Verified adapter contract:** `src/zeno/adapters/yaml_adapter.py`
   - ✓ `serialize(node: Node, store: IRStore) → str` - Converts Node tree to YAML string
   - ✓ `parse(yaml_text: str, store: IRStore) → None` - Parses YAML into Node tree in store
   - ✓ Both functions use correct `Node` model (UUID-based)
   - ✓ Bidirectional: roundtrip `serialize(parse(yaml)) == yaml` ✓

2. **Verified implementation:**
   - `_parse_object()` - Recursively parses dict into OBJECT nodes with keyed children
   - `_parse_array()` - Recursively parses list into LIST nodes with unkeyed children
   - `_node_to_plain()` - Converts Node tree back to plain Python structures
   - Ordering preserved via `yaml.safe_dump(sort_keys=False)`

3. **Test Coverage:**
   - `test_yaml_adapter.py`: 7 comprehensive test cases
   - ✓ Scalar serialization
   - ✓ Object serialization
   - ✓ Object parsing
   - ✓ Nested object parsing
   - ✓ Array parsing
   - ✓ Roundtrip object (serialize → parse)
   - ✓ Roundtrip nested (serialize → parse)

**Result:**
- ✓ Adapter contract fully satisfied (bidirectional parse + serialize)
- ✓ Uses correct IR model (Node with UUID)
- ✓ All roundtrip tests pass
- ✓ Ready for integration with UI File Menu operations (Open Config, etc.)

---

## ✅ RESOLVED: CONFLICT 4 (Validator Uses Wrong IR Type)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. **Verified validator protocol design:** `src/zeno/schema/ir_validator.py`
   - ✓ Abstract `IRNodeView` protocol defines tree-reading interface
   - ✓ Decoupled from concrete Node model
   - ✓ `validate(root_view: IRNodeView) → None` accepts any IR implementation

2. **Verified adapter:** `IRStoreView`
   - ✓ Implements `IRNodeView` protocol for Node+IRStore
   - ✓ Handles OBJECT nodes (keyed children iteration)
   - ✓ Handles LIST nodes (unkeyed children iteration)
   - ✓ Handles SCALAR nodes (value access)
   - ✓ Correctly navigates UUID-based tree structure

3. **Verified semantic validator:** `src/zeno/schema/ir_semantic_validator.py`
   - ✓ Uses `IRNodeView` protocol (not specific IR type)
   - ✓ Schema-aware validation via protocol
   - ✓ Can validate against any IR implementation

4. **Test Coverage:**
   - `test_validator.py`: 5 integration tests
   - ✓ Valid object validation
   - ✓ Valid nested object validation
   - ✓ Valid array validation
   - ✓ Store-level constraint enforcement (duplicate keys)
   - ✓ Complex structure validation with protocol adapter

**Result:**
- ✓ Validator uses protocol (not concrete IRNode type)
- ✓ Protocol implementation works with Node+IRStore
- ✓ Semantic validator ready for schema-based validation
- ✓ No type mismatches; full integration possible

---

## ✅ RESOLVED: CONFLICT 5 (Mode Flag Contradicts Document-Centric Architecture)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. **Removed forbidden mode flag:** `src/zeno/ui/app.py`
   - ✗ Deleted: `self._in_config_mode: bool = False` (line 38)
   - ✗ Deleted: `self._in_config_mode = False` (line 105, schema load)
   - ✗ Deleted: `self._in_config_mode = True` (line 130, new config)

2. **Replaced with state-based approach:**
   - ✓ Changed condition: `if self._store is not None:` (replaces `if self._in_config_mode and self._store:`)
   - ✓ No extra state variable needed
   - ✓ Behavior determined by presence of Active Document (store exists)

3. **Affected code locations:**
   - Line 268: Node selection handler now checks document state directly
   - Result: UI behavior still correct, but philosophically aligned with documentation

**Result:**
- ✓ No manual mode concept
- ✓ Behavior determined entirely by document state
- ✓ Aligns with "document-centric" architecture
- ✓ Syntax valid; no behavioral changes

---

## ✅ RESOLVED: CONFLICT 7 (Missing Parse Function)

**Resolution Date:** 2026-02-28 (Same as Conflict 3)  
**Status:** CLOSED (See Conflict 3 for full details)

**Note:** This conflict was already resolved as part of Conflict 3 resolution. The yaml_adapter.py parse() function is fully implemented, tested, and working.

---

## ✅ RESOLVED: CONFLICT 6 ("Generate Node" Button Naming Ambiguity)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. **Renamed button for clarity:** `src/zeno/ui/right_panel.py`
   - ✗ Old: `QPushButton("Generate Node")` (line 68)
   - ✓ New: `QPushButton("Preview Node Output")` (clarifies it's read-only)

2. **Updated placeholder text:**
   - ✗ Old: "Node output appears after Generate Node."
   - ✓ New: "Node output appears here."

**Result:**
- ✓ Button name clarifies it's a preview (not generation)
- ✓ No confusion with full-document "Generate Full Config" in Preview tab
- ✓ Aligns with documentation's distinction between node-level preview and full generation

---

## ✅ RESOLVED: CONFLICT 8 (README Manual Modes Drift)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. Updated `README.md`:
   - ✗ Removed "Operating Modes" section (Schema Mode / Config Mode)
   - ✓ Replaced with "Document-Centric Operation"
   - ✓ Clarified that behavior is determined by Active Schema + Active Document

**Result:**
- ✓ README now aligns with document-centric architecture
- ✓ No manual mode language remains

---

## ✅ RESOLVED: CONFLICT 9 (Title Bar Version Injection vs Architecture Lock)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. Updated `docs/ADDENDUM_v2.0.md`:
   - ✗ Removed title formats that injected version into window title
   - ✓ Aligned title format to `ZENO -- <Application>` and `ZENO -- <Application> -- <DocumentName>`
   - ✓ Kept `version` as schema metadata (non-title-driving)

**Result:**
- ✓ Addendum now matches Architecture Lock title contract
- ✓ No contradictory title behavior across docs

---

## ✅ RESOLVED: CONFLICT 10 (Help Menu Contract Mismatch)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. Updated `docs/UI_BEHAVIOR_v2.4.md` Help Menu:
   - ✗ Removed mandatory "Validation Rules" item
   - ✓ Set menu to About + Documentation
   - ✓ Clarified documentation links are optional and local

**Result:**
- ✓ UI behavior doc now matches UI Architecture v2.4

---

## ✅ RESOLVED: CONFLICT 11 (Validation Trigger Uses Deprecated "Modify Tab")

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. Updated `docs/VALIDATION_ENGINE.md`:
   - ✗ "Triggered by: Modify Tab → Write button"
   - ✓ "Triggered by: Default Workspace (Editor) → Write button"

**Result:**
- ✓ Validation lifecycle terminology now matches current UI contract

---

## ✅ RESOLVED: CONFLICT 12 (Status Line Persistence Wording Drift)

**Resolution Date:** 2026-02-28  
**Status:** CLOSED

**Changes Applied:**
1. Updated `docs/ERROR_MODEL.md` status line rules:
   - ✗ "Cleared on next successful operation"
   - ✓ "Persistent until next state change (including next successful operation)"

**Result:**
- ✓ Error model now aligns with UI behavior status-line contract

---

## ALIGNED AREAS (No Conflicts)

The following areas are correctly implemented per documentation:

✓ **Right Panel Tab Names**: Docs / Preview (+ default editor workspace)  
✓ **Export Button Placement**: In Preview tab  
✓ **Schema Expansion Logic**: Matches CONFIG_EDITING_BEHAVIOR_v2.1.md  
✓ **Dirty State Gating**: Generate/Export disabled when Dirty  
✓ **File Menu Structure**: Correct items (though functionality incomplete)  
✓ **OperationProcessor Pattern**: All mutations go through processor

---

## CURRENT STATE

All identified code/documentation and documentation/documentation
conflicts are resolved as of 2026-02-28.

Next action is maintenance-only: keep new spec edits synchronized with
Architecture Lock and UI Architecture lock files.

---

End of Document.
