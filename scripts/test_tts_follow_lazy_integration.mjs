import assert from 'node:assert/strict';
import fs from 'node:fs';
import drawer from '../app/tts-drawer.js';
import adapter from '../app/longform-tts-adapter.js';

assert.equal(typeof adapter.requestContentPreparation, 'function', 'lazy TTS preparation API must remain available');
const longform = fs.readFileSync(new URL('../app/longform-tts-adapter.js', import.meta.url), 'utf8');
assert.ok(longform.includes('prepareSection:prepareForPlayback'), 'long-form TTS must prepare lazy content before playback');

const greatBook = fs.readFileSync(new URL('../app/great-book-reader.js', import.meta.url), 'utf8');
assert.ok(greatBook.includes("addEventListener('potato:tts-prepare'"), 'Great Book must keep the lazy TTS preparation hook');
assert.ok(greatBook.includes('detail.waitUntil(loadAllSlots({signal:detail.signal}))'), 'whole-book TTS must await cancellable lazy chapter preparation');

assert.equal(typeof drawer.centerDomRange, 'function', 'drawer must expose follow-reading centering');
let scrolled = null;
const win = {innerHeight:800,scrollY:200,scrollTo:args=>{scrolled=args},matchMedia:()=>({matches:false})};
const doc = {documentElement:{clientHeight:800}};
const range = {getBoundingClientRect:()=>({top:700,height:20})};
assert.equal(drawer.centerDomRange(win,doc,range), true);
assert.deepEqual(scrolled, {top:510,behavior:'smooth'});

const source = fs.readFileSync(new URL('../app/tts-drawer.js', import.meta.url), 'utf8');
assert.ok(source.includes("const follow=button('Follow reading','🎯')")||source.includes("follow=button('Follow reading','🎯')"), 'shared TTS drawer must contain the bullseye toggle');
assert.ok(source.includes('followReading=saved.followReading===true'), 'follow-reading choice must persist');
assert.ok(source.includes('writeSettings({followReading})'), 'follow-reading toggle must persist its setting');
assert.ok(source.includes("status.textContent=!speechOk?'speech unavailable':preparing?'loading text…'"), 'lazy preparation state must remain visible');
assert.ok(source.includes('prepareSection=typeof options.prepareSection'), 'drawer must retain async preparation support');
assert.ok(source.includes('await prepareSection(sectionId,{signal:'), 'speech must wait for cancellable lazy content preparation before starting');
assert.ok(source.includes("typeof follow==='boolean'?follow:persistedFollow()"), 'page highlighting must honor explicit live follow state with persisted fallback');
assert.ok(source.includes("block:followReading?'center':'nearest'"), 'expanded reader must center the active word only when follow is enabled');

const css = fs.readFileSync(new URL('../app/tts-drawer.css', import.meta.url), 'utf8');
assert.ok(css.includes('.ptts-button[aria-pressed="true"]'), 'active bullseye state needs visible styling');

console.log('tts follow + lazy integration contract: ok');
