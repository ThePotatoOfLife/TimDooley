import * as maplibregl from 'https://unpkg.com/maplibre-gl@6.9.0/dist/maplibre-gl.mjs';

const CFG_URL='../data/world-axis-fields.json';
const GEO_URL='../data/world-countries.geo.json';
const SOURCE_ID='axis-fields-countries';
const FILL_ID='axis-fields-fill';
const LINE_ID='axis-fields-line';
const DEFAULT_VIEW='all';
const FIELD_NAMES=['north','west','east','south','center'];
const ROLE_WEIGHT={primary:1,overlap:.76,hinge:.62,provisional:.36,future:.24,unknown:0};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let activeView=DEFAULT_VIEW;
let historicalSuppressed=false;
let installedMap=null;
let installedCfg=null;

function roleFor(code,field={}){
  for(const [key,list] of Object.entries(field)){
    if(!Array.isArray(list)||!list.includes(code))continue;
    if(/explicit|recovered_primary|primary/.test(key))return{role:'primary',key};
    if(/hinge/.test(key))return{role:'hinge',key};
    if(/provisional/.test(key))return{role:'provisional',key};
    if(/future|reconnection/.test(key))return{role:'future',key};
    if(/overlap|variable|ties/.test(key))return{role:'overlap',key};
    return{role:'overlap',key};
  }
  return{role:'unknown',key:null};
}
function bricsConfig(cfg){return cfg.empirical_layers?.BRICS||cfg.empirical_brics||{};}
function classify(code,cfg){
  const project=cfg.project_fields||{};
  const roles=Object.fromEntries(FIELD_NAMES.map(name=>[name,roleFor(code,project[name]||{})]));
  const brics=bricsConfig(cfg);
  return{roles,fields:FIELD_NAMES.filter(n=>roles[n].role!=='unknown'),bricsMember:(brics.members||[]).includes(code),bricsPartner:(brics.partners||[]).includes(code)};
}
function enrichGeoJSON(geo,cfg){
  for(const feature of geo.features||[]){
    const code=String(feature.id||feature.properties?.iso3||feature.properties?.id||'').toUpperCase();
    const c=classify(code,cfg),props={...(feature.properties||{}),iso3:code,axis_fields:c.fields.join('|')};
    for(const name of FIELD_NAMES){const role=c.roles[name].role;props[name]=role!=='unknown'?1:0;props[`${name}_role`]=role;props[`${name}_basis`]=c.roles[name].key||'';props[`${name}_strength`]=ROLE_WEIGHT[role]||0;}
    props.brics_member=c.bricsMember?1:0;props.brics_partner=c.bricsPartner?1:0;feature.properties=props;
  }
  return geo;
}
function allColorExpression(cfg){const p=cfg.palette;return['case',['==',['get','brics_member'],1],p.brics.color,['==',['get','north'],1],p.north.color,['==',['get','west'],1],p.west.color,['==',['get','east'],1],p.east.color,['==',['get','south'],1],p.south.color,['==',['get','center'],1],p.center.color,'#566262'];}
function viewFilter(view){if(FIELD_NAMES.includes(view))return['==',['get',view],1];if(view==='brics')return['any',['==',['get','brics_member'],1],['==',['get','brics_partner'],1]];return['any',...FIELD_NAMES.map(n=>['==',['get',n],1]),['==',['get','brics_member'],1],['==',['get','brics_partner'],1]];}
function viewColor(view,cfg){if(view==='brics')return['case',['==',['get','brics_member'],1],cfg.palette.brics.color,'#a75b5b'];return cfg.palette[view]?.color||allColorExpression(cfg);}
function viewOpacity(view){if(view==='brics')return['case',['==',['get','brics_member'],1],.48,.24];if(FIELD_NAMES.includes(view))return['interpolate',['linear'],['get',`${view}_strength`],0,.08,.24,.16,.36,.22,.62,.30,.76,.36,1,.46];return['case',['==',['get','brics_member'],1],.48,['==',['get','brics_partner'],1],.22,['==',['get','north'],1],['interpolate',['linear'],['get','north_strength'],0,.08,1,.42],['==',['get','west'],1],['interpolate',['linear'],['get','west_strength'],0,.08,1,.39],['==',['get','east'],1],['interpolate',['linear'],['get','east_strength'],0,.08,1,.39],['==',['get','south'],1],['interpolate',['linear'],['get','south_strength'],0,.08,1,.39],['==',['get','center'],1],['interpolate',['linear'],['get','center_strength'],0,.08,1,.35],.12];}
function addLayers(map,geo,cfg){
  if(map.getSource(SOURCE_ID))return;
  map.addSource(SOURCE_ID,{type:'geojson',data:enrichGeoJSON(geo,cfg)});
  const before=map.getLayer('countries-line')?'countries-line':undefined;
  map.addLayer({id:FILL_ID,type:'fill',source:SOURCE_ID,filter:viewFilter(DEFAULT_VIEW),paint:{'fill-color':allColorExpression(cfg),'fill-opacity':viewOpacity(DEFAULT_VIEW)}},before);
  map.addLayer({id:LINE_ID,type:'line',source:SOURCE_ID,filter:viewFilter(DEFAULT_VIEW),paint:{'line-color':allColorExpression(cfg),'line-width':['interpolate',['linear'],['zoom'],0,.55,4,1.15,7,1.8],'line-opacity':.76}},before);
}
function applyView(map,cfg,view,{writeUrl=true}={}){
  activeView=view;
  const visible=view!=='off'&&!historicalSuppressed;
  [FILL_ID,LINE_ID].forEach(id=>map.setLayoutProperty(id,'visibility',visible?'visible':'none'));
  if(view!=='off'){
    map.setFilter(FILL_ID,viewFilter(view));map.setFilter(LINE_ID,viewFilter(view));
    map.setPaintProperty(FILL_ID,'fill-color',viewColor(view,cfg));map.setPaintProperty(LINE_ID,'line-color',viewColor(view,cfg));map.setPaintProperty(FILL_ID,'fill-opacity',viewOpacity(view));
  }
  if(writeUrl){const url=new URL(location.href);if(view===DEFAULT_VIEW)url.searchParams.delete('field');else url.searchParams.set('field',view);history.replaceState(null,'',url);}
}
function installLegend(cfg){
  if(document.getElementById('axisFieldLegend'))return;
  const wrap=document.querySelector('.mapwrap');if(!wrap)return;
  const legend=document.createElement('div');legend.id='axisFieldLegend';legend.style.cssText='position:absolute;left:12px;top:12px;z-index:2;background:#080b0be8;border:1px solid #283333;border-radius:9px;padding:8px 10px;font-size:11px;max-width:430px;pointer-events:none';
  legend.innerHTML=['north','west','east','south','center','brics'].map(k=>{const p=cfg.palette[k];return`<span style="display:inline-flex;align-items:center;gap:5px;margin-right:10px"><i style="width:9px;height:9px;border-radius:50%;background:${esc(p.color)}"></i>${esc(p.label)}</span>`}).join('')+'<div style="margin-top:5px;color:#aab4aa">solid = stronger recovered assignment · faint = hinge / provisional / future · Center = convergence, not territory</div>';wrap.appendChild(legend);
}
function installControl(map,cfg){
  if(document.getElementById('axisFieldView'))return;
  const relation=document.getElementById('relationType'),select=document.createElement('select');select.id='axisFieldView';select.title='Project fields and convergence view';select.innerHTML='<option value="all">Fields · all</option><option value="north">North · icy blue</option><option value="west">West · marine blue</option><option value="east">East · red</option><option value="south">South · gold</option><option value="center">Center · convergence</option><option value="brics">BRICS · red</option><option value="off">Fields · off</option>';relation?.insertAdjacentElement('beforebegin',select);
  const params=new URL(location.href).searchParams,allowed=['all','north','west','east','south','center','brics','off'];select.value=allowed.includes(params.get('field'))?params.get('field'):DEFAULT_VIEW;activeView=select.value;
  select.addEventListener('change',()=>applyView(map,cfg,select.value));applyView(map,cfg,select.value);
}
function setHistoricalSuppressed(on){
  historicalSuppressed=Boolean(on);
  const select=document.getElementById('axisFieldView');
  if(select){select.disabled=historicalSuppressed;select.title=historicalSuppressed?'Current project-field snapshot hidden in historical mode until a dated field snapshot is available':'Project fields and convergence view';}
  if(installedMap&&installedCfg)applyView(installedMap,installedCfg,activeView,{writeUrl:false});
  const legend=document.getElementById('axisFieldLegend');if(legend)legend.hidden=historicalSuppressed;
}
function roleLabel(r){return({primary:'primary/recovered',overlap:'overlap',hinge:'hinge',provisional:'provisional',future:'future/reconnection'}[r]||r);}
function installInteractions(map){
  const popup=new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:8});
  map.on('mouseenter',FILL_ID,e=>{if(historicalSuppressed)return;map.getCanvas().style.cursor='pointer';const p=e.features?.[0]?.properties||{};const lines=FIELD_NAMES.filter(n=>p[n]===1).map(n=>`${n[0].toUpperCase()+n.slice(1)} · ${roleLabel(p[`${n}_role`])}`);const institutional=p.brics_member===1?'BRICS · member':p.brics_partner===1?'BRICS · partner':'';popup.setLngLat(e.lngLat).setHTML(`<div class="atlas-hover"><b>${esc(p.name||p.iso3||'Country')}</b><br>${lines.length?lines.map(esc).join('<br>'):'No project-field assignment'}${institutional?`<br><span>${esc(institutional)}</span>`:''}<br><small>Project fields are interpretive and confidence-weighted; Center is convergence; BRICS is empirical.</small></div>`).addTo(map);});
  map.on('mouseleave',FILL_ID,()=>{map.getCanvas().style.cursor='';popup.remove();});
}
async function boot(){const[cfgRes,geoRes]=await Promise.all([fetch(CFG_URL),fetch(GEO_URL)]);if(!cfgRes.ok||!geoRes.ok)throw new Error('Axis field data unavailable');const[cfg,geo]=await Promise.all([cfgRes.json(),geoRes.json()]);for(let i=0;i<120&&!window.__potatoAtlasMap;i++)await new Promise(r=>setTimeout(r,50));const map=window.__potatoAtlasMap;if(!map)return;if(!map.loaded())await new Promise(r=>map.once('load',r));installedMap=map;installedCfg=cfg;addLayers(map,geo,cfg);installControl(map,cfg);installLegend(cfg);installInteractions(map);const state=window.__potatoAtlasTime?.getState?.();setHistoricalSuppressed(state&&state.mode!=='current');}
window.addEventListener('atlas-time-change',event=>setHistoricalSuppressed(event.detail?.mode!=='current'));
boot().catch(error=>console.warn('World axis fields unavailable:',error));
