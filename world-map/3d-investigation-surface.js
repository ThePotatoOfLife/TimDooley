// Presentation-only arbitration for temporary World Map investigation panels.
// Domain modules keep their own state and semantics; this only prevents stacked
// floating surfaces from competing for the same map space.
const handlers = new Map();
let activeId = null;

function register(id, handler = {}) {
  const key = String(id || '').trim();
  if (!key) return false;
  handlers.set(key, handler || {});
  return true;
}

function open(id) {
  const key = String(id || '').trim();
  if (!key) return false;
  if (activeId && activeId !== key) handlers.get(activeId)?.close?.({ coordinated:true });
  activeId = key;
  window.dispatchEvent(new CustomEvent('potato-atlas-investigation-change', { detail:{ id:activeId } }));
  return true;
}

function close(id) {
  const key = String(id || '').trim();
  if (activeId === key) activeId = null;
  window.dispatchEvent(new CustomEvent('potato-atlas-investigation-change', { detail:{ id:activeId } }));
  return true;
}

function active() { return activeId; }

window.__potatoAtlasInvestigationSurface = { register, open, close, active };
