import assert from 'node:assert/strict';
import fs from 'node:fs';

const workflow = fs.readFileSync(new URL('../.github/workflows/quality-checks.yml', import.meta.url), 'utf8');
const runner = fs.readFileSync(new URL('./run_quality_group.py', import.meta.url), 'utf8');

for (const command of [
  'python scripts/validate_world_map_context_visibility.py',
  'node scripts/test_world_map_context_policy.mjs',
  'node scripts/test_world_map_ui_surface_budget.mjs',
  'node scripts/test_world_map_time_policy.mjs',
  'node scripts/test_world_map_investigation_contract.mjs',
  'node scripts/test_world_map_investigation_surface_ownership.mjs',
  'python scripts/validate_world_map_investigation_utility.py',
  'node scripts/test_world_map_pinned_context_contract.mjs',
  'node scripts/test_world_map_context_status.mjs',
  'node scripts/test_world_map_display_system_contract.mjs',
  'node scripts/test_world_map_reset_context_contract.mjs',
  'node scripts/test_world_map_search_selection_contract.mjs',
  'node scripts/test_world_map_relation_budget_contract.mjs',
  'python scripts/validate_world_map_runtime_telemetry.py',
]) {
  assert.ok(runner.includes(command), `world-map quality runner missing ${command}`);
}

assert.ok(workflow.includes('python scripts/run_quality_group.py world_map'), 'quality workflow must delegate World Map checks to the grouped runner');
assert.ok(workflow.includes('pull_request:'), 'quality checks must run for pull requests');
assert.ok(workflow.includes('workflow_dispatch:'), 'quality checks must support manual verification');
assert.ok(!fs.existsSync(new URL('../.github/workflows/world-map-context-checks.yml', import.meta.url)), 'context checks must not add workflow sprawl');

console.log('World Map context CI contract tests passed');
