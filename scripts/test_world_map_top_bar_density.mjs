import assert from 'node:assert/strict';
import fs from 'node:fs';

const bar = fs.readFileSync(new URL('../world-map/3d-world-bar.js', import.meta.url), 'utf8');
const html = fs.readFileSync(new URL('../world-map/index.html', import.meta.url), 'utf8');
const audit = fs.readFileSync(new URL('../docs/WORLD-MAP-TOP-BAR-AUDIT.md', import.meta.url), 'utf8');

assert.ok(
  bar.includes("const FAMILIES = [['groups','Groups'],['religion','Religion'],['stats','Stats']]"),
  'top-level registry families should not include a standalone Relations menu',
);
assert.ok(!bar.includes("['relations','Relations']"), 'Relations must stay consolidated under Analyze');
assert.ok(bar.includes('function installAnalyzeRelations('), 'Analyze must own relation-context controls');
assert.ok(bar.includes('function syncAnalyzeRelations('), 'Analyze relation state must stay synchronized');
assert.ok(bar.includes("id = 'atlasAnalyzeRelations'") || bar.includes("id='atlasAnalyzeRelations'"), 'Analyze relation block needs a stable identity');
assert.ok(bar.includes("className='atlas-axis-cluster'"), 'N/W/E/S must render as one grouped control');
assert.ok(bar.includes("aria-label','Project axis lenses'"), 'axis cluster must expose a full accessible group label');
assert.ok(bar.includes("width:26px;min-width:26px"), 'axis buttons must retain compact width');
assert.ok(bar.includes('atlas-compact-icon'), 'projection/reset controls must share icon-width treatment');
assert.ok(bar.includes('#atlasWorldResult{width:82px;flex:0 0 82px'), 'result feedback must reserve a compact fixed width');
assert.ok(bar.includes("min-height:28px;padding:4px 7px"), 'ordinary registry controls should retain compact dimensions');

const compactHtml = html.replace(/\s+/g, '');
for (const token of [
  '.top{display:flex;gap:5px',
  'min-height:46px',
  '.topinput{width:170px',
  '.quick-actions{display:flex;gap:4px',
]) {
  assert.ok(compactHtml.includes(token), `first-paint header lost compact marker: ${token}`);
}

for (const label of ['Search','Compare','Inspect','N/W/E/S','Groups','Religion','Stats','Geography','Analyze','Time','View','Projection','Reset','Home']) {
  assert.ok(audit.includes(`| ${label} |`), `top-bar audit must justify ${label}`);
}
assert.ok(audit.includes('new persistent controls must satisfy one of three tests') || audit.includes('New persistent controls must satisfy one of three tests'));
assert.ok(audit.includes('Relations') && audit.includes('merged into **Analyze**'));

console.log('WORLD MAP TOP BAR DENSITY REGRESSION PASSED');
