# Project-wide navigation and focus audit — 2026-09-20

## Goal

Make a very large archive feel smaller without deleting its depth.

The project already has good ownership machinery: canonical public surfaces, Rooms, topology, source boundaries, TTS, search/discovery files, and validators. The remaining problem is reader orientation. Growth has produced many legitimate specialist pages, but a visitor can still lose the answer to four simple questions:

1. Where am I?
2. What larger subject owns this page?
3. What are the few main ways back into the project?
4. Where do I go if I want to find something specific rather than keep reading linearly?

The rule for this pass is therefore **less visible navigation, stronger orientation**.

## Site-wide priorities

- [x] Add a compact project compass to ordinary reader pages. It should identify the current surface, its parent where known, the five canonical gateways, and the global discovery tools without replacing local navigation.
- [ ] Make every mature reader page state its job in the first screen: one sentence answering “what is this page for?”
- [ ] Keep exactly one dominant local reading path per page. Secondary links belong inline or in the compass, not in competing card grids.
- [ ] Prefer parent → current → adjacent relationships over generic “more” links.
- [ ] Treat Home, five gateways, Rooms/House, and discovery tools as different navigation layers. Do not let them compete visually.
- [ ] Audit pages that expose more than seven first-screen links; reduce repeated links before adding anything new.
- [ ] Audit pages that contain multiple introductions saying nearly the same thing. Keep the strongest one and move detail lower.
- [ ] Keep TTS controls out of navigation prose and keep navigation out of TTS reading.
- [ ] Preserve specialist depth. The objective is not fewer pages; it is clearer ownership and fewer dead ends.
- [ ] Extend validators so generated pages can be checked for orientation markers and broken parent routes.

## Page-family refinement

### Home
- Keep the first screen about what the project is, not every capability it has.
- Preserve the four-step spine: Center → Structure → Knowledge → Views.
- Let “Current World” remain a window, not another primary branch.
- Compress repeated archive/discovery links if they duplicate the new compass or footer routes.

### Tim Dooley
- Treat it as the main human/project portrait.
- Keep biography, public witness, 100,000 Hours, claims, story and chronology discoverable from prose rather than a dense button field.
- Make the difference between biography, project self-description, public record and later interpretation visible early.

### Potato of Life
- Keep this as the canonical meaning-center rather than a directory.
- Lead with the integrated concept, then route Father/Son/Spirit, body, geometry and comparative material outward.
- Avoid duplicating Religion or Science inside the page when one contextual door is enough.

### Religion
- Keep internal Potatoism theology and comparative traditions visibly distinct.
- Bible, Trinity and historical traditions should read as specialist continuations, not rival homepages.
- Prefer “internal claim → textual comparison → evidence boundary” as the repeated reading rhythm.

### Philosophy
- Keep the Spiral Reader as the primary route.
- Reduce auxiliary structure above the first turn.
- Use examples to connect philosophy to practice instead of adding more abstract category cards.

### Science
- Make “model / analogy / evidence / falsifier” the page’s repeated grammar.
- Put the research library after the reader understands what kind of claim each document can make.
- Keep biology, physics, neuroscience and formal models easy to distinguish by evidence type.

### World
- Keep World as the readable hub; Map, Politics, North, Economy, Law and Systems are specialist lenses.
- Make country/institution/current-event routes obvious without making them equal top-level branches.
- Current news should link into World and relevant specialist views, not become a parallel ownership system.

### World Map
- Keep interaction primary and prose secondary.
- Continue improving region/country/city selection, conflict/time layers and contextual statistics.
- Avoid global site navigation occupying map workspace; use a compact return/orientation affordance.

### House
- Explain architecture before exposing registries.
- Keep Center, Rooms, operators, interfaces and ownership rules visually distinct.
- The House should answer “how does this project fit together?” rather than becoming another content index.

### Rooms
- Make each Dwelling and nested Room answer three things immediately: what it owns, what it excludes, what lives here.
- Keep generated holdings and inhabitants below that explanation.
- Add “best next door” cues only when the relation is meaningful; adjacency should not become link spam.

### Explore / A–Z / Questions / Paths
- Treat these as discovery modes with different jobs:
  - Explore = relationships and archive views.
  - A–Z = known-term lookup.
  - Questions = start from uncertainty.
  - Paths = guided multi-page traversal.
- Cross-link them lightly, but do not merge their purposes.

### Timeline / History / Sources
- Timeline owns sequence.
- History owns interpretation/revision over time.
- Sources owns provenance/evidence rules.
- Keep these three mutually visible because confusion between them creates many downstream errors.

### Below / Culture / Farm / Sektur
- Keep project metaphors, observed platform behavior, sourced institutions and allegations explicitly typed.
- Give each page a strong local scope so the lower-system material does not feel like one enormous undifferentiated archive.
- Use chronology and named mechanisms to create orientation rather than more labels.

### Life & Body
- Lead with anatomy/biology where the page is scientific and symbolism where the page is symbolic.
- Preserve the boundary between resemblance and evidence.
- Use the 33 vertebrae / brain / CSF / pineal / thalamus material as nested routes, not simultaneous first-screen demands.

### Works / Great Book / creative surfaces
- Distinguish finished work, evolving canon, archive artifact and experiment.
- Provide one route back to the conceptual context and one route to chronology; avoid over-navigation.

## Navigation quality tests

A page is healthy when a new reader can answer, within roughly ten seconds:

- What is this?
- Why is it here?
- What larger area am I in?
- What is the most important next thing to read?
- How do I get back to a main gateway?
- How do I search/find a specific thing?

A page needs refinement when:

- the first screen contains multiple competing menus;
- the same destination appears repeatedly under different labels;
- “deep”, “more”, “archive”, “explore” or “context” links do not say what the reader will find;
- the page behaves like a hub even though another canonical hub already owns the subject;
- a specialist page has no visible parent;
- cards are being used to compensate for unclear prose hierarchy;
- the reader must understand House terminology before understanding why the material is interesting.

## Next implementation waves

1. **Orientation coverage** — validate that ordinary public reader pages receive the shared compass and that mapped specialist surfaces resolve to a valid parent.
2. **First-screen focus** — audit the canonical hubs and remove duplicated or competing navigation from their opening viewport.
3. **Specialist continuity** — audit World, Tim, Religion, Science, Below/Culture and Body descendants for parent/adjacent continuity.
4. **Discovery separation** — refine Explore, A–Z, Questions and Paths so each has one unmistakable use case.
5. **Link-language audit** — replace vague anchors with destination intent while preserving compact inline links.
6. **Dead-end audit** — find pages with no useful onward route and connect them to their owning hub or Room.
7. **Mobile pass** — check that the same hierarchy survives narrow screens without turning every navigation system into stacked button walls.
