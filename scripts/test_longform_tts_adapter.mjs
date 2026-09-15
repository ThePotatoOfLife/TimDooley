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

function assertLongformPage(source,{name,host,css,reader,drawer,adapter:adapterSrc,mount,itemSelector,rootMarker}){
  for (const marker of [host,css,reader,drawer,adapterSrc,mount,itemSelector,rootMarker]) {
    assert.ok(source.includes(marker),`${name} TTS integration missing ${marker}`);
  }
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
  mount:'PotatoLongformTTS.mount',
  itemSelector:"itemSelector:'.story-entry'",
  rootMarker:"getElementById('story-stream')"
});

const philosophy = fs.readFileSync(new URL('../philosophy/index.html', import.meta.url),'utf8');
assertLongformPage(philosophy,{
  name:'philosophy',
  host:'id="philosophy-tts"',
  css:'href="../app/tts-drawer.css"',
  reader:'src="../app/tts-reader.js"',
  drawer:'src="../app/tts-drawer.js"',
  adapter:'src="../app/longform-tts-adapter.js"',
  mount:'PotatoLongformTTS.mount',
  itemSelector:"itemSelector:'.movement'",
  rootMarker:"querySelector('.journey')"
});
assert.ok(philosophy.includes("allLabel:'Whole journey'"),'philosophy must label whole-scope reading as Whole journey');
assert.ok(philosophy.includes("currentLabel:'Current movement'"),'philosophy must label focused scope as Current movement');

console.log('longform tts adapter contract: ok');