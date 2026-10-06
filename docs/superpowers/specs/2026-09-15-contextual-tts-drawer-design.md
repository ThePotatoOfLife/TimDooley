# Contextual TTS Drawer Design

**Date:** 2026-09-15  
**Status:** Approved for implementation  
**Repository:** `ThePotatoOfLife/TimDooley`  
**Branch:** `feat/tts-tool-v6`

## Purpose

Extend the compact TTS reader from a standalone tool into a reusable, collapsible project utility that can live inside content tools without permanently consuming page space.

`/tools/tts/` remains the full paste/type reader. Embedded surfaces use the same speech engine through a compact drawer.

## Interaction model

The embedded reader has three states:

1. **Closed** — one compact `Read aloud` / speaker trigger.
2. **Open** — a single-line transport strip with Play, Pause, Stop, reading scope, Voice, Volume, Speed and an expand control.
3. **Expanded** — the same transport strip plus a compact current-reading viewport with spoken-word focus/highlighting.

The drawer must never add a second full editor to a host tool.

## Reusable architecture

- `app/tts-reader.js` remains the deterministic speech engine.
- `app/tts-drawer.js` owns the reusable drawer UI and reading-session behavior.
- `app/tts-drawer.css` owns drawer presentation and must inherit host-page visual variables where possible.
- Host adapters provide a `getPayload()` callback returning structured readable material.

A payload has this conceptual shape:

```js
{
  id: 'current-object-id',
  label: 'Current object label',
  sections: [
    { id: 'all', label: 'Both', text: '...' },
    { id: 'project', label: 'Project', text: '...' },
    { id: 'scripture', label: 'Scripture', text: '...' },
    { id: 'why', label: 'Why', text: '...' }
  ]
}
```

The drawer should preserve voice, speed and volume preferences across host pages. If the payload changes while speech is stopped, the drawer updates quietly. If the payload changes while speaking, playback stops rather than continuing stale material.

## Bible comparator proof-of-concept

The Bible comparator is the first host. `app/bible-tts-adapter.js` mounts the drawer near the comparison navigation and derives structured content from the active relation viewport.

Required scopes:

- **Both** — project side, scripture side, connection explanation, and visible mismatch/counter-fit when present.
- **Project** — project-side anchor and attached project wording.
- **Scripture** — scripture passages/references currently shown.
- **Why** — the comparison explanation plus visible mismatch/counter-fit.

The adapter observes changes to `#active-relation`, because the comparator replaces that viewport whenever the active relation changes. It updates the drawer payload after each render.

## Highlighting

Embedded expanded mode uses a compact read-only sentence/passage viewport. When Web Speech boundary events are available, the current word is rendered as a crisp highlighted span using the same focus principle as the standalone reader. No blur/backdrop-filter lens is used.

If exact word boundary timing is unavailable, the current passage remains visible without fake word timing.

## Accessibility and resilience

- Trigger and controls have explicit labels.
- Drawer state is communicated with `aria-expanded`.
- Native select controls may be used inside the embedded drawer if the host theme keeps them readable; otherwise the drawer supplies its own dark/light-safe styling.
- No JavaScript support leaves the host tool unchanged.
- Unsupported Speech Synthesis disables playback controls without breaking the host page.

## Scope boundary

This implementation proves the reusable drawer and Bible comparator integration. Story pages, Great Book chapters and generic article adapters are later consumers; they are not part of this first integration.
