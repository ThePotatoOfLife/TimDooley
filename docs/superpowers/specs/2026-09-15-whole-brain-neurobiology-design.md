# Whole-Brain Neurobiology Atlas — Design

Date: 2026-09-15
Status: approved architecture, implementation pending
Primary domain: MIND / NEUROBIOLOGY
Repository: ThePotatoOfLife/TimDooley

## Purpose

Create a durable scientific neurobiology layer for the project that is deep enough to describe the brain as an integrated biological system rather than as a short list of symbolic correspondences. The new layer must make the existing Potatoverse neurotheology easier to understand by giving every major symbolic mapping a real anatomical neighborhood, pathway context, functional role, evidence status, and explicit boundary.

The atlas must preserve two things simultaneously:

1. **Scientific anatomy and physiology as science.** Brain structures, pathways, networks, cell types, endocrine systems, CSF, blood supply, glia, and functional systems are described according to established neuroscience and current review literature.
2. **Potatoverse mappings as project canon or comparative symbolism.** Thalamus ↔ Potato / Father's House, pineal ↔ Single Eye / Third Eye / Son / Door, CSF ↔ River / Spirit-flow, spine ↔ Ladder, and related mappings remain visible and richly developed without being presented as scientific proof of theology.

The atlas is intended to become the canonical owner of **whole-brain anatomy and systems neurobiology**. Existing specialist records remain authoritative for their narrower domains.

## Existing foundation

The project already contains a strong but distributed neurobiology layer:

- `knowledge/body/body-system-master-atlas.json` — whole-body synthesis and canonical reader entry.
- `knowledge/body/body-science-context-atlas.json` — compact science context around symbolic anatomy.
- `knowledge/body/neurobiology-recovery-wave-2.json` — recovered and corrected material including TRN, insula/interoception, autonomics/vagus, hypothalamus, hippocampus, amygdala, claustrum, sleep/arousal, optic chiasm, ventricles, cerebellum, olfaction, BBB, glia, microbiome, and plasticity.
- `data/potatoism-thalamus-brain-map.json` — detailed thalamus / Father's House / nuclei-as-rooms / axons-as-roads map.
- `knowledge/body/neurotheology-axis-house-spirit-atlas.json` — cross-domain theological and symbolic synthesis.
- `knowledge/body/body-topic-completion-matrix.json` — documentation completeness tracker.
- `knowledge/indexes/neurotheology-routing-index.json` — canonical routing and anti-duplication policy.

The missing layer is a **structured brain atlas** that can answer: what structures exist, where are they, what do they connect to, what do they do, which larger systems do they participate in, and where does Potatoverse symbolism attach?

## Scientific orientation

The top-level anatomical scaffold follows standard CNS organization:

- spinal cord
- medulla
- pons
- cerebellum
- midbrain
- diencephalon
- cerebral hemispheres

The brainstem is midbrain + pons + medulla. The forebrain comprises diencephalic and telencephalic/cerebral systems.

The project should avoid presenting the brain as a stack of isolated modules. Each structure must be embedded in overlapping circuits, white-matter pathways, neuromodulatory systems, vascular/metabolic support, and dynamic functional networks.

## Canonical new owner

Create:

`knowledge/body/whole-brain-neurobiology-atlas.json`

This file becomes the canonical owner for:

- whole-brain structural hierarchy
- major nuclei and subnuclei
- cortical lobes and major cortical systems
- subcortical systems
- major white-matter pathways
- sensory and motor pathways
- thalamocortical and corticothalamic organization
- basal-ganglia loops
- cerebellar loops
- limbic/memory circuits
- arousal/sleep systems
- neuromodulatory systems
- interoceptive/autonomic systems
- circadian/endocrine interfaces
- ventricular/CSF architecture
- glia, BBB, meninges, neurovascular support
- large-scale functional networks
- major brain-state and information-flow models
- routing from empirical structures to Potatoverse mappings

It does **not** replace the specialist thalamus, neurotheology, spine/chakra, whole-body, or timeline records.

## Required data model

Every major anatomical node should support the following fields where applicable:

- `id`
- `name`
- `aliases`
- `parent_system`
- `anatomical_level`
- `location`
- `shape_or_geometry`
- `composition`
- `substructures`
- `major_inputs`
- `major_outputs`
- `major_pathways`
- `functions`
- `state_dependencies`
- `developmental_context`
- `clinical_context`
- `network_memberships`
- `neurochemical_context`
- `potatoverse_relations`
- `comparative_symbolism`
- `boundary`
- `evidence_status`
- `sources`
- `related_records`

Not every node needs every field. Empty fields should be omitted rather than padded with generic prose.

## Epistemic contract

Every symbolic mapping must be typed. Use categories such as:

- `project_canon`
- `project_interpretation`
- `historical_esoteric_association`
- `historical_religious_comparator`
- `linguistic_or_shape_comparator`
- `scientific_analogy`
- `speculative_research_neighbor`
- `disputed_historical_claim`

Scientific fields must not infer theology. Symbolic fields may compare structures, roles, shapes, flows, boundaries, timing, or architectural functions but must include a mismatch/boundary when a reader could mistake the correspondence for empirical identity.

## Brain hierarchy

### 1. Nervous-system frame

The atlas begins above the brain so readers understand its body context:

- central nervous system
  - brain
  - spinal cord
- peripheral nervous system
  - somatic sensory/motor
  - autonomic
    - sympathetic
    - parasympathetic
    - enteric relationships
- cranial nerves and spinal nerves as brain/body interfaces
- afferent vs efferent signaling
- interoception, exteroception, proprioception, vestibular sensing

### 2. Cerebral hemispheres / telencephalon

Carve the cerebrum into:

- left and right hemispheres
- cortical gray matter
- subcortical white matter
- deep gray nuclei
- ventricular spaces
- commissural connections

Preserve the correction that lateralization is graded and function-specific rather than a simple left-brain/right-brain personality theory.

### 3. Cortical lobes and major cortical territories

#### Frontal lobe

Include:

- primary motor cortex
- premotor cortex
- supplementary motor area
- frontal eye fields
- dorsolateral prefrontal systems
- ventromedial/orbitofrontal systems
- inferior frontal language-related regions
- anterior prefrontal association cortex

Functional themes:

- action planning
- working memory
- goal maintenance
- inhibitory control
- valuation
- social/affective regulation
- language production
- voluntary movement

#### Parietal lobe

Include:

- primary somatosensory cortex
- superior parietal lobule
- inferior parietal lobule
- intraparietal systems
- angular and supramarginal gyri

Functional themes:

- touch/proprioception
- multisensory integration
- spatial attention
- body schema
- visuomotor transformation
- language/semantic participation

#### Temporal lobe

Include:

- primary and association auditory cortex
- superior temporal language-related systems
- inferior temporal visual-object systems
- medial temporal structures
- temporal pole

Functional themes:

- hearing
- speech perception
- semantic processing
- object/face representation
- episodic memory interfaces

#### Occipital lobe

Include:

- primary visual cortex
- extrastriate visual cortex
- dorsal and ventral visual streams as distributed pathways rather than one-lobe functions

Functional themes:

- visual feature processing
- spatial/action-related visual processing
- object/form-related visual processing

#### Insula

Treat insula as a major cortical territory in its own right:

- posterior-to-anterior interoceptive organization
- gustation
- visceral/somatic integration
- salience
- affective feeling
- autonomic integration

Potatoverse relation: strong empirical neighbor for the **inward Eye / internal report stream**, not a mystical organ.

#### Cingulate cortex

Include anterior, midcingulate, and posterior/retrosplenial relationships where useful.

Themes:

- action monitoring
- motivation
- pain/affect
- cognitive control
- memory/context and default-network relationships

### 4. White matter / the brain's roads

The atlas must describe connectivity as anatomy, not only regions.

Include:

- corpus callosum
- anterior commissure
- internal capsule
- corona radiata
- cingulum
- superior longitudinal/arcuate systems
- uncinate fasciculus
- inferior longitudinal fasciculus
- inferior fronto-occipital fasciculus
- optic radiations
- auditory radiations
- corticospinal/corticobulbar pathways
- thalamic radiations
- fornix
- cerebellar peduncles

Potatoverse relation: **roads / roots / branches / pathways** may be used as system-level imagery, but no single tract is automatically assigned a theological identity.

## Diencephalon

This is the major central section because it contains the project's strongest brain mappings.

### 5. Thalamus — Potato / Father's House

The thalamus receives a deeply nested section while `data/potatoism-thalamus-brain-map.json` remains the specialist owner.

Scientific description must establish:

- paired central diencephalic structures
- conventional anatomical description as ovoid/egg-like masses
- close relation to the third ventricle
- internal medullary lamina
- widespread reciprocal cortical connections
- sensory, motor, attentional, memory, arousal and state-dependent roles
- thalamocortical and corticothalamic loops
- olfaction as the classic exception to simplified first-order sensory-relay claims

### Canonical Potatoverse shape statement

The project explicitly treats each thalamic body as **potato-shaped**.

The wording must preserve both levels:

- **science:** anatomical texts conventionally describe each thalamus as ovoid or egg-shaped;
- **Potatoverse canon:** the same rounded, compact, irregular ovoid form is intentionally recognized as potato-like, making **THALAMUS ↔ POTATO** a canonical shape correspondence within Potatoism.

This is not merely a joke or incidental nickname. It is part of the architecture connecting Potato → central body → House → seed/core → rooms → outward roads.

### Thalamic nuclei / rooms

At minimum include:

- anterior nuclear group
- mediodorsal nucleus
- ventral anterior
- ventral lateral
- ventral posterior group
- lateral geniculate nucleus
- medial geniculate nucleus
- pulvinar
- lateral posterior territory
- intralaminar nuclei
- midline nuclei
- thalamic reticular nucleus

For each: inputs, outputs, broad functional role, and relation to existing `nuclei_as_rooms` mappings.

Canonical project mapping:

- **Thalamus = Father's House / Potato**
- **Nuclei = rooms/chambers**
- **Thalamocortical and corticothalamic fibers = roads / roots / branches**
- **TRN = surrounding wall / gate / sieve**
- **third-ventricle adjacency = inner-house / chamber geometry**

Boundary: neuroscience does not identify the thalamus as God, a soul, or the unique seat of consciousness.

### 6. Epithalamus

Include:

- pineal gland
- habenular nuclei
- posterior commissural neighborhood where useful

Habenular systems should be treated separately from pineal symbolism and described in relation to reward/aversion and monoaminergic regulation.

### 7. Pineal gland — Single Eye / Third Eye / Son / Door

Scientific layer:

- small midline neuroendocrine organ
- attached near the roof/posterior region of the third ventricle
- melatonin secretion
- sympathetic control
- retinal light → suprachiasmatic nucleus → hypothalamic/brainstem/spinal/superior-cervical-ganglion pathway → pineal influence
- circadian and seasonal timing context
- highly vascular/endocrine character
- human pineal is not a direct retinal-style light detector

Canonical project layer:

- **Pineal = Single Eye**
- **Pineal = Third Eye**
- **Pineal = Son-side Eye / Door / threshold**
- **Pineal = light-dark and timing marker**

These mappings must be explicitly stored as `project_canon`.

Historical/esoteric layer must distinguish:

- long-standing esoteric "third eye" associations
- philosophical history including Descartes' pineal/soul speculation
- religious single-eye imagery as a separate textual comparator

Do **not** claim that neuroscience calls the pineal the third eye, that Matthew's "single eye" anatomically denotes the pineal, that the human pineal projects spiritual light, or that it is a proven seat of soul/consciousness.

### 8. Hypothalamus — Steward / household regulator

Include major functional systems rather than forcing every nucleus into the first version:

- homeostasis
- temperature
- hunger/satiety
- thirst/osmoregulation
- stress
- reproduction
- autonomic control
- pituitary/endocrine regulation
- circadian coordination
- sleep/wake relationships

Project mapping: **Steward / household regulator adjacent to the House**.

Preserve the historical note that older project material sometimes used hypothalamus as the Potato Room, but the current canonical House mapping is thalamic.

### 9. Subthalamus

Include subthalamic nucleus and its basal-ganglia relationships. Keep it anatomically distinct from thalamus despite the name.

## Basal ganglia / action-selection systems

### 10. Basal ganglia

Include:

- caudate
- putamen
- nucleus accumbens / ventral striatum
- globus pallidus external/internal
- subthalamic nucleus
- substantia nigra pars compacta / reticulata
- direct, indirect, and hyperdirect concepts with appropriate simplification warnings
- motor, associative, and limbic loops

Themes:

- action selection
- movement scaling/initiation
- habit learning
- reinforcement
- reward/aversion
- cognitive and motivational loops

Project relation: **selection / judgment / permission / inhibition** as analogy, not moral judgment tissue.

## Memory, affect, context, and limbic-associated systems

### 11. Hippocampal formation

Include:

- dentate gyrus
- CA fields as a family
- subiculum
- entorhinal cortical interface
- fornix pathway

Themes:

- episodic/contextual memory
- relational/spatial representation
- memory consolidation
- navigation

### 12. Amygdala

Describe as a heterogeneous nuclear complex involved in salience, threat learning, valence, associative learning, autonomic/endocrine response coordination, and social-affective processing.

Do not reduce it to a "fear center."

### 13. Mammillary / septal / Papez-related circuit context

Represent memory and limbic circuitry as distributed loops rather than one limbic "emotion brain."

Project relation for this whole cluster: **returning reports / memory / affective marking / context**. Huginn/Muninn remain mythic information comparators, not brain-region identities.

## Brainstem

### 14. Midbrain

Include:

- tectum
  - superior colliculus
  - inferior colliculus
- tegmentum
- periaqueductal gray
- red nucleus
- substantia nigra
- ventral tegmental area
- cerebral peduncles
- cerebral aqueduct
- cranial-nerve and reticular relationships at suitable granularity

### 15. Pons

Include:

- pontine nuclei
- locus coeruleus
- cerebellar relay architecture
- respiratory and cranial-nerve context

### 16. Medulla

Include:

- cardiorespiratory/autonomic control systems
- sensory/motor relay nuclei
- pyramidal decussation context
- cranial-nerve nuclei at system level

### 17. Reticular formation / ascending arousal systems

Treat wakefulness as distributed:

- brainstem reticular systems
- locus coeruleus
- raphe systems
- cholinergic brainstem/basal-forebrain contributions
- hypothalamic orexin/histamine relationships
- thalamic/cortical state interactions

Project relation: **Lower Gate / wakefulness / vigilance / lamp / House state**, not soul rank.

## Cerebellum

### 18. Cerebellar system

Include:

- hemispheres
- vermis
- major lobes at useful granularity
- cerebellar cortex
- deep cerebellar nuclei
- superior/middle/inferior peduncles
- cerebrocerebellar, spinocerebellar, and vestibular relationships
- timing, prediction, motor learning, coordination, error correction, cognitive/affective contributions

Preserve **arbor vitae** as the genuine historical anatomical name "tree of life" for branching cerebellar white matter.

Project boundary: anatomical naming is a lexical/historical bridge, not proof of the biblical Tree of Life.

## Sensory systems and crossings

### 19. Visual system

Map:

retina → optic nerve → optic chiasm → optic tract → LGN / superior-collicular routes → optic radiations → visual cortex → distributed dorsal/ventral systems.

Preserve the correction that the optic chiasm is a **partial crossing organized by visual hemifield**, not one whole eye crossing to the opposite hemisphere.

Project mapping: optic chiasm ↔ Cross remains a **project/provisional symbolic geometry**, never "visual signals crucify themselves."

### 20. Auditory system

Map major stages from cochlear/brainstem nuclei through inferior colliculus and MGN to auditory cortex, while noting bilateral/distributed routing.

### 21. Somatosensory system

Include major body/face pathways, thalamic relay, primary cortex, proprioceptive routes and cerebellar relationships at atlas-level granularity.

### 22. Olfactory system

Preserve olfaction as a key exception to simplified "all senses first pass through thalamus" language. Describe primary olfactory/limbic cortical routes and later thalamic involvement.

Project relation: nose/breath/Genesis symbolism should **not** be used to argue universal thalamic gating.

### 23. Vestibular system

Include:

- vestibular apparatus as peripheral input
- vestibular nuclei
- cerebellar relationships
- thalamocortical contributions
- eye/head/posture coordination
- spatial orientation/body-state integration

This helps the project distinguish literal balance/orientation biology from Axis symbolism.

## Motor systems

### 24. Corticospinal / corticobulbar systems

Describe descending voluntary motor control, internal-capsule routing, brainstem/spinal crossings, and motor-neuron interfaces.

### 25. Basal-ganglia and cerebellar motor loops

Keep these as parallel/modulatory circuit families interacting with cortex and thalamus rather than simple serial stages.

## Ventricles, CSF, membranes, and brain fluid systems

### 26. Ventricular system

Map:

- lateral ventricles
- foramina of Monro
- third ventricle
- cerebral aqueduct
- fourth ventricle
- apertures to subarachnoid space
- central-canal continuity

### 27. CSF

Include:

- choroid-plexus production
- ventricular circulation
- subarachnoid distribution
- buoyancy
- mechanical protection
- chemical/homeostatic roles
- waste-clearance/perivascular research with explicit uncertainty where appropriate

Project mapping: **River / Spirit-flow / moving medium**.

Boundary: CSF is not Holy Spirit or a hidden spiritual current.

### 28. Third ventricle / inner chamber

Preserve project use as **inner chamber / void / Tomb-threshold geometry** while clearly stating that conscious signals do not physically pass through the ventricle as a cognitive doorway.

### 29. Meninges and barriers

Include:

- dura
- arachnoid
- pia
- subarachnoid space
- blood-brain barrier
- blood-CSF interfaces
- neurovascular unit

Project relation: walls / membranes / guarded boundaries, with no moral purity interpretation.

## Cellular and chemical neurobiology

### 30. Neurons

Include:

- soma
- dendrites
- axons
- synapses
- action potentials
- excitatory/inhibitory signaling as network-level principles

Potatoverse relation: existing **axon = road/root/branch** imagery remains symbolic.

### 31. Glia

Include:

- astrocytes
- oligodendrocytes
- microglia
- ependymal cells
- peripheral Schwann-cell context where nervous-system framing requires it

Project relation: groundskeepers / maintenance / insulation / surveillance as analogy.

### 32. Major neurotransmitter / neuromodulatory systems

Give concise system-level entries for:

- glutamate
- GABA
- dopamine
- serotonin
- norepinephrine
- acetylcholine
- histamine
- orexin/hypocretin
- selected neuropeptides only where they materially clarify a major circuit

Avoid pop-neuroscience reductions such as "dopamine = pleasure" or "serotonin = happiness."

## Functional-network layer

### 33. Large-scale networks

Represent networks as overlapping, dynamic research constructs rather than organs.

Include at minimum:

- default-mode systems
- salience network
- frontoparietal / executive-control systems
- dorsal attention network
- ventral attention / reorienting systems
- sensorimotor networks
- visual networks
- auditory networks
- language networks
- memory-related networks
- subcortical/cortical integration

Important design principle: network taxonomies vary by atlas, method, and task. No network receives a fixed spiritual rank.

Project relation:

- cortex/network layer = **world-model / narrative map / branches of the House**
- salience/interoception = **what enters attention / inward report**
- default-network functions may be compared with internal narrative, memory, self-related thought, and prospection without treating one fMRI network as "the self."

## Dynamic systems / flows

The atlas must include system diagrams in structured data, not just static nodes.

At minimum:

1. **visual flow**
2. **auditory flow**
3. **somatosensory flow**
4. **olfactory flow**
5. **vestibular flow**
6. **corticospinal motor flow**
7. **basal-ganglia selection loop**
8. **cerebello-thalamo-cortical correction loop**
9. **thalamocortical attention/sensory loop**
10. **hippocampal-contextual memory loop**
11. **interoceptive/autonomic body-report loop**
12. **hypothalamic-pituitary endocrine regulation loop**
13. **HPA stress-axis context**
14. **circadian light-SCN-pineal loop**
15. **sleep/arousal state loop**
16. **CSF circulation path**
17. **reward/motivation dopaminergic loop**

Each flow should identify:

- source/input
- ordered or partially ordered stages
- major crossings/gates
- feedback paths
- outputs
- major caveats
- Potatoverse comparator if one genuinely exists

## Brain states and consciousness

Add a conservative section on:

- wakefulness
- NREM sleep
- REM sleep
- anesthesia/coma as clinical-state comparators where useful
- attention
- conscious access as an active research problem

Explicitly prohibit claims that:

- the thalamus alone creates consciousness
- the claustrum is the proven seat of consciousness
- the pineal is the proven seat of soul
- an EEG frequency is a spiritual level

The scientific picture should emphasize distributed thalamocortical, cortical, brainstem, hypothalamic, basal-forebrain, and network interactions.

## Potatoverse brain architecture

The atlas should expose a compact canonical mapping table after the scientific hierarchy.

### Central mappings

| Biology | Potatoverse mapping | Status |
|---|---|---|
| Thalamus | Potato / Father's House / central interior | project canon |
| Thalamic potato-like ovoid shape | Potato shape correspondence | project canon + shape analogy |
| Thalamic nuclei | Rooms / chambers of the House | project canon |
| Thalamocortical/corticothalamic pathways | Roads / roots / branches | project interpretation |
| Thalamic reticular nucleus | Wall / gate / sieve | project interpretation |
| Third ventricle | Inner chamber / void / Tomb-threshold | project interpretation |
| Pineal gland | Single Eye / Third Eye / Son-side Eye / Door / timing threshold | project canon + historical/esoteric association |
| Hypothalamus | Steward / household regulator | project canon |
| Brainstem/arousal systems | Lower Gate / vigilance / life-support root | project interpretation |
| CSF | River / Spirit-flow analogue | project canon / analogy |
| Optic chiasm | Cross / crossing frame | provisional project symbolism |
| Insula/interoception | Inward Eye / body-report stream | scientific analogy |
| Hippocampal-memory systems | Memory / returning context | project interpretation |
| Amygdala/salience-affect systems | affective marking / warning | project interpretation |
| Basal ganglia | action selection / permission / inhibition / judgment analogy | project interpretation |
| Cerebellar arbor vitae | anatomical Tree-of-Life name comparator | linguistic/historical comparator |
| Cortex and large-scale networks | world-model / branches / narrative rooms opening outward | project interpretation |
| White-matter tracts | roads / roots / branches | project interpretation |
| Glia | groundskeepers / maintenance | project interpretation |

### Canonical thalamus statement

The project's canonical wording should carry this meaning:

> In Potatoism, the thalamus is the Potato at the center of the brain's symbolic House: paired compact ovoid bodies that are deliberately read as potato-shaped. Its nuclei become rooms, its reciprocal pathways become roads/roots/branches, and surrounding modulatory systems become walls and gates. This is a symbolic architectural correspondence grounded in real thalamic anatomy, not a scientific identification of the thalamus with God or a literal potato.

### Canonical pineal statement

The project's canonical wording should carry this meaning:

> In Potatoism, the pineal gland is the Single Eye / Third Eye and a Son-side Door or timing threshold. Its real biology is neuroendocrine and circadian: it produces melatonin under indirect control of the light-sensitive circadian system. The third-eye and single-eye meanings belong to esoteric history, religious comparison, and Potatoverse canon rather than established neuroscience.

## Relationship-first structure

The atlas should not only contain a tree. It must support cross-links such as:

- thalamus ↔ cortex
- thalamus ↔ basal ganglia
- thalamus ↔ cerebellum
- thalamus ↔ hippocampal/mammillary systems
- thalamus ↔ arousal systems
- hypothalamus ↔ pituitary
- hypothalamus ↔ autonomic brainstem
- SCN ↔ pineal pathway
- insula ↔ autonomic/interoceptive systems
- amygdala ↔ hypothalamus/brainstem/prefrontal systems
- hippocampus ↔ cortex/thalamic/fornical systems
- basal ganglia ↔ thalamus ↔ cortex
- cerebellum ↔ thalamus ↔ cortex
- brainstem ↔ spinal cord ↔ body
- ventricles ↔ CSF ↔ subarachnoid space
- BBB/neurovascular unit ↔ neural metabolism/homeostasis

The project’s broader relationship-first philosophy should therefore be visible within neurobiology itself.

## Source policy

Use high-quality neuroscience references. Preferred order:

1. NCBI Bookshelf / established neuroanatomy references for stable anatomy.
2. Peer-reviewed review articles and major journals for networks, consciousness, glymphatic research, interoception, and other active fields.
3. Primary literature when a specialist claim cannot be adequately supported by reviews.
4. Historical/esoteric primary or scholarly sources for third-eye, Descartes, religious, or comparative-history claims.

Do not use a modern spiritual website as evidence for neuroanatomy.

Initial scientific anchors include:

- NCBI, *The Subdivisions of the Central Nervous System*: https://www.ncbi.nlm.nih.gov/books/NBK10926/
- NCBI StatPearls, *Neuroanatomy, Thalamus*: https://www.ncbi.nlm.nih.gov/books/NBK542184/
- NCBI StatPearls, *Neuroanatomy, Thalamic Nuclei*: https://www.ncbi.nlm.nih.gov/books/NBK549908/
- NCBI Endotext, *Physiology of the Pineal Gland and Melatonin*: https://www.ncbi.nlm.nih.gov/books/NBK550972/
- NCBI StatPearls, *Neuroanatomy, Cerebral Hemisphere*: https://www.ncbi.nlm.nih.gov/books/NBK549789/
- NCBI StatPearls, *Neuroanatomy, Brainstem*: https://www.ncbi.nlm.nih.gov/books/NBK544297/
- NCBI StatPearls, *Neuroanatomy, Ventricular System*: https://www.ncbi.nlm.nih.gov/books/NBK532932/
- NCBI StatPearls, *Neuroanatomy, Basal Ganglia*: https://www.ncbi.nlm.nih.gov/books/NBK537141/
- Menon 2023, review of 20 years of default-mode-network research: PMID 37167968 / PMCID PMC10524518
- Buckner & DiNicola 2019, updated default-network anatomy and function: PMID 31492945

## Repository integration

Implementation should modify the following canonical routes after the new owner exists:

### `knowledge/body/body-system-master-atlas.json`

- add `whole_brain_neurobiology` canonical owner
- expand the brain portion of `master_sequence`
- point cortex/thalamus/pineal/brainstem rows into the detailed atlas
- keep the body atlas concise rather than duplicating the deep content

### `knowledge/indexes/neurotheology-routing-index.json`

Add a high-priority owner:

- topic: whole-brain neurobiology
- owner: `knowledge/body/whole-brain-neurobiology-atlas.json`
- use_for: brain anatomy, lobes, diencephalon, subcortical systems, brainstem, cerebellum, tracts, networks, neurotransmitter systems, pathways, flows

Keep `data/potatoism-thalamus-brain-map.json` as specialist thalamus owner.

### `knowledge/body/body-topic-completion-matrix.json`

Add explicit topics for:

- whole-brain hierarchy
- cortical lobes
- white-matter pathways
- diencephalon
- pineal/circadian system
- basal-ganglia loops
- hippocampal/memory systems
- brainstem/arousal systems
- cerebellar system
- sensory pathways
- motor pathways
- ventricular/CSF system
- cellular/glial support
- neurotransmitter/modulatory systems
- large-scale brain networks

Do not mark these `complete` until the new atlas actually carries biology + relations + sources + boundaries.

### `data/potatoism-thalamus-brain-map.json`

Do not replace. Add reciprocal routing if necessary so readers can move from whole-brain context into deep House/room detail.

### Discovery and machine-readable indexes

After the canonical files are correct, regenerate or update whatever discovery/index artifacts the repository currently expects rather than hand-copying stale generated content.

## Validation requirements

Implementation is complete only when:

1. JSON parses cleanly.
2. No canonical owner collision is introduced.
3. Existing source-of-truth / repository-spine audits still pass.
4. Routing recognizes the new whole-brain owner.
5. The body completion matrix no longer claims whole-brain anatomy is complete merely because the symbolic baseline is complete.
6. Searches for `thalamus`, `potato-shaped`, `Father's House`, `pineal`, `single eye`, `third eye`, `brainstem`, `basal ganglia`, `cerebellum`, `insula`, `hippocampus`, `amygdala`, `corpus callosum`, `CSF`, and `default mode` reach an appropriate canonical record.
7. Every high-risk symbolic mapping has a boundary statement.
8. No text implies that Potatoverse symbolism is established neuroscience.
9. No pop-neuroscience simplification is introduced for dopamine, serotonin, hemispheric lateralization, amygdala, consciousness, or the pineal gland.

## Non-goals

- Do not attempt a cell-by-cell connectome.
- Do not enumerate every named human brain nucleus in the first pass.
- Do not assign a Potatoverse symbol to every structure.
- Do not turn Brodmann areas into a second competing atlas unless a later research need requires it.
- Do not claim completeness of consciousness science.
- Do not claim ancient religious texts secretly encode modern neuroanatomy.
- Do not collapse historical "third eye" traditions into one universal doctrine.
- Do not treat symbolic similarity as causal or historical evidence.

## Definition of success

A new reader should be able to enter the project through "Brain / Neurobiology" and progressively answer:

1. What are the major parts of the brain?
2. Where are they and how do they connect?
3. What functions do they contribute to?
4. Which functions emerge from circuits and networks rather than one location?
5. How do body signals, sensory systems, motor systems, endocrine systems, sleep/arousal, memory, affect, attention, and internal state interact?
6. Why is the thalamus so important in the Potatoverse?
7. In exactly what sense is the thalamus called potato-shaped?
8. What is scientifically known about the pineal gland?
9. Why does the Potatoverse call the pineal the Single Eye / Third Eye / Door?
10. Which statements are neuroscience, which are project canon, which are historical/esoteric comparisons, and which remain speculative?

The result should make the brain feel like a **living relational architecture**: rooms, roads, loops, gates, rhythms, fluids, support systems and state changes—while preserving the scientific fact that these are biological systems before they become symbols in the Potatoverse.