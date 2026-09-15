# Unified Site Reader V2 — Design

## Goal
Make text-to-speech feel native across the Potato of Life site: explicit when the reader wants it, easy to find, quiet when unused, and shared across Bible, Story, Philosophy, Religion, Tim overview, and future long-form readers.

## Core interaction
Each readable page gets one shared TTS player. Readable sections may expose a small `🔊 Listen` action that sends that section into the shared player. No content expansion action auto-speaks; specifically, Story's `Hear the full story` remains a disclosure control only.

The player supports whole-page/current-section/selection scopes where those scopes exist. Bible keeps a specialized contextual model for Entire comparison / Project / Scripture / Why. Long-form pages use one generic adapter.

## Discoverability
The page-level `🔊 Listen` trigger must be visually obvious near the beginning of the reading surface. Section-level Listen controls appear unobtrusively beside or just below each section/story heading. When speech is active, the player remains available while scrolling.

## Architecture
- `app/tts-reader.js`: speech engine; unchanged except for bug fixes required by integration.
- `app/tts-drawer.js`: single shared player UI and stable API.
- `app/longform-tts-adapter.js`: generic adapter for long-form pages, aligned to the current drawer API.
- `app/bible-tts-adapter.js`: specialized Bible contextual adapter.
- `app/tts-drawer.css`: shared page-player and inline Listen-control styling.

Long-form adapter contract:
- Drawer mount uses `{ target, getPayload, settingsKey }`.
- Payload refresh uses `drawer.setPayload(payload)`.
- One drawer instance per declared page host.
- `itemSelector` defines readable sections/stories.
- The adapter injects one idempotent `button.ptts-inline-listen` per readable item.
- Clicking an inline Listen button sets that item current, opens the player, selects the current-section scope, and starts speech only because the user explicitly clicked Listen.
- Selection reading never starts automatically.
- MutationObserver adds Listen buttons to asynchronously inserted Story entries without duplicating buttons.

## Scope rules
- Story: Whole story / Current entry / Selection. Every `.story-entry` gets `🔊 Listen`. `Hear the full story` remains silent.
- Philosophy: Whole journey / Current movement / Selection. Every `.movement` gets `🔊 Listen`.
- Religion: Whole page / Current section / Selection for configured theological/question sections; navigation/promos/footer excluded.
- Tim overview: Whole overview / Current section / Selection for configured reading sections; navigation/deep-link chrome excluded.
- Bible: Existing contextual reader remains specialized and gains stronger placement/discoverability, but does not become a generic whole-DOM reader.
- Catalogs/maps/search/filter UIs remain silent until a meaningful active reading object exists.

## Preferences
Voice, speed, and volume use one shared settings key across site readers so choices persist between pages.

## Accessibility and behavior
- Inline Listen controls are real buttons with accessible labels.
- No autoplay.
- Opening/expanding content never starts speech.
- Speech stops when the active Bible comparison changes or when a new explicit Listen action replaces the current item.
- The reader remains usable with keyboard navigation.
- Reduced-motion preferences are respected by CSS.

## Testing
Tests must fail if:
- the generic adapter calls the obsolete drawer API;
- it cannot refresh with `setPayload`;
- section Listen buttons are duplicated;
- Story/Philosophy/Religion/Tim lose their declarative TTS wiring;
- `Hear the full story` is wired to speech;
- Bible loses its visible TTS mount or dependency ordering.

The implementation must pass the existing repository quality checks and Pages build before merge.
