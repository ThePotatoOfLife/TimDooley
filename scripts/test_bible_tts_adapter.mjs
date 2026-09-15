import assert from 'node:assert/strict';
import fs from 'node:fs';
import adapter from '../app/bible-tts-adapter.js';

const payload = adapter.buildBiblePayload({
  id:'rel-7',
  title:'Seed / Return',
  project:'Project anchor. Project quote.',
  scripture:'John 12 text.',
  why:'The grain pattern connects the two.',
  mismatch:'Where it breaks: roles differ.',
  selection:'grain pattern'
});

assert.equal(payload.id,'rel-7');
assert.deepEqual(payload.sections.map(x=>x.id),['both','project','scripture','why','selection']);
assert.match(payload.sections[0].text,/Project anchor/);
assert.match(payload.sections[0].text,/John 12 text./);
assert.match(payload.sections[0].text,/roles differ/);
assert.equal(payload.sections[1].text,'Project anchor. Project quote.');
assert.equal(payload.sections[2].text,'John 12 text.');
assert.match(payload.sections[3].text,/grain pattern/);
assert.match(payload.sections[3].text,/roles differ/);
assert.equal(payload.sections[4].text,'grain pattern');

const bible = fs.readFileSync(new URL('../traditions/bible/index.html', import.meta.url),'utf8');
for (const marker of [
  'id="bible-tts-drawer"',
  'href="../../app/tts-drawer.css"',
  'src="../../app/tts-reader.js"',
  'src="../../app/tts-drawer.js"',
  'src="../../app/bible-tts-adapter.js"'
]) assert.ok(bible.includes(marker),`Bible TTS integration missing ${marker}`);

const mountPos = bible.indexOf('id="bible-tts-drawer"');
const navPos = bible.indexOf('class="comparison-nav"');
assert.ok(mountPos >= 0 && navPos >= 0 && mountPos < navPos,'Bible TTS mount must appear immediately before comparison navigation');

const readerPos=bible.indexOf('src="../../app/tts-reader.js"');
const drawerPos=bible.indexOf('src="../../app/tts-drawer.js"');
const adapterPos=bible.indexOf('src="../../app/bible-tts-adapter.js"');
assert.ok(readerPos < drawerPos && drawerPos < adapterPos,'Bible TTS dependencies must load engine -> drawer -> adapter');

const adapterSource=fs.readFileSync(new URL('../app/bible-tts-adapter.js', import.meta.url),'utf8');
assert.ok(adapterSource.includes('function ensureRelationListen()'),'Bible adapter must expose a contextual Listen affordance');
assert.ok(adapterSource.includes("className='ptts-inline-listen'"),'Bible comparison must use the shared inline Listen style');
assert.ok(adapterSource.includes("drawer?.playSection?.('both')"),'Bible Listen action must start the whole active comparison');
assert.ok(adapterSource.includes("host.dataset.ttsPrimary=''"),'Bible page-level reader must mark itself as the primary TTS host');
assert.ok(adapterSource.includes('selectionInsideActive'),'Bible adapter must constrain selection reading to the active relation');
assert.ok(adapterSource.includes('mountSelectionAction'),'Bible comparator must use the shared read-selection action');

console.log('bible tts adapter contract: ok');
