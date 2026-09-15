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
assert.deepEqual(drawer.renderFocusedText('alpha beta gamma', {start:6,end:10}), {before:'alpha ',active:'beta',after:' gamma'});

const source = fs.readFileSync(new URL('../app/tts-drawer.js', import.meta.url),'utf8');
assert.ok(source.includes('function playSection(id)'), 'drawer must expose explicit section playback');
assert.ok(source.includes('playSection,'), 'drawer public API must return playSection');
assert.ok(source.includes("'🔊 Listen'"), 'collapsed shared player should use the Listen label');
assert.ok(source.includes('function mountSelectionAction(options={})'), 'drawer must expose shared read-selection UI');
assert.ok(source.includes("className='ptts-selection-listen'"), 'selection UI must use the shared selection class');
assert.ok(source.includes("drawer.playSection?.('selection')"), 'selection action must only start explicit selection playback');
assert.ok(source.includes('options.onEvent?.({...event,sectionId})'), 'drawer must forward speech events with active section context');
assert.ok(source.includes('function buildNormalizedTextMap(container,excludeSelector='), 'drawer must map normalized speech text back to DOM text nodes');
assert.ok(source.includes('function createPageHighlighter(options={})'), 'drawer must expose a non-mutating page highlighter');
assert.ok(source.includes("highlights.set(name,new HighlightCtor(domRange))"), 'page highlighting must use the browser Highlight API instead of rewriting article markup');
assert.ok(source.includes("highlights?.delete?.(name)"), 'page highlighter must safely clear its named highlight');

console.log('tts drawer contract: ok');
