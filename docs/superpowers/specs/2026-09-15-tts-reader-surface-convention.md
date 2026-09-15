# Project TTS Reader Surface Convention

**Date:** 2026-09-15  
**Status:** Working architecture on `feat/tts-tool-v6`

## Purpose

Text to Speech is project infrastructure, not a sixth subject branch. The full laboratory lives at `/tools/tts/`; other pages may expose the same speech capability through a compact contextual drawer.

The goal is maximal reading capability with minimal permanent UI. A page should gain one small `Read aloud` doorway, not a duplicate speech application.

## Architecture

### 1. Speech engine

`app/tts-reader.js`

Owns Web Speech scheduling, chunking, recovery, voice identity, progress and word-boundary events. Other surfaces must not implement their own speech queue.

### 2. Context drawer

`app/tts-drawer.js` + `app/tts-drawer.css`

Owns the three-state embedded interface:

1. collapsed trigger;
2. compact one-line controls;
3. optional expanded reading strip with spoken-word focus.

The drawer consumes a normalized payload:

```js
{
  id: 'context-id',
  label: 'Reader label',
  sections: [
    { id: 'scope-id', label: 'Scope label', text: 'Readable text' }
  ]
}
```

When payload identity changes, stale playback stops rather than continuing old context.

### 3. Specialized adapters

Use a specialized adapter when the page has a meaningful active object or domain-specific reading order.

Current example: `app/bible-tts-adapter.js`.

The Bible comparator understands one active relation and exposes `Both`, `Project`, `Scripture` and `Why`. This is preferable to scraping whichever comparator text happens to be visible.

### 4. Declarative long-form adapter

`app/longform-tts-adapter.js`

Use this for prose/reader surfaces whose DOM already contains the content to read. Pages opt in with data attributes rather than page-specific JavaScript.

Example:

```html
<div
  data-tts-longform
  data-tts-root=".journey"
  data-tts-id="philosophy-journey"
  data-tts-label="Potatoism Philosophy"
  data-tts-all-label="Whole journey"
  data-tts-current-label="Current movement"
  data-tts-selection-label="Selection"
  data-tts-item=".movement"
  data-tts-exclude=".page-nav,.footer">
</div>
```

The shared assets load in dependency order:

```html
<link rel="stylesheet" href="../app/tts-drawer.css">
<script src="../app/tts-reader.js"></script>
<script src="../app/tts-drawer.js"></script>
<script src="../app/longform-tts-adapter.js"></script>
```

Supported declarative attributes:

- `data-tts-root`: the content region that owns the whole-reading scope.
- `data-tts-item`: optional selector for a current entry/section scope.
- `data-tts-exclude`: optional selector list removed from the cloned text before reading; use it for navigation, promos, controls and other chrome.
- `data-tts-id`: stable payload identity.
- `data-tts-label`: reader label.
- `data-tts-all-label`: whole-reading scope label.
- `data-tts-current-label`: current-item scope label.
- `data-tts-selection-label`: selected-text scope label.

The adapter observes asynchronous content changes, tracks the current item from click/focus, and exposes selected text when the selection belongs to the declared root.

## Current integrations

- `/tools/tts/` — full advanced reader.
- `/traditions/bible/` — specialized context adapter for active comparisons.
- `/tim-dooley/story/` — declarative long-form reader over the asynchronous chronological story stream.
- `/tim-dooley/` — declarative overview reader spanning question, work, developmental and quotation sections while skipping route/navigation chrome.
- `/philosophy/` — declarative reader over the eight-stage philosophical journey.
- `/religion/` — declarative mixed-content reader using exclusion rules to skip site chrome and the Bible-lab promo.

## What should stay quiet

Do not attach whole-DOM TTS to navigation hubs, search-result catalogs or dense control surfaces merely because they contain text.

Examples:

- The Science index contains a filterable catalog, not an active document viewport. The catalog itself should remain quiet; individual full science documents are better TTS targets.
- The Great Book route is still a restoration shell. TTS should target the validated chapter reader once the chapter payload is restored, not read the restoration notice as though it were the book.
- Map interfaces should use a specialized adapter for the selected place/card/brief rather than read labels, legends and controls indiscriminately.

## Expansion rule

Before adding TTS to a surface, choose one of two questions:

1. **Is there a meaningful active object?** Build a thin specialized adapter that returns a structured reading payload.
2. **Is this primarily prose with stable sections?** Use the declarative long-form adapter.

If neither is true, do not add an embedded reader yet.
