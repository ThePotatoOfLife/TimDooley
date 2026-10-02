import assert from 'node:assert/strict';
import fs from 'node:fs';

const bar = fs.readFileSync(new URL('../world-map/3d-world-bar.js', import.meta.url), 'utf8');
const html = fs.readFileSync(new URL('../world-map/index.html', import.meta.url), 'utf8');
const audit = fs.readFileSync(new URL('../docs/WORLD-MAP-TOP-BAR-AUDIT.md', import.meta.url), 'utf8');

for (const marker of [
  "details.innerHTML = '<summary>Countries</summary>",
  "details.innerHTML = '<summary>Now</summary>",
  "adoptLegacyMenu('traceMenu','Connections')",
  "adoptLegacyMenu('timeMenu','History'",
  "adoptLegacyMenu('viewMenu','Map')",
]) assert.ok(bar.includes(marker), `purpose-first top bar missing ${marker}`);

for (const forbidden of [
  "const FAMILIES = [['groups','Groups']",
  "['relations','Relations']",
  "className='atlas-axis-cluster'",
  "<summary>Geography</summary>",
  "<summary>Analyze</summary>",
]) assert.ok(!bar.includes(forbidden), `retired first-level control returned: ${forbidden}`);

assert.ok(bar.includes('Project lenses'), 'N/W/E/S project lenses should remain available inside Countries');
assert.ok(bar.includes('Compare countries'), 'Compare should remain available inside Map');
assert.ok(bar.includes('Details panel'), 'Details should remain available inside Map');
assert.ok(bar.includes("reset.setAttribute('aria-label','Reset map layers and investigation state')"), 'Reset must retain accessible naming');
assert.ok(bar.includes('#atlasWorldResult{width:82px;flex:0 0 82px'), 'conditional result feedback should retain bounded width');

const compactHtml = html.replace(/\s+/g, '');
for (const token of [
  '.top{display:flex;gap:5px',
  'min-height:46px',
  '.topinput{width:170px',
]) assert.ok(compactHtml.includes(token), `first-paint header lost compact marker: ${token}`);

for (const label of ['Search','Countries','Now','Connections','History','Map','Home']) {
  assert.ok(audit.includes(`| ${label} |`), `interface contract must justify ${label}`);
}
assert.ok(audit.includes('Features may be numerous; top-level intentions may not.'), 'contract must protect progressive disclosure');
assert.ok(audit.includes('Runtime-weight rule'), 'interface contract must protect runtime weight as well as visual density');

console.log('WORLD MAP PURPOSE-FIRST TOP BAR REGRESSION PASSED');
