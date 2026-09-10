// Experimental North / Axis threshold overlay for the 3D World Relational Atlas.
// This is a project-symbolic rendering attached to the real northern geography;
// it is not a country boundary, territorial claim, or physical feature.

const AXIS_ARC_DEGREES = 42;
const HALF_ARC = AXIS_ARC_DEGREES / 2;
const ARC_EDGE_LAT = 84;
const ARC_CENTER_LAT = 78.5;
const AXIS_SOURCE = 'north-axis-threshold';
const AXIS_LINE = 'north-axis-threshold-line';
const AXIS_GLOW = 'north-axis-threshold-glow';
const AXIS_GATE = 'north-axis-gate';
const AXIS_LABEL = 'north-axis-label';

function arcCoordinates() {
  const points = [];
  const steps = 84;
  // A U-shaped / inverted-rainbow curve across a 42° longitudinal sweep.
  // The angle is a visual design parameter, not a theological or geographic fact.
  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps;
    const lon = -HALF_ARC + AXIS_ARC_DEGREES * t;
    const lat = ARC_EDGE_LAT - (ARC_EDGE_LAT - ARC_CENTER_LAT) * Math.sin(Math.PI * t);
    points.push([lon, lat]);
  }
  return points;
}

function axisGeoJSON() {
  return {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        properties: {
          kind: 'threshold_arc',
          name: 'North / Axis threshold',
          subtitle: `${AXIS_ARC_DEGREES}° experimental inverted polar arc`,
          plane: 'project-symbolic',
        },
        geometry: { type: 'LineString', coordinates: arcCoordinates() },
      },
      {
        type: 'Feature',
        properties: {
          kind: 'axis_gate',
          name: 'North / Axis Gate',
          subtitle: 'Threshold toward North of North · project-symbolic overlay',
          plane: 'project-symbolic',
        },
        // 89°N is used as a renderable near-pole anchor. The geographic North Pole
        // itself is 90°N; Mercator cannot represent that latitude directly.
        geometry: { type: 'Point', coordinates: [0, 89] },
      },
    ],
  };
}

function addAxisLayers(map) {
  if (map.getSource(AXIS_SOURCE)) return;
  map.addSource(AXIS_SOURCE, { type: 'geojson', data: axisGeoJSON() });

  map.addLayer({
    id: AXIS_GLOW,
    type: 'line',
    source: AXIS_SOURCE,
    filter: ['==', ['get', 'kind'], 'threshold_arc'],
    paint: {
      'line-color': '#e7d9ff',
      'line-width': 9,
      'line-opacity': 0.11,
      'line-blur': 5,
    },
  });

  map.addLayer({
    id: AXIS_LINE,
    type: 'line',
    source: AXIS_SOURCE,
    filter: ['==', ['get', 'kind'], 'threshold_arc'],
    paint: {
      'line-color': '#d7b6ff',
      'line-width': 2.3,
      'line-opacity': 0.82,
      'line-dasharray': [2, 1.4],
    },
  });

  map.addLayer({
    id: AXIS_GATE,
    type: 'circle',
    source: AXIS_SOURCE,
    filter: ['==', ['get', 'kind'], 'axis_gate'],
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 0, 4, 3, 7, 6, 10],
      'circle-color': '#efe6ff',
      'circle-stroke-color': '#b98be8',
      'circle-stroke-width': 2,
      'circle-opacity': 0.93,
    },
  });

  map.addLayer({
    id: AXIS_LABEL,
    type: 'symbol',
    source: AXIS_SOURCE,
    filter: ['==', ['get', 'kind'], 'axis_gate'],
    minzoom: 1.2,
    layout: {
      'text-field': 'NORTH · AXIS',
      'text-size': 11,
      'text-offset': [0, 1.6],
      'text-anchor': 'top',
      'text-letter-spacing': 0.12,
      'text-allow-overlap': true,
    },
    paint: {
      'text-color': '#efe6ff',
      'text-halo-color': '#080b0b',
      'text-halo-width': 1.3,
    },
  });
}

function setAxisVisible(map, visible) {
  [AXIS_GLOW, AXIS_LINE, AXIS_GATE, AXIS_LABEL].forEach(id => {
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
  button.title = `Toggle experimental ${AXIS_ARC_DEGREES}° North / Axis threshold`;
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

  const enter = (event) => {
    map.getCanvas().style.cursor = 'pointer';
    const feature = event.features?.[0];
    if (!feature) return;
    const p = feature.properties || {};
    popup
      .setLngLat(event.lngLat)
      .setHTML(`<div class="atlas-hover"><b>${p.name || 'North / Axis'}</b><br><span>${p.subtitle || ''}</span><br><small>Symbolic atlas layer · not a territorial boundary</small></div>`)
      .addTo(map);
  };
  const leave = () => {
    map.getCanvas().style.cursor = '';
    popup.remove();
  };

  [AXIS_LINE, AXIS_GATE].forEach(layer => {
    map.on('mouseenter', layer, enter);
    map.on('mouseleave', layer, leave);
  });

  map.on('click', AXIS_GATE, () => {
    map.easeTo({ center: [0, 78], zoom: Math.max(map.getZoom(), 2.25), pitch: 48, bearing: 0, duration: 1300 });
    const panel = document.getElementById('panel');
    if (panel) {
      panel.innerHTML = `
        <div class="eyebrow">Project-symbolic threshold</div>
        <h1>North / Axis Gate</h1>
        <p class="muted">An experimental ${AXIS_ARC_DEGREES}° inverted polar arc marks a visual threshold between the ordinary geographic atlas and a future non-geographic “North of North” relational plane.</p>
        <div class="boundary"><b>Boundary:</b> the geographic North Pole is a real place at 90°N. This arc, gate, Axis, Tree, Ladder and “North of North” are rendered as project-symbolic structure and do not define a nation, border, territory or physical feature.</div>
        <div class="card"><b>Prototype logic</b><div class="row">Earth → North → threshold</div><div class="row">Threshold → Axis / Tree / Ladder</div><div class="row">Axis → future North-of-North scene</div></div>
        <div class="card"><b>42°?</b><p class="muted">For now 42° is simply the arc's opening/sweep parameter. It is intentionally easy to change after seeing it in the live map.</p></div>
        <div class="actions"><button onclick="location.reload()">Return to atlas panel</button></div>`;
    }
  });
}

async function bootAxis() {
  // Enhancement modules load independently; wait briefly for the captured core map.
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
