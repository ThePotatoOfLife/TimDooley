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

function assertLongformPage(source,{name,host,css,reader,drawer,adapter:adapterSrc,root,item,allLabel,currentLabel}){
  for (const marker of [host,css,reader,drawer,adapterSrc,'data-tts-longform',root,item,allLabel,currentLabel]) {
    assert.ok(source.includes(marker),`${name} TTS integration missing ${marker}`);
  }
  assert.ok(!source.includes('PotatoLongformTTS.mount({'),`${name} should use declarative auto-mounting instead of page-specific TTS JavaScript`);
  const readerPos=source.indexOf(reader);
  const drawerPos=source.indexOf(drawer);
  const adapterPos=source.indexOf(adapterSrc);
  assert.ok(readerPos < drawerPos && drawerPos < adapterPos,`${name} TTS dependencies must load engine -> drawer -> longform adapter`);
}

const story = fs.readFileSync(new URL('../tim-dooley/story/index.html', import.meta.url),'utf8');
assertLongformPage(story,{
  name:'story',
  host:'id="story-tts"',
  css:'href="../../app/tts-drawer.css"',
  reader:'src="../../app/tts-reader.js"',
  drawer:'src="../../app/tts-drawer.js"',
  adapter:'src="../../app/longform-tts-adapter.js"',
  root:'data-tts-root="#story-stream"',
  item:'data-tts-item=".story-entry"',
  allLabel:'data-tts-all-label="Whole story"',
  currentLabel:'data-tts-current-label="Current entry"'
});

const philosophy = fs.readFileSync(new URL('../philosophy/index.html', import.meta.url),'utf8');
assertLongformPage(philosophy,{
  name:'philosophy',
  host:'id="philosophy-tts"',
  css:'href="../app/tts-drawer.css"',
  reader:'src="../app/tts-reader.js"',
  drawer:'src="../app/tts-drawer.js"',
  adapter:'src="../app/longform-tts-adapter.js"',
  root:'data-tts-root=".journey"',
  item:'data-tts-item=".movement"',
  allLabel:'data-tts-all-label="Whole journey"',
  currentLabel:'data-tts-current-label="Current movement"'
});

console.log('longform tts adapter contract: ok');