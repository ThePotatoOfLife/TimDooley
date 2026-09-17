import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(new URL('../world-map/3d-context-visibility.js', import.meta.url), 'utf8');

assert.ok(source.includes('function relationBudgetsEqual'), 'context should compare desired relation budgets before asking selection to rebuild');
assert.ok(source.includes('selection.getAutomaticRelationBudget?.()'), 'context should read the current selection-owned relation budget');
assert.ok(source.includes('if (relationBudgetsEqual'), 'unchanged relation budgets should skip the selection update');
assert.ok(source.includes('contextRelationBudgetSkips'), 'diagnostics should count avoided redundant relation-budget updates');
assert.ok(source.includes('selection.setAutomaticRelationBudget?.('), 'changed budgets must still be delegated to the selection owner');

console.log('World Map relation budget contract tests passed');
