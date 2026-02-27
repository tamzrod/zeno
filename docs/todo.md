# ZENO Project Initialization TODO

This checklist initializes the project in a deterministic, architecture-first manner.

---

## 1. Environment Setup

- [ ] Confirm Python version (>= 3.10)
- [ ] Create and activate virtual environment
- [ ] Install project dependencies
- [ ] Freeze dependencies to `requirements.txt`
- [ ] Verify VS Code settings (Python interpreter, linting, formatting)

---

## 2. Repository Structure Validation

- [ ] Verify `/src/zeno/` folder structure
- [ ] Verify `/docs/` contains authoritative specs
- [ ] Confirm `.continue/` config is correct (local Ollama only)
- [ ] Remove legacy or duplicate config files
- [ ] Ensure no conflicting YAML/JSON configs exist

---

## 3. Architecture Lock Confirmation

- [ ] Confirm `ARCHITECTURE_LOCK.md` is authoritative
- [ ] Mark superseded documents clearly (if any)
- [ ] Ensure UI spec matches File Menu spec
- [ ] Confirm Write / Generate / Export lifecycle consistency
- [ ] Confirm Dirty-state gating rules are documented

---

## 4. IR Layer Readiness

- [ ] Confirm IR node model matches `IR_v0.1.md`
- [ ] Validate structural invariants are documented
- [ ] Ensure no schema rules leak into IR layer
- [ ] Confirm UUID identity rule enforcement plan

---

## 5. Schema Layer Validation

- [ ] Confirm strict grammar enforcement rules
- [ ] Verify `unique_by` rules documented and scoped
- [ ] Confirm array expansion rules defined
- [ ] Ensure no implicit node creation policy is documented

---

## 6. Validation Engine Initialization

- [ ] Confirm Write-phase validation scope
- [ ] Confirm Generate-phase validation scope
- [ ] Confirm error object schema defined
- [ ] Confirm no popup validation policy

---

## 7. UI Surface Contract

- [ ] Confirm exactly 3 tabs (Model / Docs / Preview)
- [ ] Confirm File / Edit / Help menu only
- [ ] Confirm Generate is Preview-only
- [ ] Confirm Export does NOT call Generate
- [ ] Confirm Title Bar contract documented

---

## 8. File Menu Integrity

- [ ] Confirm no "Close" or "Unload Schema"
- [ ] Confirm Config Wizard exists and obeys validation rules
- [ ] Confirm Save does not trigger Generate
- [ ] Confirm Dirty state protection on Exit

---

## 9. Local AI Workflow Setup

- [ ] Confirm Ollama running
- [ ] Confirm `deepseek-coder:6.7b` loads
- [ ] Confirm Continue uses local model only
- [ ] Create `AUDIT_CONTEXT.md`
- [ ] Define Planner → Worker prompt structure

---

## 10. Next Phase Definition

- [ ] Define MVP feature scope
- [ ] Define first implementation target (UI shell or IR core)
- [ ] Create implementation roadmap document
- [ ] Define test strategy (unit vs integration)

---

# Initialization Complete When:

- All authoritative documents aligned
- No conflicting configs
- Lifecycle rules consistent
- Local AI workflow stable
- Implementation phase clearly scoped