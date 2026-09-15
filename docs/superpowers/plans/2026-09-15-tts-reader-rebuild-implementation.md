# TTS Reader Rebuild Implementation Plan

**Goal:** Build a tested Web Speech TTS core, a standalone downloadable reader, and a modular project edition.

**Architecture:** A pure/testable UMD playback engine owns chunking and state. The browser UI is a thin controller around the engine. The standalone artifact embeds the same project JS/CSS rather than maintaining a second engine.

**Tech Stack:** HTML5, CSS, vanilla JavaScript, Web Speech API, Node.js `node:test`.

**Spec:** `docs/superpowers/specs/2026-09-15-tts-reader-rebuild-design.md`

## Global constraints

- No runtime dependencies.
- No network requirement in the standalone file.
- Never rewrite editable HTML for highlighting.
- Ignore stale speech callbacks after stop/restart.
- Never queue the next utterance until the current utterance ends.
- Tests cover chunk integrity, stale callbacks, sequential speech, stop, bounded recovery, pause/resume edge cases, and enormous whitespace runs.

## Planned repository files

- `app/tts-reader.js` — reusable deterministic speech core.
- `app/tts-reader.css` — namespaced reader presentation.
- `tts/index.html` — full project-facing TTS page.
- `scripts/test_tts_reader.mjs` — Node regression suite.
- `scripts/build_tts_standalone.py` — builds the single-file distribution.

## Promotion rule

The standalone HTML is tested first in real browsers. The modular code is developed from the same tested core on this feature branch and should not be merged to `main` until the standalone behavior has been tried with the user's preferred installed voices and long-form texts.
