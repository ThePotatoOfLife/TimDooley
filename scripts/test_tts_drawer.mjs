import assert from 'node:assert/strict';
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
assert.deepEqual(drawer.renderFocusedText('alpha beta gamma', {start:6,end:10}), {before:'alpha ',active:'beta',after:' gamma'});

console.log('tts drawer contract: ok');
