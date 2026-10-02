import assert from 'node:assert/strict';
import fs from 'node:fs';

const bootstrap = fs.readFileSync(new URL('../world-map/3d-bootstrap.js', import.meta.url), 'utf8');
const card = fs.readFileSync(new URL('../world-map/3d-country-card.js', import.meta.url), 'utf8');

for (const marker of [
  'async function loadBatchAfterPaint',
  "declareDormant('Country Pulse', './3d-country-pulse.js', 'Country → Statistics')",
  "declareDormant('Evidence', './3d-evidence.js', 'Country → More data')",
  "declareDormant('System Intelligence', './3d-gateways.js', 'Country → Context')",
  "declareDormant('Functional Chains', './3d-chain-explorer.js', 'Country → Context')",
  "declareDormant('Infrastructure Context', './3d-infrastructure.js', 'Country → Context')",
  "declareDormant('Impact Trace', './3d-impact-trace.js', 'Country → Impact')",
]) assert.ok(bootstrap.includes(marker), `inspection bootstrap missing marker: ${marker}`);

for (const forbidden of [
  'const promoteInspection = async () =>',
  'promoteInspectionOnce',
  'loadInspectionBasics()',
  'loadInspectionContext()',
  'loadInspectionDeep()',
]) assert.ok(!bootstrap.includes(forbidden), `ordinary country selection must not auto-promote specialist stack: ${forbidden}`);

for (const marker of [
  "window.__potatoAtlasLoadModule?.('Country Pulse', './3d-country-pulse.js')",
  "window.__potatoAtlasLoadModule?.('Evidence', './3d-evidence.js')",
  "window.__potatoAtlasLoadModule?.('System Intelligence', './3d-gateways.js')",
  "window.__potatoAtlasLoadModule?.('Functional Chains', './3d-chain-explorer.js')",
  "window.__potatoAtlasLoadModule?.('Infrastructure Context', './3d-infrastructure.js')",
  "window.__potatoAtlasLoadModule('Impact Trace', './3d-impact-trace.js')",
]) assert.ok(card.includes(marker), `country card must own explicit specialist trigger: ${marker}`);

console.log('WORLD MAP ACTION-DRIVEN INSPECTION LOADING REGRESSION PASSED');
