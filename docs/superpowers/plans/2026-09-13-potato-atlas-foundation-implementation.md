# Potato Atlas Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish the approved Atlas architecture as executable repository infrastructure before destructive migration.

**Architecture:** Add a machine-readable constitution, Node schema, North-spine registry and validators first. Then introduce one shared web shell, generate canonical Atlas pages, convert domain pages into Views, overhaul the summit, and deprecate old ownership contracts only after compatibility checks pass.

**Tech Stack:** Python 3 stdlib, JSON/JSON Schema, static HTML/CSS/JS, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-13-potato-atlas-permanent-architecture-design.md`

## Global Constraints
- Work on `potato-atlas-foundation`, not `main`.
- Do not move/delete canonical content in foundation tasks.
- One active non-root Node has one `north_parent`; North chains are acyclic and terminate at root.
- Domain pages are Views, not canonical owners.
- Builders produce; validators only inspect.
- Static HTML owns meaning/navigation; JS progressively enhances.
- Preserve epistemic and provenance boundaries.
- Preserve compatibility routes during migration.

---

### Task 1: Machine-readable constitution
Create `data/atlas-constitution.json` and `scripts/validate_atlas_constitution.py`; add the validator to CI. Write the validator first, verify it fails while the JSON is absent, add the constitution, verify PASS, then commit `feat: encode Potato Atlas constitution`.

### Task 2: Atlas Node schema
Create `knowledge/schema/atlas-node.schema.json` and `scripts/validate_atlas_node_schema.py`; add CI. Require stable identity, status, owner path, `north_parent`, summary, epistemic classes, relations, Archive refs, Views and stable route. Keep relations and Archive refs separate. Commit `feat: add Atlas node schema`.

### Task 3: Seed North registry
Create `data/atlas-registry.json` and `scripts/validate_atlas_north.py`; add CI. Enforce one active root, one parent for each active non-root, resolving parents, no cycles, every chain reaching root, unique IDs/routes and existing owner paths. Seed conservatively rather than auto-promoting the repository. Commit `feat: establish Atlas North spine`.
