function createStyleLifecycle(map, options = {}) {
  if (!map?.on) throw new TypeError('style lifecycle requires a MapLibre-compatible map');
  const enqueue = typeof options.queue === 'function' ? options.queue : queueMicrotask;
  const emit = typeof options.emit === 'function'
    ? options.emit
    : detail => {
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('potato-atlas-style-generation', { detail }));
        }
      };

  const registrations = new Map();
  let generation = 0;
  let scheduled = false;
  let restoreRuns = 0;
  let styleEvents = 0;
  let lastReason = 'init';

  function normalizePriority(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : 0;
  }

  function sorted() {
    return [...registrations.values()]
      .sort((a, b) => a.priority - b.priority || a.owner.localeCompare(b.owner));
  }

  function register(owner, options = {}) {
    const key = String(owner || '').trim();
    if (!key || typeof options.restore !== 'function') return false;
    registrations.set(key, {
      owner:key,
      priority:normalizePriority(options.priority),
      restore:options.restore,
    });
    return true;
  }

  function unregister(owner) {
    return registrations.delete(String(owner || '').trim());
  }

  function run(reason = 'styledata') {
    generation += 1;
    const restored = [];
    const errors = [];
    for (const row of sorted()) {
      try {
        row.restore({ generation, reason });
        restoreRuns += 1;
        restored.push(row.owner);
      } catch (error) {
        const message = error?.message || String(error);
        errors.push({ owner:row.owner, message });
        console.warn(`Style Lifecycle could not restore ${row.owner}:`, error);
      }
    }
    lastReason = reason;
    const detail = { generation, reason, restored, errors };
    emit(detail);
    return detail;
  }

  function schedule(reason = 'styledata') {
    lastReason = reason;
    if (scheduled) return false;
    scheduled = true;
    enqueue(() => {
      scheduled = false;
      run(lastReason);
    });
    return true;
  }

  function state() {
    return {
      generation,
      scheduled,
      restoreRuns,
      styleEvents,
      lastReason,
      registrations:sorted().map(({ owner, priority }) => ({ owner, priority })),
    };
  }

  map.on('styledata', () => {
    styleEvents += 1;
    schedule('styledata');
  });

  return Object.freeze({ register, unregister, schedule, state });
}

if (typeof window !== 'undefined') {
  const map = window.__potatoAtlasMap;
  if (map && !window.__potatoAtlasStyleLifecycle) {
    window.__potatoAtlasStyleLifecycle = createStyleLifecycle(map);
  }
}

export { createStyleLifecycle };
