import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

// North / Axis threshold overlay for the 3D World Relational Atlas.
// This is a project-symbolic rendering attached to real northern geography;
// it is not a country boundary, territorial claim, or physical feature.

const AXIS_ARC_DEGREES = 42;
const ARC_CENTER_LON = -36;
const HALF_ARC = AXIS_ARC_DEGREES / 2;
const ARC_TOP_LAT = 84.7;
const ARC_LIP_LAT = 80.1;
const ARC_CENTER_DIP = 78.35;
const AXIS_SOURCE = 'north-axis-threshold';
const AXIS_FILL = 'north-axis-threshold-fill';
const AXIS_GLOW = 'north-axis-threshold-glow';
const AXIS_LINE = 'north-axis-threshold-line';
const AXIS_GATE = 'north-axis-gate';
const AXIS_LABEL = 'north-axis-label';

function lowerArcCoordinates() {
  const points = [];
  const steps = 84;
  // Negative / upside-down-rainbow lip. The middle dips toward northern Greenland.
  // 42° is a visual design parameter, not a geographic or theological fact.
  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps;
    const lon = ARC_CENTER_LON - HALF_ARC + AXIS_ARC_DEGREES * t;
    const lat = ARC_LIP_LAT - (ARC_LIP_LAT - ARC_CENTER_DIP) * Math.sin(Math.PI * t);
    points.push([lon, lat]);
  }
  return points;
}

function upperArcCoordinates() {
  const points = [];
  const steps = 84;
  // Rounded upper shell of the bubble, kept below Web Mercator's ~85.0511° limit.
  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps;
    const lon = ARC_CENTER_LON + HALF_ARC - AXIS_ARC_DEGREES * t;
    const lat = ARC_LIP_LAT + (ARC_TOP_LAT - ARC_LIP_LAT) * Math.sin(Math.PI * t);
    points.push([lon, lat]);
  }
  return points;
}

function bubblePolygon() {
  const ring = [...lowerArcCoordinates(), ...upperArcCoordinates()];
  ring.push(ring[0]);
  return ring;
}

function axisGeoJSON() {
  const lowerArc = lowerArcCoordinates();
  return {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        properties: {
          kind: 'threshold_bubble',
          name: 'North / Axis threshold',
          subtitle: `${AXIS_ARC_DEGREES}° polar bubble`,
          plane: 'project-symbolic',
        },
        geometry: { type: 'Polygon', coordinates: [bubblePolygon()] },
      },
      {
        type: 'Feature',
        properties: {
          kind: 'threshold_arc',
          name: 'North / Axis threshold',
          subtitle: `${AXIS_ARC_DEGREES}° negative arc over northern Greenland`,
          plane: 'project-symbolic',
        },
        geometry: { type: 'LineString', coordinates: lowerArc },
      },
      {
        type: 'Feature',
        properties: {
          kind: 'axis_gate',
          name: 'North / Axis Gate',
          subtitle: 'Threshold toward North of North · project-symbolic overlay',
          plane: 'project-symbolic',
        },
        // A renderable polar anchor. Mercator cannot display 90°N directly.
        geometry: { type: 'Point', coordinates: [ARC_CENTER_LON, 84.45] },
      },
    ],
  };
}

function addAxisLayers(map) {
  if (map.getSource(AXIS_SOURCE)) return;
  map.addSource(AXIS_SOURCE, { type: 'geojson', data: axisGeoJSON() });

  map.addLayer({
    id: AXIS_FILL,
    type: 'fill',
    source: AXIS_SOURCE,
    filter: ['==', ['get', 'kind'], 'threshold_bubble'],
    paint: {
      'fill-color': '#cbb8ef',
      'fill-opacity': ['interpolate', ['linear'], ['zoom'], 0, 0.12, 3, 0.18, 6, 0.22],
      'fill-outline-color': '#d7c7f4',
    },
  });

  map.addLayer({
    id: AXIS_GLOW,
    type: 'line',
    source: AXIS_SOURCE,
    filter: ['==', ['get', 'kind'], 'threshold_arc'],
    paint: {
      'line-color': '#efe6ff',
      'line-width': 11,
      'line-opacity': 0.14,
      'line-blur': 6,
    },
  });

  map.addLayer({
    id: AXIS_LINE,
    type: 'line',
    source: AXIS_SOURCE,
    filter: ['==', ['get', 'kind'], 'threshold_arc'],
    paint: {
      'line-color': '#dfc8ff',
      'line-width': 2.7,
      'line-opacity': 0.92,
      'line-dasharray': [2, 1.2],
    },
  });

  map.addLayer({
    id: AXIS_GATE,
    type: 'circle',
    source: AXIS_SOURCE,
    filter: ['==', ['get', 'kind'], 'axis_gate'],
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 0, 5, 3, 7.5, 6, 10],
      'circle-color': '#f2ebff',
      'circle-stroke-color': '#b98be8',
      'circle-stroke-width': 2,
      'circle-opacity': 0.97,
    },
  });

  map.addLayer({
    id: AXIS_LABEL,
    type: 'symbol',
    source: AXIS_SOURCE,
    filter: ['==', ['get', 'kind'], 'axis_gate'],
    minzoom: 1.0,
    layout: {
      'text-field': 'NORTH · AXIS',
      'text-size': 11,
      'text-offset': [0, 1.7],
      'text-anchor': 'top',
      'text-letter-spacing': 0.12,
      'text-allow-overlap': true,
    },
    paint: {
      'text-color': '#f1eaff',
      'text-halo-color': '#080b0b',
      'text-halo-width': 1.5,
    },
  });
}

function setAxisVisible(map, visible) {
  [AXIS_FILL, AXIS_GLOW, AXIS_LINE, AXIS_GATE, AXIS_LABEL].forEach(id => {
    if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none');
  });
}

function installAxisToggle(map) {
  if (document.getElementById('axisLayer')) return;
  const worldButton = document.getElementById('world');
  const button = document.createElement('button');
  button.id = 'axisLayer';
  button.className = 'active';
  button.textContent = 'Axis';
  button.title = `Toggle ${AXIS_ARC_DEGREES}° North / Axis polar bubble`;
  worldButton?.insertAdjacentElement('beforebegin', button);

  let visible = true;
  const params = new URL(location.href).searchParams;
  if (params.get('axis') === '0') visible = false;
  button.classList.toggle('active', visible);

  button.addEventListener('click', () => {
    visible = !visible;
    setAxisVisible(map, visible);
    button.classList.toggle('active', visible);
    const url = new URL(location.href);
    if (visible) url.searchParams.delete('axis');
    else url.searchParams.set('axis', '0');
    history.replaceState(null, '', url);
  });

  setAxisVisible(map, visible);
}

function installAxisInteractions(map) {
  const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 10 });

  const enter = event => {
    map.getCanvas().style.cursor = 'pointer';
    const feature = event.features?.[0];
    if (!feature) return;
    const p = feature.properties || {};
    popup
      .setLngLat(event.lngLat)
      .setHTML(`<div class="atlas-hover"><b>${p.name || 'North / Axis'}</b><br><span>${p.subtitle || ''}</span><br><small>Project-symbolic atlas layer · not a nation, border, territory, or physical feature</small></div>`)
      .addTo(map);
  };
  const leave = () => {
    map.getCanvas().style.cursor = '';
    popup.remove();
  };

  [AXIS_FILL, AXIS_LINE, AXIS_GATE].forEach(layer => {
    map.on('mouseenter', layer, enter);
    map.on('mouseleave', layer, leave);
  });

  const openGate = () => {
    map.easeTo({ center: [ARC_CENTER_LON, 79.7], zoom: Math.max(map.getZoom(), 2.55), pitch: 48, bearing: 0, duration: 1300 });
    const panel = document.getElementById('panel');
    if (panel) {
      panel.innerHTML = `
        <div class="eyebrow">Project-symbolic threshold</div>
        <h1>North / Axis Gate</h1>
        <p class="muted">A translucent polar bubble shaped around a ${AXIS_ARC_DEGREES}° negative arc sits north of Greenland and slightly overlaps its northern edge as a visual threshold into the project's “North of North” plane.</p>
        <div class="boundary"><b>Boundary:</b> Greenland and the geographic Arctic remain ordinary geography. This bubble, Axis Gate, Tree, Ladder, and “North of North” are project-symbolic structures and do not define sovereignty, borders, territory, or physical geography.</div>
        <div class="card"><b>Axis logic</b><div class="row">Earth / Greenland / Arctic</div><div class="row">North bubble → threshold</div><div class="row">Threshold → Axis / Tree / Ladder</div><div class="row">Axis → North-of-North scene</div></div>
        <div class="card"><b>42° geometry</b><p class="muted">42° controls the horizontal sweep of the negative arc. It is a visual parameter and can be tuned independently of the layer's meaning.</p></div>
        <div class="actions"><button onclick="location.reload()">Return to atlas panel</button></div>`;
    }
  };

  map.on('click', AXIS_GATE, openGate);
  map.on('click', AXIS_FILL, openGate);
}

async function bootAxis() {
  for (let i = 0; i < 120 && !window.__potatoAtlasMap; i += 1) {
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  const map = window.__potatoAtlasMap;
  if (!map) return;
  if (!map.loaded()) await new Promise(resolve => map.once('load', resolve));
  addAxisLayers(map);
  installAxisToggle(map);
  installAxisInteractions(map);
}

bootAxis().catch(error => console.warn('North / Axis enhancement unavailable:', error));
