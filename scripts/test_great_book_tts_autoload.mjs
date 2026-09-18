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
const controller = new AbortController();
const lazyRoot = {
  dispatchEvent(event) {
    assert.equal(event.type, 'potato:tts-prepare');
    assert.equal(event.detail.sectionId, 'all');
    assert.equal(event.detail.signal, controller.signal);
    event.detail.waitUntil(Promise.resolve().then(() => { prepared = true; }));
    return true;
  }
};

assert.equal(typeof adapter.requestContentPreparation, 'function', 'longform adapter must expose lazy-content preparation');
const didPrepare = await adapter.requestContentPreparation(lazyRoot, 'all', FakeCustomEvent, {signal:controller.signal});
assert.equal(didPrepare, true, 'preparation should report when a lazy loader joined the request');
assert.equal(prepared, true, 'preparation must await lazy-loading work before TTS continues');

const drawerSource = fs.readFileSync(new URL('../app/tts-drawer.js', import.meta.url), 'utf8');
assert.ok(drawerSource.includes('prepareSection'), 'drawer must support an async prepare hook');
assert.ok(drawerSource.includes('await prepareSection(sectionId,{signal:'), 'drawer must wait for cancellable lazy text before taking the speech snapshot');
assert.ok(drawerSource.includes("'loading text…'"), 'drawer should expose loading state while lazy text is prepared');
assert.ok(drawerSource.includes('AbortController'), 'drawer must be able to cancel pending lazy preparation');

const adapterSource = fs.readFileSync(new URL('../app/longform-tts-adapter.js', import.meta.url), 'utf8');
assert.ok(adapterSource.includes("'potato:tts-prepare'"), 'adapter must dispatch the shared TTS preparation event');
assert.ok(adapterSource.includes('waitUntil'), 'adapter preparation event must allow lazy readers to register async work');
assert.ok(adapterSource.includes('prepareSection:prepareForPlayback'), 'adapter must connect lazy preparation to the drawer');
assert.ok(adapterSource.includes('signal:options.signal'), 'adapter must forward cancellation to lazy readers');

const readerSource = fs.readFileSync(new URL('../app/great-book-reader.js', import.meta.url), 'utf8');
assert.ok(readerSource.includes('async function loadAllSlots'), 'Great Book needs a whole-book loader for TTS');
assert.ok(readerSource.includes("addEventListener('potato:tts-prepare'"), 'Great Book must respond to TTS preparation requests');
assert.ok(readerSource.includes("detail.sectionId!=='all'"), 'Great Book should only force full preloading for whole-book speech');
assert.ok(readerSource.includes('detail.waitUntil(loadAllSlots({signal:detail.signal}))'), 'TTS must await cancellable loading of missing Great Book chapters');

const greatBookHtml = fs.readFileSync(new URL('../great-book/index.html', import.meta.url), 'utf8');
assert.ok(greatBookHtml.includes('data-tts-all-label="Whole book"'), 'Great Book scope label should describe the now-complete book text');
assert.ok(greatBookHtml.includes('src="../app/great-book-loader.js"'), 'Great Book must load the resilient chapter loader before the reader');

console.log('great book tts autoload contract: ok');
