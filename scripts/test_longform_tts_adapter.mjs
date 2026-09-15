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

const story = fs.readFileSync(new URL('../tim-dooley/story/index.html', import.meta.url),'utf8');
for (const marker of [
  'id="story-tts"',
  'href="../../app/tts-drawer.css"',
  'src="../../app/tts-reader.js"',
  'src="../../app/tts-drawer.js"',
  'src="../../app/longform-tts-adapter.js"',
  'PotatoLongformTTS.mount',
  "itemSelector:'.story-entry'"
]) assert.ok(story.includes(marker),`story TTS integration missing ${marker}`);

const readerPos=story.indexOf('src="../../app/tts-reader.js"');
const drawerPos=story.indexOf('src="../../app/tts-drawer.js"');
const adapterPos=story.indexOf('src="../../app/longform-tts-adapter.js"');
assert.ok(readerPos < drawerPos && drawerPos < adapterPos,'TTS dependencies must load engine -> drawer -> longform adapter');

console.log('longform tts adapter contract: ok');
