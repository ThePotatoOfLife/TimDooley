// Pure time-window helpers for the World Relational Atlas.
// Keeps URL/control input normalized before domain runtimes consume it.

const MODES = new Set(['current','as_of','changed_between']);
const DAY_MS = 24 * 60 * 60 * 1000;

function validIsoDate(value) {
  const text = String(value || '');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(text)) return false;
  const date = new Date(`${text}T00:00:00Z`);
  return !Number.isNaN(date.getTime()) && date.toISOString().slice(0,10) === text;
}

function normalizeTimeState(input = {}) {
  const mode = MODES.has(input.mode) ? input.mode : 'current';
  let time = String(input.time || '');
  let time2 = String(input.time2 || '');
  let normalized = mode !== input.mode && input.mode != null;
  let issue = null;

  if (mode === 'current') {
    normalized = normalized || Boolean(time || time2);
    return { mode:'current', time:'', time2:'', valid:true, normalized, issue:null };
  }

  if (!time) return { mode, time:'', time2:mode === 'changed_between' ? time2 : '', valid:false, normalized, issue:'missing-date' };
  if (!validIsoDate(time)) return { mode, time, time2:mode === 'changed_between' ? time2 : '', valid:false, normalized, issue:'invalid-date' };

  if (mode === 'as_of') {
    normalized = normalized || Boolean(time2);
    return { mode, time, time2:'', valid:true, normalized, issue:null };
  }

  if (!time2) return { mode, time, time2:'', valid:false, normalized, issue:'missing-range-end' };
  if (!validIsoDate(time2)) return { mode, time, time2, valid:false, normalized, issue:'invalid-date' };

  if (time2 < time) {
    [time, time2] = [time2, time];
    normalized = true;
    issue = 'reordered-range';
  }
  return { mode, time, time2, valid:true, normalized, issue };
}

function describeTimeWindow(input = {}) {
  const state = normalizeTimeState(input);
  if (state.mode === 'current') return { ...state, kind:'current', label:'Current', days:null };
  if (state.mode === 'as_of') return { ...state, kind:'instant', label:state.time || 'As of', days:0 };
  let days = null;
  if (state.valid) {
    const start = new Date(`${state.time}T00:00:00Z`);
    const end = new Date(`${state.time2}T00:00:00Z`);
    days = Math.round((end - start) / DAY_MS);
  }
  return {
    ...state,
    kind:'range',
    label:`${state.time || '—'} → ${state.time2 || '—'}`,
    days,
  };
}

export { validIsoDate, normalizeTimeState, describeTimeWindow };
