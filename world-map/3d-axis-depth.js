const DATA_URL = '../data/axis-depths.json';
const ROOT_ID = 'axisDepthNavigator';
const TINT_ID = 'axisDepthTint';
const ACTIVE_CLASS = 'axis-depth-active';

const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));

function levelByValue(data, value) {
  return (data.levels || []).find(item => Number(item.level) === Number(value)) || (data.levels || []).find(item => item.level === 0);
}

function spiralPosition(index, total) {
  const centerX = 50;
  const top = 12;
  const spanY = 76;
  const y = top + (index / Math.max(total - 1, 1)) * spanY;
  const phase = index * Math.PI * 0.88;
  const amplitude = 22;
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

function tintFor(level) {
  if (level >= 3) return {background:'radial-gradient(circle at 50% 8%,rgba(215,247,255,.28),rgba(170,225,255,.08) 34%,rgba(0,0,0,0) 68%)',opacity:.92};
  if (level === 2) return {background:'radial-gradient(circle at 50% 12%,rgba(184,235,201,.20),rgba(130,205,235,.06) 42%,rgba(0,0,0,0) 70%)',opacity:.82};
  if (level === 1) return {background:'radial-gradient(circle at 50% 10%,rgba(159,232,255,.18),rgba(0,0,0,0) 60%)',opacity:.72};
  if (level === 0) return {background:'transparent',opacity:0};
  if (level === -1) return {background:'linear-gradient(to bottom,rgba(0,0,0,0) 30%,rgba(65,47,31,.18) 100%)',opacity:.75};
  if (level === -2) return {background:'linear-gradient(to bottom,rgba(0,0,0,0) 18%,rgba(42,36,28,.18) 48%,rgba(31,24,16,.34) 100%)',opacity:.9};
  return {background:'linear-gradient(to bottom,rgba(0,0,0,.04),rgba(17,17,17,.46) 100%)',opacity:1};
}

function renderPanel(data, current) {
  const panel = document.getElementById('panel');
  if (!panel || !current) return;
  const direction = current.level > 0 ? 'Ascending the Axis' : current.level < 0 ? 'Descending the roots' : 'Threshold level';
  const above = levelByValue(data, current.level + 1);
  const below = levelByValue(data, current.level - 1);
  panel.innerHTML = `
    <div class="eyebrow">${esc(direction)} · project-symbolic plane</div>
    <h1>${esc(current.label)}</h1>
    <p class="muted">${esc(current.description)}</p>
    <div class="boundary"><b>Boundary:</b> Axis depth is conceptual navigation. Only Earth / North Gate is ordinary geographic map space. No symbolic level is a claim about physical altitude, underground geography, sovereignty, or empirical cosmology.</div>
    <div class="card"><b>${esc(current.symbol)}</b><div class="row">Axis level ${current.level > 0 ? '+' : ''}${current.level}</div><div class="row">Direction · ${esc(current.direction)}</div><div class="row">Tone · ${esc(current.tone)}</div></div>
    <div class="card"><b>Vertical relation</b>
      ${above && above.level !== current.level ? `<div class="row">↑ ${esc(above.label)}</div>` : ''}
      <div class="row">● ${esc(current.label)}</div>
      ${below && below.level !== current.level ? `<div class="row">↓ ${esc(below.label)}</div>` : ''}
    </div>
    <div class="card"><b>Axis grammar</b><p class="muted">Downward: roots → buried causes → Swamp/subculture → subterrain. Upward: spiral ladder → Tree/Garden → North of North. The North bubble is the Earth-side doorway joining those directions.</p></div>
    <div class="actions"><button id="axisReturnEarth">Return to Earth</button><button id="axisFocusNorth">Focus North Gate</button></div>`;
  document.getElementById('axisReturnEarth')?.addEventListener('click',()=>window.__potatoAxisDepth?.setLevel(0));
  document.getElementById('axisFocusNorth')?.addEventListener('click',()=>window.__potatoAxisDepth?.focusNorth());
}

function installNavigator(map, data) {
  if (document.getElementById(ROOT_ID)) return;
  const wrap = document.querySelector('.mapwrap');
  if (!wrap) return;
  const levels = [...(data.levels || [])].sort((a,b)=>b.level-a.level);
  const root = document.createElement('div');
  root.id = ROOT_ID;
  root.style.cssText = 'position:absolute;right:12px;top:62px;width:138px;height:330px;z-index:3;background:#080b0be0;border:1px solid #344343;border-radius:14px;padding:10px 8px;backdrop-filter:blur(8px);box-shadow:0 8px 30px rgba(0,0,0,.28)';
  root.innerHTML = '<div style="font:700 10px system-ui;letter-spacing:.14em;text-transform:uppercase;color:#9fe8ff;text-align:center;margin-bottom:4px">Axis stair</div><div style="font-size:9px;color:#aab4aa;text-align:center;margin-bottom:4px">↑ North of North · ↓ roots</div>';
  const track = document.createElement('div');
  track.style.cssText = 'position:relative;height:268px';
  const curve = document.createElement('div');
  curve.style.cssText = 'position:absolute;left:50%;top:5px;width:2px;height:258px;background:linear-gradient(to bottom,#dff8ff,#9fe8ff 38%,#6e695f 58%,#33291f);transform:translateX(-50%);opacity:.42;border-radius:999px';
  track.appendChild(curve);

  levels.forEach((level,index)=>{
    const pos = spiralPosition(index,levels.length);
    const button = document.createElement('button');
    button.dataset.axisLevel = String(level.level);
    button.title = level.description;
    button.innerHTML = `<span style="display:block;font-size:10px;font-weight:700">${level.level>0?'+':''}${level.level}</span><span style="display:block;font-size:9px;white-space:nowrap">${esc(level.label.replace(' / Heaven','').replace(' / Subculture',''))}</span>`;
    button.style.cssText = `position:absolute;left:${pos.x}%;top:${pos.y}%;transform:translate(-50%,-50%);min-width:72px;padding:4px 6px;border-radius:999px;font-size:9px;line-height:1.05;background:#101616;border:1px solid #3b4949;color:#dce5e5;transition:transform .2s ease,border-color .2s ease,color .2s ease,background .2s ease`;
    button.addEventListener('click',()=>setLevel(level.level));
    track.appendChild(button);
  });
  root.appendChild(track);
  wrap.appendChild(root);
  const tint = createTint();

  function updateButtons(level) {
    root.querySelectorAll('button[data-axis-level]').forEach(btn=>{
      const active = Number(btn.dataset.axisLevel) === Number(level);
      btn.classList.toggle(ACTIVE_CLASS,active);
      btn.style.borderColor = active ? '#9fe8ff' : '#3b4949';
      btn.style.color = active ? '#e7fbff' : '#dce5e5';
      btn.style.background = active ? '#17323a' : '#101616';
      btn.style.transform = active ? 'translate(-50%,-50%) scale(1.08)' : 'translate(-50%,-50%)';
    });
  }

  function setLevel(value, options={}) {
    const current = levelByValue(data,value);
    if (!current) return;
    updateButtons(current.level);
    const style = tintFor(current.level);
    if (tint) { tint.style.background = style.background; tint.style.opacity = String(style.opacity); }
    const url = new URL(location.href);
    if (current.level === 0) url.searchParams.delete('axisLevel'); else url.searchParams.set('axisLevel',String(current.level));
    history.replaceState(null,'',url);

    if (!options.silentCamera) {
      const baseZoom = Math.max(map.getZoom(),2.4);
      if (current.level > 0) map.easeTo({center:[-36,80.2],zoom:baseZoom + Math.min(current.level*.12,.36),pitch:50 + current.level*4,bearing:current.level*18,duration:850});
      else if (current.level < 0) map.easeTo({center:[-36,77.8],zoom:Math.max(2.25,baseZoom-.08*Math.abs(current.level)),pitch:38-Math.abs(current.level)*7,bearing:-current.level*14,duration:850});
      else map.easeTo({center:[-36,79.7],zoom:Math.max(2.4,map.getZoom()),pitch:42,bearing:0,duration:750});
    }
    renderPanel(data,current);
    window.dispatchEvent(new CustomEvent('atlas-axis-level-change',{detail:{level:current.level,id:current.id,label:current.label}}));
  }

  function focusNorth(){map.easeTo({center:[-36,79.7],zoom:Math.max(map.getZoom(),2.55),pitch:48,bearing:0,duration:900});}
  window.__potatoAxisDepth = {data,setLevel,focusNorth,getLevel:()=>Number(new URL(location.href).searchParams.get('axisLevel')||0)};
  const initial = Number(new URL(location.href).searchParams.get('axisLevel')||0);
  setLevel(levelByValue(data,initial)?.level ?? 0,{silentCamera:true});
  window.addEventListener('atlas-axis-open',()=>{root.style.display='block';setLevel(0);focusNorth();});
}

async function boot(){
  const response = await fetch(DATA_URL);
  if (!response.ok) throw new Error('Axis depth model unavailable');
  const data = await response.json();
  for(let i=0;i<120&&!window.__potatoAtlasMap;i+=1) await new Promise(resolve=>setTimeout(resolve,50));
  const map=window.__potatoAtlasMap;if(!map)return;
  if(!map.loaded()) await new Promise(resolve=>map.once('load',resolve));
  installNavigator(map,data);
}

boot().catch(error=>console.warn('Axis depth navigation unavailable:',error));
