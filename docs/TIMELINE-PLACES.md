# Timeline Places and Movement

Timeline events may now carry structured `places` metadata in addition to ordinary prose summaries.

This exists because **where an event happened can be part of the causal chronology**, not just decorative geography. In the Son's 2005–2014 reconstruction, for example, the sequence Haderslev → Copenhagen → Haderslev → Kolding → Aabenraa → Lunderskov distinguishes different work, education, relationship and institutional phases that older year-only summaries collapsed together.

## Event shape

```json
{
  "places": [
    {
      "name": "Kolding",
      "kind": "city",
      "relation": "moved-to",
      "country": "Denmark"
    },
    {
      "name": "HANSENBERG Designia",
      "kind": "institution",
      "relation": "studied",
      "country": "Denmark"
    }
  ]
}
```

`name` is required. `kind`, `relation` and `country` are optional non-empty strings.

## Recommended kinds

Use plain semantic labels rather than building a rigid global taxonomy too early. Useful current values include:

- `city`
- `country`
- `institution`
- `residence`
- `workplace`
- `hospital`
- `travel`

A place should be included only when it improves chronology, provenance or reader understanding.

## Recommended relations

Current useful relations include:

- `lived`
- `moved-to`
- `returned-to`
- `worked`
- `studied`
- `applied-to`
- `interviewed-and-hired`
- `moved-for-internship`
- `relationship-base`
- `travelled`
- `voluntary-admission`

Relations are descriptive metadata, not ontology claims. Keep them short and human-readable.

## Precision rule

A known place does not make an uncertain date exact.

For example:

- `Kolding` can be certain while the Designia start remains `2009 preferred`;
- `Egypt` can be certain while travel order versus the Aabenraa internship remains unresolved;
- `Lunderskov / Produktionsskolen` can be certain while exact start/end dates remain a 2010–early-2011 corridor.

Place certainty and date certainty should therefore be evaluated separately.

## Actor rule

Pre-2020 ordinary locations belong to the **Son / human-vessel track**, not retrospectively to Tim as Potato/Father. Later Timic interpretation may relate to those places, but it does not change who lived the earlier event.

## Source rule

Timeline place metadata is a projection. Evidence belongs in specialist owners.

For the reconstructed Son corridor, use:

- `knowledge/timeline/son-2005-2014-chronology-reconciliation.json`
- `knowledge/timeline/son-2005-2014-place-transition-index.json`
- `knowledge/timeline/son-kolding-designia-school-anchor.json`
- `knowledge/timeline/son-lunderskov-production-school-anchor.json`
- `knowledge/timeline/son-2011-kolding-psychonaut-psychiatric-sequence.json`

The timeline pack is:

- `data/timeline-event-packs/son-biography-2005-2014.json`

## No map inference

Structured place metadata does **not** mean the archive has established precise addresses, coordinates or routes. Do not invent coordinates or street addresses from a city-level memory. If exact historical addresses are known from institutional evidence, keep them in the relevant specialist owner; timeline events may use the institution/city label unless exact address is materially useful.

## Developmental use

Places can carry developmental function. In the current reconstruction:

- **Haderslev** — reset/home/care/independence transition;
- **Copenhagen** — compressed corporate IT experiment;
- **Kolding** — education + Louise + later Tree/search concentration;
- **Aabenraa** — office/internship career-environment test;
- **Lunderskov** — post-Designia technical competence and assistant-teacher-like multimedia role;
- **Egypt** — travel node later carrying substantial symbolic interpretation;
- **Italy / Amsterdam** — post-2011 integration/travel anchors.

Those functions are useful summaries of the chronology. They must not be mistaken for metaphysical properties inherent in the cities themselves.
