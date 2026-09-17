import assert from 'node:assert/strict';
import fs from 'node:fs';
import drawer from '../app/tts-drawer.js';

const { normalizePayload, resolveSection, buildReadingText, centerDomRange } = drawer;

const payload = normalizePayload({
  id: 'rel-1',
  label: 'Relation One',
  sections: [
    { id: 'both', label: 'Both', text: 'Project text. Scripture text.' },
    { id: 'project', label: 'Project', text: 'Project text.' },
    { id: 'scripture', label: 'Scripture', text: 'Scripture text.' },
    { id: 'why', label: 'Why', text: 'Why they connect.' },
  ],
});

assert.equal(payload.id, 'rel-1');
assert.equal(payload.sections.length, 4);
assert.equal(resolveSection(payload, 'project').text, 'Project text.');
assert.equal(resolveSection(payload, 'missing').id, 'both');
assert.equal(buildReadingText(payload, 'scripture'), 'Scripture text.');

const sparse = normalizePayload({ id: 'x', sections: [{ id: 'project', label: 'Project', text: '  hello   world  ' }] });
assert.equal(sparse.sections[0].text, 'hello world');
assert.equal(buildReadingText(sparse, 'project'), 'hello world');
assert.equal(typeof drawer.mount, 'function');
assert.equal(typeof drawer.renderFocusedText, 'function');
assert.equal(typeof drawer.mountSelectionAction, 'function');
assert.equal(typeof drawer.createPageHighlighter, 'function');
assert.equal(typeof centerDomRange, 'function');
assert.deepEqual(drawer.renderFocusedText('alpha beta gamma', {start:6,end:10}), {before:'alpha ',active:'beta',after:' gamma'});

const scrolls=[];
const fakeWin={innerHeight:800,scrollY:300,scrollTo:opts=>scrolls.push(opts),matchMedia:()=>({matches:false})};
const fakeDoc={documentElement:{clientHeight:800}};
assert.equal(centerDomRange(fakeWin,fakeDoc,{getBoundingClientRect:()=>({top:700,height:20})}),true);
assert.deepEqual(scrolls[0],{top:610,behavior:'smooth'});

const source = fs.readFileSync(new URL('../app/tts-drawer.js', import.meta.url),'utf8');
assert.ok(source.includes('function playSection(id)'), 'drawer must expose explicit section playback');
assert.ok(source.includes('playSection,'), 'drawer public API must return playSection');
assert.ok(source.includes("'🔊 Listen'"), 'collapsed shared player should use the Listen label');
assert.ok(source.includes("button('Follow reading','🎯')"), 'shared player must expose the bullseye follow-reading toggle');
assert.ok(source.includes("writeSettings({followReading})"), 'follow-reading preference must persist in shared TTS settings');
assert.ok(source.includes("block:followReading?'center':'nearest'"), 'expanded reader should center the active word only while follow-reading is enabled');
assert.ok(source.includes("persistedFollow()"), 'page highlighter must read the persisted follow-reading preference');
assert.ok(source.includes('function mountSelectionAction(options={})'), 'drawer must expose shared read-selection UI');
assert.ok(source.includes("className='ptts-selection-listen'"), 'selection UI must use the shared selection class');
assert.ok(source.includes("drawer.playSection?.('selection')"), 'selection action must only start explicit selection playback');
assert.ok(source.includes('options.onEvent?.({...event,sectionId,followReading})'), 'drawer must forward speech events with active section and follow context');
assert.ok(source.includes('function buildNormalizedTextMap(container,excludeSelector='), 'drawer must map normalized speech text back to DOM text nodes');
assert.ok(source.includes('function createPageHighlighter(options={})'), 'drawer must expose a non-mutating page highlighter');
assert.ok(source.includes("highlights.set(name,new HighlightCtor(domRange))"), 'page highlighting must use the browser Highlight API instead of rewriting article markup');
assert.ok(source.includes("highlights?.delete?.(name)"), 'page highlighter must safely clear its named highlight');
assert.ok(source.includes('prepareSection=typeof options.prepareSection'), 'drawer must preserve async content preparation for lazy-loaded longform reading');
assert.ok(source.includes('await prepareSection(sectionId,{signal:'), 'drawer must await cancellable content preparation before speech');
assert.ok(source.includes('preparationController?.abort?.()'), 'drawer stop/collapse must abort pending preparation');

const css = fs.readFileSync(new URL('../app/tts-drawer.css', import.meta.url),'utf8');
assert.match(css,/\.ptts-button\[aria-pressed="true"\]/,'active follow-reading toggle needs a visible pressed state');
assert.match(css,/\.ptts-select\s+option\s*\{[^}]*background\s*:\s*#(?:111|121|141|1[0-9a-f]{5}|[0-9a-f]{6})/i,'TTS native dropdown options need an explicit dark background');
assert.match(css,/\.ptts-select\s+option\s*\{[^}]*color\s*:\s*#(?:e|f)[0-9a-f]{5}/i,'TTS native dropdown options need an explicit readable foreground');
assert.ok(css.includes('@media(prefers-color-scheme:light)'), 'TTS controls must support light color scheme');
assert.match(css,/@media\(prefers-color-scheme:light\)[\s\S]*\.ptts-select\s+option\s*\{[^}]*background\s*:\s*#(?:f[0-9a-f]{5}|fff(?:fff)?)/i,'Light-mode dropdown options need an explicit light background');
assert.match(css,/@media\(prefers-color-scheme:light\)[\s\S]*\.ptts-select\s+option\s*\{[^}]*color\s*:\s*#(?:1|2|3)[0-9a-f]{5}/i,'Light-mode dropdown options need an explicit dark foreground');

console.log('tts drawer contract: ok');
