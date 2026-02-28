# CODE vs. DOCUMENTATION CONFLICTS

**Status:** In Progress (2 of 7 RESOLVED)  
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

## CONFLICT 4: Validator Uses Wrong IR Type (CRITICAL)

**Priority:** P0 (Blocking validation)

**Documentation Authority:**
- [VALIDATION_ENGINE.md](VALIDATION_ENGINE.md): Validates IR
- [IR_v0.1.md](IR_v0.1.md): Defines IR as UUID-based Node

**Documentation States:**
- Validation engine validates IR
- IR is UUID-based Node model

**Current Implementation:**
```python
# src/zeno/schema/ir_validator.py
def validate(root: IRNode) -> None:  # ✗ Uses IRNode, not Node
    ...
```

**Impact:**
- Cannot validate core engine's IR (`Node` instances)
- Write and Generate validation phases cannot function
- Type mismatch prevents integration

**Resolution Required:**
1. Update validator to accept `Node` instead of `IRNode`
2. Navigate tree using `node.children` (list of UUIDs) and `IRStore`
3. Align with schema-driven validation rules from documentation

---

## CONFLICT 5: Mode Flag Contradicts Document-Centric Architecture

**Priority:** P2 (Architectural hygiene)

**Documentation Authority:**
- [OPERATION_MODEL_v2.0.md](OPERATION_MODEL_v2.0.md) Section 1: "ZENO is document-centric. There are no manual modes."
- [UI_BEHAVIOR_v2.3.md](UI_BEHAVIOR_v2.3.md) Section 3: "There is no Schema Mode or Config Mode."

**Documentation States:**
- No manual mode switching
- Behavior determined by Active Schema and Active Document state
- No mode flags

**Current Implementation:**
```python
# src/zeno/ui/app.py
self._in_config_mode: bool = False  # ✗ Violates "no modes" rule
```

**Impact:**
- Introduces forbidden mode concept
- Conflicts with document-centric philosophy

**Resolution Required:**
1. Remove `_in_config_mode` flag
2. Determine state by checking: `self._store is not None and self._root_id is not None`
3. Use presence of Active Document as state indicator, not mode flag

---

## CONFLICT 6: "Generate Node" Button Placement Ambiguity

**Priority:** P3 (UX clarity)

**Documentation Authority:**
- [ZENO_UI_Architecture_v2.3.md](ZENO_UI_Architecture_v2.3.md) Section 3.1: "Model Tab... Optional: Node-level read-only preview"
- [ZENO_UI_Architecture_v2.3.md](ZENO_UI_Architecture_v2.3.md) Section 3.3: "Full-document Generate belongs exclusively to Preview tab"
- [ZENO_UI_Architecture_v2.3.md](ZENO_UI_Architecture_v2.3.md) Section 8: "Generate Location Clarification (LOCKED)"

**Documentation States:**
- Model tab may include "node-level read-only preview"
- Full projection must occur only in Preview tab
- Generate belongs to Preview tab

**Current Implementation:**
```python
# src/zeno/ui/right_panel.py (Model Tab)
self.btn_generate_node = QPushButton("Generate Node")  # Ambiguous
```

**Ambiguity:**
- Button name suggests generation action
- Documentation allows "node-level preview" but doesn't call it "Generate"

**Resolution Required:**
1. Rename button to clarify it's preview-only: "Preview Node Output" or "Show Node"
2. OR: Remove button entirely and show preview automatically on Write
3. Ensure it doesn't confuse users expecting full Generate in Preview tab

---

## CONFLICT 7: Missing Parse Function (HIGH)

**Priority:** P0 (Blocking Open Config)

**Documentation Authority:**
- [FILE_MENU_SPEC.md](FILE_MENU_SPEC.md) Section 5.2: Open Config
- [OPERATION_MODEL_v2.0.md](OPERATION_MODEL_v2.0.md) Section 4.3: "Config parsed into IR via adapter"

**Documentation States:**
- Open Config must parse YAML/config file into IR
- Adapter provides parse capability

**Current Implementation:**
```python
# src/zeno/adapters/yaml_adapter.py
# Only serialize() exists
# parse() is MISSING
```

**Impact:**
- Open Config menu item cannot function
- Users cannot load existing configuration files
- Core workflow broken

**Resolution Required:**
1. Implement `def parse(yaml_text: str, schema: SchemaType) -> Node`
2. Create Node tree with proper UUID assignment
3. Preserve ordering from YAML source
4. Link nodes correctly using IRStore

---

## ALIGNED AREAS (No Conflicts)

The following areas are correctly implemented per documentation:

✓ **Right Panel Tab Names**: Model / Docs / Preview  
✓ **Export Button Placement**: In Preview tab  
✓ **Schema Expansion Logic**: Matches CONFIG_EDITING_BEHAVIOR_v2.0.md  
✓ **Dirty State Gating**: Generate/Export disabled when Dirty  
✓ **File Menu Structure**: Correct items (though functionality incomplete)  
✓ **OperationProcessor Pattern**: All mutations go through processor

---

## RESOLUTION PRIORITY

### Phase 1 (P0 — Blocking)
1. Resolve Dual IR Models (Conflict 1)
2. Fix Adapter Contract (Conflict 3)
3. Fix Validator Type (Conflict 4)
4. Implement Parse Function (Conflict 7)

### Phase 2 (P1 — Documentation)
5. Document `key` field (Conflict 2)

### Phase 3 (P2 — Architecture Cleanup)
6. Remove mode flag (Conflict 5)

### Phase 4 (P3 — UX Polish)
7. Clarify Generate Node button (Conflict 6)

---

**Next Steps:**
1. Fix Conflict 1 first (dual IR models)
2. All other conflicts depend on resolving the IR split
3. Work through priority order
4. Validate each fix against documentation
5. Update this document as conflicts are resolved

---

End of Document.
