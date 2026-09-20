const EARTH_MEAN_RADIUS_KM = 6371.0088;

function finiteNumber(value, label) {
  const number = Number(value);
  if (!Number.isFinite(number)) throw new TypeError(`${label} must be finite`);
  return number;
}

function normalizeLongitude(lng) {
  const value = finiteNumber(lng, 'longitude');
  return ((value + 180) % 360 + 360) % 360 - 180;
}

function shortestLongitudeDelta(fromLng, toLng) {
  return normalizeLongitude(normalizeLongitude(toLng) - normalizeLongitude(fromLng));
}

function unwrapLongitude(lng, referenceLng) {
  const reference = finiteNumber(referenceLng, 'reference longitude');
  return reference + shortestLongitudeDelta(reference, lng);
}

function minimalLongitudeInterval(longitudes, referenceLng = null) {
  if (!Array.isArray(longitudes) || !longitudes.length) throw new TypeError('at least one longitude coordinate is required');
  const values = longitudes.map(value => normalizeLongitude(value)).sort((a, b) => a - b);
  if (values.length === 1) {
    let west = values[0];
    if (referenceLng != null) west = unwrapLongitude(west, referenceLng);
    return { west, east:west, span:0, crossesAntimeridian:false };
  }
  let largestGap = -1;
  let gapAfter = 0;
  for (let i = 0; i < values.length; i += 1) {
    const current = values[i];
    const next = i === values.length - 1 ? values[0] + 360 : values[i + 1];
    const gap = next - current;
    if (gap > largestGap) {
      largestGap = gap;
      gapAfter = i;
    }
  }
  const startIndex = (gapAfter + 1) % values.length;
  let west = values[startIndex];
  let east = values[gapAfter];
  if (gapAfter < startIndex) east += 360;
  const span = Math.max(0, east - west);
  if (referenceLng != null) {
    const reference = finiteNumber(referenceLng, 'reference longitude');
    const center = (west + east) / 2;
    const turns = Math.round((reference - center) / 360);
    west += turns * 360;
    east += turns * 360;
  }
  const crossesAntimeridian = west < -180 || east > 180 || (normalizeLongitude(west) > normalizeLongitude(east) && span > 0);
  return { west, east, span, crossesAntimeridian };
}

function collectCoordinates(value, target) {
  if (value == null) return;
  if (typeof value === 'object' && !Array.isArray(value) && 'coordinates' in value) {
    collectCoordinates(value.coordinates, target);
    return;
  }
  if (!Array.isArray(value)) return;
  if (value.length >= 2 && typeof value[0] === 'number' && typeof value[1] === 'number') {
    const lng = finiteNumber(value[0], 'longitude coordinate');
    const lat = finiteNumber(value[1], 'latitude coordinate');
    if (lat < -90 || lat > 90) throw new RangeError('latitude coordinate must be between -90 and 90');
    target.push([lng, lat]);
    return;
  }
  for (const child of value) collectCoordinates(child, target);
}

function antimeridianAwareBounds(input, referenceLng = null) {
  const points = [];
  collectCoordinates(input, points);
  if (!points.length) throw new TypeError('at least one coordinate is required');
  const interval = minimalLongitudeInterval(points.map(point => point[0]), referenceLng);
  const latitudes = points.map(point => point[1]);
  return {
    west: interval.west,
    south: Math.min(...latitudes),
    east: interval.east,
    north: Math.max(...latitudes),
    spanLongitude: interval.span,
    crossesAntimeridian: interval.crossesAntimeridian,
  };
}

function validatedPoint(point, label) {
  if (!Array.isArray(point) || point.length < 2) throw new TypeError(`${label} must be [longitude, latitude]`);
  const lng = finiteNumber(point[0], `${label} longitude`);
  const lat = finiteNumber(point[1], `${label} latitude`);
  if (lat < -90 || lat > 90) throw new RangeError(`${label} latitude must be between -90 and 90`);
  return [normalizeLongitude(lng), lat];
}

function pointInRing(point, ring) {
  const [lng, lat] = validatedPoint(point, 'point');
  if (!Array.isArray(ring) || ring.length < 3) return false;
  const rawPoints = ring.map(coord => {
    if (!Array.isArray(coord) || coord.length < 2) return null;
    const x = Number(coord[0]);
    const y = Number(coord[1]);
    if (!Number.isFinite(x) || !Number.isFinite(y)) return null;
    return [normalizeLongitude(x), y];
  }).filter(Boolean);
  if (rawPoints.length < 3) return false;

  // Choose the ring's own minimum-width longitude frame. Unwrapping every
  // vertex relative to the query point makes a narrow dateline polygon look
  // almost world-wide when the query is near Greenwich.
  const interval = minimalLongitudeInterval(rawPoints.map(coord => coord[0]));
  const reference = (interval.west + interval.east) / 2;
  const testLng = unwrapLongitude(lng, reference);
  const points = rawPoints.map(([x, y]) => [unwrapLongitude(x, reference), y]);

  let inside = false;
  for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
    const [xi, yi] = points[i];
    const [xj, yj] = points[j];
    const intersects = ((yi > lat) !== (yj > lat))
      && (testLng < (xj - xi) * (lat - yi) / ((yj - yi) || Number.EPSILON) + xi);
    if (intersects) inside = !inside;
  }
  return inside;
}

function pointInPolygon(point, polygonCoordinates) {
  if (!Array.isArray(polygonCoordinates) || !polygonCoordinates.length) return false;
  if (!pointInRing(point, polygonCoordinates[0])) return false;
  for (let i = 1; i < polygonCoordinates.length; i += 1) {
    if (pointInRing(point, polygonCoordinates[i])) return false;
  }
  return true;
}

function pointInGeometry(point, geometry) {
  if (!geometry || typeof geometry !== 'object') return false;
  if (geometry.type === 'Polygon') return pointInPolygon(point, geometry.coordinates);
  if (geometry.type === 'MultiPolygon') {
    return (geometry.coordinates || []).some(polygon => pointInPolygon(point, polygon));
  }
  return false;
}

function haversineDistanceKm(a, b) {
  const [lng1, lat1] = validatedPoint(a, 'first point');
  const [lng2, lat2] = validatedPoint(b, 'second point');
  const toRadians = degrees => degrees * Math.PI / 180;
  const phi1 = toRadians(lat1);
  const phi2 = toRadians(lat2);
  const dPhi = toRadians(lat2 - lat1);
  const dLambda = toRadians(shortestLongitudeDelta(lng1, lng2));
  const sinPhi = Math.sin(dPhi / 2);
  const sinLambda = Math.sin(dLambda / 2);
  const h = sinPhi * sinPhi + Math.cos(phi1) * Math.cos(phi2) * sinLambda * sinLambda;
  return 2 * EARTH_MEAN_RADIUS_KM * Math.asin(Math.min(1, Math.sqrt(h)));
}

const api = Object.freeze({
  EARTH_MEAN_RADIUS_KM,
  normalizeLongitude,
  shortestLongitudeDelta,
  unwrapLongitude,
  minimalLongitudeInterval,
  antimeridianAwareBounds,
  pointInGeometry,
  haversineDistanceKm,
});

if (typeof window !== 'undefined') window.__potatoAtlasGeo = api;

export {
  EARTH_MEAN_RADIUS_KM,
  normalizeLongitude,
  shortestLongitudeDelta,
  unwrapLongitude,
  minimalLongitudeInterval,
  antimeridianAwareBounds,
  pointInGeometry,
  haversineDistanceKm,
};
