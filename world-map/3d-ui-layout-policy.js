// Pure layout policy helpers for the World Relational Atlas.
// Keeps presentation budgeting testable without DOM ownership.

function normalizedBudget(value) {
  if (value === Infinity) return Infinity;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return Infinity;
  return Math.max(0, Math.floor(parsed));
}

function surfaceNaturallyVisible(row) {
  if (!row) return false;
  if (row.element && typeof row.element.hidden === 'boolean') return !row.element.hidden;
  return row.visible !== false;
}

function selectVisibleSurfaceIds(rows = [], budget = Infinity) {
  const limit = normalizedBudget(budget);
  const eligible = rows
    .filter(row => surfaceNaturallyVisible(row) && row?.id)
    .sort((a, b) => (Number(a.priority) || 0) - (Number(b.priority) || 0) || String(a.id).localeCompare(String(b.id)));
  if (limit === Infinity) return eligible.map(row => row.id);
  return eligible.slice(0, limit).map(row => row.id);
}

export { surfaceNaturallyVisible, selectVisibleSurfaceIds };
