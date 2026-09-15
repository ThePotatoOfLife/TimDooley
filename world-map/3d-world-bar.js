(async () => {
  const layers = window.__potatoAtlasLayers;
  const query = window.__potatoAtlasQuery;
  const map = window.__potatoAtlasMap;
  if (!layers || !query || !map) throw new Error('World toolbar requires map, layers and query APIs.');
  await layers.ready;

  const AXES = ['axis.north','axis.west','axis.east','axis.south'];
  const FAMILIES = [['groups','Groups'],['religion','Religion'],['stats','Stats'],['relations','Relations']];
  const RELATIONS = [['all','All context'],['money','Money'],['systems','Systems'],['institutions','Institutions'],['project','Project'],['other','Other']];
  const spatial = window.__potatoAtlasSpatialOverlays;
  const GEOGRAPHIES = [
    ['father.mesopotamia-core','Mesopotamia'],
    ['father.eden-context','Eden'],
    ['biblical.dan-to-beersheba','Dan → Beer-sheba'],
    ['biblical.genesis-15','Genesis 15'],
    ['modern.greater-israel','Greater Israel'],
  ];
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const entries = family => layers.entries(family, {availableOnly:true, ordinaryOnly:true});
  let projection = new URL(location.href).searchParams.get('projection') === 'globe' ? 'globe' : 'flat';
  let activeView = window.__potatoAtlasActiveView?.current || null;
  let timeState = window.__potatoAtlasTime?.getState?.() || null;

  function relationLabel(mode) {
    return RELATIONS.find(([id]) => id === mode)?.[1] || mode || 'All context';
  }
  function timeLabel(state) {
    if (!state || state.mode === 'current') return 'Current';
    if (state.label) return state.label;
    if (state.mode === 'as_of') return `As of ${state.time || '—'}`;
    return `${state.time || '—'} → ${state.time2 || '—'}`;
  }
  function closeMenus(current) {
    document.querySelectorAll('#atlasWorldBar details[open]').forEach(menu => { if (menu !== current) menu.removeAttribute('open'); });
  }
  function menu(family, label) {
    const details = document.createElement('details');
    details.className = 'atlas-world-menu';
    details.dataset.family = family;
    details.innerHTML = `<summary>${esc(label)}</summary><div class="atlas-world-menu-pop"></div>`;
    details.addEventListener('toggle', () => { if (details.open) closeMenus(details); });
    details.addEventListener('click', event => {
      const relationButton = event.target.closest('[data-relation-mode]');
      if (relationButton) return window.__potatoAtlasSelection?.setRelationMode?.(relationButton.dataset.relationMode);
      const layerButton = event.target.closest('[data-layer-option]');
      if (layerButton) layers.toggle(layerButton.dataset.layerOption);
    });
    return details;
  }
  function geographyMenu() {
    const details = document.createElement('details');
    details.id = 'atlasGeographyMenu';
    details.className = 'atlas-world-menu';
    details.innerHTML = '<summary>Geography</summary><div class="atlas-world-menu-pop"></div>';
    details.addEventListener('toggle', () => { if (details.open) { closeMenus(details); syncGeographyMenu(details); } });
    details.addEventListener('click', async event => {
      const button = event.target.closest('[data-geography-overlay]');
      if (!button || !spatial) return;
      const id = button.dataset.geographyOverlay;
      if (!spatial.isActive(id)) await spatial.activate(id);
      spatial.fit(id);
      syncGeographyMenu(details);
    });
    return details;
  }
  function syncGeographyMenu(details = document.getElementById('atlasGeographyMenu')) {
    if (!details) return;
    const pop = details.querySelector('.atlas-world-menu-pop');
    if (!pop) return;
    if (!spatial) {
      pop.innerHTML = '<div class="atlas-world-empty">Geography overlays unavailable</div>';
      return;
    }
    const rows = GEOGRAPHIES.map(([id,label]) => {
      const entry = spatial.get(id);
      if (!entry || entry.availability !== 'current') return '';
      const active = spatial.isActive(id);
      const kind = String(entry.epistemic_type || '').replaceAll('_',' ');
      return `<button type="button" class="atlas-world-option${active?' active':''}" data-geography-overlay="${esc(id)}"><span>${esc(label)}<small>${esc(kind)}</small></span></button>`;
    }).join('');
    pop.innerHTML = `<div class="atlas-world-static"><span>Geographies</span><small>stackable overlays</small></div>${rows || '<div class="atlas-world-empty">No current geographies</div>'}`;
    details.classList.toggle('active', GEOGRAPHIES.some(([id]) => spatial.isActive(id)));
  }
  function adoptLegacyMenu(id, label, onOpen) {
    const details = document.getElementById(id);
    if (!details) return null;
    details.hidden = false;
    details.classList.remove('menu');
    details.classList.add('atlas-world-menu','atlas-world-legacy-menu');
    const summary = details.querySelector(':scope > summary');
    if (summary) summary.textContent = label;
    const pop = details.querySelector(':scope > .menu-pop');
    if (pop) pop.classList.add('atlas-world-menu-pop');
    details.addEventListener('toggle', () => {
      if (!details.open) return;
      closeMenus(details);
      onOpen?.();
    });
    return details;
  }
  async function ensureTime() {
    if (window.__potatoAtlasTime) return true;
    return Boolean(await window.__potatoAtlasLoadModule?.('Time', './3d-time.js'));
  }
  function applyProjection() {
    try { map.setProjection({type: projection === 'globe' ? 'globe' : 'mercator'}); }
    catch { projection = 'flat'; try { map.setProjection({type:'mercator'}); } catch {} }
    const url = new URL(location.href); url.searchParams.set('projection', projection); history.replaceState({}, '', url);
    const button = document.getElementById('atlasProjectionToggle');
    if (button) {
      button.textContent = projection === 'globe' ? '▭' : '◉';
      button.title = projection === 'globe' ? 'Projection · switch to flat map' : 'Projection · switch to globe';
      button.classList.toggle('active', projection === 'globe');
      button.setAttribute('aria-pressed', projection === 'globe' ? 'true' : 'false');
    }
    window.dispatchEvent(new CustomEvent('potato-atlas-projection-change', {detail:{mode:projection}}));
    renderContext();
  }
  window.__potatoAtlasProjection = {get:()=>projection,set(mode){projection=mode==='globe'?'globe':'flat';applyProjection();return projection;},toggle(){projection=projection==='globe'?'flat':'globe';applyProjection();return projection;}};

  function renderSummary(view = activeView) {
    const node = document.getElementById('atlasWorldResult');
    if (!node) return;
    const active = layers.active();
    if (!active.length) { node.hidden = true; node.textContent = ''; return; }
    node.hidden = false;
    const setCount = query.activeSetCount();
    const matchCount = Number(view?.matchCount);
    node.textContent = setCount && Number.isFinite(matchCount) ? `${matchCount} countries` : `${active.length} layer${active.length===1?'':'s'}`;
  }
  function renderContext(view = activeView) {
    const node = document.getElementById('atlasWorldContext');
    if (!node) return;
    const currentEntries = layers.active().map(id => layers.get(id)).filter(Boolean);
    const scalar = view?.scalar || currentEntries.find(entry => entry.kind === 'scalar') || null;
    const sets = view?.sets || currentEntries.filter(entry => entry.kind === 'set');
    const pinned = window.__potatoAtlasSelection?.current?.pinnedCodes || window.__potatoAtlasSelection?.current?.selectedCodes || [];
    const relationMode = view?.relationMode || window.__potatoAtlasSelection?.getRelationMode?.() || 'all';
    const currentTime = view?.timeState || timeState;
    if (!currentEntries.length && !pinned.length && relationMode === 'all' && (!currentTime || currentTime.mode === 'current')) {
      node.hidden = true; node.innerHTML = ''; return;
    }
    const lines = [];
    if (scalar) {
      lines.push(`<div><span>Color</span><b>${esc(scalar.label)}</b></div>`);
      const coverage = view?.coverage;
      if (coverage) {
        const covered = Number(coverage.coverage ?? 0), countries = Number(coverage.countries ?? coverage.country_count ?? 0);
        if (countries) lines.push(`<div><span>Coverage</span><b>${covered}/${countries} countries</b></div>`);
        if (coverage.period_min || coverage.period_max) {
          const period = coverage.period_min === coverage.period_max ? coverage.period_max : `${coverage.period_min || '?'}–${coverage.period_max || '?'}`;
          lines.push(`<div><span>Period</span><b>${esc(period)}</b></div>`);
        }
      }
    }
    if (sets.length) {
      const labels = sets.slice(0,3).map(entry => entry.label).join(' · ');
      lines.push(`<div><span>Sets</span><b>${esc(labels)}${sets.length>3?` +${sets.length-3}`:''}</b></div>`);
      const matchCount = Number(view?.matchCount);
      lines.push(`<div><span>Matches</span><b>${esc((view?.memberships?.mode || query.getMode() || 'any').toUpperCase())} · ${Number.isFinite(matchCount) ? `${matchCount} countries` : 'calculating…'}</b></div>`);
    }
    if (view?.code) lines.push(`<div><span>Active</span><b>${esc(view.code)}</b></div>`);
    if (pinned.length) lines.push(`<div><span>Pinned</span><b>${pinned.length} countr${pinned.length===1?'y':'ies'}</b></div>`);
    if (relationMode !== 'all') lines.push(`<div><span>Connections</span><b>${esc(relationLabel(relationMode))}</b></div>`);
    lines.push(`<div><span>Projection</span><b>${projection === 'globe' ? 'Globe' : 'Flat'}</b></div>`);
    if (currentTime) lines.push(`<div><span>Time</span><b>${esc(timeLabel(currentTime))}</b></div>`);
    node.innerHTML = `<small>Current map view</small>${lines.join('')}`;
    node.hidden = false;
  }
  function syncMenus() {
    AXES.forEach(id => document.querySelector(`[data-layer-id="${CSS.escape(id)}"]`)?.classList.toggle('active', layers.isActive(id)));
    document.querySelectorAll('#atlasWorldBar .atlas-world-menu[data-family]').forEach(menuNode => {
      const family = menuNode.dataset.family;
      const pop = menuNode.querySelector('.atlas-world-menu-pop');
      if (!pop) return;
      if (family === 'relations') {
        const mode = window.__potatoAtlasSelection?.getRelationMode?.() || 'all';
        pop.innerHTML = `<div class="atlas-world-static"><span>Active-country connections</span><small>bounded context</small></div>${RELATIONS.map(([id,label])=>`<button type="button" class="atlas-world-option${mode===id?' active':''}" data-relation-mode="${esc(id)}"><span>${esc(label)}</span></button>`).join('')}`;
        const summary = menuNode.querySelector(':scope > summary'); if (summary) summary.textContent = 'Relations';
        menuNode.classList.toggle('active', mode !== 'all');
        return;
      }
      const rows = entries(family);
      pop.innerHTML = rows.map(entry => `<button type="button" class="atlas-world-option${layers.isActive(entry.id)?' active':''}" data-layer-option="${esc(entry.id)}">${entry.color?`<i style="--layer-color:${esc(entry.color)}"></i>`:''}<span>${esc(entry.label)}</span></button>`).join('') || '<div class="atlas-world-empty">No current layers</div>';
      const count = rows.filter(entry => layers.isActive(entry.id)).length;
      menuNode.classList.toggle('active', count > 0);
    });
    const queryBox = document.getElementById('atlasWorldQuery');
    if (queryBox) {
      queryBox.hidden = query.activeSetCount() < 2;
      queryBox.querySelectorAll('[data-query-mode]').forEach(button => button.classList.toggle('active', button.dataset.queryMode === query.getMode()));
    }
    syncGeographyMenu();
    renderSummary(); renderContext();
  }
  function installStyle() {
    if (document.getElementById('atlasWorldBarStyle')) return;
    const style = document.createElement('style'); style.id = 'atlasWorldBarStyle';
    style.textContent = `body.atlas-registry-ui .top{min-height:50px;overflow:visible!important}body.atlas-registry-ui .brand small{display:none}body.atlas-registry-ui .brand b{font-size:15px}#atlasWorldBarHost{display:flex;align-items:center;flex:1 1 auto;min-width:0;overflow:visible}#atlasWorldBar{position:relative;display:flex;align-items:center;gap:5px;width:100%;min-width:0;padding:0;background:transparent;border:0;box-shadow:none}#atlasWorldBar button,#atlasWorldBar summary{min-height:30px;padding:5px 8px;border-radius:7px;background:#111818;border:1px solid #2d3939;color:#e9efea;font-size:11px;line-height:1;white-space:nowrap}#atlasWorldBar button.active,#atlasWorldBar .atlas-world-menu.active>summary,#atlasWorldBar .atlas-world-menu[open]>summary{border-color:#7a9892;color:#dff1d8;background:#172120}#atlasWorldBar .atlas-axis-button{font-weight:800;min-width:31px}.atlas-world-menu{position:relative}.atlas-world-menu>summary{list-style:none;cursor:pointer}.atlas-world-menu>summary::-webkit-details-marker{display:none}.atlas-world-menu-pop{position:absolute;left:0;top:calc(100% + 7px);z-index:30;min-width:210px;max-width:280px;max-height:58vh;overflow:auto;padding:6px;background:#0b1010f7;border:1px solid #344343;border-radius:10px;box-shadow:0 12px 28px #000a}.atlas-world-legacy-menu>.atlas-world-menu-pop{right:0;left:auto}.atlas-world-option{display:flex!important;align-items:center;gap:7px;width:100%;margin:2px 0;text-align:left}.atlas-world-option i{width:9px;height:9px;border-radius:3px;background:var(--layer-color);flex:0 0 auto}.atlas-world-option.active:after{content:'✓';margin-left:auto;color:#bbdc8a}.atlas-world-static{display:flex;justify-content:space-between;gap:10px;padding:7px 6px;font-size:11px}.atlas-world-static small,.atlas-world-empty{color:#9aa6a0;font-size:9px}#atlasWorldQuery{display:flex;gap:2px;padding-left:4px;border-left:1px solid #2d3939}#atlasWorldResult{width:92px;flex:0 0 92px;padding:0 4px;color:#aab4aa;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}#atlasWorldContext{position:absolute;left:10px;bottom:10px;z-index:7;width:min(290px,calc(100% - 20px));padding:8px 10px;background:#080b0bdc;border:1px solid #30403e;border-radius:10px;box-shadow:0 6px 22px #0007;pointer-events:none}#atlasWorldContext[hidden]{display:none!important}#atlasWorldContext>small{display:block;margin-bottom:3px;color:#77857f;font-size:8px;text-transform:uppercase;letter-spacing:.1em}#atlasWorldContext>div{display:flex;justify-content:space-between;gap:10px;padding:2px 0;font-size:10px}#atlasWorldContext span{color:#92a099}#atlasWorldContext b{max-width:190px;text-align:right;font-weight:600;color:#d7dfda;overflow-wrap:anywhere}#atlasWorldBar #viewMenu #globe,#atlasWorldBar #traceMenu #relations{display:none}@media(max-width:1150px){#atlasWorldResult{display:none}.top-home{font-size:11px}}@media(max-width:900px){body.atlas-registry-ui .top{overflow-x:auto!important;overflow-y:visible!important}#atlasWorldBarHost{flex:0 0 auto}#atlasWorldBar{width:max-content}.atlas-world-menu-pop{position:fixed;left:8px!important;right:8px!important;top:52px;max-width:none}.top input{width:145px;min-width:130px}#atlasWorldContext{left:8px;bottom:58px;width:min(270px,calc(100% - 16px))}}`;
    document.head.appendChild(style);
  }
  function install() {
    if (document.getElementById('atlasWorldBar')) return;
    installStyle(); document.body.classList.add('atlas-registry-ui');
    const host = document.getElementById('atlasWorldBarHost') || document.querySelector('.top');
    if (!host) return;
    const bar = document.createElement('div'); bar.id='atlasWorldBar'; bar.setAttribute('role','toolbar'); bar.setAttribute('aria-label','World map analytical layers');
    AXES.forEach(id => {
      const entry = layers.get(id); if (!entry || entry.availability !== 'current') return;
      const button=document.createElement('button'); button.type='button'; button.className='atlas-axis-button'; button.dataset.layerId=id; button.title=entry.label; button.textContent=entry.label.slice(0,1).toUpperCase(); button.addEventListener('click',()=>layers.toggle(id)); bar.appendChild(button);
    });
    FAMILIES.forEach(([family,label]) => bar.appendChild(menu(family,label)));
    const geography=geographyMenu(); bar.appendChild(geography);
    const analyze=adoptLegacyMenu('traceMenu','Analyze'); if (analyze) bar.appendChild(analyze);
    const time=adoptLegacyMenu('timeMenu','Time',ensureTime); if (time) bar.appendChild(time);
    const view=adoptLegacyMenu('viewMenu','View'); if (view) bar.appendChild(view);
    const interior=document.getElementById('interior'); if (interior && view?.querySelector('.atlas-world-menu-pop')) { interior.textContent='Interior modules'; view.querySelector('.atlas-world-menu-pop').prepend(interior); }
    const projectionButton=document.createElement('button'); projectionButton.id='atlasProjectionToggle'; projectionButton.type='button'; projectionButton.addEventListener('click',()=>window.__potatoAtlasProjection.toggle()); bar.appendChild(projectionButton);
    const queryBox=document.createElement('div'); queryBox.id='atlasWorldQuery'; queryBox.hidden=true; queryBox.innerHTML='<button type="button" data-query-mode="any">ANY</button><button type="button" data-query-mode="all">ALL</button>'; queryBox.addEventListener('click',event=>{const b=event.target.closest('[data-query-mode]');if(b)query.setMode(b.dataset.queryMode);}); bar.appendChild(queryBox);
    const result=document.createElement('span'); result.id='atlasWorldResult'; result.hidden=true; bar.appendChild(result);
    const reset=document.createElement('button'); reset.id='atlasWorldReset'; reset.type='button'; reset.textContent='×'; reset.title='Clear analytical layers'; reset.addEventListener('click',()=>window.__potatoAtlasCompositor?.reset?.()); bar.appendChild(reset);
    host.appendChild(bar);
    const mapHost=document.querySelector('.mapwrap'); if (mapHost && !document.getElementById('atlasWorldContext')) { const context=document.createElement('aside'); context.id='atlasWorldContext'; context.hidden=true; context.setAttribute('aria-label','Current map view'); mapHost.appendChild(context); }
    applyProjection(); syncMenus();
  }

  window.addEventListener('potato-atlas-layer-change', syncMenus);
  window.addEventListener('potato-atlas-query-change', syncMenus);
  window.addEventListener('potato-atlas-query-result-change', () => window.__potatoAtlasActiveView?.refresh?.('query-result'));
  window.addEventListener('potato-atlas-composition-change', () => window.__potatoAtlasActiveView?.refresh?.('composition'));
  window.addEventListener('potato-atlas-working-selection-change', () => window.__potatoAtlasActiveView?.refresh?.('selection'));
  window.addEventListener('potato-atlas-pin-change', () => window.__potatoAtlasActiveView?.refresh?.('pins'));
  window.addEventListener('potato-atlas-relation-mode-change', syncMenus);
  window.addEventListener('potato-atlas-spatial-overlay-change', () => syncGeographyMenu());
  window.addEventListener('potato-atlas-active-view-change', event => { activeView=event.detail||null; renderSummary(activeView); renderContext(activeView); });
  window.addEventListener('atlas-time-change', event => { timeState=event.detail||null; renderContext(); window.__potatoAtlasActiveView?.refresh?.('time'); });
  window.addEventListener('potato-atlas-projection-change', renderContext);
  install();
})().catch(error => console.warn('World Map toolbar unavailable:', error));
