import assert from 'node:assert/strict';
import fs from 'node:fs';

const evidenceUrl = new URL('../world-map/3d-evidence.js', import.meta.url);
const source = fs.readFileSync(evidenceUrl, 'utf8');

function extractFunction(name) {
  const marker = `function ${name}(`;
  const start = source.indexOf(marker);
  assert.ok(start >= 0, `missing ${name} in world-map/3d-evidence.js`);
  const bodyStart = source.indexOf('{', start);
  assert.ok(bodyStart >= 0, `missing body for ${name}`);
  let depth = 0;
  let quote = null;
  let escaped = false;
  for (let i = bodyStart; i < source.length; i += 1) {
    const char = source[i];
    if (quote) {
      if (escaped) { escaped = false; continue; }
      if (char === '\\') { escaped = true; continue; }
      if (char === quote) quote = null;
      continue;
    }
    if (char === '"' || char === "'" || char === '`') { quote = char; continue; }
    if (char === '{') depth += 1;
    if (char === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`unterminated ${name}`);
}

const card = { hidden:false };
const box = { hidden:true };
const elements = new Map([['atlasCountryCard', card]]);
const document = { getElementById(id) { return elements.get(id) || null; } };
let rendered = 0;
const window = { __potatoAtlasCountryCard:{ render() { rendered += 1; } } };

const suspendCountryCard = new Function(
  'document', 'box',
  `"use strict"; let countryCardWasVisible = false; ${extractFunction('suspendCountryCard')}; return {run:suspendCountryCard, wasVisible:()=>countryCardWasVisible};`,
)(document, box);

const suspended = suspendCountryCard.run();
assert.equal(suspended, true, 'opening Eye should record a visible country card');
assert.equal(card.hidden, true, 'opening Eye must hide the overlapping country card');
assert.equal(suspendCountryCard.wasVisible(), true);

// A country-card rerender while Eye is open must be suppressed without changing
// the original restoration intent.
box.hidden = false;
card.hidden = false;
suspendCountryCard.run();
assert.equal(card.hidden, true, 'Eye must retain exclusive ownership of the top-left overlay corner');
assert.equal(suspendCountryCard.wasVisible(), true, 'rerender suppression must not rewrite restore intent');

// Test the restore helper independently with the remembered state injected.
const restoreFactory = new Function(
  'document', 'window',
  `"use strict"; let countryCardWasVisible = true; ${extractFunction('restoreCountryCard')}; return {run:restoreCountryCard, wasVisible:()=>countryCardWasVisible};`,
);
const restore = restoreFactory(document, window);
const restored = restore.run();
assert.equal(restored, true, 'closing Eye should restore a card that was visible before Eye opened');
assert.equal(rendered, 1, 'restoration should rerender current card data instead of revealing stale HTML');
assert.equal(restore.wasVisible(), false, 'restore ownership flag must reset after close');

// If no card was visible before Eye opened, closing Eye must not invent one.
const noRestoreFactory = new Function(
  'document', 'window',
  `"use strict"; let countryCardWasVisible = false; ${extractFunction('restoreCountryCard')}; return {run:restoreCountryCard};`,
);
const noRestore = noRestoreFactory(document, window);
assert.equal(noRestore.run(), false);
assert.equal(rendered, 1, 'closing Eye must not create a country card that was previously hidden');

console.log('WORLD MAP OVERLAY OVERLAP REGRESSION PASSED');
