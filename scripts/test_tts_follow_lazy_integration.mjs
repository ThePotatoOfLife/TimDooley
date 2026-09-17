import assert from 'node:assert/strict';
import fs from 'node:fs';
import drawer from '../app/tts-drawer.js';
import adapter from '../app/longform-tts-adapter.js';

// Great Book lazy-loading contract must stay intact.
assert.equal(typeof adapter.requestContentPreparation, 'function', 'lazy TTS preparation API must remain available');
const mainAdapterSource = fs.readFileSync(new URL('../app/longform-tts-adapter.js', import.meta.url), 'utf8');
assert.ok(mainAdapterSource.includes('prepareSection:prepareForPlayback'), 'long-form TTS must still prepare lazy content before playback');
assert.ok(mainAdapterSource.includes("pageHighlighter.highlight(target,event.absoluteWord,config.excludeSelector||'',event.followReading)"), 'long-form TTS must pass follow state into page highlighting after lazy preparation');

const greatBookReaderSource = fs.readFileSync(new URL('../app/great-book-reader.js', import.meta.url), 'utf8');
assert.ok(greatBookReaderSource.includes("addEventListener('potato:tts-prepare'"), 'Great Book must keep the lazy TTS preparation hook');
assert.ok(greatBookReaderSource.includes('detail.waitUntil(loadAllSlots())'), 'whole-book TTS must still await every lazy chapter');

// Follow-reading contract must coexist with the lazy-loading flow.
assert.equal(typeof drawer.centerDomRange, 'function', 'drawer must expose page-centering for follow-reading');
let scrolled=null;
const win={innerHeight:800,scrollY:200,scrollTo:args=>{scrolled=args},matchMedia:()=>({matches:false})};
const doc={documentElement:{clientHeight:800}};
const range={getBoundingClientRect:()=>({top:700,height:20})};
assert.equal(drawer.centerDomRange(win,doc,range),true);
assert.deepEqual(scrolled,{top:510,behavior:'smooth'});

const drawerSource = fs.readFileSync(new URL('../app/tts-drawer.js', import.meta.url), 'utf8');
assert.ok(drawerSource.includes("const follow=button('Follow reading','🎯')"), 'shared TTS drawer must contain the bullseye follow toggle');
assert.ok(drawerSource.includes('let followReading=saved.followReading===true'), 'follow-reading choice must persist');
assert.ok(drawerSource.includes('options.onEvent?.({...event,sectionId,followReading})'), 'speech events must carry follow state to page adapters');
assert.ok(drawerSource.includes("status.textContent=!speechOk?'speech unavailable':preparing?'loading text…'"), 'follow integration must preserve the lazy-loading status state');
assert.ok(drawerSource.includes('const prepareSection=typeof options.prepareSection'), 'follow integration must preserve async preparation before speech starts');
assert.ok(drawerSource.includes('await prepareSection(sectionId)'), 'speech must still await lazy content before starting');

const bibleSource = fs.readFileSync(new URL('../app/bible-tts-adapter.js', import.meta.url), 'utf8');
assert.ok(bibleSource.includes('event.followReading'), 'Bible TTS should honor the same follow toggle');

const cssSource = fs.readFileSync(new URL('../app/tts-drawer.css', import.meta.url), 'utf8');
assert.ok(cssSource.includes('.ptts-button[aria-pressed="true"]'), 'active bullseye state needs visible styling');

console.log('tts follow + lazy integration contract: ok');
