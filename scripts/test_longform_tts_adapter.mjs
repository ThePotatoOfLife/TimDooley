import assert from 'node:assert/strict';
import fs from 'node:fs';
import adapter from '../app/longform-tts-adapter.js';

const payload = adapter.buildLongformPayload({
  id:'tim-story',
  label:'Tim Dooley — The Story',
  whole:'1987. Born in Denmark. 2011. Tree ordeal. 2020. GTA roleplay.',
  current:'2020. GTA roleplay.',
  selection:'Tree ordeal.'
});
assert.equal(payload.id,'tim-story');
assert.deepEqual(payload.sections.map(x=>x.id),['all','current','selection']);
assert.equal(payload.sections[0].label,'Whole story');
assert.equal(payload.sections[0].text,'1987. Born in Denmark. 2011. Tree ordeal. 2020. GTA roleplay.');
assert.equal(payload.sections[1].text,'2020. GTA roleplay.');
assert.equal(payload.sections[2].text,'Tree ordeal.');

const sparse = adapter.buildLongformPayload({id:'x',label:'X',whole:'  hello   world  ',current:'',selection:''});
assert.deepEqual(sparse.sections.map(x=>x.id),['all']);
assert.equal(sparse.sections[0].text,'hello world');
assert.equal(adapter.cleanText('  Alpha\n\n Beta \t Gamma  '),'Alpha Beta Gamma');
assert.equal(typeof adapter.mount,'function');
assert.equal(typeof adapter.configFromElement,'function');
assert.equal(typeof adapter.autoMount,'function');

const fakeHost={dataset:{ttsRoot:'.journey',ttsId:'philosophy-journey',ttsLabel:'Potatoism Philosophy',ttsAllLabel:'Whole journey',ttsCurrentLabel:'Current movement',ttsSelectionLabel:'Selection',ttsItem:'.movement'}};
const fakeRoot={id:'journey'};
const fakeDoc={title:'Philosophy',querySelector(selector){return selector==='.journey'?fakeRoot:null;}};
const declarative=adapter.configFromElement(fakeHost,fakeDoc);
assert.equal(declarative.mount,fakeHost);
assert.equal(declarative.root,fakeRoot);
assert.equal(declarative.id,'philosophy-journey');
assert.equal(declarative.allLabel,'Whole journey');
assert.equal(declarative.currentLabel,'Current movement');
assert.equal(declarative.itemSelector,'.movement');

const removalState={removed:false};
const fakeReadable={cloneNode(){return {querySelectorAll(selector){assert.ok(selector.includes('.chrome'));assert.ok(selector.includes('.ptts-inline-listen'));assert.ok(selector.includes('.ptts-drawer'));return [{remove(){removalState.removed=true;}}]},get textContent(){return removalState.removed?'Keep this':'Keep this Skip this';}}}};
assert.equal(adapter.readableText(fakeReadable,'.chrome'),'Keep this');
const excludeHost={dataset:{ttsRoot:'#main',ttsExclude:'.nav,.footer'}};
const mainRoot={id:'main'};
const excludeDoc={querySelector(selector){return selector==='#main'?mainRoot:null;}};
assert.equal(adapter.configFromElement(excludeHost,excludeDoc).excludeSelector,'.nav,.footer');

const adapterSource=fs.readFileSync(new URL('../app/longform-tts-adapter.js', import.meta.url),'utf8');
assert.ok(adapterSource.includes('target:host'), 'longform adapter must use drawer target API');
assert.ok(adapterSource.includes('getPayload:source'), 'longform adapter must use drawer getPayload API');
assert.ok(adapterSource.includes('drawer?.setPayload?.(source())'), 'longform adapter must refresh with setPayload');
assert.ok(!adapterSource.includes('updatePayload('), 'obsolete updatePayload API must not return');
assert.ok(adapterSource.includes("className='ptts-inline-listen'"), 'readable items need explicit Listen buttons');
assert.ok(adapterSource.includes("drawer.playSection?.('current')"), 'inline Listen must start only the current readable item');
assert.ok(adapterSource.includes("ttsListenReady==='true'"), 'inline Listen injection must be idempotent');
assert.ok(adapterSource.includes("'.ptts-inline-listen'"), 'injected Listen controls must be excluded from spoken text');
assert.ok(adapterSource.includes("host.dataset.ttsPrimary=''"), 'page-level reader host should mark itself as primary automatically');
assert.ok(adapterSource.includes('mountSelectionAction'), 'longform pages must mount the shared read-selection action');
assert.ok(adapterSource.includes("classList.add('ptts-reading-active')"), 'current spoken item must gain an active-reading state');
assert.ok(adapterSource.includes("classList.remove('ptts-reading-active')"), 'active-reading state must be cleared when speech ends or context changes');
assert.ok(adapterSource.includes('onEvent:event=>'), 'longform adapter must consume drawer speech events');

function assertLongformPage(source,{name,host,css,reader,drawer,adapter:adapterSrc,root,item,allLabel,currentLabel,exclude}){
  for (const marker of [host,css,reader,drawer,adapterSrc,'data-tts-longform',root,item,allLabel,currentLabel,exclude].filter(Boolean)) {
    assert.ok(source.includes(marker),`${name} TTS integration missing ${marker}`);
  }
  assert.ok(!source.includes('PotatoLongformTTS.mount({'),`${name} should use declarative auto-mounting instead of page-specific TTS JavaScript`);
  const readerPos=source.indexOf(reader);
  const drawerPos=source.indexOf(drawer);
  const adapterPos=source.indexOf(adapterSrc);
  assert.ok(readerPos < drawerPos && drawerPos < adapterPos,`${name} TTS dependencies must load engine -> drawer -> longform adapter`);
}

const story = fs.readFileSync(new URL('../tim-dooley/story/index.html', import.meta.url),'utf8');
assertLongformPage(story,{name:'story',host:'id="story-tts"',css:'href="../../app/tts-drawer.css"',reader:'src="../../app/tts-reader.js"',drawer:'src="../../app/tts-drawer.js"',adapter:'src="../../app/longform-tts-adapter.js"',root:'data-tts-root="#story-stream"',item:'data-tts-item=".story-entry"',allLabel:'data-tts-all-label="Whole story"',currentLabel:'data-tts-current-label="Current entry"'});
assert.ok(story.includes('Hear the full story'), 'Story must preserve its content expander');
assert.ok(!story.includes('data-tts-item=".full-story"'), 'Hear the full story must not become a TTS trigger');
assert.ok(!story.includes('data-tts-item="summary"'), 'Story disclosure summaries must remain silent');

const philosophy = fs.readFileSync(new URL('../philosophy/index.html', import.meta.url),'utf8');
assertLongformPage(philosophy,{name:'philosophy',host:'id="philosophy-tts"',css:'href="../app/tts-drawer.css"',reader:'src="../app/tts-reader.js"',drawer:'src="../app/tts-drawer.js"',adapter:'src="../app/longform-tts-adapter.js"',root:'data-tts-root=".journey"',item:'data-tts-item=".movement"',allLabel:'data-tts-all-label="Whole journey"',currentLabel:'data-tts-current-label="Current movement"'});

const religion = fs.readFileSync(new URL('../religion/index.html', import.meta.url),'utf8');
assertLongformPage(religion,{name:'religion',host:'id="religion-tts"',css:'href="../app/tts-drawer.css"',reader:'src="../app/tts-reader.js"',drawer:'src="../app/tts-drawer.js"',adapter:'src="../app/longform-tts-adapter.js"',root:'data-tts-root=".religion-page"',item:'data-tts-item=".theology-core,.question-stub"',allLabel:'data-tts-all-label="Whole page"',currentLabel:'data-tts-current-label="Current section"',exclude:'data-tts-exclude="#religion-tts,.page-nav,.bible-lab-cta,.minor,.footer"'});

const tim = fs.readFileSync(new URL('../tim-dooley/index.html', import.meta.url),'utf8');
assertLongformPage(tim,{name:'tim overview',host:'id="tim-tts"',css:'href="../app/tts-drawer.css"',reader:'src="../app/tts-reader.js"',drawer:'src="../app/tts-drawer.js"',adapter:'src="../app/longform-tts-adapter.js"',root:'data-tts-root=".tim-page"',item:'data-tts-item=".reading-frame,.question-stub,.work-row,.sequence>div"',allLabel:'data-tts-all-label="Whole overview"',currentLabel:'data-tts-current-label="Current section"',exclude:'data-tts-exclude="#tim-tts,.page-nav,.primary,.deep"'});

console.log('longform tts adapter contract: ok');
