const DATA_URL = '../data/axis-depths.json';
const ROOT_ID = 'axisDepthNavigator';
const TINT_ID = 'axisDepthTint';
const ACTIVE_CLASS = 'axis-depth-active';
const DEFAULT_DIMENSION = 4;

const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

function levelByDimension(data, value) {
  return (data.levels || []).find(item => Number(item.dimension) === Number(value)) || (data.levels || []).find(item => item.dimension === DEFAULT_DIMENSION);
}

function spiralPosition(index, total) {
  const centerX = 50;
  const top = 7;
  const spanY = 86;
  const y = top + (index / Math.max(total - 1, 1)) * spanY;
  const phase = index * Math.PI * 0.72;
  const amplitude = 25;
  return {x:centerX + Math.sin(phase) * amplitude, y};
}

function createTint() {
  let tint = document.getElementById(TINT_ID);
  if (tint) return tint;
  const mapwrap = document.querySelector('.mapwrap');
  if (!mapwrap) return null;
  tint = document.createElement('div');
  tint.id = TINT_ID;
  tint.style.cssText = 'position:absolute;inset:0;z-index:1;pointer-events:none;opacity:0;transition:opacity .55s ease,background .55s ease;mix-blend-mode:screen';
  mapwrap.appendChild(tint);
  return tint;
}

function tintFor(dimension) {
  if (dimension >= 11) return {background:'radial-gradient(circle at 50% 4%,rgba(245,253,255,.34),rgba(196,238,255,.14) 30%,rgba(0,0,0,0) 66%)',opacity:1};
  if (dimension === 10) return {background:'radial-gradient(circle at 50% 6%,rgba(228,249,255,.28),rgba(174,229,255,.09) 36%,rgba(0,0,0,0) 68%)',opacity:.95};
  if (dimension === 9) return {background:'radial-gradient(circle at 50% 8%,rgba(218,249,255,.24),rgba(190,236,211,.08) 40%,rgba(0,0,0,0) 70%)',opacity:.9};
  if (dimension === 8) return {background:'radial-gradient(circle at 50% 10%,rgba(188,236,202,.22),rgba(150,220,235,.07) 44%,rgba(0,0,0,0) 72%)',opacity:.84};
  if (dimension === 7) return {background:'radial-gradient(circle at 50% 11%,rgba(168,224,183,.18),rgba(135,208,232,.06) 48%,rgba(0,0,0,0) 74%)',opacity:.78};
  if (dimension === 6) return {background:'radial-gradient(circle at 50% 10%,rgba(159,232,255,.18),rgba(0,0,0,0) 62%)',opacity:.72};
  if (dimension === 5) return {background:'radial-gradient(circle at 50% 9%,rgba(159,232,255,.14),rgba(0,0,0,0) 56%)',opacity:.62};
  if (dimension === 4) return {background:'transparent',opacity:0};
  if (dimension === 3) return {background:'linear-gradient(to bottom,rgba(0,0,0,0) 28%,rgba(72,51,34,.18) 100%)',opacity:.76};
  if (dimension === 2) return {background:'linear-gradient(to bottom,rgba(0,0,0,0) 12%,rgba(48,38,27,.20) 48%,rgba(31,24,16,.39) 100%)',opacity:.92};
  return {background:'linear-gradient(to bottom,rgba(0,0,0,.08),rgba(15,15,15,.56) 100%)',opacity:1};
}

function directionLabel(current) {
  if (current.dimension > 5) return 'Ascending above the Door';
  if (current.dimension === 5) return 'Door / first-heaven threshold';
  if (current.dimension === 4) return 'Ordinary world layer';
  return 'Descending below Earth';
}

function renderPanel(data, current) {
  const panel = document.getElementById('panel');
  if (!panel || !current) return;
  const above = levelByDimension(data, current.dimension + 1);
  const below = levelByDimension(data, current.dimension - 1);
  const upMarkers = data.directional_law?.up?.markers || [];
  const downMarkers = data.directional_law?.down?.markers || [];
  panel.innerHTML = `
    <div class="eyebrow">${esc(directionLabel(current))} · project-symbolic scaffold</div>
    <h1>${esc(current.label)}</h1>
    <p class="muted">${esc(current.description)}</p>
    <div class="boundary"><b>Boundary:</b> D1–D11 is a spiritual/project-symbolic navigation grammar. D4 is ordinary geographic map space. D5 is the North Door. The M-theory resemblance is structural analogy only; no physical equivalence is asserted.</div>
    <div class="grid">
      <div class="metric"><span>Dimension</span><b>D${current.dimension}</b><small>${esc(current.status || 'scaffold')}</small></div>
      <div class="metric"><span>Direction</span><b>${esc(current.direction)}</b><small>${esc(current.tone)}</small></div>
    </div>
    <div class="card"><b>${esc(current.symbol)}</b><p class="muted">${esc(current.description)}</p></div>
    <div class="card"><b>Vertical relation</b>
      ${above && above.dimension !== current.dimension ? `<div class="row">↑ ${esc(above.label)}</div>` : ''}
      <div class="row">● ${esc(current.label)}</div>
      ${below && below.dimension !== current.dimension ? `<div class="row">↓ ${esc(below.label)}</div>` : ''}
    </div>
    <div class="card"><b>Axis traffic</b><div class="row">↑ growth markers · ${upMarkers.slice(0,7).map(esc).join(' · ')}</div><div class="row">↓ descent markers · ${downMarkers.slice(0,7).map(esc).join(' · ')}</div><p class="muted">Markers describe project symbolism, not measurable forces. The same Door/Ladder carries movement in both directions.</p></div>
    <div class="actions"><button id="axisReturnEarth">D4 · World map</button><button id="axisDoor">D5 · North Door</button><button id="axisFocusNorth">Focus North</button></div>`;
  document.getElementById('axisReturnEarth')?.addEventListener('click',()=>window.__potatoAxisDepth?.setDimension(4));
  document.getElementById('axisDoor')?.addEventListener('click',()=>window.__potatoAxisDepth?.setDimension(5));
  document.getElementById('axisFocusNorth')?.addEventListener('click',()=>window.__potatoAxisDepth?.focusNorth());
}

function installNavigator(map, data) {
  if (document.getElementById(ROOT_ID)) return;
  const wrap = document.querySelector('.mapwrap');
  if (!wrap) return;
  const levels = [...(data.levels || [])].sort((a,b)=>b.dimension-a.dimension);
  const root = document.createElement('div');
  root.id = ROOT_ID;
  root.style.cssText = 'position:absolute;right:12px;top:62px;width:156px;height:476px;z-index:3;background:#080b0be0;border:1px solid #344343;border-radius:14px;padding:10px 8px;backdrop-filter:blur(8px);box-shadow:0 8px 30px rgba(0,0,0,.28)';
  root.innerHTML = '<div style="font:700 10px system-ui;letter-spacing:.14em;text-transform:uppercase;color:#9fe8ff;text-align:center;margin-bottom:3px">Axis · D1–D11</div><div style="font-size:9px;color:#aab4aa;text-align:center;line-height:1.25">↑ North of North<br>D5 Door · D4 Earth<br>↓ roots / Swamp</div>';
  const track = document.createElement('div');
  track.style.cssText = 'position:relative;height:398px;margin-top:4px';
  const curve = document.createElement('div');
  curve.style.cssText = 'position:absolute;left:50%;top:4px;width:2px;height:388px;background:linear-gradient(to bottom,#f1fbff,#9fe8ff 46%,#78a8a2 56%,#6e695f 68%,#33291f);transform:translateX(-50%);opacity:.48;border-radius:999px';
  track.appendChild(curve);

  levels.forEach((level,index)=>{
    const pos = spiralPosition(index,levels.length);
    const button = document.createElement('button');
    button.dataset.axisDimension = String(level.dimension);
    button.title = level.description;
    const short = level.label.replace(/^D\d+ · /,'').replace(' / First Heaven','').replace(' / Disintegration','').replace(' / World Map','');
    button.innerHTML = `<span style="display:block;font-size:10px;font-weight:800">D${level.dimension}</span><span style="display:block;font-size:8px;white-space:nowrap;max-width:86px;overflow:hidden;text-overflow:ellipsis">${esc(short)}</span>`;
    button.style.cssText = `position:absolute;left:${pos.x}%;top:${pos.y}%;transform:translate(-50%,-50%);min-width:76px;padding:3px 6px;border-radius:999px;font-size:9px;line-height:1.05;background:#101616;border:1px solid #3b4949;color:#dce5e5;transition:transform .2s ease,border-color .2s ease,color .2s ease,background .2s ease`;
    button.addEventListener('click',()=>setDimension(level.dimension));
    track.appendChild(button);
  });
  root.appendChild(track);
  const traffic = document.createElement('div');
  traffic.style.cssText='font-size:8px;line-height:1.3;text-align:center;color:#aab4aa;border-top:1px solid #273333;padding-top:5px';
  traffic.innerHTML='<span style="color:#dff8ff">↑ seed · virtue · angel · light</span><br><span style="color:#aa9982">↓ debt · ash · strife · disintegration</span>';
  root.appendChild(traffic);
  wrap.appendChild(root);
  const tint = createTint();

  function updateButtons(dimension) {
    root.querySelectorAll('button[data-axis-dimension]').forEach(btn=>{
      const active = Number(btn.dataset.axisDimension) === Number(dimension);
      const d = Number(btn.dataset.axisDimension);
      btn.classList.toggle(ACTIVE_CLASS,active);
      btn.style.borderColor = active ? '#9fe8ff' : d===5 ? '#6caec1' : d===4 ? '#84958d' : '#3b4949';
      btn.style.color = active ? '#e7fbff' : '#dce5e5';
      btn.style.background = active ? '#17323a' : d===5 ? '#12282f' : d===4 ? '#17201d' : '#101616';
      btn.style.transform = active ? 'translate(-50%,-50%) scale(1.10)' : 'translate(-50%,-50%)';
    });
  }

  function setDimension(value, options={}) {
    const current = levelByDimension(data,value);
    if (!current) return;
    updateButtons(current.dimension);
    const style = tintFor(current.dimension);
    if (tint) { tint.style.background = style.background; tint.style.opacity = String(style.opacity); }
    const url = new URL(location.href);
    if (current.dimension === DEFAULT_DIMENSION) url.searchParams.delete('axisD'); else url.searchParams.set('axisD',String(current.dimension));
    history.replaceState(null,'',url);

    if (!options.silentCamera) {
      const baseZoom = Math.max(map.getZoom(),2.35);
      if (current.dimension >= 5) {
        const rise = current.dimension - 5;
        map.easeTo({center:[-36,80.0],zoom:baseZoom + Math.min(rise*.075,.42),pitch:48 + Math.min(rise*4.5,28),bearing:rise*16,duration:900});
      } else if (current.dimension === 4) {
        map.easeTo({center:[-36,74.5],zoom:Math.max(2.1,Math.min(map.getZoom(),2.8)),pitch:30,bearing:0,duration:800});
      } else {
        const depth = 4-current.dimension;
        map.easeTo({center:[-36,73.4],zoom:Math.max(2.0,baseZoom-.12*depth),pitch:28-depth*7,bearing:-depth*16,duration:900});
      }
    }
    renderPanel(data,current);
    window.dispatchEvent(new CustomEvent('atlas-axis-dimension-change',{detail:{dimension:current.dimension,id:current.id,label:current.label,direction:current.direction}}));
  }

  function focusNorth(){map.easeTo({center:[-36,79.7],zoom:Math.max(map.getZoom(),2.55),pitch:48,bearing:0,duration:900});}
  window.__potatoAxisDepth = {data,setDimension,setLevel:setDimension,focusNorth,getDimension:()=>Number(new URL(location.href).searchParams.get('axisD')||DEFAULT_DIMENSION)};
  const legacy = new URL(location.href).searchParams.get('axisLevel');
  const requested = Number(new URL(location.href).searchParams.get('axisD') || (legacy !== null ? Number(legacy)+4 : DEFAULT_DIMENSION));
  setDimension(levelByDimension(data,requested)?.dimension ?? DEFAULT_DIMENSION,{silentCamera:true});
  window.addEventListener('atlas-axis-open',()=>{root.style.display='block';setDimension(5);focusNorth();});
}

async function boot(){
  const response = await fetch(DATA_URL);
  if (!response.ok) throw new Error('Axis dimension model unavailable');
  const data = await response.json();
  for(let i=0;i<120&&!window.__potatoAtlasMap;i+=1) await new Promise(resolve=>setTimeout(resolve,50));
  const map=window.__potatoAtlasMap;if(!map)return;
  if(!map.loaded()) await new Promise(resolve=>map.once('load',resolve));
  installNavigator(map,data);
}

boot().catch(error=>console.warn('Axis dimension navigation unavailable:',error));
