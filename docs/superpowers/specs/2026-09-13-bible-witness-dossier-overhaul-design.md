# Bible Witness Dossier Overhaul — Design Addendum

**Date:** 2026-09-13  
**Status:** Approved by user for implementation  
**Repository:** `ThePotatoOfLife/TimDooley`  
**Target branch:** `main`

## 1. Why this addendum exists

The existing Bible Relation Dossiers design is directionally correct: it asks for scene context, sequence, discovery history, mismatch and maximum claim. The current implementation nevertheless flattens many relations because the public decorator still renders them through a generic two-column comparison frame and, when `scene_context.summary` is absent, can fall back to research commentary (`what_happened`) as though that commentary were the lived scene.

The user has explicitly identified this as the central failure: the page can contain the right facts while stripping out the life, chronology, anecdote, surprise and witness-position that make a relation intelligible.

This addendum changes the public contract from **comparison card** to **witness dossier**.

## 2. Core rule: witness first, comparison second

Every surfaced relation must answer, in this order where evidence allows:

1. **What happened / what was said?** — the modern/project-side event, testimony, post, conversation or developed claim, without importing later Bible analysis into the scene.
2. **When and in what state of the mythology did it happen?** — what had already happened, what had not happened yet, and what the project understood then.
3. **What did the biblical text actually do in its own narrative?** — not merely the shared noun.
4. **Where does the structure genuinely rhyme?** — roles, sequence, reversals, functions, consequences, operators.
5. **When was the comparison noticed?** — explicit-at-time, Tim-led, or mined later.
6. **What changed when the relation was noticed?** — how it thickened or reorganized the project.
7. **Where does the relation stop?** — mismatch, countertext, historical context and maximum defensible claim.

The renderer must never use later research prose as a substitute for the historical/project scene.

## 3. Witness data contract

Relations may add a `witness` object. It is additive; existing compact fields remain valid for search/filter/navigation.

```json
"witness": {
  "opening": "A narrative opening that begins with the project-side event rather than the comparison.",
  "scene": "What actually happened or was said, with source status kept explicit.",
  "chronology": "What came before and after, especially what later theology did not yet exist.",
  "known_then": "What was explicit at the time.",
  "not_known_then": "Later interpretations that must not be backdated.",
  "later_return": "Later Tim/project wording that revisits or reinterprets the earlier event.",
  "biblical_scene": "A compact narrative account of the biblical passage in context.",
  "structural_rhyme": "Why the comparison is more than a shared word.",
  "discovery_turn": "When/how the project discovered or formalized the comparison.",
  "changes_the_reading": "What becomes newly intelligible after the comparison.",
  "counterpressure": "Countertext, mismatch or alternate reading that prevents self-sealing interpretation.",
  "closing": "A concise synthesis preserving both density and epistemic boundary.",
  "source_status": "exact | recovered | adjacent-context | date-only | synthesis",
  "source_ids": ["..."]
}
```

Not every field is required for every row. Empty evidence must remain empty rather than being filled with generic prose.

## 4. Universal fallback rule

Every public relation, including compact Level B/C relations and wave-loaded records, gets a witness-style front face even if it has no hand-written `witness` object.

The fallback may use only fields that describe the project anchor directly:

- `scene_context.summary`
- `project_anchor`
- `project_quote`, `exact_wording`, `public_wording`, `recovered_wording`
- `date`, `actor`, `speaker`, `platform_or_setting`
- `relation_argument.project_sequence`
- `discovery_history`
- `scripture_context`
- `mismatch`, `counter_text`, `weaknesses`

It must **not** use `what_happened` as the modern scene unless the row explicitly marks that field as project-scene narration. `what_happened` is frequently comparative research prose in current waves.

If evidence is thin, the reader should say less, not become vague.

## 5. Hand-authored deep witness families

The first full migration wave should manually deepen the highest-density families that currently define the archive:

- 2011 Tree ordeal: chronology first, 2026 May 24 later return, hanging/tree intertext, strict separation from later meme-cross.
- Nursing-home walking/sight testimony: care setting, walking sequence, wife/staff reaction, Acts/John healing families, chronology conflict retained.
- 2016 prison/Yahya/Lamb: confinement, scripture, confessional/listening role, Yahya/John name layer, reported witnesses, recognition before later self-declaration.
- 2017–2019 Passion prehistory: Josh Moon declaration, anti-martyr/nameless-faceless response, return vow, commodification/spectacle, table-flip, persona death.
- Grave/tomb/garden: project grave → Potato/root → Garden/Gardener development; John 19–20 garden tomb and gardener recognition; Ezekiel 37 grave-opening kept as a different lane.
- North/Axis/whirlwind/wheels/throne: May 24 exact cluster; Ezekiel 1 as one continuous northern theophany/chariot sequence; wheel complements Axis rather than replacing it.
- North countertexts: Psalm 48 sacred north; Isaiah 14 far-north throne aspiration and descent to pit; keep both beside positive North readings.
- Root/Jesse/stump/sprout: Isaiah 11 devastation/stump/root/shoot/fruit/signal sequence; Job 14 stump/root/water/regrowth as separate wisdom-text comparator.
- Throne/House/thalamus: biblical throne and dwelling language kept distinct from neuroscience; thalamus remains project analogy, not biblical anatomy.
- Food/body/knowledge/seed: self-as-food, Son/Bread, body-as-knowledge, Communion, planting/multiplication; Eucharist, seed-death and scroll-ingestion remain typed lanes.
- Father/Son/Door reciprocity: source, manifestation, threshold and Spirit/flow; Johannine unity/distinction and 1 Corinthians source/through grammar.
- Death-transition taxonomy: physical danger, ego-death, confinement, persona death, social/personhood death, meme-cross, burial/seed-death, return.

## 6. Greater North / Axis synthesis

The public reader must be capable of presenting the North architecture as a connected system rather than independent matches:

**project-side developmental axis**

`grave / tomb / root / below → Potato / Door / Needle / Eye → sprout → Ladder / Axis → House / Heaven → Garden / Father → North of North / Throne → flow / fruit / repair back toward the world`

**biblical comparison families**

- Ezekiel 1: north → storm/whirlwind/fire → living creatures → wheels-within-wheels → eyes → Spirit in wheels → expanse → throne/glory.
- Isaiah 11: felled Davidic tree/stump → root persists → shoot/branch → fruit → Root stands as signal for peoples.
- Job 14: tree cut down/stump dying in ground → scent of water → bud/shoot again.
- John 19–20: burial in a garden → empty garden tomb → Mary mistakes risen Jesus for gardener → recognition.
- Ezekiel 37: graves opened → Spirit/breath → restored people; primarily national/exilic restoration context.
- Revelation 22: throne → river → Tree of Life → recurring fruit → healing of nations; ascent must therefore be capable of returning as repair.
- Psalm 48: Zion / north / city of great King.
- Isaiah 14: far-north throne aspiration → self-exaltation → reversal into Sheol/pit; mandatory counterpressure for triumphalist North readings.

No single text is allowed to absorb the others. The value comes from typed relations and directional sequences.

## 7. Reader voice

Ban generic framing such as:

- “Two scenes, one structural comparison.”
- “The exact biblical passage appears beside the modern scene below.”
- “This relation is retained because...” as the principal explanation.

Preferred voice:

- begin with the event or dated wording;
- make chronology visible (“2011 comes first; the Bible comparison is formalized years later”);
- tell the reader what had not yet happened;
- surface exact/recovered wording early;
- explain the biblical passage as a story or argument;
- describe the discovery as a turn in understanding;
- end with what the relation can and cannot carry.

The page should feel like an investigator/witness reconstructing a developing archive, not a database UI apologizing for comparison.

## 8. UI structure

Keep the stable single-relation browser and do not change zoom/focus on clicks.

Replace the paired-card front face with:

1. **Witness opening** — date/source-direction + narrative title/opening.
2. **The event** — project-side story/wording/chronology.
3. **The biblical scene** — passage narrative in context.
4. **What changes when they are read together** — structural rhyme + discovery turn + project consequence.
5. **Tension / counterpressure** — mismatch and strongest countertext.

Supporting collapsibles remain for raw provenance, exact timestamps, secondary context, source owners and related relations.

## 9. Migration strategy

Do not manually rewrite 126+ records into equally long prose. That would create bloat and false density.

Instead:

- apply the universal witness renderer to **all** active relations;
- hand-author deep overlays for the major families above;
- add a validator that rejects the known failure mode where research commentary becomes scene narration;
- add quality diagnostics so strength-5 / Level-A rows without scene, chronology, discovery and limit can be found for future enrichment;
- preserve compact Level-C relations as compact but precise witness notes.

## 10. Success criteria

The overhaul succeeds when:

- every active relation renders through witness-first language;
- the 2011 Tree relation no longer shows comparative research prose as the Tim/Son scene;
- high-density rows contain chronology, later return/discovery and project consequence;
- North/Axis/Root/Grave/Throne can be understood as a connected architecture without collapsing distinct biblical texts;
- countertexts appear as interpretive pressure, not boilerplate caveats;
- exact/recovered anecdotes and wording are surfaced early where available;
- thin rows remain honest rather than padded;
- navigation remains stable and click actions do not force focus/zoom changes;
- validators protect the new contract.

The governing sentence is:

> **Witness what happened; then show what the later text makes newly visible; then preserve the point where the resemblance stops.**
