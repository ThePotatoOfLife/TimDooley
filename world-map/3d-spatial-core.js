function finitePoint(value) {
  return Array.isArray(value) && value.length >= 2 && Number.isFinite(Number(value[0])) && Number.isFinite(Number(value[1]));
}

function pointOnSegment(point, a, b, epsilon = 1e-10) {
  if (!finitePoint(point) || !finitePoint(a) || !finitePoint(b)) return false;
  const px = Number(point[0]), py = Number(point[1]);
  const ax = Number(a[0]), ay = Number(a[1]);
  const bx = Number(b[0]), by = Number(b[1]);
  const cross = (px - ax) * (by - ay) - (py - ay) * (bx - ax);
  if (Math.abs(cross) > epsilon) return false;
  const dot = (px - ax) * (px - bx) + (py - ay) * (py - by);
  return dot <= epsilon;
}

function pointInRing(point, ring) {
  if (!finitePoint(point) || !Array.isArray(ring) || ring.length < 3) return false;
  const x = Number(point[0]), y = Number(point[1]);
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const a = ring[j], b = ring[i];
    if (!finitePoint(a) || !finitePoint(b)) continue;
    if (pointOnSegment(point, a, b)) return true;
    const xi = Number(b[0]), yi = Number(b[1]);
    const xj = Number(a[0]), yj = Number(a[1]);
    const intersects = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersects) inside = !inside;
  }
  return inside;
}

function pointInPolygonCoordinates(point, coordinates) {
  if (!Array.isArray(coordinates) || !coordinates.length) return false;
  if (!pointInRing(point, coordinates[0])) return false;
  for (const hole of coordinates.slice(1)) {
    if (pointInRing(point, hole)) return false;
  }
  return true;
}

export function pointInGeometry(point, geometry) {
  if (!finitePoint(point) || !geometry || !Array.isArray(geometry.coordinates)) return false;
  if (geometry.type === 'Polygon') return pointInPolygonCoordinates(point, geometry.coordinates);
  if (geometry.type === 'MultiPolygon') {
    return geometry.coordinates.some(polygon => pointInPolygonCoordinates(point, polygon));
  }
  return false;
}

export function assetsWithinGeometry(assets, geometry) {
  return (assets || []).filter(asset => {
    if (!asset || asset.geometry_status === 'no-geometry') return false;
    const location = asset.location;
    if (location?.type !== 'Point' || !finitePoint(location.coordinates)) return false;
    return pointInGeometry(location.coordinates, geometry);
  });
}
