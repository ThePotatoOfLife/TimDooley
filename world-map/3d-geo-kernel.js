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

function destinationPointKm(origin, bearingDegrees, distanceKm) {
  const [lng, lat] = validatedPoint(origin, 'origin');
  const bearing = finiteNumber(bearingDegrees, 'bearing');
  const distance = finiteNumber(distanceKm, 'distance');
  if (distance < 0) throw new RangeError('distance must be non-negative');
  const toRadians = degrees => degrees * Math.PI / 180;
  const toDegrees = radians => radians * 180 / Math.PI;
  const angular = distance / EARTH_MEAN_RADIUS_KM;
  const theta = toRadians(bearing);
  const phi1 = toRadians(lat);
  const lambda1 = toRadians(lng);
  const sinPhi1 = Math.sin(phi1);
  const cosPhi1 = Math.cos(phi1);
  const sinAngular = Math.sin(angular);
  const cosAngular = Math.cos(angular);
  const phi2 = Math.asin(
    sinPhi1 * cosAngular + cosPhi1 * sinAngular * Math.cos(theta)
  );
  const lambda2 = lambda1 + Math.atan2(
    Math.sin(theta) * sinAngular * cosPhi1,
    cosAngular - sinPhi1 * Math.sin(phi2)
  );
  return [normalizeLongitude(toDegrees(lambda2)), toDegrees(phi2)];
}

function wrappedSegmentCoordinates(a, b) {
  const [lng1, lat1] = validatedPoint(a, 'segment start');
  const [lng2, lat2] = validatedPoint(b, 'segment end');
  return [[lng1, lat1], [unwrapLongitude(lng2, lng1), lat2]];
}

const api = Object.freeze({
  EARTH_MEAN_RADIUS_KM,
  normalizeLongitude,
  shortestLongitudeDelta,
  unwrapLongitude,
  minimalLongitudeInterval,
  antimeridianAwareBounds,
  haversineDistanceKm,
  destinationPointKm,
  wrappedSegmentCoordinates,
});

if (typeof window !== 'undefined') window.__potatoAtlasGeo = api;

export {
  EARTH_MEAN_RADIUS_KM,
  normalizeLongitude,
  shortestLongitudeDelta,
  unwrapLongitude,
  minimalLongitudeInterval,
  antimeridianAwareBounds,
  haversineDistanceKm,
  destinationPointKm,
  wrappedSegmentCoordinates,
};
