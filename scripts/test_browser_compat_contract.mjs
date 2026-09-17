import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = path => fs.readFileSync(path, 'utf8');
const siteCss = read('app/site-system.css');
const styleCss = read('app/style.css');
const longformCss = read('app/longform-reader.css');
const ttsCss = read('app/tts-drawer.css');
const minimalCss = read('minimal.css');
const greatBook = read('app/great-book-reader.js');
const timeline = read('app/timeline.js');
const ttsReader = read('app/tts-reader.js');
const standaloneTts = read('tools/tts/index.html');

assert.match(siteCss, /overflow-wrap\s*:\s*anywhere/, 'shared site CSS should contain a long-content overflow fallback');
assert.match(siteCss, /max-width\s*:\s*100%/, 'shared site CSS should constrain media/content to the viewport');
assert.match(ttsCss, /safe-area-inset-(?:bottom|left|right|top)/, 'viewport-edge TTS controls should account for device safe areas');
assert.match(minimalCss, /100dvh|100svh/, 'full-height legacy/minimal layout should include a modern mobile viewport unit after its vh fallback');
assert.match(longformCss, /overflow-x\s*:\s*auto/, 'wide longform content should stay inside its own horizontal scroller');

assert.match(greatBook, /typeof\s+IntersectionObserver|['"]IntersectionObserver['"]\s+in\s+(?:window|globalThis)/, 'Great Book must feature-detect IntersectionObserver');
assert.match(timeline, /navigator\.clipboard\?\.|navigator\.clipboard\s*&&|if\s*\(\s*navigator\.clipboard/, 'timeline copy must feature-detect Clipboard API');

assert.match(ttsReader, /CSS\.highlights|Highlight/, 'shared TTS should retain its Custom Highlight capability path');
assert.match(ttsReader, /createRange|Range/, 'shared TTS should retain a DOM/range fallback path');
assert.match(standaloneTts, /navigator\.clipboard\?\./, 'standalone TTS copy should remain guarded when Clipboard API is unavailable');

console.log('Browser compatibility contract OK');
