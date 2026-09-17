import assert from 'node:assert/strict';
import fs from 'node:fs';

const workflow = fs.readFileSync(new URL('../.github/workflows/quality-checks.yml', import.meta.url), 'utf8');

for (const command of [
  'python scripts/validate_world_map_context_visibility.py',
  'node scripts/test_world_map_context_policy.mjs',
  'node scripts/test_world_map_time_policy.mjs',
  'node scripts/test_world_map_investigation_contract.mjs',
  'node scripts/test_world_map_pinned_context_contract.mjs',
  'node scripts/test_world_map_context_status.mjs',
  'python scripts/validate_world_map_runtime_telemetry.py',
]) {
  assert.ok(workflow.includes(command), `quality workflow missing ${command}`);
}

console.log('World Map context CI contract tests passed');
