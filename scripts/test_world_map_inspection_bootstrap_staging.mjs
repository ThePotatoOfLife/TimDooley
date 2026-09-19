import assert from 'node:assert/strict';
import fs from 'node:fs';

const bootstrap = fs.readFileSync(new URL('../world-map/3d-bootstrap.js', import.meta.url), 'utf8');

for (const marker of [
  'async function loadInspectionBasics()',
  'async function loadInspectionContext()',
  'async function loadInspectionDeep()',
  "loadAfterPaint('Demography', './3d-demography.js')",
  "loadAfterPaint('Country Pulse', './3d-country-pulse.js')",
  "loadAfterPaint('Evidence', './3d-evidence.js')",
  "loadSpecialist('System Intelligence', './3d-gateways.js')",
  "loadSpecialist('Functional Chains', './3d-chain-explorer.js')",
  "loadSpecialist('Infrastructure Context', './3d-infrastructure.js')",
  "loadSpecialist('Impact Trace', './3d-impact-trace.js')",
  "await loadSpecialist('Impact Actions', './3d-impact-actions.js')",
  'await loadInspectionBasics();',
  'await loadInspectionContext();',
  'await nextIdle(1200);',
  'await loadInspectionDeep();',
]) assert.ok(bootstrap.includes(marker), `inspection bootstrap missing marker: ${marker}`);

const promoteStart = bootstrap.indexOf('const promoteInspection = async () =>');
const promoteEnd = bootstrap.indexOf('let inspectionPromoted = false;', promoteStart);
assert.ok(promoteStart >= 0 && promoteEnd > promoteStart, 'missing promoteInspection body');
const promote = bootstrap.slice(promoteStart, promoteEnd);
assert.ok(
  /await loadInspectionBasics\(\);[\s\S]*await nextPaint\(\);[\s\S]*await loadInspectionContext\(\);[\s\S]*await nextIdle\(1200\);[\s\S]*await loadInspectionDeep\(\);/.test(promote),
  'inspection promotion must yield a paint before context and idle time before deep specialists',
);

console.log('WORLD MAP INSPECTION BOOTSTRAP STAGING REGRESSION PASSED');
