import assert from 'node:assert/strict';
import fs from 'node:fs';

const page=fs.readFileSync(new URL('../great-book/index.html',import.meta.url),'utf8');
const reader=fs.readFileSync(new URL('../app/great-book-reader.js',import.meta.url),'utf8');

for(const marker of [
  'href="../app/tts-drawer.css"',
  'id="great-book-tts"',
  'data-tts-manual="true"',
  'data-tts-root="#gb-document"',
  'data-tts-item=".gb-chapter-fragment"',
  'data-tts-all-label="Whole book"',
  'data-tts-current-label="Current chapter"',
  'src="../app/tts-reader.js"',
  'src="../app/tts-drawer.js"',
  'src="../app/longform-tts-adapter.js"',
  'src="../app/great-book-reader.js"',
]) assert.ok(page.includes(marker),`Great Book TTS integration missing ${marker}`);

assert.ok(!page.includes('data-tts-longform'), 'Great Book must not auto-mount TTS because the reader owns whole-book preloading');
const enginePos=page.indexOf('src="../app/tts-reader.js"');
const drawerPos=page.indexOf('src="../app/tts-drawer.js"');
const adapterPos=page.indexOf('src="../app/longform-tts-adapter.js"');
const readerPos=page.indexOf('src="../app/great-book-reader.js"');
assert.ok(enginePos<drawerPos&&drawerPos<adapterPos&&adapterPos<readerPos,'Great Book TTS dependencies must load engine -> drawer -> adapter -> book reader');

for(const marker of [
  'PotatoLongformTTS',
  'Longform.mount({',
  'itemSelector:\'.gb-chapter-fragment\'',
  'async function loadAllSlots()',
  'async function prepareWholeBook()',
  "id==='all'",
  'select[aria-label="Reading scope"]',
  'button[title="Play"]',
  "scope?.value!=='all'",
  'await loadAllSlots()',
  "slot.dataset.loaded==='error'",
  'ttsInstance?.ensureListenButtons?.()',
  'ttsInstance?.refresh?.()',
]) assert.ok(reader.includes(marker),`Great Book reader TTS contract missing ${marker}`);

assert.ok(reader.includes("status.textContent='Loading the complete book for reading…'"),'Whole-book playback must expose preload progress');
assert.ok(reader.includes("status.textContent='Complete book loaded for reading.'"),'Whole-book playback must expose preload completion');
assert.ok(reader.includes('event.preventDefault();event.stopImmediatePropagation();'),'Whole-book Play must be blocked until lazy loading finishes');

console.log('great book tts contract: ok');
