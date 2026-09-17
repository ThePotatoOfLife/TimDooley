import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-country-selection.js', import.meta.url), 'utf8');

assert.ok(source.includes('function relationBudgetsEqual'), 'selection should compare relation budgets before rebuilding relation data');
assert.ok(source.includes('if (relationBudgetsEqual'), 'unchanged relation budgets should take an early return');
assert.ok(source.includes('automaticRelationBudgetSkips'), 'diagnostics should count avoided redundant relation rebuilds');
assert.ok(source.includes('applyAutomaticRelations();'), 'changed budgets must still rebuild automatic relation data');
assert.ok(source.includes('potato-atlas-automatic-relation-budget-change'), 'changed budgets must still publish their state');

console.log('World Map relation budget contract tests passed');
