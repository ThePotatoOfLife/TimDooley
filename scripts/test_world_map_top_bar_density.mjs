import assert from 'node:assert/strict';
import fs from 'node:fs';

const bar = fs.readFileSync(new URL('../world-map/3d-world-bar.js', import.meta.url), 'utf8');
const html = fs.readFileSync(new URL('../world-map/index.html', import.meta.url), 'utf8');
const audit = fs.readFileSync(new URL('../docs/WORLD-MAP-TOP-BAR-AUDIT.md', import.meta.url), 'utf8');

// Purpose-first top level: internal registry families and project axes live inside Countries.
for (const marker of [
  "details.id = 'atlasCountriesMenu'",
  "details.id = 'atlasNowMenu'",
  "adoptLegacyMenu('traceMenu','Connections')",
  "adoptLegacyMenu('timeMenu','History'",
  "adoptLegacyMenu('viewMenu','Map')",
  "Project lenses",
  "Compare countries",
  "Details panel",
  "Reset map",
]) {
  assert.ok(bar.includes(marker), `purpose-first World Bar missing: ${marker}`);
}

for (const retired of [
  "className='atlas-axis-cluster'",
  "const FAMILIES = [['groups','Groups']",
  "geographyMenu()",
]) {
  assert.ok(!bar.includes(retired), `first-screen internal taxonomy returned: ${retired}`);
}

assert.ok(bar.includes("const COUNTRY_FAMILIES = [['groups','Groups & alliances'],['religion','Religion'],['stats','Numbers']]"), 'Countries must own ordinary registry families');
assert.ok(bar.includes('function installAnalyzeRelations('), 'Connections must own relation-context controls');
assert.ok(bar.includes('function syncAnalyzeRelations('), 'Connections relation state must stay synchronized');
assert.ok(bar.includes("id = 'atlasAnalyzeRelations'") || bar.includes("id='atlasAnalyzeRelations'"), 'Connections relation block needs a stable identity');
assert.ok(bar.includes("project.below.us-cases") && bar.includes("Below · U.S. cases"), 'deep project context must remain reachable without becoming a top-level control');

const compactHtml = html.replace(/\s+/g, '');
for (const token of [
  '.top{display:flex;gap:5px',
  'min-height:46px',
  '.topinput{width:170px',
]) {
  assert.ok(compactHtml.includes(token), `first-paint header lost compact marker: ${token}`);
}

for (const label of ['Search','Countries','Now','Connections','History','Map','Home']) {
  assert.ok(audit.includes(`| ${label} |`), `interface contract must justify ${label}`);
}
assert.ok(audit.includes('Features may be numerous; top-level intentions may not.'));
assert.ok(audit.includes('Project lenses are secondary.'));
assert.ok(audit.includes('Workspace tools are secondary.'));
assert.ok(audit.includes('spatial doorway into the world knowledge system'));

console.log('WORLD MAP PURPOSE-FIRST TOP BAR REGRESSION PASSED');
