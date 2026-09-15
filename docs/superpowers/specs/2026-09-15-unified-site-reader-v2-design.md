# Unified Site Reader V2 — Design

## Goal
Make text-to-speech feel native across the Potato of Life site: explicit when the reader wants it, easy to find, quiet when unused, and shared across Bible, Story, Philosophy, Religion, Tim overview, and future long-form readers.

## Core interaction
Each readable page gets one shared TTS player. Readable sections may expose a small `🔊 Listen` action that sends that section into the shared player. No content expansion action auto-speaks; specifically, Story's `Hear the full story` remains a disclosure control only.

The player supports whole-page/current-section/selection scopes where those scopes exist. Bible keeps a specialized contextual model for Entire comparison / Project / Scripture / Why. Long-form pages use one generic adapter.

Selecting readable text reveals a temporary `🔊 Read selection` action near the selection. The selection is spoken only after that explicit click. The action disappears when the selection is cleared or the page context changes.

## Discoverability
The page-level `🔊 Listen` trigger must be visually obvious near the beginning of the reading surface. Section-level Listen controls appear unobtrusively beside or just below each section/story heading. When speech is active, the page-level player remains available while scrolling.

The section being explicitly read receives a restrained active-reading treatment so the user can see which story/movement/section owns the current speech without duplicating the article into a second reading pane.

## Architecture
- `app/tts-reader.js`: speech engine; unchanged except for bug fixes required by integration.
- `app/tts-drawer.js`: single shared player UI, stable API, shared selection action, and event hook.
- `app/longform-tts-adapter.js`: generic adapter for long-form pages, aligned to the current drawer API.
- `app/bible-tts-adapter.js`: specialized Bible contextual adapter.
- `app/tts-drawer.css`: shared page-player, inline Listen-control, selection action, sticky host, and active-reading styling.

Long-form adapter contract:
- Drawer mount uses `{ target, getPayload, settingsKey, onEvent }`.
- Payload refresh uses `drawer.setPayload(payload)`.
- One drawer instance per declared page host.
- `itemSelector` defines readable sections/stories.
- The adapter injects one idempotent `button.ptts-inline-listen` per readable item.
- Clicking an inline Listen button sets that item current, opens the player, selects the current-section scope, and starts speech only because the user explicitly clicked Listen.
- Selection reading never starts automatically.
- MutationObserver adds Listen buttons to asynchronously inserted Story entries without duplicating buttons.
- The shared selection action calls `drawer.playSection('selection')` only after an explicit user click.
- The active-reading class is applied only while the `current` scope is speaking and is removed on complete, stop, or error.

## Scope rules
- Story: Whole story / Current entry / Selection. Every `.story-entry` gets `🔊 Listen`. `Hear the full story` remains silent.
- Philosophy: Whole journey / Current movement / Selection. Every `.movement` gets `🔊 Listen`.
- Religion: Whole page / Current section / Selection for configured theological/question sections; navigation/promos/footer excluded.
- Tim overview: Whole overview / Current section / Selection for configured reading sections; navigation/deep-link chrome excluded.
- Bible: Existing contextual reader remains specialized, keeps Both / Project / Scripture / Why, gains Selection when the user selects text inside the active relation, and uses the same contextual Listen/selection language as long-form pages.
- Catalogs/maps/search/filter UIs remain silent until a meaningful active reading object exists.

## Preferences
Voice, speed, and volume use one shared settings key across site readers so choices persist between pages.

## Accessibility and behavior
- Inline Listen controls and selection actions are real buttons with accessible labels.
- No autoplay.
- Opening/expanding content never starts speech.
- Speech stops when the active Bible comparison changes or when a new explicit Listen action replaces the current item.
- The reader remains usable with keyboard navigation.
- Selection reading preserves the user's selected text long enough to start speech and never steals focus on pointer down.
- Reduced-motion preferences are respected by CSS.

## Testing
Tests must fail if:
- the generic adapter calls the obsolete drawer API;
- it cannot refresh with `setPayload`;
- section Listen buttons are duplicated;
- selection actions autoplay or fail to target the `selection` scope;
- active-reading state is not cleared after speech ends;
- Story/Philosophy/Religion/Tim lose their declarative TTS wiring;
- `Hear the full story` is wired to speech;
- Bible loses its visible TTS mount, contextual Listen action, selection scope, or dependency ordering.

The implementation must pass the existing repository quality checks and Pages build before merge.
