# TTS Reader Rebuild Design

## Goal
Replace the prototype lineage with a reliable, dependency-free Web Speech reader that has one tested core and two distributions: a self-contained downloadable HTML file and a modular GitHub edition.

## Reliability decisions

1. Treat the eight old HTML files as behavioral references only; do not transplant their playback loops.
2. Use a plain textarea for authoring. Speech highlighting never rewrites editable HTML.
3. Snapshot text when playback starts. Editing during playback does not mutate the active read session.
4. Maintain strict single-utterance sequencing. The next utterance is submitted only from the previous utterance's successful end callback.
5. Every playback run has a session token and every utterance has a serial token. Late callbacks from `cancel()` or prior sessions are ignored.
6. Chunk lazily from absolute character offsets. Prefer paragraph/sentence/phrase/word boundaries, with a hard maximum fallback.
7. Persist voices by stable identity (`voiceURI`, name, language), never by list index.
8. Use one per-utterance watchdog based on chunk length and speech rate, not a permanent pause/resume keep-alive loop.
9. Recovery restarts the current chunk from its known start, reduces chunk size, and is bounded. No approximate rollback into the middle of words.
10. Pause clears the watchdog. Resume recreates it. Stop invalidates callbacks before calling browser `cancel()`.
11. The UI uses a separate current-passage display and progress meter. Large documents never require rebuilding a mirrored DOM.
12. No external fonts, libraries, RSS proxies, or network dependencies in the standalone build.

## User-facing features

- Voice chooser with language/name labels
- Rate, pitch, volume
- Speak, pause, resume, stop
- Read all / read selection / read from cursor
- Natural long-text chunking
- Auto-recovery with bounded adaptive chunk reduction
- Progress, current passage, elapsed position, recovery counter
- Local draft and preference persistence with privacy-safe opt-out for draft saving
- Import `.txt`/`.md`; export `.txt`; copy
- Light, dark, system appearance
- Font size and comfortable reading width
- Keyboard shortcuts (Ctrl/Cmd+Enter start, Space pause/resume when editor is not focused, Esc stop)
- Advanced diagnostics and chunk-size control
- Graceful unsupported-browser state

## Project placement

- `app/tts-reader.js`: dependency-free UMD module exporting chunker, engine, and browser controller helpers.
- `app/tts-reader.css`: namespaced `.tts-*` presentation styles.
- `tts/index.html`: dedicated project tool using the reusable assets.
- `scripts/test_tts_reader.mjs`: Node regression tests for deterministic core behavior.
- `docs/superpowers/specs/2026-09-15-tts-reader-rebuild-design.md`: architectural memory.
- `docs/superpowers/plans/2026-09-15-tts-reader-rebuild-implementation.md`: implementation record.

## Standalone distribution

`TTS Ultimate.html` embeds the tested JS and CSS into a single file so it can be opened directly from disk without a local server.
