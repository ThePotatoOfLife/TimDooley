import assert from 'node:assert/strict';
import fs from 'node:fs';

const layout = fs.readFileSync(new URL('../world-map/3d-ui-layout.js', import.meta.url), 'utf8');
const fields = fs.readFileSync(new URL('../world-map/3d-fields.js', import.meta.url), 'utf8');
const operators = fs.readFileSync(new URL('../world-map/3d-axis-operators.js', import.meta.url), 'utf8');

assert.ok(
  !layout.includes(".filter(row => row.zone === 'left-status' && row.element?.isConnected)"),
  'left-status layout must accept detached registered surfaces so modules do not briefly paint at legacy coordinates',
);
assert.ok(
  layout.includes(".filter(row => row.zone === 'left-status' && row.element)"),
  'left-status layout must attach registered elements itself',
);
assert.ok(
  layout.includes('#atlasUILeftStatus #axisOperatorHud{width:min(420px,100%)!important}'),
  'Axis operator HUD needs a hosted width override inside the shared status stack',
);

assert.ok(
  fields.includes("id:'axis-field-legend', zone:'left-status'"),
  'Fields legend must register with shared left-status placement instead of owning the top-left corner',
);
assert.ok(
  fields.includes('function syncLegendVisibility()'),
  'Fields must have one visibility owner for its legend',
);
assert.ok(
  fields.includes("const visible=activeView!=='off'&&!historicalSuppressed"),
  'Fields legend must disappear when Fields are off or historically suppressed',
);
assert.ok(
  fields.includes("setVisible?.('axis-field-legend',visible)"),
  'Fields visibility must be reported through the layout coordinator',
);

assert.ok(
  operators.includes("id:'axis-operator-hud', zone:'left-status'"),
  'Axis Operator HUD must register with shared left-status placement instead of owning top-left coordinates',
);
assert.ok(
  operators.includes("const layout = window.__potatoAtlasUILayout"),
  'Axis Operator HUD must prefer the canonical layout coordinator when available',
);

console.log('WORLD MAP REMAINING FLOATER OWNERSHIP REGRESSION PASSED');
