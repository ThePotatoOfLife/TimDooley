import assert from 'node:assert/strict';
import adapter from '../app/bible-tts-adapter.js';

const payload = adapter.buildBiblePayload({
  id:'rel-7',
  title:'Seed / Return',
  project:'Project anchor. Project quote.',
  scripture:'John 12 text.',
  why:'The grain pattern connects the two.',
  mismatch:'Where it breaks: roles differ.'
});

assert.equal(payload.id,'rel-7');
assert.deepEqual(payload.sections.map(x=>x.id),['both','project','scripture','why']);
assert.match(payload.sections[0].text,/Project anchor/);
assert.match(payload.sections[0].text,/John 12 text/);
assert.match(payload.sections[0].text,/roles differ/);
assert.equal(payload.sections[1].text,'Project anchor. Project quote.');
assert.equal(payload.sections[2].text,'John 12 text.');
assert.match(payload.sections[3].text,/grain pattern/);
assert.match(payload.sections[3].text,/roles differ/);

console.log('bible tts adapter contract: ok');
