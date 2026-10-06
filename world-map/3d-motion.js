// Shared World Map camera-motion policy.
// Respects OS/browser reduced-motion preference without changing destination state.

const QUERY = '(prefers-reduced-motion: reduce)';
const media = typeof window.matchMedia === 'function' ? window.matchMedia(QUERY) : null;

function prefersReducedMotion() {
  return Boolean(media?.matches);
}
function options(input = {}) {
  const next = { ...input };
  if (prefersReducedMotion()) {
    next.duration = 0;
    next.animate = false;
    next.essential = false;
  }
  return next;
}
function easeTo(map, input = {}) {
  if (!map?.easeTo) return false;
  map.easeTo(options(input));
  return true;
}
function fitBounds(map, bounds, input = {}) {
  if (!map?.fitBounds) return false;
  map.fitBounds(bounds, options(input));
  return true;
}

window.__potatoAtlasMotion = Object.freeze({
  query:QUERY,
  prefersReducedMotion,
  options,
  easeTo,
  fitBounds,
});
