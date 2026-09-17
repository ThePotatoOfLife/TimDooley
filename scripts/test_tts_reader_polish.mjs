import assert from 'node:assert/strict';
import fs from 'node:fs';
import drawer from '../app/tts-drawer.js';

const loaderUrl = new URL('../app/great-book-loader.js', import.meta.url);
assert.ok(fs.existsSync(loaderUrl), 'Great Book needs a reusable/testable chapter loader');
const loaderModule = await import(loaderUrl);
const loaderApi = loaderModule.default || loaderModule;
assert.equal(typeof loaderApi.createChapterLoader, 'function', 'chapter loader factory must be exported');

const makeSlot = (id, path=id) => ({id,dataset:{loaded:'false',path},innerHTML:'placeholder'});

let retryAttempts = 0;
const retryLoader = loaderApi.createChapterLoader({
  fetchImpl: async () => {
    retryAttempts += 1;
    if(retryAttempts === 1) return {ok:false,status:503,text:async()=>''};
    return {ok:true,status:200,text:async()=>'<p>recovered</p>'};
  },
});
const retrySlot = makeSlot('retry','chapter-retry.html');
await assert.rejects(retryLoader.loadSlot(retrySlot), /503/);
assert.equal(retrySlot.dataset.loaded,'error');
await retryLoader.loadSlot(retrySlot);
assert.equal(retryAttempts,2,'failed chapter should issue a fresh request on retry');
assert.equal(retrySlot.dataset.loaded,'true');
assert.equal(retrySlot.innerHTML,'<p>recovered</p>');

let active = 0;
let maxActive = 0;
const boundedLoader = loaderApi.createChapterLoader({
  fetchImpl: async path => {
    active += 1;
    maxActive = Math.max(maxActive,active);
    await new Promise(resolve=>setTimeout(resolve,8));
    active -= 1;
    return {ok:true,status:200,text:async()=>`<p>${path}</p>`};
  },
});
const boundedSlots = Array.from({length:7},(_,i)=>makeSlot(`s${i}`,`chapter-${i}.html`));
const boundedResult = await boundedLoader.loadSlots(boundedSlots,{concurrency:2});
assert.equal(boundedResult.failed.length,0);
assert.equal(boundedResult.loaded.length,7);
assert.ok(maxActive<=2,`preload exceeded concurrency limit: ${maxActive}`);

let started = 0;
const abortLoader = loaderApi.createChapterLoader({
  fetchImpl: (path,{signal}={}) => new Promise((resolve,reject)=>{
    started += 1;
    const timer=setTimeout(()=>resolve({ok:true,status:200,text:async()=>`<p>${path}</p>`}),80);
    signal?.addEventListener?.('abort',()=>{
      clearTimeout(timer);
      const error=new Error('aborted');error.name='AbortError';reject(error);
    },{once:true});
  }),
});
const abortController = new AbortController();
const abortPromise = abortLoader.loadSlots(Array.from({length:6},(_,i)=>makeSlot(`a${i}`,`a-${i}.html`)),{concurrency:1,signal:abortController.signal});
setTimeout(()=>abortController.abort(),10);
await assert.rejects(abortPromise,error=>error?.name==='AbortError');
assert.ok(started<6,`abort should stop queueing new chapters, but started ${started}`);

const scrolls=[];
const fakeWin={innerHeight:800,scrollY:300,scrollTo:opts=>scrolls.push(opts),matchMedia:()=>({matches:false})};
const fakeDoc={documentElement:{clientHeight:800}};
assert.equal(drawer.centerDomRange(fakeWin,fakeDoc,{getBoundingClientRect:()=>({top:360,height:20})}),false,'word already in central comfort zone should not scroll');
assert.equal(scrolls.length,0);
assert.equal(drawer.centerDomRange(fakeWin,fakeDoc,{getBoundingClientRect:()=>({top:700,height:20})}),true,'word outside comfort zone should recenter');
assert.deepEqual(scrolls[0],{top:610,behavior:'smooth'});

const drawerSource=fs.readFileSync(new URL('../app/tts-drawer.js', import.meta.url),'utf8');
const longformSource=fs.readFileSync(new URL('../app/longform-tts-adapter.js', import.meta.url),'utf8');
const bibleSource=fs.readFileSync(new URL('../app/bible-tts-adapter.js', import.meta.url),'utf8');
const greatBookSource=fs.readFileSync(new URL('../app/great-book-reader.js', import.meta.url),'utf8');
const greatBookHtml=fs.readFileSync(new URL('../great-book/index.html', import.meta.url),'utf8');

assert.ok(drawerSource.includes('AbortController'),'drawer must own an AbortController for pending content preparation');
assert.ok(drawerSource.includes('prepareSection(sectionId,{signal:'),'drawer must pass cancellation into lazy preparation');
assert.ok(drawerSource.includes('readSettings().voice'),'voice refresh must use the latest persisted voice rather than the mount-time snapshot');
assert.ok(longformSource.includes('event.followReading'),'long-form highlighting must consume the live follow state from the speech event');
assert.ok(bibleSource.includes('event.followReading'),'Bible highlighting must consume the live follow state from the speech event');
assert.ok(longformSource.includes("addEventListener('potato:tts-current'"),'long-form reader must accept scroll-driven current-item updates');
assert.ok(greatBookSource.includes("new CustomEvent('potato:tts-current'"),'Great Book must publish the chapter that becomes active while scrolling');
assert.ok(greatBookSource.includes("result.id===activeCurrentId"),'a chapter that finishes lazy-loading while active must immediately become the current TTS chapter');
assert.ok(greatBookSource.includes('detail.signal'),'Great Book preload must honor TTS cancellation');
assert.ok(greatBookSource.includes('failed.length'),'Great Book must distinguish partial load failure from ready state');
assert.ok(greatBookHtml.includes('data-tts-exclude=".gb-placeholder,.gb-load-error"'),'placeholder/error prose must never become spoken book content');

console.log('tts reader polish interaction contract: ok');
