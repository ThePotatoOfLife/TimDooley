# World Map Interface Contract

**Date:** 2026-10-02  
**Status:** active public-interface contract  
**Owner:** `world-map/3d-world-bar.js` + `world-map/index.html`

## Product purpose

The World Map answers one broad human question:

> **What is happening where, and how is it connected?**

A stranger should be able to open it and understand the first move without knowing the repository, Potatoverse vocabulary, graph terminology, or the internal layer architecture.

The map may remain deep. The first screen must remain simple.

## Public navigation

Persistent controls are intentionally limited to:

| Control | Public question |
| --- | --- |
| Search | Where is the place I care about? |
| Countries | What is this country like, and how do countries compare? |
| Now | What important current context is happening where? |
| Connections | How is this place connected to other places and systems? |
| History | What was true at another time, or how was this place understood historically? |
| Map | How should the map itself be displayed or reset? |
| Home | How do I leave the map? |

Everything else belongs **inside** one of those concepts or appears contextually after selection.

## Progressive-disclosure rules

1. **Do not expose internal taxonomy as primary navigation.** Registry families, epistemic enums, project-axis abbreviations, renderer vocabulary and graph jargon can exist in deeper explanation, not as unexplained first-screen controls.
2. **Features may be numerous; top-level intentions may not.** New functionality must fit Countries, Now, Connections, History or Map before a new persistent control is considered.
3. **Context before machinery.** A country click should reveal ordinary country meaning before investigation tools. A conflict click should explain the conflict before exposing provenance machinery.
4. **Project lenses are secondary.** North/West/East/South remain available, but inside Countries as project lenses rather than four unexplained permanent buttons.
5. **Workspace tools are secondary.** Compare, Details, projection, reset and extra modules live inside Map rather than occupying the permanent header.
6. **Current events and history are different jobs.** Current conflict context belongs under Now; historical reconstruction and time travel belong under History.
7. **Conditional logic stays conditional.** ANY/ALL, result counts, evidence controls, region controls and specialist tools appear only when their state makes them meaningful.
8. **Plain labels beat clever labels.** Prefer Countries, Now, Connections, History and Map over names that require prior explanation.
9. **Home remains directly visible.** Do not hide the global escape route in another menu.
10. **Desktop should not require horizontal toolbar scrolling at ordinary widths.** Mobile may scroll if necessary.

## Runtime-weight rule

Hiding a control is not sufficient if its expensive implementation still loads on initial paint.

The core boot should own only what is required to:
- draw and move the map;
- search/select a country;
- render the ordinary country experience;
- compose the public control shell;
- activate lightweight current context.

Expensive investigation, evidence, time, deep graph traversal, detailed physical layers, Axis machinery and specialist analysis should remain lazy or become lazy when practical.

## Direction

The map is not a dashboard of every dataset in the repository. It is a **spatial doorway into the world knowledge system**.

A useful feature earns its place when it helps a visitor:
- locate something;
- understand a place;
- understand what is happening there;
- compare it with somewhere else;
- follow an important connection;
- move through time;
- or reach deeper evidence/research from a geographic starting point.

Capabilities that cannot answer one of those needs should be demoted, consolidated, or removed from the public map.
