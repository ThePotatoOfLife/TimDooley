import assert from 'node:assert/strict';
import fs from 'node:fs';

const modules = {
  path: fs.readFileSync(new URL('../world-map/3d-pathfinder.js', import.meta.url), 'utf8'),
  impact: fs.readFileSync(new URL('../world-map/3d-impact-trace.js', import.meta.url), 'utf8'),
  chain: fs.readFileSync(new URL('../world-map/3d-chain-explorer.js', import.meta.url), 'utf8'),
};

for (const [id, source] of Object.entries(modules)) {
  assert.ok(
    source.includes('window.__potatoAtlasInvestigationSurface'),
    `${id} overlay must use the shared Investigation Surface coordinator`,
  );
  assert.ok(
    source.includes(`surface?.open?.('${id}')`),
    `${id} overlay must claim the temporary investigation surface before becoming visible`,
  );
  assert.ok(
    source.includes(`surface?.register?.('${id}'`),
    `${id} overlay must register a coordinated close callback`,
  );
  assert.ok(
    source.includes("coordinated:true"),
    `${id} overlay close callback must avoid recursively closing the coordinator`,
  );
}

const chain = modules.chain;
assert.ok(chain.includes("surface?.close?.('chain')"), 'clearing Chain directly must release investigation-surface ownership');
assert.ok(chain.includes('if (!coordinated)'), 'coordinated Chain close must not recurse into the surface controller');

console.log('WORLD MAP INVESTIGATION SURFACE OWNERSHIP REGRESSION PASSED');
