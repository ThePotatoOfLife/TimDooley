// Presentation-only arbitration for temporary World Map investigation panels.
// Domain modules keep their own state and semantics; this only prevents stacked
// floating surfaces from competing for the same map space.
const handlers = new Map();
let activeId = null;

function snapshot(reason = 'read') {
  return { id:activeId, active:Boolean(activeId), reason };
}

function publish(reason) {
  const detail = snapshot(reason);
  window.dispatchEvent(new CustomEvent('potato-atlas-investigation-change', { detail }));
  return detail;
}

function register(id, handler = {}) {
  const key = String(id || '').trim();
  if (!key) return false;
  handlers.set(key, handler || {});
  return true;
}

function unregister(id) {
  const key = String(id || '').trim();
  if (!key) return false;
  if (activeId === key) close(key);
  handlers.delete(key);
  return true;
}

function open(id) {
  const key = String(id || '').trim();
  if (!key) return false;
  if (activeId && activeId !== key) handlers.get(activeId)?.close?.({ coordinated:true });
  activeId = key;
  publish('opened');
  return true;
}

function close(id) {
  const key = String(id || '').trim();
  if (!key) return false;
  if (activeId === key) activeId = null;
  publish('closed');
  return true;
}

function active() { return activeId; }
function isActive(id) { return activeId === String(id || '').trim(); }

window.__potatoAtlasInvestigationSurface = {
  register,
  unregister,
  open,
  close,
  active,
  isActive,
  get current() { return snapshot('read'); },
};
