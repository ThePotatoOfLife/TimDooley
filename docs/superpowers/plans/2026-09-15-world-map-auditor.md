# World Map Auditor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic static architecture auditor for the canonical World Map, publish its report in CI, and use the first live report to select the next hardening wave from evidence.

**Architecture:** A Python scanner inventories high-confidence literal MapLibre/runtime mutations across `world-map/3d-*.js`, normalizes them into stable resource identities, applies a checked-in ownership contract, and emits findings/risk domains to JSON. Existing World Map validators remain authoritative; the auditor detects cross-module ownership/lifecycle risks they cannot see globally.

**Tech Stack:** Python 3 standard library, JSON, regex/static source scanning, existing GitHub Actions workflow.

**Spec:** `docs/superpowers/specs/2026-09-15-world-map-auditor-design.md`

## Global Constraints

- Python standard library only; no new parser/runtime dependency.
- Only high-confidence static findings independently block CI in v1.
- Existing World Map specialist validators are retained unchanged unless CI wiring requires a reference.
- `world-map-audit-report.json` is generated, deterministic except `generated_at`, and not committed.
- Every contract exception/shared owner needs a human-readable rationale.
- TDD RED must precede production scanner/rule implementation.

---

### Task 1: RED contract for auditor surface

**Files:**
- Create: `scripts/test_world_map_auditor.py`

**Interfaces:**
- Consumes: future CLI `python scripts/audit_world_map.py --root <dir> --contract <file> --report <file>`.
- Produces: executable test contract covering report shape, extraction, collisions, popup convention, stale contract warning, and deterministic ordering.

- [ ] **Step 1: Write failing tests**

Create temporary mini-repositories in Python. Each fixture must contain `world-map/3d-a.js`, optional `3d-b.js`, and a contract file. Tests invoke the future CLI and assert on JSON output/exit code.

Required cases:

```python
class AuditorTests(unittest.TestCase):
    def test_inventory_extracts_literal_mutations(self): ...
    def test_duplicate_source_and_layer_creation_block(self): ...
    def test_duplicate_feature_state_blocks_unless_shared(self): ...
    def test_hover_popup_requires_atlas_hover_class(self): ...
    def test_multiple_styledata_participants_warn(self): ...
    def test_stale_contract_owner_warns_or_errors_by_semantics(self): ...
    def test_report_order_is_deterministic(self): ...
```

- [ ] **Step 2: Run test to verify RED**

Run: `python scripts/test_world_map_auditor.py`

Expected: FAIL because `scripts/audit_world_map.py` does not exist.

- [ ] **Step 3: Commit RED**

Commit message: `test(world-map): define architecture auditor contract`

---

### Task 2: Minimal scanner and report engine

**Files:**
- Create: `scripts/audit_world_map.py`
- Modify: `scripts/test_world_map_auditor.py`

**Interfaces:**
- CLI: `audit_world_map.py [--root PATH] [--contract PATH] [--report PATH]`
- Core functions:
  - `discover_modules(root: Path) -> list[Path]`
  - `scan_module(path: Path, repo_root: Path) -> list[dict]`
  - `load_contract(path: Path) -> dict`
  - `analyze(records: list[dict], contract: dict, existing_modules: set[str]) -> tuple[list[dict], dict]`
  - `build_report(records: list[dict], findings: list[dict], ownership: dict) -> dict`
  - `main(argv: list[str] | None = None) -> int`

- [ ] **Step 1: Implement only extraction needed by current RED tests**

Recognize literal `addSource`, `addLayer`, `setFeatureState`, `setPaintProperty`, `setLayoutProperty`, `getSource(...).setData`, `map.on`, `styledata`, popup creation/hover markup, search-param writes, `window.__potatoAtlas*` assignment, and DOM id assignment. Store file+line evidence.

- [ ] **Step 2: Implement rule engine minimally**

Blocking: duplicate source/layer creation, duplicate feature-state source/key writer, hover popup convention violation, absent declared canonical owner.

Warning: multiple styledata participants and stale shared/ignore entries.

- [ ] **Step 3: Implement deterministic JSON report**

Sort modules, records, ownership keys, findings and actions. Keep `generated_at` as the sole non-deterministic field.

- [ ] **Step 4: Run tests GREEN**

Run: `python scripts/test_world_map_auditor.py`

Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat(world-map): add static architecture auditor`

---

### Task 3: Live ownership contract and repository audit

**Files:**
- Create: `data/world-map-audit-contract.json`
- Modify: `scripts/test_world_map_auditor.py`

**Interfaces:**
- Contract top-level: `schema_version`, `owners`, `shared`, `style_restoration`, `conventions`, `ignore`, `render_stack_slots`.

- [ ] **Step 1: Add RED assertions for contract validation**

Tests must reject shared entries without rationale, owner entries with missing modules, and unknown render-stack slot usage when scanner can resolve it.

- [ ] **Step 2: Run RED**

Run: `python scripts/test_world_map_auditor.py`

Expected: FAIL on new contract-validation behaviors.

- [ ] **Step 3: Add contract validation and render-stack extraction**

Known slots:

```json
[
  "physical-surface",
  "physical-water",
  "physical-line",
  "geography-context",
  "context-network",
  "selection-emphasis"
]
```

- [ ] **Step 4: Build live contract from actual repository inventory**

Declare only intentional owners/sharing that can be explained from current code. Do not silence unexplained collisions.

- [ ] **Step 5: Run live audit**

Run: `python scripts/audit_world_map.py`

Expected: report generated. Blocking errors must be investigated; warnings are allowed.

- [ ] **Step 6: Commit**

Commit message: `chore(world-map): declare runtime ownership contract`

---

### Task 4: CI report retention and enforcement

**Files:**
- Modify: `.github/workflows/quality-checks.yml`
- Modify: `scripts/test_world_map_auditor.py`

**Interfaces:**
- Workflow step id: `world_map_audit`
- Artifact name: `world-map-audit-report`

- [ ] **Step 1: Add RED workflow-source assertions**

Test requires all three markers:

```text
Audit World Map runtime architecture
Upload World Map audit report
Enforce World Map audit gate
```

and requires upload to occur under `always()` before enforcement.

- [ ] **Step 2: Run RED**

Run: `python scripts/test_world_map_auditor.py`

Expected: FAIL because workflow steps are absent.

- [ ] **Step 3: Modify workflow**

Place audit immediately after `Validate canonical World Map runtime`, use `continue-on-error: true`, upload report with `actions/upload-artifact@v4`, then enforce if audit outcome is failure.

- [ ] **Step 4: Run focused GREEN**

Run:

```bash
python scripts/test_world_map_auditor.py
python scripts/audit_world_map.py
python scripts/validate_world_map_source.py
```

Expected: all pass; live report has zero blocking errors.

- [ ] **Step 5: Commit**

Commit message: `ci(world-map): retain architecture audit report`

---

### Task 5: Evidence-led first hardening decision

**Files:**
- Read generated: `world-map-audit-report.json`
- Modify only if a bounded root cause is confirmed: relevant World Map module/test files.

**Interfaces:**
- Consumes `risk_domains`, `findings`, `next_actions` from the auditor report.
- Produces either a documented no-change decision or one focused TDD bug/hardening slice.

- [ ] **Step 1: Rank live findings**

Inspect blocking/warning evidence for `feature_state`, `style_lifecycle`, `render_ownership`, and `event_lifecycle`.

- [ ] **Step 2: Select one root-cause hypothesis**

State the exact resource/module collision or lifecycle race. Do not patch a general category.

- [ ] **Step 3: If confirmed, write the failing regression first**

Add one focused regression reproducing the identified architecture defect.

- [ ] **Step 4: Implement one fix and verify**

Run the focused regression, auditor, canonical World Map runtime validator, UI layout validator, and full exact-head CI before merge.

- [ ] **Step 5: Commit**

Use a message naming the actual root cause, not generic “cleanup”.

---

### Task 6: Integration verification

**Files:** no new files required unless reconciliation is needed.

- [ ] **Step 1: Rebase/reconcile against current `main` without losing concurrent Great Book work**

- [ ] **Step 2: Run exact-head focused checks**

```bash
python scripts/test_world_map_auditor.py
python scripts/audit_world_map.py
python scripts/validate_world_map_source.py
python scripts/validate_world_map_ui_layout.py
```

- [ ] **Step 3: Run full Repository quality checks on the exact reconciled head**

Expected: success with audit artifact uploaded.

- [ ] **Step 4: Review report artifact**

Confirm zero blocking errors and record top remaining warnings for the next map wave.

- [ ] **Step 5: Merge only after exact-head CI success**

Preserve the feature branch and use expected-head/merge SHA verification.