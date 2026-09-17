import assert from 'node:assert/strict';
import fs from 'node:fs';
import adapter from '../app/longform-tts-adapter.js';

class FakeCustomEvent {
  constructor(type, options={}) {
    this.type = type;
    this.detail = options.detail;
    this.bubbles = Boolean(options.bubbles);
  }
}

let prepared = false;
const lazyRoot = {
  dispatchEvent(event) {
    assert.equal(event.type, 'potato:tts-prepare');
    assert.equal(event.detail.sectionId, 'all');
    event.detail.waitUntil(Promise.resolve().then(() => { prepared = true; }));
    return true;
  }
};

assert.equal(typeof adapter.requestContentPreparation, 'function', 'longform adapter must expose lazy-content preparation');
const didPrepare = await adapter.requestContentPreparation(lazyRoot, 'all', FakeCustomEvent);
assert.equal(didPrepare, true, 'preparation should report when a lazy loader joined the request');
assert.equal(prepared, true, 'preparation must await lazy-loading work before TTS continues');

const drawerSource = fs.readFileSync(new URL('../app/tts-drawer.js', import.meta.url), 'utf8');
assert.ok(drawerSource.includes('prepareSection'), 'drawer must support an async prepare hook');
assert.ok(drawerSource.includes('await prepareSection(sectionId)'), 'drawer must wait for lazy text before taking the speech snapshot');
assert.ok(drawerSource.includes("status.textContent='loading text…'"), 'drawer should expose loading state while lazy text is prepared');

const adapterSource = fs.readFileSync(new URL('../app/longform-tts-adapter.js', import.meta.url), 'utf8');
assert.ok(adapterSource.includes("'potato:tts-prepare'"), 'adapter must dispatch the shared TTS preparation event');
assert.ok(adapterSource.includes('waitUntil'), 'adapter preparation event must allow lazy readers to register async work');
assert.ok(adapterSource.includes('prepareSection:prepareForPlayback'), 'adapter must connect lazy preparation to the drawer');

const readerSource = fs.readFileSync(new URL('../app/great-book-reader.js', import.meta.url), 'utf8');
assert.ok(readerSource.includes('async function loadAllSlots'), 'Great Book needs a whole-book loader for TTS');
assert.ok(readerSource.includes("addEventListener('potato:tts-prepare'"), 'Great Book must respond to TTS preparation requests');
assert.ok(readerSource.includes("detail.sectionId!=='all'"), 'Great Book should only force full preloading for whole-book speech');
assert.ok(readerSource.includes('detail.waitUntil(loadAllSlots())'), 'TTS must await all missing Great Book chapters');

const greatBookHtml = fs.readFileSync(new URL('../great-book/index.html', import.meta.url), 'utf8');
assert.ok(greatBookHtml.includes('data-tts-all-label="Whole book"'), 'Great Book scope label should describe the now-complete book text');

console.log('great book tts autoload contract: ok');
