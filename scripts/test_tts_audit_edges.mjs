import assert from 'node:assert/strict';
import fs from 'node:fs';
import drawer from '../app/tts-drawer.js';
import longform from '../app/longform-tts-adapter.js';

// Passive viewport changes must not retarget the item while its "current" text
// is already being spoken. Otherwise the old speech offsets get applied to a
// different chapter/section.
assert.equal(typeof longform.createCurrentPlaybackGuard,'function','longform adapter needs a testable current-playback guard');
const applied=[];
const guard=longform.createCurrentPlaybackGuard(item=>applied.push(item));
const a={id:'a'},b={id:'b'},c={id:'c'};
assert.equal(guard.offer(a),true);
assert.deepEqual(applied,[a]);
guard.setActive(true);
assert.equal(guard.offer(b),false,'passive current changes must defer during current playback');
assert.equal(guard.offer(c),false,'latest passive current should replace older pending choice');
assert.deepEqual(applied,[a],'speaking target must remain stable');
guard.setActive(false);
assert.deepEqual(applied,[a,c],'latest deferred current should apply once playback releases the lock');

// If live page content changes while the engine is reading an older snapshot,
// word offsets are no longer trustworthy. The active playback must be stopped
// rather than allowing old speech boundaries to point at new text.
assert.equal(typeof drawer.playbackPayloadChanged,'function','drawer needs a testable payload-drift guard');
const before={id:'page',sections:[{id:'all',label:'All',text:'alpha beta'},{id:'current',label:'Current',text:'alpha'}]};
const same={id:'page',sections:[{id:'all',label:'All',text:'alpha beta'},{id:'current',label:'Current',text:'alpha'}]};
const changedCurrent={id:'page',sections:[{id:'all',label:'All',text:'alpha beta'},{id:'current',label:'Current',text:'gamma'}]};
const changedOther={id:'page',sections:[{id:'all',label:'All',text:'alpha beta changed'},{id:'current',label:'Current',text:'alpha'}]};
assert.equal(drawer.playbackPayloadChanged(before,same,'current'),false);
assert.equal(drawer.playbackPayloadChanged(before,changedCurrent,'current'),true,'active section text mutation must invalidate playback');
assert.equal(drawer.playbackPayloadChanged(before,changedOther,'current'),false,'unrelated section mutation should not interrupt current playback');
assert.equal(drawer.playbackPayloadChanged(before,{...same,id:'other'},'current'),true,'payload identity change must invalidate playback');

const drawerSource=fs.readFileSync(new URL('../app/tts-drawer.js',import.meta.url),'utf8');
const longformSource=fs.readFileSync(new URL('../app/longform-tts-adapter.js',import.meta.url),'utf8');
const bibleSource=fs.readFileSync(new URL('../app/bible-tts-adapter.js',import.meta.url),'utf8');

// Switching follow ON mid-playback must immediately hand the current spoken
// word to the page adapter; waiting for another speech boundary can leave the
// page visibly detached, especially while paused.
assert.ok(drawerSource.includes("type:'followchange'"),'bullseye toggle must emit a follow-change event');
assert.ok(drawerSource.includes('absoluteWord:currentWord'),'follow-change event must carry the current spoken word');
assert.ok(longformSource.includes("event.type==='followchange'"),'longform page must react immediately when follow is enabled');
assert.ok(bibleSource.includes("event.type==='followchange'"),'Bible page must react immediately when follow is enabled');

// Turning follow OFF must never schedule page movement. The shared page lock
// is intentionally instant, so there is no smooth animation left running.
assert.ok(drawerSource.includes("behavior:'auto'"),'page-highlight follow must use immediate positioning');
assert.ok(!drawerSource.includes("scrollIntoView?.({block:followReading"),'drawer copy must never compete with the real page highlight');

console.log('tts audit edge-case contract: ok');
