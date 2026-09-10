import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

const CFG_URL = '../data/world-axis-fields.json';
const GEO_URL = '../data/world-countries.geo.json';
const SOURCE_ID = 'axis-fields-countries';
const FILL_ID = 'axis-fields-fill';
const LINE_ID = 'axis-fields-line';
const DEFAULT_VIEW = 'all';

const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const FIELD_NAMES = ['north','west','east','south'];
const ROLE_WEIGHT = {primary:1, overlap:.76, hinge:.62, provisional:.36, future:.24, unknown:0};

function roleFor(code, field = {}) {
  const groups = Object.entries(field).filter(([,value]) => Array.isArray(value));
  for (const [key,list] of groups) {
    if (!list.includes(code)) continue;
    if (/explicit|recovered_primary|primary/.test(key)) return {role:'primary', key};
    if (/hinge/.test(key)) return {role:'hinge', key};
    if (/provisional/.test(key)) return {role:'provisional', key};
    if (/future|reconnection/.test(key)) return {role:'future', key};
    if (/overlap|variable|ties/.test(key)) return {role:'overlap', key};
    return {role:'overlap', key};
  }
  return {role:'unknown', key:null};
}

function bricsConfig(cfg) {
  return cfg.empirical_layers?.BRICS || cfg.empirical_brics || {};
}

function classify(code, cfg) {
  const project = cfg.project_fields || {};
  const roles = Object.fromEntries(FIELD_NAMES.map(name => [name, roleFor(code, project[name] || {})]));
  const brics = bricsConfig(cfg);
  return {
    roles,
    fields: FIELD_NAMES.filter(name => roles[name].role !== 'unknown'),
    bricsMember: (brics.members || []).includes(code),
    bricsPartner: (brics.partners || []).includes(code)
  };
}

function enrichGeoJSON(geo, cfg) {
  for (const feature of geo.features || []) {
    const code = String(feature.id || feature.properties?.iso3 || feature.properties?.id || '').toUpperCase();
    const c = classify(code, cfg);
    const props = {...(feature.properties || {}), iso3:code, axis_fields:c.fields.join('|')};
    for (const name of FIELD_NAMES) {
      const role = c.roles[name].role;
      props[name] = role !== 'unknown' ? 1 : 0;
      props[`${name}_role`] = role;
      props[`${name}_basis`] = c.roles[name].key || '';
      props[`${name}_strength`] = ROLE_WEIGHT[role] || 0;
    }
    props.brics_member = c.bricsMember ? 1 : 0;
    props.brics_partner = c.bricsPartner ? 1 : 0;
    feature.properties = props;
  }
  return geo;
}

function allColorExpression(cfg) {
  const p = cfg.palette;
  return ['case',
    ['==',['get','brics_member'],1], p.brics.color,
    ['==',['get','north'],1], p.north.color,
    ['==',['get','west'],1], p.west.color,
    ['==',['get','east'],1], p.east.color,
    ['==',['get','south'],1], p.south.color,
    '#566262'
  ];
}

function viewFilter(view) {
  if (FIELD_NAMES.includes(view)) return ['==',['get',view],1];
  if (view === 'brics') return ['any',['==',['get','brics_member'],1],['==',['get','brics_partner'],1]];
  return ['any',
    ...FIELD_NAMES.map(name => ['==',['get',name],1]),
    ['==',['get','brics_member'],1],['==',['get','brics_partner'],1]
  ];
}

function viewColor(view, cfg) {
  if (view === 'brics') return ['case',['==',['get','brics_member'],1],cfg.palette.brics.color,'#a75b5b'];
  if (cfg.palette[view]) return cfg.palette[view].color;
  return allColorExpression(cfg);
}

function viewOpacity(view) {
  if (view === 'brics') return ['case',['==',['get','brics_member'],1],.48,.24];
  if (FIELD_NAMES.includes(view)) {
    return ['interpolate',['linear'],['get',`${view}_strength`],0,.08,.24,.16,.36,.22,.62,.30,.76,.36,1,.46];
  }
  return ['case',
    ['==',['get','brics_member'],1],.48,
    ['==',['get','brics_partner'],1],.22,
    ['==',['get','north'],1],['interpolate',['linear'],['get','north_strength'],0,.08,1,.42],
    ['==',['get','west'],1],['interpolate',['linear'],['get','west_strength'],0,.08,1,.39],
    ['==',['get','east'],1],['interpolate',['linear'],['get','east_strength'],0,.08,1,.39],
    ['==',['get','south'],1],['interpolate',['linear'],['get','south_strength'],0,.08,1,.39],
    .12
  ];
}

function addLayers(map, geo, cfg) {
  if (map.getSource(SOURCE_ID)) return;
  map.addSource(SOURCE_ID, {type:'geojson', data:enrichGeoJSON(geo,cfg)});
  const before = map.getLayer('countries-line') ? 'countries-line' : undefined;
  map.addLayer({id:FILL_ID,type:'fill',source:SOURCE_ID,filter:viewFilter(DEFAULT_VIEW),paint:{'fill-color':allColorExpression(cfg),'fill-opacity':viewOpacity(DEFAULT_VIEW)}}, before);
  map.addLayer({id:LINE_ID,type:'line',source:SOURCE_ID,filter:viewFilter(DEFAULT_VIEW),paint:{'line-color':allColorExpression(cfg),'line-width':['interpolate',['linear'],['zoom'],0,.55,4,1.15,7,1.8],'line-opacity':.76}}, before);
}

function installLegend(cfg) {
  if (document.getElementById('axisFieldLegend')) return;
  const mapwrap = document.querySelector('.mapwrap');
  if (!mapwrap) return;
  const legend = document.createElement('div');
  legend.id = 'axisFieldLegend';
  legend.style.cssText = 'position:absolute;left:12px;top:12px;z-index:2;background:#080b0be8;border:1px solid #283333;border-radius:9px;padding:8px 10px;font-size:11px;max-width:390px;pointer-events:none';
  legend.innerHTML = ['north','west','east','south','brics'].map(key => {
    const p = cfg.palette[key];
    return `<span style="display:inline-flex;align-items:center;gap:5px;margin-right:10px"><i style="width:9px;height:9px;border-radius:50%;background:${esc(p.color)}"></i>${esc(p.label)}</span>`;
  }).join('') + '<div style="margin-top:5px;color:#aab4aa">solid = stronger recovered assignment · faint = hinge / provisional / future</div>';
  mapwrap.appendChild(legend);
}

function installControl(map, cfg) {
  if (document.getElementById('axisFieldView')) return;
  const relationType = document.getElementById('relationType');
  const select = document.createElement('select');
  select.id = 'axisFieldView';
  select.title = 'North / West / East / South project fields and empirical BRICS';
  select.innerHTML = `<option value="all">Fields · all</option><option value="north">North · icy blue</option><option value="west">West · marine blue</option><option value="east">East · red</option><option value="south">South · gold</option><option value="brics">BRICS · red</option><option value="off">Fields · off</option>`;
  relationType?.insertAdjacentElement('beforebegin',select);
  const params = new URL(location.href).searchParams;
  const allowed = ['all','north','west','east','south','brics','off'];
  const initial = allowed.includes(params.get('field')) ? params.get('field') : DEFAULT_VIEW;
  select.value = initial;

  function apply(view) {
    const visible = view !== 'off';
    [FILL_ID,LINE_ID].forEach(id => { if (map.getLayer(id)) map.setLayoutProperty(id,'visibility',visible?'visible':'none'); });
    if (visible) {
      map.setFilter(FILL_ID,viewFilter(view));
      map.setFilter(LINE_ID,viewFilter(view));
      map.setPaintProperty(FILL_ID,'fill-color',viewColor(view,cfg));
      map.setPaintProperty(LINE_ID,'line-color',viewColor(view,cfg));
      map.setPaintProperty(FILL_ID,'fill-opacity',viewOpacity(view));
    }
    const url = new URL(location.href);
    if (view === DEFAULT_VIEW) url.searchParams.delete('field'); else url.searchParams.set('field',view);
    history.replaceState(null,'',url);
  }

  select.addEventListener('change',()=>apply(select.value));
  apply(initial);
}

function roleLabel(role) {
  return ({primary:'primary/recovered',overlap:'overlap',hinge:'hinge',provisional:'provisional',future:'future/reconnection'}[role] || role);
}

function installInteractions(map) {
  const popup = new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:8});
  map.on('mouseenter',FILL_ID,event => {
    map.getCanvas().style.cursor = 'pointer';
    const p = event.features?.[0]?.properties || {};
    const lines = FIELD_NAMES.filter(name => p[name] === 1).map(name => `${name[0].toUpperCase()+name.slice(1)} · ${roleLabel(p[`${name}_role`])}`);
    const institutional = p.brics_member === 1 ? 'BRICS · member' : p.brics_partner === 1 ? 'BRICS · partner' : '';
    popup.setLngLat(event.lngLat).setHTML(`<div class="atlas-hover"><b>${esc(p.name || p.iso3 || 'Country')}</b><br>${lines.length ? lines.map(esc).join('<br>') : 'No project-field assignment'}${institutional ? `<br><span>${esc(institutional)}</span>` : ''}<br><small>Project fields are interpretive and confidence-weighted; BRICS status is empirical.</small></div>`).addTo(map);
  });
  map.on('mouseleave',FILL_ID,()=>{map.getCanvas().style.cursor='';popup.remove();});
}

async function boot() {
  const [cfgRes,geoRes] = await Promise.all([fetch(CFG_URL),fetch(GEO_URL)]);
  if (!cfgRes.ok || !geoRes.ok) throw new Error('Axis field data unavailable');
  const [cfg,geo] = await Promise.all([cfgRes.json(),geoRes.json()]);
  for (let i=0;i<120&&!window.__potatoAtlasMap;i+=1) await new Promise(resolve=>setTimeout(resolve,50));
  const map = window.__potatoAtlasMap;
  if (!map) return;
  if (!map.loaded()) await new Promise(resolve=>map.once('load',resolve));
  addLayers(map,geo,cfg);
  installControl(map,cfg);
  installLegend(cfg);
  installInteractions(map);
}

boot().catch(error => console.warn('World axis fields unavailable:',error));
