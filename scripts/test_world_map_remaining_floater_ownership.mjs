import assert from 'node:assert/strict';
import fs from 'node:fs';

const layout = fs.readFileSync(new URL('../world-map/3d-ui-layout.js', import.meta.url), 'utf8');
const operators = fs.readFileSync(new URL('../world-map/3d-axis-operators.js', import.meta.url), 'utf8');

assert.ok(
  !layout.includes(".filter(row => row.zone === 'left-status' && row.element?.isConnected)"),
  'left-status layout must accept detached registered surfaces so modules do not briefly paint at legacy coordinates',
);
assert.ok(
  layout.includes('.filter(row => row.zone === zone && row.element)') &&
  layout.includes("const rows = refreshZone('left-status', ensureLeftStatusHost());"),
  'left-status layout must route detached registered elements through the shared zone attachment path',
);
assert.ok(
  layout.includes('for (const row of rows) if (row.element.parentElement !== host) host.appendChild(row.element);'),
  'shared zone attachment must move registered surfaces into the canonical host',
);
assert.ok(
  layout.includes('#atlasUILeftStatus #axisOperatorHud{') &&
  layout.includes('width:min(420px,100%)!important') &&
  layout.includes('pointer-events:none!important'),
  'Axis operator HUD needs hosted sizing and must remain input-transparent inside the shared status stack',
);

assert.equal(fs.existsSync(new URL('../world-map/3d-fields.js', import.meta.url)), false, 'retired Fields module must stay deleted');
assert.equal(fs.existsSync(new URL('../world-map/3d-networks.js', import.meta.url)), false, 'retired Networks module must stay deleted');

assert.ok(
  operators.includes("id:'axis-operator-hud', zone:'left-status'"),
  'Axis Operator HUD must register with shared left-status placement instead of owning top-left coordinates',
);
assert.ok(
  operators.includes("const layout = window.__potatoAtlasUILayout"),
  'Axis Operator HUD must prefer the canonical layout coordinator when available',
);

console.log('WORLD MAP REMAINING FLOATER OWNERSHIP REGRESSION PASSED');
