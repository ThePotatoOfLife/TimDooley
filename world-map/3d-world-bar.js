(async () => {
  if (!window.__potatoAtlasUrlState) await import('./3d-url-state.js');
  const urlState = window.__potatoAtlasUrlState;
  urlState.claim('projection', ['projection']);
  const layers = window.__potatoAtlasLayers;
  const query = window.__potatoAtlasQuery;
  const map = window.__potatoAtlasMap;
  if (!layers || !query || !map) throw new Error('World toolbar requires map, layers and query APIs.');
  await layers.ready;

  const AXES = ['axis.north','axis.west','axis.east','axis.south'];
  const COUNTRY_FAMILIES = [['groups','Groups & alliances'],['religion','Religion'],['stats','Numbers']];
  const RELATIONS = [['all','All connections'],['money','Money'],['systems','Systems'],['institutions','Institutions'],['project','Project'],['other','Other']];
  const spatial = window.__potatoAtlasSpatialOverlays;
  const CURRENT_CONTEXT = [
    ['conflict.active-theatres','Active conflicts · 2 Oct 2026'],
  ];
  const HISTORY_CONTEXT = [
    ['father.mesopotamia-core','Mesopotamia · historical region'],
    ['physical.tigris-euphrates-basin','Tigris–Euphrates basin'],
    ['father.eden-context','Eden · hypothesis marker'],
  ];
  const GEOGRAPHIES = [...CURRENT_CONTEXT, ...HISTORY_CONTEXT];
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const entries = family => layers.entries(family, {availableOnly:true, ordinaryOnly:true});
  let projection = new URL(location.href).searchParams.get('projection') === 'globe' ? 'globe' : 'flat';
  let activeView = window.__potatoAtlasActiveView?.current || null;
  let timeState = window.__potatoAtlasTime?.getState?.() || null;
  let lastContextMarkup = '';

  function relationLabel(mode) {
    return RELATIONS.find(([id]) => id === mode)?.[1] || mode || 'All context';
  }
  function timeLabel(state) {
    if (!state || state.mode === 'current') return 'Current';
    if (state.label) return state.label;
    if (state.mode === 'as_of') return `As of ${state.time || '—'}`;
    return `${state.time || '—'} → ${state.time2 || '—'}`;
  }
  function humanMeta(value) {
    return String(value || '').replaceAll('_', ' ').trim();
  }
  function layerMeta(entry) {
    if (!entry) return '';
    return [humanMeta(entry.epistemic_type), humanMeta(entry.visual_channel)].filter(Boolean).join(' · ');
  }
  function layerSource(entry) {
    const owner = String(entry?.source_owner || '').trim();
    return owner ? owner.replace(/^data\//, '').replace(/\.json$/i, '') : '';
  }
  function layerTitle(entry) {
    return [entry?.label, layerMeta(entry), layerSource(entry), entry?.notes].filter(Boolean).join(' · ');
  }
  function closeMenus(current) {
    document.querySelectorAll('#atlasWorldBar details[open]').forEach(menu => { if (menu !== current) menu.removeAttribute('open'); });
  }
  function countryLayersMenu() {
    const details = document.createElement('details');
    details.id = 'atlasCountriesMenu';
    details.className = 'atlas-world-menu';
    details.innerHTML = '<summary>Countries</summary><div class="atlas-world-menu-pop"></div>';
    details.addEventListener('toggle', () => { if (details.open) { closeMenus(details); syncCountryLayersMenu(details); } });
    details.addEventListener('click', event => {
      const layerButton = event.target.closest('[data-layer-option]');
      if (layerButton) layers.toggle(layerButton.dataset.layerOption);
      const axisButton = event.target.closest('[data-axis-layer]');
      if (axisButton) layers.toggle(axisButton.dataset.axisLayer);
    });
    return details;
  }
  function syncCountryLayersMenu(details = document.getElementById('atlasCountriesMenu')) {
    if (!details) return;
    const pop = details.querySelector('.atlas-world-menu-pop');
    if (!pop) return;
    const sections = COUNTRY_FAMILIES.map(([family,label]) => {
      const rows = entries(family);
      const buttons = rows.map(entry => {
        const active = layers.isActive(entry.id);
        const encoding = entry.kind === 'scalar' ? 'map color + exact value' : entry.kind === 'set' ? 'membership pattern' : (entry.visual_channel || entry.kind || 'layer');
        return `<button type="button" class="atlas-world-option${active?' active':''}" data-layer-option="${esc(entry.id)}" aria-pressed="${active?'true':'false'}" aria-label="${esc(`${entry.label}, ${encoding}`)}" title="${esc(layerTitle(entry))}">${entry.color?`<i aria-hidden="true" style="--layer-color:${esc(entry.color)}"></i>`:''}<span>${esc(entry.label)}<small>${esc(layerMeta(entry))}</small></span></button>`;
      }).join('');
      return buttons ? `<section class="atlas-world-section"><div class="menu-title">${esc(label)}</div>${buttons}</section>` : '';
    }).join('');
    const axes = AXES.map(id => {
      const entry = layers.get(id);
      if (!entry || entry.availability !== 'current') return '';
      const active = layers.isActive(id);
      return `<button type="button" class="atlas-world-option${active?' active':''}" data-axis-layer="${esc(id)}" aria-pressed="${active?'true':'false'}" title="${esc(layerTitle(entry))}"><span>${esc(entry.label)}<small>Project lens</small></span></button>`;
    }).join('');
    pop.innerHTML = `<div class="atlas-world-static"><span>Compare countries</span><small>Choose one question, then click the map</small></div>${sections}<section class="atlas-world-section"><div class="menu-title">Project lenses</div>${axes}</section>`;
    const active = COUNTRY_FAMILIES.some(([family]) => entries(family).some(entry => layers.isActive(entry.id))) || AXES.some(id => layers.isActive(id));
    details.classList.toggle('active', active);
  }
  function nowMenu() {
    const details = document.createElement('details');
    details.id = 'atlasNowMenu';
    details.className = 'atlas-world-menu';
    details.innerHTML = '<summary>Now</summary><div class="atlas-world-menu-pop"></div>';
    details.addEventListener('toggle', () => { if (details.open) { closeMenus(details); syncNowMenu(details); } });
    details.addEventListener('click', async event => {
      const button = event.target.closest('[data-now-overlay]');
      if (!button || !spatial) return;
      const id = button.dataset.nowOverlay;
      const wasActive = spatial.isActive(id);
      await spatial.toggle(id);
      if (!wasActive) spatial.fit(id);
      syncNowMenu(details);
    });
    return details;
  }
  function syncNowMenu(details = document.getElementById('atlasNowMenu')) {
    if (!details || !spatial) return;
    const pop = details.querySelector('.atlas-world-menu-pop');
    if (!pop) return;
    const rows = CURRENT_CONTEXT.map(([id,label]) => {
      const entry = spatial.get(id);
      if (!entry || entry.availability !== 'current') return '';
      const active = spatial.isActive(id);
      return `<button type="button" class="atlas-world-option${active?' active':''}" data-now-overlay="${esc(id)}" aria-pressed="${active?'true':'false'}"><span>${esc(label)}<small>Broad, dated context — not live tactical tracking</small></span></button>`;
    }).join('');
    pop.innerHTML = `<div class="atlas-world-static"><span>What is happening now?</span><small>Dated current-world context</small></div>${rows || '<div class="atlas-world-empty">No current context available</div>'}`;
    details.classList.toggle('active', CURRENT_CONTEXT.some(([id]) => spatial.isActive(id)));
  }
  function installHistoryGeographies(details) {
    const pop = details?.querySelector('.atlas-world-menu-pop');
    if (!pop || pop.querySelector('#atlasHistoryGeographies')) return;
    const block = document.createElement('section');
    block.id = 'atlasHistoryGeographies';
    block.className = 'atlas-world-section';
    block.innerHTML = '<div class="menu-title">Places through history</div><div data-history-geographies></div><div class="menu-sep"></div>';
    pop.prepend(block);
    details.addEventListener('click', async event => {
      const button = event.target.closest('[data-history-overlay]');
      if (!button || !spatial) return;
      const id = button.dataset.historyOverlay;
      const wasActive = spatial.isActive(id);
      await spatial.toggle(id);
      if (!wasActive) spatial.fit(id);
      syncHistoryGeographies(details);
    });
    syncHistoryGeographies(details);
  }
  function syncHistoryGeographies(details = document.getElementById('timeMenu')) {
    const host = details?.querySelector('[data-history-geographies]');
    if (!host || !spatial) return;
    host.innerHTML = HISTORY_CONTEXT.map(([id,label]) => {
      const entry = spatial.get(id);
      if (!entry || entry.availability !== 'current') return '';
      const active = spatial.isActive(id);
      const note = id === 'father.eden-context' ? 'Hypothesis, not an exact site' : String(entry.epistemic_type || '').replaceAll('_',' ');
      return `<button type="button" class="atlas-world-option${active?' active':''}" data-history-overlay="${esc(id)}" aria-pressed="${active?'true':'false'}"><span>${esc(label)}<small>${esc(note)}</small></span></button>`;
    }).join('');
    details?.classList.toggle('active', HISTORY_CONTEXT.some(([id]) => spatial.isActive(id)) || (timeState && timeState.mode !== 'current'));
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
  function installAnalyzeRelations(details) {
    const pop = details?.querySelector('.atlas-world-menu-pop');
    if (!pop || pop.querySelector('#atlasAnalyzeRelations')) return;
    const block = document.createElement('div');
    block.id = 'atlasAnalyzeRelations';
    block.className = 'atlas-analyze-relations';
    block.innerHTML = `<div class="atlas-world-static"><span>How is this place connected?</span><small>Select a country, then filter the links</small></div><div class="atlas-analyze-mode-grid">${RELATIONS.map(([id,label])=>`<button type="button" data-relation-mode="${esc(id)}" aria-pressed="false">${esc(label)}</button>`).join('')}</div><div class="menu-sep"></div>`;
    pop.prepend(block);
    details.addEventListener('click', event => {
      const button = event.target.closest('[data-relation-mode]');
      if (button) window.__potatoAtlasSelection?.setRelationMode?.(button.dataset.relationMode);
    });
  }
  function syncAnalyzeRelations(details = document.getElementById('traceMenu')) {
    if (!details) return;
    const mode = window.__potatoAtlasSelection?.getRelationMode?.() || 'all';
    details.querySelectorAll('[data-relation-mode]').forEach(button => {
      const active = button.dataset.relationMode === mode;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
    details.classList.toggle('active', mode !== 'all');
  }
  async function ensureTime() {
    if (window.__potatoAtlasTime) return true;
    return Boolean(await window.__potatoAtlasLoadModule?.('Time', './3d-time.js'));
  }
  function applyProjection() {
    try { map.setProjection({type: projection === 'globe' ? 'globe' : 'mercator'}); }
    catch { projection = 'flat'; try { map.setProjection({type:'mercator'}); } catch {} }
    urlState.patch('projection', { set:{ projection } });
    const button = document.getElementById('atlasProjectionToggle');
    if (button) {
      button.textContent = projection === 'globe' ? 'Flat map' : 'Globe view';
      button.title = projection === 'globe' ? 'Switch to a flat map' : 'Switch to a globe';
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
    const physicalIds = window.__potatoAtlasPhysicalLayers?.active?.() || [];
    const geographyIds = window.__potatoAtlasSpatialOverlays?.active?.() || [];
    const evidenceIds = window.__potatoAtlasEvidenceLayers?.active?.() || [];
    const scalar = view?.scalar || currentEntries.find(entry => entry.kind === 'scalar') || null;
    const sets = view?.sets || currentEntries.filter(entry => entry.kind === 'set');
    const currentSelection = window.__potatoAtlasSelection?.current || {};
    const activeCode = currentSelection.activeCode || currentSelection.code || '';
    const pinned = currentSelection.pinnedCodes || currentSelection.selectedCodes || [];
    const relationMode = view?.relationMode || window.__potatoAtlasSelection?.getRelationMode?.() || 'all';
    const currentTime = view?.timeState || timeState;
    if (!currentEntries.length && !physicalIds.length && !geographyIds.length && !evidenceIds.length && !pinned.length && relationMode === 'all' && (!currentTime || currentTime.mode === 'current')) {
      node.hidden = true;
      if (lastContextMarkup) { node.innerHTML = ''; lastContextMarkup = ''; }
      return;
    }
    const lines = [];
    if (scalar) {
      lines.push(`<div><span>Color</span><b>${esc(scalar.label)}</b></div>`);
      lines.push('<div><span>Encoding</span><b>Color fill + exact value text</b></div>');
      const semantic = layerMeta(scalar);
      if (semantic) lines.push(`<div><span>Layer type</span><b>${esc(semantic)}</b></div>`);
      const source = layerSource(scalar);
      if (source) lines.push(`<div><span>Source owner</span><b>${esc(source)}</b></div>`);
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
      lines.push('<div><span>Encoding</span><b>Pattern + membership text</b></div>');
      const semantics = [...new Set(sets.map(layerMeta).filter(Boolean))].join(' · ');
      if (semantics) lines.push(`<div><span>Set types</span><b>${esc(semantics)}</b></div>`);
      const matchCount = Number(view?.matchCount);
      lines.push(`<div><span>Matches</span><b>${esc((view?.memberships?.mode || query.getMode() || 'any').toUpperCase())} · ${Number.isFinite(matchCount) ? `${matchCount} countries` : 'calculating…'}</b></div>`);
    }
    if (pinned.length) lines.push(`<div><span>Pinned</span><b>${pinned.length} countr${pinned.length===1?'y':'ies'}</b></div>`);
    if (relationMode !== 'all') {
      const relation = relationLabel(relationMode);
      lines.push(`<div><span>Connections</span><b>${esc(activeCode ? relation : `${relation} · select a country`)}</b></div>`);
    }
    const compactIds = ids => ids.slice(0, 2).map(id => String(id).split('.').at(-1).replaceAll('-', ' ')).join(' · ') + (ids.length > 2 ? ` +${ids.length - 2}` : '');
    if (physicalIds.length) lines.push(`<div><span>Physical</span><b>${esc(compactIds(physicalIds))}</b></div>`);
    if (geographyIds.length) lines.push(`<div><span>Map context</span><b>${esc(compactIds(geographyIds))}</b></div>`);
    if (evidenceIds.length) lines.push(`<div><span>Evidence</span><b>${esc(compactIds(evidenceIds))}</b></div>`);
    const freshnessRows = window.__potatoAtlasFreshness?.active?.() || [];
    if (freshnessRows.length) {
      const compactFreshness = freshnessRows.slice(0, 3).map(row => {
        const state=row.freshness || {};
        const asOf=state.asOf ? ` (${state.asOf})` : '';
        return `${row.label}: ${state.label || 'Unknown vintage'}${asOf}`;
      });
      lines.push(`<div><span>Data status</span><b>${esc(compactFreshness.join(' · '))}${freshnessRows.length > 3 ? ` +${freshnessRows.length - 3}` : ''}</b></div>`);
    }
    const projectionMeta = view?.projection;
    if (projectionMeta?.informationLoss?.length) {
      const loss = projectionMeta.informationLoss.slice(0, 2).join(' · ');
      lines.push(`<div><span>View omits</span><b>${esc(loss)}${projectionMeta.informationLoss.length > 2 ? ` +${projectionMeta.informationLoss.length - 2}` : ''}</b></div>`);
    }
    if (projectionMeta?.reconstructability) {
      const label = projectionMeta.reconstructability === 'source-linked' ? 'Source-linked' : 'Partial';
      lines.push(`<div><span>Reconstructability</span><b>${esc(label)}</b></div>`);
    }
    lines.push(`<div><span>Projection</span><b>${projection === 'globe' ? 'Globe' : 'Flat'}</b></div>`);
    if (currentTime) lines.push(`<div><span>Time</span><b>${esc(timeLabel(currentTime))}</b></div>`);
    const markup = `<small>Current map view</small>${lines.join('')}`;
    if (markup !== lastContextMarkup) {
      node.innerHTML = markup;
      lastContextMarkup = markup;
    }
    node.hidden = false;
  }
  function syncMenus() {
    syncCountryLayersMenu();
    syncNowMenu();
    syncHistoryGeographies();
    const queryBox = document.getElementById('atlasWorldQuery');
    if (queryBox) {
      queryBox.hidden = query.activeSetCount() < 2;
      queryBox.querySelectorAll('[data-query-mode]').forEach(button => button.classList.toggle('active', button.dataset.queryMode === query.getMode()));
    }
    syncAnalyzeRelations();
    renderSummary(); renderContext();
  }
  function installStyle() {
    if (document.getElementById('atlasWorldBarStyle')) return;
    const style = document.createElement('style'); style.id = 'atlasWorldBarStyle';
    style.textContent = `body.atlas-registry-ui .top{min-height:46px;overflow:visible!important}body.atlas-registry-ui .brand small{display:none}body.atlas-registry-ui .brand b{font-size:15px}body.atlas-registry-ui .quick-actions{display:none}#atlasWorldBarHost{display:flex;align-items:center;flex:1 1 auto;min-width:0;overflow:visible}#atlasWorldBar{position:relative;display:flex;align-items:center;gap:4px;width:100%;min-width:0;padding:0;background:transparent;border:0;box-shadow:none}#atlasWorldBar button,#atlasWorldBar summary{min-height:29px;padding:5px 8px;border-radius:7px;background:#111818;border:1px solid #2d3939;color:#e9efea;font-size:11px;line-height:1;white-space:nowrap}#atlasWorldBar button.active,#atlasWorldBar .atlas-world-menu.active>summary,#atlasWorldBar .atlas-world-menu[open]>summary{border-color:#7a9892;color:#dff1d8;background:#172120}.atlas-world-menu{position:relative}.atlas-world-menu>summary{list-style:none;cursor:pointer}.atlas-world-menu>summary::-webkit-details-marker{display:none}.atlas-world-menu-pop{position:absolute;left:0;top:calc(100% + 7px);z-index:var(--atlas-z-menu,30);min-width:210px;max-width:280px;max-height:58vh;overflow:auto;padding:6px;background:var(--atlas-surface-menu-bg,#0b1010f7);border:1px solid var(--atlas-surface-border,#344343);border-radius:var(--atlas-surface-radius,11px);box-shadow:var(--atlas-surface-shadow,0 10px 28px #0009)}.atlas-world-legacy-menu>.atlas-world-menu-pop{right:0;left:auto}.atlas-world-option{display:flex!important;align-items:center;gap:7px;width:100%;margin:2px 0;text-align:left}.atlas-analyze-mode-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:3px}.atlas-analyze-mode-grid button{width:100%;text-align:left}.atlas-world-option>span{display:block;min-width:0;flex:1}.atlas-world-option>span>small{display:block;margin-top:3px;color:#87958e;font-size:9px;line-height:1.15;text-transform:none;white-space:normal}.atlas-world-option i{width:9px;height:9px;border-radius:3px;background:var(--layer-color);flex:0 0 auto}.atlas-world-option.active:after{content:'✓';margin-left:auto;color:#bbdc8a}.atlas-world-section{padding:2px 0 5px}.atlas-world-section+.atlas-world-section{border-top:1px solid #253130;margin-top:4px;padding-top:6px}.atlas-world-static{display:flex;justify-content:space-between;gap:10px;padding:7px 6px;font-size:11px}.atlas-world-static small,.atlas-world-empty{color:#9aa6a0;font-size:9px}#atlasWorldQuery{display:flex;gap:2px;padding-left:4px;border-left:1px solid #2d3939}#atlasWorldResult{width:82px;flex:0 0 82px;padding:0 3px;color:#aab4aa;font-size:9.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}#atlasWorldContext{position:absolute;left:10px;bottom:10px;z-index:var(--atlas-z-context,7);width:min(290px,calc(100% - 20px));padding:8px 10px;background:var(--atlas-surface-context-bg,#080b0be8);border:1px solid #30403e;border-radius:var(--atlas-surface-radius,11px);box-shadow:var(--atlas-surface-shadow,0 10px 28px #0009);pointer-events:none}#atlasWorldContext[hidden]{display:none!important}#atlasWorldContext>small{display:block;margin-bottom:3px;color:#77857f;font-size:8px;text-transform:uppercase;letter-spacing:.1em}#atlasWorldContext>div{display:flex;justify-content:space-between;gap:10px;padding:2px 0;font-size:10px}#atlasWorldContext span{color:#92a099}#atlasWorldContext b{max-width:190px;text-align:right;font-weight:600;color:#d7dfda;overflow-wrap:anywhere}#atlasWorldBar #viewMenu #globe,#atlasWorldBar #traceMenu #relations{display:none}@media(max-width:1150px){#atlasWorldResult{display:none}.top-home{font-size:11px}}@media(max-width:900px){body.atlas-registry-ui .top{overflow-x:auto!important;overflow-y:visible!important}#atlasWorldBarHost{flex:0 0 auto}#atlasWorldBar{width:max-content}.atlas-world-menu-pop{position:fixed;left:8px!important;right:8px!important;top:52px;max-width:none}.top input{width:145px;min-width:130px}#atlasWorldContext{left:8px;bottom:58px;width:min(270px,calc(100% - 16px))}}`;
    document.head.appendChild(style);
  }
  function install() {
    if (document.getElementById('atlasWorldBar')) return;
    installStyle(); document.body.classList.add('atlas-registry-ui');
    const host = document.getElementById('atlasWorldBarHost') || document.querySelector('.top');
    if (!host) return;
    const bar = document.createElement('div'); bar.id='atlasWorldBar'; bar.setAttribute('role','toolbar'); bar.setAttribute('aria-label','World map layers and controls');
    const countries=countryLayersMenu(); bar.appendChild(countries);
    const now=nowMenu(); bar.appendChild(now);
    const connections=adoptLegacyMenu('traceMenu','Connections'); if (connections) { installAnalyzeRelations(connections); bar.appendChild(connections); }
    const history=adoptLegacyMenu('timeMenu','History',async()=>{ await ensureTime(); syncHistoryGeographies(history); }); if (history) { installHistoryGeographies(history); bar.appendChild(history); }
    const mapMenu=adoptLegacyMenu('viewMenu','Map'); if (mapMenu) bar.appendChild(mapMenu);

    const queryBox=document.createElement('div'); queryBox.id='atlasWorldQuery'; queryBox.hidden=true; queryBox.innerHTML='<button type="button" data-query-mode="any">ANY</button><button type="button" data-query-mode="all">ALL</button>'; queryBox.addEventListener('click',event=>{const b=event.target.closest('[data-query-mode]');if(b)query.setMode(b.dataset.queryMode);}); bar.appendChild(queryBox);
    const result=document.createElement('span'); result.id='atlasWorldResult'; result.hidden=true; bar.appendChild(result);

    if (mapMenu?.querySelector('.atlas-world-menu-pop')) {
      const pop=mapMenu.querySelector('.atlas-world-menu-pop');
      const divider=document.createElement('div'); divider.className='menu-sep'; pop.appendChild(divider);
      const title=document.createElement('div'); title.className='menu-title'; title.textContent='Workspace'; pop.appendChild(title);
      const compare=document.getElementById('compare'); if (compare) { compare.textContent='Compare countries'; compare.title='Add countries to a comparison'; pop.appendChild(compare); }
      const inspect=document.getElementById('panelToggle'); if (inspect) { inspect.textContent='Details panel'; inspect.title='Show or hide the deeper details panel'; pop.appendChild(inspect); }
      const projectionButton=document.createElement('button'); projectionButton.id='atlasProjectionToggle'; projectionButton.type='button'; projectionButton.addEventListener('click',()=>window.__potatoAtlasProjection.toggle()); pop.appendChild(projectionButton);
      const reset=document.createElement('button'); reset.id='atlasWorldReset'; reset.type='button'; reset.textContent='Reset map'; reset.title='Clear map layers, selections and investigation state'; reset.setAttribute('aria-label','Reset map layers and investigation state'); reset.addEventListener('click',()=>window.__potatoAtlasCompositor?.reset?.()); pop.appendChild(reset);
    }
    const interior=document.getElementById('interior'); if (interior && mapMenu?.querySelector('.atlas-world-menu-pop')) { interior.textContent='Extra map modules'; mapMenu.querySelector('.atlas-world-menu-pop').prepend(interior); }
    host.appendChild(bar);
    const mapHost=document.querySelector('.mapwrap'); if (mapHost && !document.getElementById('atlasWorldContext')) { const context=document.createElement('aside'); context.id='atlasWorldContext'; context.hidden=true; context.setAttribute('aria-label','Current map view'); context.setAttribute('role','status'); context.setAttribute('aria-live','polite'); context.setAttribute('aria-atomic','true'); mapHost.appendChild(context); }
    applyProjection(); syncMenus();
  }

  window.addEventListener('potato-atlas-layer-change', syncMenus);
  window.addEventListener('potato-atlas-query-change', syncMenus);
  window.addEventListener('potato-atlas-query-result-change', () => window.__potatoAtlasActiveView?.refresh?.('query-result'));
  window.addEventListener('potato-atlas-composition-change', () => window.__potatoAtlasActiveView?.refresh?.('composition'));
  window.addEventListener('potato-atlas-working-selection-change', () => window.__potatoAtlasActiveView?.refresh?.('selection'));
  window.addEventListener('potato-atlas-pin-change', () => window.__potatoAtlasActiveView?.refresh?.('pins'));
  window.addEventListener('potato-atlas-relation-mode-change', syncMenus);
  window.addEventListener('potato-atlas-spatial-overlay-change', () => { syncNowMenu(); syncHistoryGeographies(); renderContext(); });
  window.addEventListener('potato-atlas-evidence-layer-change', () => renderContext());
  window.addEventListener('potato-atlas-places-change', () => renderContext());
  window.addEventListener('potato-atlas-places-ready', () => renderContext());
  window.addEventListener('potato-atlas-freshness-change', () => renderContext());
  window.addEventListener('potato-atlas-physical-layer-change', () => renderContext());
  window.addEventListener('potato-atlas-active-view-change', event => { activeView=event.detail||null; renderSummary(activeView); renderContext(activeView); });
  window.addEventListener('atlas-time-change', event => { timeState=event.detail||null; renderContext(); window.__potatoAtlasActiveView?.refresh?.('time'); });
  window.addEventListener('potato-atlas-projection-change', renderContext);
  install();
})().catch(error => console.warn('World Map toolbar unavailable:', error));