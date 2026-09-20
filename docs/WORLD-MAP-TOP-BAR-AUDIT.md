# World Map Top-Bar Audit

**Date:** 2026-09-20  
**Status:** active UI-density contract  
**Owner:** `world-map/3d-world-bar.js` + `world-map/index.html`

## Goal

Keep the World Map map-first. The top bar should expose only frequent direct actions, distinct map dimensions, and global navigation/reset. Deeper or overlapping capability belongs inside the relevant menu.

This audit is intentionally conservative: reduce visual weight and duplication without redesigning the World Map or removing meaningful capability.

## Persistent controls and justification

| Control | Keep visible? | Why it earns persistent space | Density rule |
| --- | --- | --- | --- |
| Search | Yes | Primary direct navigation to a country/place target. | Compact input; do not grow with result text. |
| Compare | Yes | Changes the working comparison set and is a frequent map-level action. | Small text button beside Search. |
| Inspect | Yes | Opens/closes the deeper semantic inspector; distinct from map selection. | Small text button; no duplicate top-bar inspector action. |
| N/W/E/S | Yes, grouped | Fast project-axis lenses are intentionally one-tap comparative views. | One compact four-button cluster; full names live in labels/tooltips, not button width. |
| Groups | Yes | Distinct set-membership layer family. | One menu. |
| Religion | Yes | Distinct analytical/set family with its own layer inventory. | One menu. |
| Stats | Yes | Scalar/statistical map family. | One menu. |
| Geography | Yes | Real/symbolic typed spatial overlays are a distinct map dimension. | One menu. |
| Analyze | Yes | Owns relationship lines, relation context, trace depth, relation type, and fit. | Relation-context filters live here; no separate Relations menu. |
| Time | Yes | Independent temporal dimension: current / as-of / changed-between. | One menu; lazy implementation remains behind it. |
| View | Yes | Camera/cartographic presentation: height, tilt, reset-world, focus mode. | One menu. |
| Projection | Yes | Flat/globe projection is a global map state used frequently enough for direct access. | Icon-width button only. |
| ANY/ALL | Conditional | Only meaningful when multiple set layers are active. | Hidden unless required. |
| Result count | Conditional | Gives compact feedback for active sets/layers. | Fixed compact width; hidden when irrelevant. |
| Reset | Yes | Global recovery action for map/layer/investigation state. | Icon-width button only. |
| Home | Yes | Direct global navigation escape from the map. | Small text link; never hidden in a More menu. |

## Controls deliberately not given their own persistent slot

- **Relations** — merged into **Analyze** because both operate on relationship exploration.
- **Interior modules** — remains inside **View** rather than becoming another top-level category.
- **Physical / Evidence specialist controls** — stay under their existing registry/menus and contextual owners rather than multiplying the header.
- **Region controls** — appear contextually in the country card, not globally.
- **Place controls** — appear contextually in region/place inspectors, not globally.
- **Conflict snapshots** — remain a Geography/Time capability, not a permanent top-level war button.

## Density limits

1. New persistent controls must satisfy one of three tests:
   - frequent direct action;
   - independent map dimension;
   - global navigation/reset.
2. A new control that overlaps an existing owner must be nested or merged instead of appended.
3. N/W/E/S remain a grouped control, not four ordinary-width actions.
4. Icon-only controls must use compact width.
5. Result/status text must not change the header footprint unpredictably.
6. Conditional controls remain hidden until their state makes them meaningful.
7. Mobile may scroll the toolbar, but desktop should not depend on horizontal scrolling at ordinary widths.
8. The top bar must remain one level deep; no nested toolbox or fifth “More” menu.

## Current judgment

The retained controls are justified after the 2026-09-20 density pass. The main redundancy was the standalone Relations menu; removing it and reducing visual weight is sufficient. No drastic redesign is warranted.
