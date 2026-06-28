# Specification — M2-03: Publish and Verify Platform Documentation

**Source:** GitHub Issue #74
**Priority:** P0
**Labels:** `documentation`

---

## Problem Statement

Platform documentation files must be verified and published. ARCHITECTURE.md,
KNOWN_LIMITATIONS.md, and CHANGE_IMPACT_MAP.md exist but may contain stale paths,
outdated version references, or missing cross-links. A final pass ensures these
three core docs are accurate, complete, and pass validation gates.

---

## Requirements

### Functional Requirements

1. **FR-1:** `docs/ARCHITECTURE.md` must map OTel Collector pipelines, service ports,
   container dependencies, and all configuration file paths with current values from
   `compose.yaml`
2. **FR-2:** `docs/KNOWN_LIMITATIONS.md` must document storage limits, retention behaviors,
   authentication gaps, and development setup caveats
3. **FR-3:** `docs/CHANGE_IMPACT_MAP.md` must map cross-service and cross-plane effects
   with correct file paths

### Non-functional Requirements

4. **NFR-1:** All three docs pass `markdownlint`
5. **NFR-2:** All file paths referenced in CHANGE_IMPACT_MAP.md must resolve to actual files

---

## Acceptance Criteria

- [ ] `docs/ARCHITECTURE.md` exists and passes markdownlint
- [ ] `docs/KNOWN_LIMITATIONS.md` exists and passes markdownlint
- [ ] `docs/CHANGE_IMPACT_MAP.md` exists and passes markdownlint
- [ ] All file paths in CHANGE_IMPACT_MAP.md are verified against actual filesystem paths

---

## Out of Scope

- Creating new documentation files beyond the three target docs
- Adding new limitations or architecture changes
- Updating README.md or GitHub metadata (M2-04)
- Adding version badge or CI status badge (M2-04)
