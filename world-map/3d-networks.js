import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

const DATA_URL = '../data/world-empirical-networks.json';
const GEO_URL = '../data/world-countries.geo.json';
const SOURCE_ID = 'empirical-network-countries';
const FILL_ID = 'empirical-network-fill';
const LINE_ID = 'empirical-network-line';
const DEFAULT_VIEW = 'off';
const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

function memberLists(network = {}) {
  return {
    primary: network.members || network.members_mapped_to_canonical_states || network.states_parties_active || [],
    secondary: [
      ...(network.partners || []),
      ...(network.areas || []),
      ...(network.candidates_relevant_to_project || []),
      ...(network.associated_states || [])
    ],
    suspended: network.suspended_state_party || []
  };
}

function enrich(geo, registry) {
  const networks = registry.networks || {};
  for (const feature of geo.features || []) {
    const code = String(feature.id || feature.properties?.iso3 || '').toUpperCase();
    const memberships = [];
    for (const [id,network] of Object.entries(networks)) {
      const lists = memberLists(network);
      if (lists.primary.includes(code)) memberships.push(`${id}:primary`);
      else if (lists.secondary.includes(code)) memberships.push(`${id}:secondary`);
      else if (lists.suspended.includes(code)) memberships.push(`${id}:suspended`);
    }
    feature.properties = {...(feature.properties || {}), iso3:code, empirical_memberships:memberships.join('|')};
    for (const id of Object.keys(networks)) {
      const lists = memberLists(networks[id]);
      feature.properties[`net_${id}`] = lists.primary.includes(code) ? 2 : lists.secondary.includes(code) ? 1 : lists.suspended.includes(code) ? -1 : 0;
    }
  }
  return geo;
}

function filterFor(id) {
  if (!id || id === 'off') return ['==',['get','iso3'],'__NONE__'];
  return ['!=',['get',`net_${id}`],0];
}

function colorFor(id, registry) {
  const network = registry.networks?.[id];
  if (!network) return '#9aa5a5';
  return ['case',
    ['==',['get',`net_${id}`],2], network.color || '#9aa5a5',
    ['==',['get',`net_${id}`],1], network.color || '#9aa5a5',
    '#777777'
  ];
}

function opacityFor(id) {
  return ['case',
    ['==',['get',`net_${id}`],2], .42,
    ['==',['get',`net_${id}`],1], .22,
    ['==',['get',`net_${id}`],-1], .14,
    .05
  ];
}

function addLayers(map, geo, registry) {
  if (map.getSource(SOURCE_ID)) return;
  map.addSource(SOURCE_ID,{type:'geojson',data:enrich(geo,registry)});
  const before = map.getLayer('countries-line') ? 'countries-line' : undefined;
  map.addLayer({id:FILL_ID,type:'fill',source:SOURCE_ID,filter:filterFor(DEFAULT_VIEW),paint:{'fill-color':'#9aa5a5','fill-opacity':.3}},before);
  map.addLayer({id:LINE_ID,type:'line',source:SOURCE_ID,filter:filterFor(DEFAULT_VIEW),paint:{'line-color':'#d9e1e1','line-width':['interpolate',['linear'],['zoom'],0,.7,4,1.3,7,2.1],'line-opacity':.86}},before);
}

function installControl(map, registry) {
  if (document.getElementById('empiricalNetworkView')) return;
  const field = document.getElementById('axisFieldView');
  const relationType = document.getElementById('relationType');
  const select = document.createElement('select');
  select.id = 'empiricalNetworkView';
  select.title = 'Observable institutions and regional networks';
  const order = ['BRICS','NATO','EU','ARCTIC_COUNCIL','NORDIC','SCO','ASEAN','APEC','PACIFIC_ISLANDS_FORUM','SADC','GCC','MERCOSUR'];
  const labels = registry.networks || {};
  select.innerHTML = `<option value="off">Networks · off</option>` + order.filter(id=>labels[id]).map(id=>`<option value="${id}">${esc(labels[id].label)}</option>`).join('');
  (field || relationType)?.insertAdjacentElement('afterend',select);

  const url = new URL(location.href);
  const requested = url.searchParams.get('network');
  select.value = labels[requested] ? requested : DEFAULT_VIEW;

  function apply(id) {
    const visible = id !== 'off' && labels[id];
    [FILL_ID,LINE_ID].forEach(layer => map.setLayoutProperty(layer,'visibility',visible?'visible':'none'));
    if (visible) {
      map.setFilter(FILL_ID,filterFor(id));
      map.setFilter(LINE_ID,filterFor(id));
      map.setPaintProperty(FILL_ID,'fill-color',colorFor(id,registry));
      map.setPaintProperty(LINE_ID,'line-color',colorFor(id,registry));
      map.setPaintProperty(FILL_ID,'fill-opacity',opacityFor(id));
    }
    const next = new URL(location.href);
    if (!visible) next.searchParams.delete('network'); else next.searchParams.set('network',id);
    history.replaceState(null,'',next);
  }

  select.addEventListener('change',()=>apply(select.value));
  apply(select.value);
}

function roleText(value) {
  return value === 2 ? 'member / primary' : value === 1 ? 'partner / associated / candidate' : value === -1 ? 'suspended' : '';
}

function installInteractions(map, registry) {
  const popup = new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:8});
  map.on('mouseenter',FILL_ID,event=>{
    map.getCanvas().style.cursor='pointer';
    const p = event.features?.[0]?.properties || {};
    const memberships = String(p.empirical_memberships || '').split('|').filter(Boolean).map(item=>{
      const [id,role] = item.split(':');
      const label = registry.networks?.[id]?.label || id;
      return `${label} · ${role}`;
    });
    popup.setLngLat(event.lngLat).setHTML(`<div class="atlas-hover"><b>${esc(p.name || p.iso3 || 'Country')}</b><br>${memberships.length ? memberships.map(esc).join('<br>') : 'No selected network membership'}<br><small>Observable institutional/regional layer · separate from project fields.</small></div>`).addTo(map);
  });
  map.on('mouseleave',FILL_ID,()=>{map.getCanvas().style.cursor='';popup.remove();});
}

async function boot() {
  const [dataRes,geoRes] = await Promise.all([fetch(DATA_URL),fetch(GEO_URL)]);
  if (!dataRes.ok || !geoRes.ok) throw new Error('Empirical network data unavailable');
  const [registry,geo] = await Promise.all([dataRes.json(),geoRes.json()]);
  for (let i=0;i<120&&!window.__potatoAtlasMap;i+=1) await new Promise(resolve=>setTimeout(resolve,50));
  const map = window.__potatoAtlasMap;
  if (!map) return;
  if (!map.loaded()) await new Promise(resolve=>map.once('load',resolve));
  addLayers(map,geo,registry);
  installControl(map,registry);
  installInteractions(map,registry);
}

boot().catch(error=>console.warn('Empirical network enhancement unavailable:',error));
