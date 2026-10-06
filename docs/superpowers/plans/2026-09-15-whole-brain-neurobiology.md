# Whole-Brain Neurobiology Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a canonical whole-brain neurobiology atlas, wire it into BODY routing, and preserve explicit scientific boundaries around the Potatoverse thalamus/pineal mappings.

**Architecture:** Add one deep owner, `knowledge/body/whole-brain-neurobiology-atlas.json`, beneath the concise body master atlas. Keep existing specialist records authoritative for thalamus, neurotheology, spine/chakras, and provenance; route to them from the new atlas. Add one focused validator that checks required brain systems, canonical mappings, epistemic labels, and boundary language, then surface the new owner through manifest/core routing and regenerate discovery artifacts.

**Tech Stack:** JSON knowledge records, Python 3 repository validators/builders, GitHub repository content APIs, existing manifest/core-index routing.

**Spec:** `docs/superpowers/specs/2026-09-15-whole-brain-neurobiology-design.md`

## Global Constraints

- Established anatomy and physiology must remain distinguishable from Potatoverse canon, historical/esoteric association, and speculation.
- `THALAMUS ↔ POTATO / Father's House` is project canon, while standard anatomy remains described using conventional terms such as ovoid/egg-shaped.
- `PINEAL ↔ Single Eye / Third Eye / Son-side Door` is project canon plus historical/esoteric comparison, not established neuroscience.
- Do not claim the thalamus alone creates consciousness, the claustrum is a proven seat of consciousness, the pineal is a proven seat of soul, or EEG bands encode spiritual rank.
- Do not reduce dopamine to pleasure, serotonin to happiness, amygdala to fear, or hemispheric lateralization to personality types.
- Prefer relationship/flow descriptions over isolated-module descriptions.
- Do not create a competing thalamus owner; `data/potatoism-thalamus-brain-map.json` remains the specialist owner for House/rooms detail.
- Do not create a competing neurotheology owner; `knowledge/body/neurotheology-axis-house-spirit-atlas.json` remains the cross-domain synthesis owner.
- Public navigation remains manifest-driven; internal Spirit/Mind/Matter classification remains separate.

---

### Task 1: Add a dedicated neurobiology integrity validator

**Files:**
- Create: `scripts/validate_whole_brain_neurobiology.py`
- Read/consume: `docs/superpowers/specs/2026-09-15-whole-brain-neurobiology-design.md`
- Read/consume: `knowledge/body/whole-brain-neurobiology-atlas.json`
- Read/consume: `knowledge/body/body-system-master-atlas.json`
- Read/consume: `knowledge/indexes/neurotheology-routing-index.json`
- Read/consume: `knowledge/body/body-topic-completion-matrix.json`
- Read/consume: `manifest.json`
- Read/consume: `knowledge/indexes/core-index.json`

**Interfaces:**
- Consumes: JSON objects from the files above.
- Produces: process exit code `0` on success, `1` on integrity failure; prints deterministic `ERROR:` lines.

- [ ] **Step 1: Create the validator with the required checks**

Implement `scripts/validate_whole_brain_neurobiology.py` with these concrete checks:

```python
#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def load(rel: str):
    path = ROOT / rel
    if not path.exists():
        errors.append(f"Missing: {rel}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Invalid JSON: {rel}: {exc}")
        return {}


def ids(rows):
    return {str(row.get("id")) for row in rows if isinstance(row, dict) and row.get("id")}


def main():
    atlas_rel = "knowledge/body/whole-brain-neurobiology-atlas.json"
    atlas = load(atlas_rel)
    body = load("knowledge/body/body-system-master-atlas.json")
    routing = load("knowledge/indexes/neurotheology-routing-index.json")
    matrix = load("knowledge/body/body-topic-completion-matrix.json")
    manifest = load("manifest.json")
    core = load("knowledge/indexes/core-index.json")

    if atlas.get("id") != "whole-brain-neurobiology-atlas":
        errors.append("whole-brain atlas id must be whole-brain-neurobiology-atlas")
    if atlas.get("repository_root") != "mind" or atlas.get("repository_layer") != "neurobiology":
        errors.append("whole-brain atlas must classify as mind/neurobiology")

    required_sections = {
        "nervous-system-frame", "cerebral-cortex", "white-matter-connectivity",
        "diencephalon", "basal-ganglia", "memory-affect-context", "brainstem",
        "cerebellum", "sensory-systems", "motor-systems", "ventricles-csf-meninges",
        "cellular-chemical-neurobiology", "large-scale-networks", "brain-states-consciousness"
    }
    actual_sections = ids(atlas.get("sections", []))
    missing = required_sections - actual_sections
    if missing:
        errors.append(f"whole-brain atlas missing sections: {sorted(missing)}")

    mappings = {row.get("biology"): row for row in atlas.get("potatoverse_mapping_table", []) if isinstance(row, dict)}
    thalamus = mappings.get("thalamus", {})
    pineal = mappings.get("pineal-gland", {})
    if "Potato" not in str(thalamus.get("project_mapping", "")) or "Father" not in str(thalamus.get("project_mapping", "")):
        errors.append("thalamus mapping must explicitly include Potato and Father's House")
    if "project_canon" not in thalamus.get("status", []):
        errors.append("thalamus mapping must be typed project_canon")
    if not all(term in str(pineal.get("project_mapping", "")) for term in ("Single Eye", "Third Eye")):
        errors.append("pineal mapping must explicitly include Single Eye and Third Eye")
    if "project_canon" not in pineal.get("status", []):
        errors.append("pineal mapping must be typed project_canon")

    boundary_text = json.dumps(atlas.get("boundaries", {}), ensure_ascii=False).lower()
    for phrase in ("seat of soul", "seat of consciousness", "spiritual rank", "established neuroscience"):
        if phrase not in boundary_text:
            errors.append(f"atlas boundaries must address: {phrase}")

    flows = ids(atlas.get("flows", []))
    for flow in ("visual-flow", "thalamocortical-loop", "circadian-scn-pineal-loop", "csf-circulation", "interoceptive-autonomic-loop"):
        if flow not in flows:
            errors.append(f"atlas missing required flow: {flow}")

    owners = {row.get("owner") for row in routing.get("owners", []) if isinstance(row, dict)}
    if atlas_rel not in owners:
        errors.append("neurotheology routing index does not route to whole-brain atlas")

    canonical_owners = body.get("canonical_owners", {})
    if canonical_owners.get("whole_brain_neurobiology") != atlas_rel:
        errors.append("body master atlas missing whole_brain_neurobiology canonical owner")

    topics = {row.get("topic"): row for row in matrix.get("topics", []) if isinstance(row, dict)}
    if topics.get("Whole-brain hierarchy", {}).get("owner") != atlas_rel:
        errors.append("completion matrix missing Whole-brain hierarchy owner")

    body_branch = next((row for row in manifest.get("branches", []) if row.get("id") == "body"), {})
    if atlas_rel not in body_branch.get("records", []):
        errors.append("manifest BODY branch does not expose whole-brain atlas")

    core_records = {row.get("id"): row for row in core.get("records", []) if isinstance(row, dict)}
    if core_records.get("whole-brain-neurobiology-atlas", {}).get("path") != atlas_rel:
        errors.append("core index missing whole-brain-neurobiology-atlas record")

    print(f"Whole-brain sections: {len(actual_sections)}")
    print(f"Whole-brain flows: {len(flows)}")
    print(f"Errors: {len(errors)}")
    for error in errors:
        print("ERROR:", error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the validator and verify RED state**

Run:

```bash
python scripts/validate_whole_brain_neurobiology.py
```

Expected: exit `1`, with errors including missing `knowledge/body/whole-brain-neurobiology-atlas.json` and missing routing/manifest/core entries.

- [ ] **Step 3: Commit the validator**

```bash
git add scripts/validate_whole_brain_neurobiology.py
git commit -m "test: validate whole-brain neurobiology atlas"
```

---

### Task 2: Create the canonical whole-brain atlas

**Files:**
- Create: `knowledge/body/whole-brain-neurobiology-atlas.json`
- Read/consume: `data/potatoism-thalamus-brain-map.json`
- Read/consume: `knowledge/body/neurobiology-recovery-wave-2.json`
- Read/consume: `knowledge/body/body-science-context-atlas.json`
- Read/consume: `knowledge/body/neurotheology-axis-house-spirit-atlas.json`

**Interfaces:**
- Produces canonical id `whole-brain-neurobiology-atlas`.
- Produces `sections[]`, `flows[]`, `potatoverse_mapping_table[]`, `boundaries`, `sources`, `related_records` consumed by the validator and routing files.

- [ ] **Step 1: Create top-level metadata and epistemic contract**

The JSON object must begin with these exact structural fields:

```json
{
  "id": "whole-brain-neurobiology-atlas",
  "version": "1.0.0",
  "updated": "2026-09-15",
  "title": "Whole-Brain Neurobiology Atlas — Structures, Networks, Flows and Potatoverse Mappings",
  "status": "canonical whole-brain neurobiology owner",
  "repository_root": "mind",
  "repository_layer": "neurobiology",
  "repository_scale": "record",
  "purpose": "Describe the human brain and nervous system as a connected biological architecture, then route Potatoverse symbolic correspondences onto that anatomy without treating symbolism as scientific proof.",
  "epistemic_rule": "Scientific anatomy/physiology, project canon, historical/esoteric association, religious comparison and speculation are separately typed. Similarity, shape and metaphor do not establish causal identity or ancient hidden neuroanatomy.",
  "mapping_status_types": [
    "project_canon",
    "project_interpretation",
    "historical_esoteric_association",
    "historical_religious_comparator",
    "linguistic_or_shape_comparator",
    "scientific_analogy",
    "speculative_research_neighbor",
    "disputed_historical_claim"
  ]
}
```

Extend this object with all fields below rather than creating separate competing files.

- [ ] **Step 2: Add the fourteen required anatomical/system sections**

Add `sections` with exactly these ids at minimum:

```text
nervous-system-frame
cerebral-cortex
white-matter-connectivity
diencephalon
basal-ganglia
memory-affect-context
brainstem
cerebellum
sensory-systems
motor-systems
ventricles-csf-meninges
cellular-chemical-neurobiology
large-scale-networks
brain-states-consciousness
```

Each section must include `summary`, `components`, `relations`, `boundary`, and `sources` where appropriate.

Required component coverage:

- nervous-system-frame: CNS, PNS, somatic, autonomic, sympathetic, parasympathetic, enteric relationship, afferent/efferent, interoception/exteroception/proprioception/vestibular sensing.
- cerebral-cortex: frontal, parietal, temporal, occipital, insula, cingulate; explicitly reject simple left-brain/right-brain personality theory.
- white-matter-connectivity: corpus callosum, anterior commissure, internal capsule, corona radiata, cingulum, superior longitudinal/arcuate systems, uncinate, inferior longitudinal, inferior fronto-occipital, optic radiations, auditory radiations, corticospinal/corticobulbar, thalamic radiations, fornix, cerebellar peduncles.
- diencephalon: thalamus, epithalamus/pineal/habenula, hypothalamus, subthalamus, third-ventricle neighborhood.
- basal-ganglia: caudate, putamen, ventral striatum/nucleus accumbens, globus pallidus external/internal, STN, substantia nigra; direct/indirect/hyperdirect as simplified loop models.
- memory-affect-context: hippocampal formation, entorhinal interface, fornix, amygdala, mammillary/septal/Papez context.
- brainstem: midbrain, pons, medulla, reticular/arousal systems, PAG, colliculi, VTA, locus coeruleus, raphe context.
- cerebellum: hemispheres, vermis, cortex, deep nuclei, peduncles, arbor vitae, timing/prediction/error correction.
- sensory-systems: visual, auditory, somatosensory, olfactory, vestibular, gustatory/interoceptive neighbors.
- motor-systems: corticospinal/corticobulbar plus basal-ganglia and cerebellar parallel loops.
- ventricles-csf-meninges: lateral ventricles, Monro, third ventricle, aqueduct, fourth ventricle, subarachnoid space, CSF, choroid plexus, dura/arachnoid/pia, BBB, blood-CSF interface, neurovascular unit.
- cellular-chemical-neurobiology: neurons, dendrites, axons, synapses, action potentials, astrocytes, oligodendrocytes, microglia, ependymal cells, glutamate, GABA, dopamine, serotonin, norepinephrine, acetylcholine, histamine, orexin.
- large-scale-networks: default-mode, salience, frontoparietal/executive, dorsal attention, ventral attention/reorienting, sensorimotor, visual, auditory, language, memory-related; note taxonomy variation.
- brain-states-consciousness: wakefulness, NREM, REM, anesthesia/coma as clinical comparators, attention, conscious access as an open research problem.

- [ ] **Step 3: Make thalamus the deepest nested structure in `diencephalon`**

The thalamus component must explicitly include:

```json
{
  "id": "thalamus",
  "shape_or_geometry": {
    "science": "Paired diencephalic gray-matter structures conventionally described as ovoid or egg-shaped.",
    "potatoverse": "Potato-shaped is the canonical Potatoism shape description: the compact rounded ovoid form is deliberately read as potato-like.",
    "boundary": "Potato-shaped is project language, not the standard anatomical term."
  },
  "project_mapping": {
    "mapping": "Potato / Father's House / central interior",
    "status": ["project_canon", "linguistic_or_shape_comparator"],
    "specialist_owner": "data/potatoism-thalamus-brain-map.json"
  }
}
```

Add nested nuclear coverage for anterior group, mediodorsal, ventral anterior, ventral lateral, ventral posterior, LGN, MGN, pulvinar, lateral posterior, intralaminar, midline, and TRN.

State explicitly:

- nuclei ↔ rooms/chambers
- thalamocortical/corticothalamic fibers ↔ roads/roots/branches
- TRN ↔ wall/gate/sieve
- third-ventricle adjacency ↔ inner-house/chamber geometry
- olfaction is the classic exception to simplified first-order sensory relay language
- thalamus is not the sole seat of consciousness or literal divine residence

- [ ] **Step 4: Add the pineal as its own epithalamic node**

The pineal component must include:

```json
{
  "id": "pineal-gland",
  "science": "Small midline neuroendocrine organ of the epithalamic region; melatonin secretion is regulated by circadian/autonomic pathways influenced by retinal light input through the suprachiasmatic clock.",
  "project_mapping": {
    "mapping": "Single Eye / Third Eye / Son-side Eye / Door / timing threshold",
    "status": ["project_canon", "historical_esoteric_association", "historical_religious_comparator"]
  },
  "boundary": "The human pineal is not a retinal-style photoreceptor, projector of spiritual light, or proven seat of soul/consciousness. Neuroscience does not call it a literal third eye."
}
```

Also distinguish the habenula from pineal symbolism and document reward/aversion/monoaminergic relationships at atlas-level granularity.

- [ ] **Step 5: Add at least the seventeen named system flows**

Add `flows` entries with these exact ids:

```text
visual-flow
auditory-flow
somatosensory-flow
olfactory-flow
vestibular-flow
corticospinal-motor-flow
basal-ganglia-selection-loop
cerebello-thalamo-cortical-loop
thalamocortical-loop
hippocampal-contextual-memory-loop
interoceptive-autonomic-loop
hypothalamic-pituitary-loop
hpa-stress-axis-context
circadian-scn-pineal-loop
sleep-arousal-loop
csf-circulation
reward-motivation-dopamine-loop
```

Each flow must provide `input`, `stages`, `feedback_or_parallel_paths`, `output`, and `caveats`; add `potatoverse_comparator` only where it genuinely clarifies the project.

The visual flow must say optic-chiasm crossing is partial and organized by visual hemifield.

The circadian flow must preserve the indirect route from retinal light information to SCN and autonomic pathways before pineal output.

- [ ] **Step 6: Add the canonical Potatoverse mapping table**

Add `potatoverse_mapping_table` rows for at least:

```text
thalamus
thalamic-nuclei
thalamic-reticular-nucleus
thalamocortical-corticothalamic-pathways
third-ventricle
pineal-gland
hypothalamus
brainstem-arousal
csf
optic-chiasm
insula-interoception
hippocampal-memory
amygdala-affect-salience
basal-ganglia
cerebellar-arbor-vitae
cortex-large-scale-networks
white-matter-tracts
glia
```

The thalamus row must include `project_mapping: "Potato / Father's House / central interior"` and `status` containing `project_canon`.

The pineal row must include `project_mapping` containing both `Single Eye` and `Third Eye`, and `status` containing `project_canon`.

- [ ] **Step 7: Add explicit boundary and source registries**

Add `boundaries` that explicitly reject:

- thalamus as scientifically proven divine residence
- thalamus/claustrum as unique proven seat of consciousness
- pineal as proven seat of soul
- pineal as a human retinal photoreceptor or supernatural projector
- EEG frequencies as spiritual rank
- dopamine = pleasure
- serotonin = happiness
- amygdala = fear center
- simple left-brain/right-brain personality theory
- CSF = Holy Spirit
- one-to-one chakra anatomy
- ancient texts/art as proven encodings of modern neuroanatomy

Add `sources` with stable scientific anchors listed in the spec, and `related_records` linking all existing specialist owners.

- [ ] **Step 8: Parse the JSON and run the focused validator**

Run:

```bash
python -m json.tool knowledge/body/whole-brain-neurobiology-atlas.json > /dev/null
python scripts/validate_whole_brain_neurobiology.py
```

Expected: JSON parse passes; validator still exits `1`, but errors for missing atlas/sections/flows/mappings are gone. Remaining failures should only be routing/master/matrix/manifest/core integration from later tasks.

- [ ] **Step 9: Commit the atlas**

```bash
git add knowledge/body/whole-brain-neurobiology-atlas.json
git commit -m "feat: add whole-brain neurobiology atlas"
```

---

### Task 3: Wire the new owner into canonical BODY routing

**Files:**
- Modify: `knowledge/body/body-system-master-atlas.json`
- Modify: `knowledge/indexes/neurotheology-routing-index.json`
- Modify: `knowledge/body/body-topic-completion-matrix.json`

**Interfaces:**
- Consumes: `knowledge/body/whole-brain-neurobiology-atlas.json`
- Produces: one canonical routing path from BODY entrypoint → whole-brain owner → specialist thalamus/neurotheology owners.

- [ ] **Step 1: Update `body-system-master-atlas.json` metadata and sequence**

Set:

```json
"version": "1.1.0",
"updated": "2026-09-15"
```

Expand `master_sequence` so brain progression includes, in order:

```text
brainstem/arousal
hypothalamus/homeostasis
diencephalon/central regulation
thalamus/House
basal-ganglia/action selection
memory-affect-context
pineal/timing threshold
cerebellum/prediction correction
cortex/world-model
whole-brain networks and loops
whole-body return loop
```

Add to `canonical_owners`:

```json
"whole_brain_neurobiology": "knowledge/body/whole-brain-neurobiology-atlas.json"
```

Do not duplicate the deep atlas content into this file; add concise pointers in the existing brain-related rows.

- [ ] **Step 2: Add the new owner to `neurotheology-routing-index.json`**

Set:

```json
"version": "2.1.0",
"updated": "2026-09-15"
```

Insert after the body master/completion entries:

```json
{
  "priority": 3,
  "topic": "whole-brain neurobiology",
  "owner": "knowledge/body/whole-brain-neurobiology-atlas.json",
  "use_for": [
    "brain hierarchy",
    "cortical lobes",
    "white-matter pathways",
    "diencephalon",
    "basal ganglia",
    "memory-affect systems",
    "brainstem",
    "cerebellum",
    "sensory pathways",
    "motor pathways",
    "ventricles and CSF",
    "glia and neurovascular support",
    "neurotransmitter systems",
    "large-scale brain networks",
    "brain states",
    "system flows"
  ]
}
```

Renumber later priorities only if necessary for readability; priority values need not be unique.

Add a core boundary stating that `potato-shaped` is canonical Potatoverse shape language while `ovoid/egg-shaped` remains the conventional anatomical description.

- [ ] **Step 3: Expand `body-topic-completion-matrix.json`**

Set:

```json
"version": "1.1.0",
"updated": "2026-09-15"
```

Add these topics with owner `knowledge/body/whole-brain-neurobiology-atlas.json` and status `complete` only after Task 2 coverage exists:

```text
Whole-brain hierarchy
Cortical lobes and major territories
White-matter pathways and commissures
Diencephalon
Pineal / circadian system
Basal-ganglia loops
Hippocampal / memory systems
Brainstem / arousal systems
Cerebellar system
Sensory pathways
Motor pathways
Ventricular / CSF / meningeal system
Cellular / glial support
Neurotransmitter / neuromodulatory systems
Large-scale brain networks
Brain states / consciousness boundaries
```

Update `finished_baseline_summary` so it distinguishes the older symbolic/body baseline from the newly completed whole-brain baseline.

- [ ] **Step 4: Run focused validation**

```bash
python scripts/validate_whole_brain_neurobiology.py
```

Expected: errors for routing/body master/completion matrix disappear; manifest/core routing errors remain.

- [ ] **Step 5: Commit canonical routing updates**

```bash
git add knowledge/body/body-system-master-atlas.json knowledge/indexes/neurotheology-routing-index.json knowledge/body/body-topic-completion-matrix.json
git commit -m "feat: route whole-brain neurobiology through body atlas"
```

---

### Task 4: Surface the atlas in public and core navigation

**Files:**
- Modify: `manifest.json`
- Modify: `knowledge/indexes/core-index.json`
- Modify: `docs/PROJECT-OPERATING-MAP.md`
- Modify: `docs/PROJECT-STRUCTURE.md`

**Interfaces:**
- Produces discoverable BODY routing for readers and agents.

- [ ] **Step 1: Update the BODY branch in `manifest.json`**

Set top-level `updated` to `2026-09-15`.

Insert `knowledge/body/whole-brain-neurobiology-atlas.json` immediately after `knowledge/body/body-system-master-atlas.json` in BODY `records`.

Expand BODY `children` with these high-level concepts while retaining existing body systems:

```text
Whole Brain
Cerebral Cortex
White Matter / Roads
Diencephalon
Thalamus / Potato / House
Pineal / Single Eye / Third Eye
Basal Ganglia
Hippocampus / Memory
Amygdala / Salience
Brainstem / Arousal
Cerebellum / Arbor Vitae
Sensory Pathways
Motor Pathways
Ventricles / CSF
Glia / Barriers
Large-Scale Networks
Brain States
```

Do not remove Garden, skin, gut, heart, autonomic, spine, chakra, or whole-body children.

- [ ] **Step 2: Add the record to `knowledge/indexes/core-index.json`**

Set:

```json
"version": "4.2.0",
"updated": "2026-09-15"
```

Add `whole-brain-neurobiology-atlas` to `canonical_groups.body_spirit_corporium` immediately after `body-system-master-atlas`.

Add this record after the body-system master record:

```json
{
  "id": "whole-brain-neurobiology-atlas",
  "path": "knowledge/body/whole-brain-neurobiology-atlas.json",
  "branch": "body",
  "kind": "canonical whole-brain anatomy, systems, networks and flow atlas",
  "terms": [
    "brain",
    "nervous system",
    "thalamus potato Father's House",
    "pineal Single Eye Third Eye",
    "diencephalon",
    "cortex",
    "white matter",
    "basal ganglia",
    "hippocampus",
    "amygdala",
    "brainstem",
    "cerebellum",
    "insula",
    "corpus callosum",
    "CSF",
    "default mode",
    "salience",
    "circadian"
  ]
}
```

- [ ] **Step 3: Update operating documentation**

In `docs/PROJECT-OPERATING-MAP.md`, add `knowledge/body/whole-brain-neurobiology-atlas.json` under Body and describe it as the deep owner for whole-brain anatomy, pathways, networks, and flows.

In `docs/PROJECT-STRUCTURE.md`, update the Body/Neurobiology ownership row so the master atlas remains the canonical entry point while the new whole-brain atlas is identified as the deep brain owner and the thalamus file remains the specialist House/rooms owner.

- [ ] **Step 4: Run focused validation**

```bash
python scripts/validate_whole_brain_neurobiology.py
```

Expected: exit `0` and `Errors: 0`.

- [ ] **Step 5: Commit navigation changes**

```bash
git add manifest.json knowledge/indexes/core-index.json docs/PROJECT-OPERATING-MAP.md docs/PROJECT-STRUCTURE.md
git commit -m "docs: expose whole-brain neurobiology routing"
```

---

### Task 5: Regenerate discovery/index outputs and run repository-wide audits

**Files:**
- Potential generated modifications: `_site/**`, `llms.txt`, `llms-full.txt`, other outputs produced by existing builders
- Potential generated modifications: `data/repository-index.json`, `data/source-of-truth-audit.json`
- No hand-editing of generated files unless the builder itself requires a source change.

**Interfaces:**
- Consumes all canonical records and routing.
- Produces validated public/machine discovery outputs.

- [ ] **Step 1: Rebuild the data repository index**

Run:

```bash
python scripts/build_repository_index.py
```

Expected: script exits `0` and reports `0 JSON errors`.

Note: this builder indexes `data/**/*.json`; the new knowledge atlas is surfaced through manifest/core/body routing rather than by forcing it into the data index.

- [ ] **Step 2: Validate internal repository taxonomy**

Run:

```bash
python scripts/validate_repository_spine.py
```

Expected: `Errors: 0`.

- [ ] **Step 3: Run source-of-truth audit**

Run:

```bash
python scripts/audit_source_of_truth.py
```

Expected: JSON result with `"status": "pass"` and an empty `errors` array.

- [ ] **Step 4: Build public discovery**

Run:

```bash
python scripts/build_discovery.py
```

Expected: builder exits `0` and rewrites discovery/LLM/public-index outputs according to the manifest and existing FAQ/index data.

- [ ] **Step 5: Check machine discoverability**

Run:

```bash
python scripts/check_machine_discoverability.py
```

Expected: exit `0` with no missing canonical route/door errors.

- [ ] **Step 6: Run content-depth audit**

Run:

```bash
python scripts/audit_content_depth.py
```

Expected: no new failure caused by BODY/neurobiology routing.

- [ ] **Step 7: Run the focused neurobiology validator again**

```bash
python scripts/validate_whole_brain_neurobiology.py
```

Expected: `Errors: 0`.

- [ ] **Step 8: Commit generated/audit changes that are tracked by the repository**

Inspect `git status --short`; commit only tracked/generated outputs that the existing project convention expects:

```bash
git add -u
git add data/repository-index.json data/source-of-truth-audit.json 2>/dev/null || true
git commit -m "build: refresh discovery after neurobiology expansion"
```

If no generated tracked files changed, do not create an empty commit.

---

### Task 6: Final verification and content review

**Files:**
- Review all files changed in Tasks 1–5.

**Interfaces:**
- Produces final verified neurobiology baseline.

- [ ] **Step 1: Search for required canonical terms**

Run:

```bash
rg -n "potato-shaped|Father's House|Single Eye|Third Eye|seat of soul|seat of consciousness|circadian-scn-pineal-loop|thalamocortical-loop|default-mode|corpus callosum" knowledge/body/whole-brain-neurobiology-atlas.json knowledge/body/body-system-master-atlas.json knowledge/indexes/neurotheology-routing-index.json manifest.json knowledge/indexes/core-index.json
```

Expected: every positive routing term is found in the appropriate owner and boundary phrases are present in the atlas.

- [ ] **Step 2: Verify no accidental competing owner was created**

Run:

```bash
rg -n '"status": "canonical.*thalam|"status":"canonical.*thalam' knowledge data
```

Expected: no new file claims to replace `data/potatoism-thalamus-brain-map.json` as specialist thalamus owner.

- [ ] **Step 3: Run JSON parse checks for all modified JSON files**

Run:

```bash
python - <<'PY'
import json
from pathlib import Path
paths = [
    Path('knowledge/body/whole-brain-neurobiology-atlas.json'),
    Path('knowledge/body/body-system-master-atlas.json'),
    Path('knowledge/indexes/neurotheology-routing-index.json'),
    Path('knowledge/body/body-topic-completion-matrix.json'),
    Path('manifest.json'),
    Path('knowledge/indexes/core-index.json'),
]
for path in paths:
    json.loads(path.read_text(encoding='utf-8'))
    print('OK', path)
PY
```

Expected: six `OK` lines and exit `0`.

- [ ] **Step 4: Run the complete validation set one final time**

```bash
python scripts/validate_whole_brain_neurobiology.py && \
python scripts/validate_repository_spine.py && \
python scripts/audit_source_of_truth.py && \
python scripts/check_machine_discoverability.py
```

Expected: all commands exit `0`.

- [ ] **Step 5: Review the final diff for epistemic leakage**

Run:

```bash
git diff HEAD~5..HEAD -- knowledge/body/whole-brain-neurobiology-atlas.json knowledge/body/body-system-master-atlas.json knowledge/indexes/neurotheology-routing-index.json knowledge/body/body-topic-completion-matrix.json manifest.json knowledge/indexes/core-index.json
```

Review specifically for:

- symbolic statements accidentally placed in scientific fields
- scientific claims presented without caveats where the field is active/contested
- pineal described as literal photoreceptor/third eye
- thalamus described as scientifically recognized potato or divine house
- duplicate ownership
- lost existing BODY routes

- [ ] **Step 6: Commit any review corrections**

If corrections were needed:

```bash
git add knowledge/body/whole-brain-neurobiology-atlas.json knowledge/body/body-system-master-atlas.json knowledge/indexes/neurotheology-routing-index.json knowledge/body/body-topic-completion-matrix.json manifest.json knowledge/indexes/core-index.json
git commit -m "fix: tighten neurobiology boundaries and routing"
```

If no corrections were needed, do not create an empty commit.
