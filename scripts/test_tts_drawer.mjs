import assert from 'node:assert/strict';
import fs from 'node:fs';
import drawer from '../app/tts-drawer.js';

const { normalizePayload, resolveSection, buildReadingText } = drawer;

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
assert.equal(typeof drawer.centerDomRange, 'function');
assert.deepEqual(drawer.renderFocusedText('alpha beta gamma', {start:6,end:10}), {before:'alpha ',active:'beta',after:' gamma'});

const source = fs.readFileSync(new URL('../app/tts-drawer.js', import.meta.url),'utf8');
assert.ok(source.includes('function playSection(id)'), 'drawer must expose explicit section playback');
assert.ok(source.includes('playSection,'), 'drawer public API must return playSection');
assert.ok(source.includes("'🔊 Listen'"), 'collapsed shared player should use the Listen label');
assert.ok(source.includes('function mountSelectionAction(options={})'), 'drawer must expose shared read-selection UI');
assert.ok(source.includes("className='ptts-selection-listen'"), 'selection UI must use the shared selection class');
assert.ok(source.includes("drawer.playSection?.('selection')"), 'selection action must only start explicit selection playback');
assert.ok(source.includes('options.onEvent?.({...event,sectionId,followReading})'), 'drawer must forward follow-reading state with speech events');
assert.ok(source.includes('function buildNormalizedTextMap(container,excludeSelector='), 'drawer must map normalized speech text back to DOM text nodes');
assert.ok(source.includes('function createPageHighlighter(options={})'), 'drawer must expose a non-mutating page highlighter');
assert.ok(source.includes("highlights.set(name,new HighlightCtor(domRange))"), 'page highlighting must use the browser Highlight API instead of rewriting article markup');
assert.ok(source.includes("highlights?.delete?.(name)"), 'page highlighter must safely clear its named highlight');
assert.ok(source.includes("const follow=button('Follow reading','🎯')"), 'reader rail must include a bullseye follow-reading control');
assert.ok(source.includes("follow.setAttribute('aria-pressed',String(followReading))"), 'follow-reading button must expose its toggle state accessibly');
assert.ok(source.includes('writeSettings({followReading})'), 'follow-reading preference must persist with shared TTS settings');
assert.ok(source.includes("mark?.scrollIntoView?.({block:followReading?'center':'nearest',inline:'nearest'})"), 'expanded reader should center its active word while follow mode is enabled');

const longform = fs.readFileSync(new URL('../app/longform-tts-adapter.js', import.meta.url),'utf8');
assert.ok(longform.includes("pageHighlighter.highlight(target,event.absoluteWord,config.excludeSelector||'',event.followReading)"), 'long-form TTS must pass follow state into page highlighting');
const bible = fs.readFileSync(new URL('../app/bible-tts-adapter.js', import.meta.url),'utf8');
assert.ok(bible.includes("pageHighlighter.highlight(pieces.project.node,event.absoluteWord,'',event.followReading)"), 'Bible TTS must pass follow state into page highlighting');

const css = fs.readFileSync(new URL('../app/tts-drawer.css', import.meta.url),'utf8');
assert.match(css,/\.ptts-select\s+option\s*\{[^}]*background\s*:\s*#(?:111|121|141|1[0-9a-f]{5}|[0-9a-f]{6})/i,'TTS native dropdown options need an explicit dark background');
assert.match(css,/\.ptts-select\s+option\s*\{[^}]*color\s*:\s*#(?:e|f)[0-9a-f]{5}/i,'TTS native dropdown options need an explicit readable foreground');
assert.ok(css.includes('.ptts-button[aria-pressed="true"]'), 'active follow-reading toggle needs a visible pressed state');
assert.ok(css.includes('@media(prefers-color-scheme:light)'), 'TTS controls must support light color scheme');
assert.match(css,/@media\(prefers-color-scheme:light\)[\s\S]*\.ptts-select\s+option\s*\{[^}]*background\s*:\s*#(?:f[0-9a-f]{5}|fff(?:fff)?)/i,'Light-mode dropdown options need an explicit light background');
assert.match(css,/@media\(prefers-color-scheme:light\)[\s\S]*\.ptts-select\s+option\s*\{[^}]*color\s*:\s*#(?:1|2|3)[0-9a-f]{5}/i,'Light-mode dropdown options need an explicit dark foreground');

console.log('tts drawer contract: ok');
