// Pure context-policy helpers for the World Relational Atlas.
//
// This module owns no DOM or map state. It converts scale + investigation context
// into deterministic presentation budgets so the policy can be tested independently.

const BAND_BASE = Object.freeze({
  world:Object.freeze({ active:8, pinned:2, total:20, cards:4 }),
  'macro-region':Object.freeze({ active:8, pinned:2, total:22, cards:4 }),
  region:Object.freeze({ active:9, pinned:2, total:24, cards:4 }),
  country:Object.freeze({ active:10, pinned:2, total:26, cards:5 }),
  subnational:Object.freeze({ active:6, pinned:1, total:16, cards:5 }),
  local:Object.freeze({ active:4, pinned:1, total:12, cards:5 }),
});

function contextScaleBand(scale, previousBand, zoom) {
  if (!scale) return previousBand || 'world';
  if (previousBand && typeof scale.transition === 'function') {
    try { return scale.transition(previousBand, zoom); }
    catch { /* fall through */ }
  }
  if (typeof scale.bandForZoom === 'function') {
    try { return scale.bandForZoom(zoom); }
    catch { /* fall through */ }
  }
  return previousBand || 'world';
}

function contextInvestigationMode({
  evidence = false,
  specialistConnections = false,
  compare = false,
  relationFiltered = false,
} = {}) {
  if (evidence) return 'evidence';
  if (specialistConnections) return 'connections';
  if (compare) return 'compare';
  if (relationFiltered) return 'connections';
  return 'browse';
}

function contextBudgets({ band = 'world', mode = 'browse', pinCount = 0, narrow = false } = {}) {
  const source = BAND_BASE[band] || BAND_BASE.world;
  const base = { ...source, cards:narrow ? 2 : source.cards };
  let result;

  if (mode === 'connections') {
    result = {
      ...base,
      active:Math.min(12, base.active + 2),
      total:Math.min(32, base.total + 6),
      statusSurfaces:3,
    };
  } else if (mode === 'compare') {
    result = {
      ...base,
      active:Math.max(6, base.active - 1),
      pinned:Math.min(3, base.pinned + 1),
      statusSurfaces:3,
    };
  } else if (mode === 'evidence') {
    result = {
      ...base,
      active:Math.max(4, base.active - 2),
      total:Math.max(12, base.total - 4),
      statusSurfaces:4,
    };
  } else {
    result = { ...base, statusSurfaces:3 };
  }

  return {
    ...result,
    pinnedCards:Math.min(result.cards, Math.max(Number(pinCount) || 0, pinCount ? 1 : 0)),
  };
}

function contextVisibility({ band = 'world', mode = 'browse' } = {}) {
  return {
    showActiveRelations:mode !== 'evidence',
    showPinnedContext:true,
    showPlaceDetail:['country','subnational','local'].includes(band),
    showSubdivisionDetail:['subnational','local'].includes(band),
    emphasizeEvidence:mode === 'evidence',
    suppressDecorativeProjectOverlays:mode === 'evidence',
    reduceAbstractRelations:['subnational','local'].includes(band) && mode === 'browse',
  };
}

export { contextScaleBand, contextInvestigationMode, contextBudgets, contextVisibility };
